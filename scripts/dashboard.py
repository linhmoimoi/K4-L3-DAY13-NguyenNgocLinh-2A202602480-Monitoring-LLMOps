from __future__ import annotations

import json
import math
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from statistics import mean
from typing import Any
from urllib.parse import urlparse

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = REPO_ROOT / "data" / "logs.jsonl"
CONFIG_PATH = REPO_ROOT / "config" / "dashboard.yaml"
SLO_PATH = REPO_ROOT / "config" / "slo.yaml"
PANEL_SERIES = {
    "latency": ["p50_ms", "p95_ms", "p99_ms", "ttft_p95_ms"],
    "traffic": ["requests_per_minute"],
    "errors": ["error_rate_pct", "retrieval_success_rate_pct"],
    "cost": ["cumulative_cost_usd"],
    "tokens": ["cumulative_tokens_in", "cumulative_tokens_out"],
    "quality": ["mean_quality_score"],
}
COLORS = ["#2563eb", "#db2777", "#7c3aed", "#0891b2"]


def _read_records() -> list[dict[str, Any]]:
    if not LOG_PATH.exists():
        return []
    records = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        stamp = item.get("ts")
        if not isinstance(stamp, str):
            continue
        try:
            parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        except ValueError:
            continue
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        item["_time_utc"] = parsed.astimezone(timezone.utc)
        records.append(item)
    return records


def _percentile(values: list[float], percentile: int) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(percentile / 100 * len(ordered)) - 1)
    return round(ordered[index], 2)


