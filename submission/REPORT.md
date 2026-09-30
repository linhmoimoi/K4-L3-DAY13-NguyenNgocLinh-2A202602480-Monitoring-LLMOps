# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:**
- **MSSV:**
- **Lớp:** K4-L3B
- **Repository URL:**
- **Commit SHA cuối:**
- **Challenge ID:**
- **T?n project Langfuse c? nh?n:** `day13-k4-l3b-2A202602480`

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/01-pytest.png` |
| Log validator | `evidence/02-log-validator.png` |
| Dashboard validator | `evidence/03-dashboard-validator.png` |
| Structured log | `evidence/04-structured-log.png` |
| PII redaction | `evidence/05-pii-redaction.png` |
| Trace list | `evidence/06-trace-list.png` |
| Trace waterfall | `evidence/07-trace-waterfall.png` |
| Trace metadata | `evidence/08-trace-metadata.png` |
| Prompt versions | `evidence/09-prompt-versions.png` |
| Prompt promote | `evidence/10a-prompt-promote.png` |
| Prompt rollback | `evidence/10b-prompt-rollback.png` |
| Dashboard runtime | `evidence/11-dashboard-overview.png` |
| Incident metric | `evidence/12-incident-metric.png` |
| Incident log | `evidence/13-incident-log.png` |
| Incident trace | `evidence/14-incident-trace.png` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 30/100 | | Baseline: thiếu required fields, correlation ID và enrichment; PII scrubbing đạt. |
| `validate_dashboard.py` | 6/6 valid | 6/6 valid | Re-run after CP2. |
| `pytest` | 22 passed | | |
| Complete traces | 10 CP0 | 104/104 CP2 requests | Every tree has lab-agent-run with retrieval and generation; all correlation IDs match logs. |
| Số PII leak | 0 | | |
| Latency P95 / TTFT P95 | | 191 ms / 50 ms | Dashboard, UTC 60-minute window after load test. |
| Retrieval success rate | | 100% | Counts all boolean tool_success events, including response_sent and request_failed. |
| CP2 load test | | 100 requests / 10 batches, 04:07-04:19 UTC; all HTTP 200 | Two promote/rollback checks also returned 200. |
| CP2 trace test | | 1 passed | `python -m pytest -q tests/test_agent_prompt_trace.py`. |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:**
- **Các metadata được ghi vào structured log:**
- **Cách bảo đảm PII được scrub trước khi ghi:**
- **Cách kiểm chứng kết quả:** `correlation_id` trong ảnh 04: `req-a04b2026` (đối chiếu với log `request_received` và `response_sent`).

## 5. Tracing và prompt versioning

- **Trace ownership verification:** Langfuse project `day13-k4-l3b-2A202602480`; compared request log correlation IDs with root metadata. All 104 match.
- **Observation tree:** `day13-agent-request` -> `lab-agent-run` (AGENT) -> `retrieval` (RETRIEVER) and `generation` (GENERATION). Generation records model, token usage, cost, and managed prompt; raw I/O capture is disabled.
- **Log correlation:** `correlation_id` is in root trace metadata and request logs; all 104 IDs match.
- **Prompt name:** `day13-chat` (Text; variables `feature`, `docs`, and `message`).
- **Version/label baseline:** v1, labels `baseline` and `production` after rollback.
- **Version/label candidate:** v2, label `candidate` (adds a brief-answer instruction).
- **Trace IDs:** v1 baseline `85142ab9eb1571cab372b44e490a8f1c` (correlation `req-c2b00101`); v2 candidate `423255e0a85edfacc8b988cb0274b0b7` (correlation `req-c2c00202`).
- **Production promote and rollback:** temporarily promoted to v2 and verified trace `a9801ffed134e9c44e11e530f8868b2b` (`req-c2a00303`, version 2), then rolled back to v1 and verified trace `616827fee4ca1149ad8e9184f044b161` (`req-c2b00404`, version 1). `.env` remains `LANGFUSE_PROMPT_LABEL=production`; final production points to v1.

## 6. Dashboard, SLO và alerts

- **Dashboard panels:** local dashboard reads `data/logs.jsonl`, UTC 60-minute range, 30-second refresh; Latency, Traffic, Errors, Cost, Tokens, Quality. Evidence: `11-dashboard-overview.png`.
- **SLO rationale:** 99.5% availability; CP0 baseline was 10 requests, 0 failures, P95 1122 ms; 3000 ms latency threshold is above baseline.
- **Error budget:** reference volume 10,000 requests x 0.5% = 50 requests.
- **Alerts and runbooks:** elevated latency P95, high request error rate, and low retrieval success; conditions/duration/severity/owner/Slack/runbook are in `config/alert_rules.yaml`; `docs/alerts.md` has Metrics -> Logs -> Traces checks and mitigations.

> Ví dụ cách viết error budget: "SLO 99.5% trong 28 ngày nghĩa là error budget 0.5%. Nếu workload có 10,000 request thì tối đa 50 request được phép lỗi hoặc chậm hơn ngưỡng SLO."

## 7. Điều tra challenge

- **Challenge ID:**
- **Khoảng thời gian điều tra:**
- **Triệu chứng từ metrics:**
- **Log line và correlation ID liên quan:**
- **Trace ID và span gây ảnh hưởng:**
- **Root cause:**
- **Fix action:**
- **Preventive measure:**

> Gợi ý cách viết ngắn, không thay cho evidence thực tế: "Metric cho thấy `[latency/error/cost/quality]` bất thường trong `[khoảng thời gian]`. Log line `[event]` có `correlation_id=[...]` đại diện cho request bị ảnh hưởng. Trace cùng `correlation_id` cho thấy span `[retrieval/generation/prompt/tool]` có dấu hiệu `[chậm/lỗi/token tăng]`. Root cause là `[nguyên nhân suy ra từ evidence]`. Fix action là `[hành động khôi phục]`; preventive measure là `[alert/runbook/test/guardrail để ngăn tái diễn]`."

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:**
- **Một lỗi/blocker đã gặp:**
- **Cách tìm nguyên nhân và xử lý:**
- **Cách hiểu luồng Metrics → Logs → Traces:**
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:**
- **Điều quan trọng nhất đã học:**
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:**

## 9. Checklist trước khi nộp

- [ ] Kết quả và evidence thuộc commit SHA cuối.
- [ ] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [ ] Incident evidence nối đúng metric → log → trace.
- [ ] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [ ] Repository chạy lại được theo README.
- [ ] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