def build_dashboard_payload(now: datetime | None = None) -> dict[str, Any]:
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))["dashboard"]
    slo = yaml.safe_load(SLO_PATH.read_text(encoding="utf-8"))
    end = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    start = end - timedelta(minutes=config["time_range_minutes"])
    minute_start = start.replace(second=0, microsecond=0)
    minute_end = end.replace(second=0, microsecond=0)
    minutes = []
    point = minute_start
    while point <= minute_end:
        minutes.append(point)
        point += timedelta(minutes=1)

    records = [r for r in _read_records() if start <= r["_time_utc"] <= end]
    buckets: dict[datetime, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        buckets[record["_time_utc"].replace(second=0, microsecond=0)].append(record)

    latency_points = []
    traffic_points = []
    error_points = []
    cost_points = []
    token_points = []
    quality_points = []
    total_cost = 0.0
    total_tokens_in = 0
    total_tokens_out = 0
    all_latencies = []
    all_ttft = []
    all_quality = []
    error_count = 0
    request_count = 0
    retrieval_successes = 0
    retrieval_attempts = 0
    error_breakdown: dict[str, int] = defaultdict(int)

    for minute in minutes:
        rows = buckets.get(minute, [])
        requests = [r for r in rows if r.get("event") == "request_received"]
        responses = [r for r in rows if r.get("event") == "response_sent"]
        failures = [r for r in rows if r.get("event") == "request_failed"]
        tool_rows = [
            r
            for r in rows
            if r.get("event") in {"response_sent", "request_failed"}
            and isinstance(r.get("tool_success"), bool)
        ]
        latencies = [float(r["latency_ms"]) for r in responses if isinstance(r.get("latency_ms"), (int, float))]
        ttft = [float(r["ttft_ms"]) for r in responses if isinstance(r.get("ttft_ms"), (int, float))]
        costs = [float(r["cost_usd"]) for r in responses if isinstance(r.get("cost_usd"), (int, float))]
        tokens_in = sum(int(r.get("tokens_in", 0) or 0) for r in responses)
        tokens_out = sum(int(r.get("tokens_out", 0) or 0) for r in responses)
        quality = [float(r["quality_score"]) for r in responses if isinstance(r.get("quality_score"), (int, float))]
        request_count += len(requests)
        error_count += len(failures)
        for failure in failures:
            error_breakdown[str(failure.get("error_type") or "unknown")] += 1
        retrieval_attempts += len(tool_rows)
        retrieval_successes += sum(r.get("tool_success") is True for r in tool_rows)
        all_latencies.extend(latencies)
        all_ttft.extend(ttft)
        all_quality.extend(quality)
        total_cost += sum(costs)
        total_tokens_in += tokens_in
        total_tokens_out += tokens_out
        stamp = minute.isoformat().replace("+00:00", "Z")

        latency_points.append({"time": stamp, "series": {
            "p50_ms": _percentile(latencies, 50),
            "p95_ms": _percentile(latencies, 95),
            "p99_ms": _percentile(latencies, 99),
            "ttft_p95_ms": _percentile(ttft, 95),
        }})
        traffic_points.append({"time": stamp, "series": {"requests_per_minute": len(requests)}})
        error_points.append({"time": stamp, "series": {
            "error_rate_pct": round(len(failures) / len(requests) * 100, 2) if requests else 0.0,
            "retrieval_success_rate_pct": round(sum(r.get("tool_success") is True for r in tool_rows) / len(tool_rows) * 100, 2) if tool_rows else None,
        }})
        cost_points.append({"time": stamp, "series": {"cumulative_cost_usd": round(total_cost, 6)}})
        token_points.append({"time": stamp, "series": {
            "cumulative_tokens_in": total_tokens_in,
            "cumulative_tokens_out": total_tokens_out,
        }})
        quality_points.append({"time": stamp, "series": {"mean_quality_score": round(mean(quality), 4) if quality else None}})

    thresholds = {panel["id"]: panel["threshold"] for panel in config["panels"]}
    titles = {panel["id"]: panel["title"] for panel in config["panels"]}
    units = {panel["id"]: panel["unit"] for panel in config["panels"]}
    points_by_id = {
        "latency": latency_points,
        "traffic": traffic_points,
        "errors": error_points,
        "cost": cost_points,
        "tokens": token_points,
        "quality": quality_points,
    }
    total_retrieval_rate = round(retrieval_successes / retrieval_attempts * 100, 2) if retrieval_attempts else None
    panels = []
    for panel_id in PANEL_SERIES:
        panel_threshold = thresholds[panel_id]
        threshold_text = f"{panel_threshold['aggregation']} {panel_threshold['operator']} {panel_threshold['value']} {units[panel_id]}"
        if panel_id == "errors":
            threshold_text += f"; retrieval success >= {slo['guardrails']['retrieval_success_rate_pct_min']} percent"
        panels.append({
            "id": panel_id,
            "title": titles[panel_id],
            "unit": units[panel_id],
            "threshold": panel_threshold,
            "threshold_text": threshold_text,
            "series_names": PANEL_SERIES[panel_id],
            "points": points_by_id[panel_id],
        })

    return {
        "title": config["title"],
        "time_range_minutes": config["time_range_minutes"],
        "refresh_seconds": config["refresh_seconds"],
        "from_utc": start.isoformat().replace("+00:00", "Z"),
        "to_utc": end.isoformat().replace("+00:00", "Z"),
        "record_count": len(records),
        "summary": {
            "requests": request_count,
            "responses": sum(r.get("event") == "response_sent" for r in records),
            "failures": error_count,
            "error_breakdown": dict(error_breakdown),
            "latency_p95_ms": _percentile(all_latencies, 95),
            "ttft_p95_ms": _percentile(all_ttft, 95),
            "total_cost_usd": round(total_cost, 6),
            "tokens_in": total_tokens_in,
            "tokens_out": total_tokens_out,
            "quality_mean": round(mean(all_quality), 4) if all_quality else None,
            "retrieval_success_rate_pct": total_retrieval_rate,
        },
        "panels": panels,
    }


INDEX_HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Day 13 LLMOps Dashboard</title>
<style>
:root{font-family:Inter,Segoe UI,Arial,sans-serif;color:#182230;background:#eef2f7}*{box-sizing:border-box}body{margin:0;padding:24px}
header{max-width:1500px;margin:0 auto 20px;display:flex;justify-content:space-between;align-items:flex-end;gap:18px}h1{font-size:25px;margin:0 0 5px}.sub{color:#667085;font-size:13px}.refresh{font-size:12px;color:#475467;text-align:right}
#panels{max-width:1500px;margin:auto;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.panel{background:white;border:1px solid #d9e0ea;border-radius:12px;padding:16px 18px;box-shadow:0 2px 8px #1018280a;min-width:0}.panel h2{font-size:17px;margin:0}.meta{color:#667085;font-size:11px;margin:4px 0 10px}.summary{color:#344054;font-size:12px;min-height:18px}.chart{width:100%;height:190px}.chart svg{width:100%;height:100%;overflow:visible}.legend{display:flex;flex-wrap:wrap;gap:10px;font-size:11px;color:#475467;margin-top:4px}.legend span:before{content:'';display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--c);margin-right:5px}.status{max-width:1500px;margin:12px auto;color:#667085;font-size:11px}
@media(max-width:900px){#panels{grid-template-columns:1fr}body{padding:12px}header{align-items:flex-start;flex-direction:column}}
</style></head><body><header><div><h1 id="title">K4-L3B Day 13 Monitoring &amp; LLMOps</h1><div class="sub" id="range">Loading UTC window…</div></div><div class="refresh" id="refresh"></div></header><main id="panels"></main><div class="status" id="status"></div>
<script>
const colors=['#2563eb','#db2777','#7c3aed','#0891b2'];
function esc(x){return String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function chart(panel){const pts=panel.points, names=panel.series_names, values=[];for(const p of pts)for(const n of names)if(Number.isFinite(p.series[n]))values.push(p.series[n]);const threshold=Number(panel.threshold.value);if(Number.isFinite(threshold))values.push(threshold);const ymax=Math.max(1,...values)*1.12,w=760,h=190,L=48,R=12,T=12,B=25,cw=w-L-R,ch=h-T-B;const y=v=>T+ch-(v/ymax)*ch,x=i=>L+(pts.length<2?cw/2:i* cw/(pts.length-1));let svg=`<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(panel.title)} chart">`;for(let j=0;j<=4;j++){const yy=T+j*ch/4,v=ymax*(1-j/4);svg+=`<line x1="${L}" y1="${yy}" x2="${w-R}" y2="${yy}" stroke="#e6eaf0"/><text x="${L-7}" y="${yy+4}" text-anchor="end" font-size="10" fill="#667085">${v.toFixed(v<10?1:0)}</text>`}if(Number.isFinite(threshold)){const yy=y(threshold);svg+=`<line x1="${L}" y1="${yy}" x2="${w-R}" y2="${yy}" stroke="#dc2626" stroke-dasharray="6 5" stroke-width="2"/>`}names.forEach((name,k)=>{let d='',open=false;pts.forEach((p,i)=>{const v=p.series[name];if(Number.isFinite(v)){d+=(open?' L':' M')+x(i).toFixed(1)+' '+y(v).toFixed(1);open=true}else open=false});svg+=`<path d="${d}" fill="none" stroke="${colors[k%colors.length]}" stroke-width="2.5" stroke-linejoin="round"/>`});const first=pts[0]?.time?.slice(11,16)||'',last=pts.at(-1)?.time?.slice(11,16)||'';svg+=`<text x="${L}" y="${h-5}" font-size="10" fill="#667085">${first} UTC</text><text x="${w-R}" y="${h-5}" text-anchor="end" font-size="10" fill="#667085">${last} UTC</text></svg>`;const legend=names.map((n,i)=>`<span style="--c:${colors[i%colors.length]}">${esc(n)}</span>`).join('')+(Number.isFinite(threshold)?'<span style="--c:#dc2626">threshold</span>':'');return `<div class="chart">${svg}</div><div class="legend">${legend}</div>`}
function render(d){document.title=d.title;document.getElementById('title').textContent=d.title;document.getElementById('range').textContent=`Last ${d.time_range_minutes} minutes | ${d.from_utc} to ${d.to_utc} | timestamps UTC`;document.getElementById('refresh').textContent=`Refresh every ${d.refresh_seconds}s | ${d.record_count} log records`;document.getElementById('panels').innerHTML=d.panels.map(p=>{const s=d.summary;let summary='';if(p.id==='latency')summary=`P95 ${s.latency_p95_ms??'—'} ms · TTFT P95 ${s.ttft_p95_ms??'—'} ms`;if(p.id==='traffic')summary=`${s.requests} requests in window`;if(p.id==='errors')summary=`${s.failures} failures · breakdown ${JSON.stringify(s.error_breakdown)} · retrieval success ${s.retrieval_success_rate_pct??'—'}%`;if(p.id==='cost')summary=`Total ${s.total_cost_usd} USD`;if(p.id==='tokens')summary=`Input ${s.tokens_in} · Output ${s.tokens_out} tokens`;if(p.id==='quality')summary=`Mean quality ${s.quality_mean??'—'} / 1`;return `<section class="panel"><h2>${esc(p.title)}</h2><div class="meta">Unit: ${esc(p.unit)} · Time range: ${d.time_range_minutes} min · Threshold: ${esc(p.threshold_text)}</div><div class="summary">${summary}</div>${chart(p)}</section>`}).join('');document.getElementById('status').textContent=`Updated ${new Date().toISOString()} · source data/logs.jsonl`}
async function refresh(){try{const r=await fetch('/data?now='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error(`HTTP ${r.status}`);render(await r.json())}catch(e){document.getElementById('status').textContent='Dashboard refresh failed: '+e}}
refresh();setInterval(refresh,30000);
</script></body></html>"""


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/data":
            body = json.dumps(build_dashboard_payload(), ensure_ascii=False).encode("utf-8")
            content_type = "application/json; charset=utf-8"
        elif path in {"/", "/index.html"}:
            body = INDEX_HTML.encode("utf-8")
            content_type = "text/html; charset=utf-8"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        return


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Local six-panel LLMOps dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8501)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    print(f"Dashboard available at http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
