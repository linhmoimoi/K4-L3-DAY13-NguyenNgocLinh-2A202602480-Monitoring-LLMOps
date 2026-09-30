# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Rà soát ngày 2026-09-30. Các kết quả dưới đây được đối chiếu với lệnh chạy, log cục bộ, cấu hình và ảnh hiện có. Evidence 05 thiếu PNG; ảnh 08 và 14 cần chụp lại vì hiển thị public key. Các mục này chưa đạt điều kiện nộp an toàn.

## 1. Thông tin học viên

- **Họ và tên:** Nguyễn Ngọc Linh (theo tên repository).
- **MSSV:** 2A202602480; **lớp:** K4-L3B.
- **Repository:** [K4-L3-DAY13-NguyenNgocLinh-2A202602480-Monitoring-LLMOps](https://github.com/linhmoimoi/K4-L3-DAY13-NguyenNgocLinh-2A202602480-Monitoring-LLMOps).
- **HEAD lúc rà soát:** bf98f7f Done CP34. Report được sửa sau commit này; cần cập nhật SHA sau commit nộp.
- **Challenge ID:** day13-k4-l3b-monitoring-llmops-v1, đọc từ config/challenge.json cục bộ. File challenge, seed và query không được đưa vào Git.
- **Project Langfuse:** day13-k4-l3b-2A202602480, khớp MSSV trong report và tên repo.

## 2. Evidence index

| Mục | Bằng chứng hiện có | Đánh giá |
|---|---|---|
| 01 — pytest | [Ảnh 01](evidence/01-pytest.png) | 24 passed trong .venv; ảnh chưa chứa git log theo hướng dẫn chụp. |
| 02 — log validator | [Ảnh 02](evidence/02-log-validator.png) | 100/100, 0 PII leak; ảnh chụp lúc có 33 log, lần chạy hiện tại có 123. |
| 03 — dashboard validator | [Ảnh 03](evidence/03-dashboard-validator.png) | 6/6 panel. |
| 04 — structured log | [Ảnh 04](evidence/04-structured-log.png) | ID req-4d97486a khớp log và trace; dòng response_sent bị cắt trong ảnh, cần chụp lại. |
| 05 — PII redaction | evidence/05-pii-redaction.txt | Log có đủ bốn nhãn redaction; file text bị lẫn ký tự terminal và chưa có PNG. |
| 06 — trace list | [Ảnh 06](evidence/06-trace-list.png) | Project cá nhân hiển thị khoảng 132 root observations; hàng 12:40:32 khớp trace ở ảnh 07–08. |
| 07 — trace waterfall | [Ảnh 07](evidence/07-trace-waterfall.png) | Trace 0bb93c2942f3dc8a9863cb5273c63edd có retrieval và generation. |
| 08 — metadata/usage/cost | evidence/08-trace-metadata.png | Cùng trace với 07, có version 1, 133 tokens và 0.001659 USD; cần chụp lại để không hiển thị public key. |
| 09 — prompt versions | [Ảnh 09](evidence/09-prompt-versions.png) | v1 có production/baseline; v2 có candidate/latest. |
| 10 — prompt change | [Ảnh 10](evidence/10-prompt-rollback.png) | Chứng minh promote production sang v2. Tên file ghi rollback nhưng ảnh chưa chứng minh rollback. |
| 11 — dashboard runtime | [Ảnh 11a](evidence/11a-dashboard-latency-traffic.png), [ảnh 11b](evidence/11b-dashboard-error-cost-token-quality.png) | Hai ảnh bao phủ sáu panel; được chụp ở hai thời điểm khác nhau. |
| 12 — incident metric | [Ảnh 12](evidence/12-incident-metric.png) | Cửa sổ 09:00:39–10:00:39 UTC, P95 2678 ms. |
| 13 — incident log | [Ảnh 13](evidence/13-incident-log.png) | ID req-7f896a7a, response_sent lúc 09:59:25.481Z, 2678 ms. |
| 14 — incident trace | evidence/14-incident-trace.png | Cùng ID req-7f896a7a, retrieval 2.50 s; cần chụp lại để không hiển thị public key. |

Ảnh 08 và 14 đang dùng để đối chiếu nội bộ nhưng cần thay bằng ảnh an toàn trước khi nộp. Hướng dẫn chụp ở [evidence/README.md](evidence/README.md).

## 3. Kết quả kiểm tra kỹ thuật

| Lệnh / phép kiểm tra | Kết quả lúc rà soát | Ghi chú |
|---|---|---|
| .venv\Scripts\python.exe -m pytest -q | **24 passed** trong 2.36 s | Khớp số pass trên ảnh 01. |
| python -m pytest -q bằng Python hệ thống | **Lỗi khi collect** | Thiếu structlog và langfuse; cần kích hoạt .venv trước khi chạy lệnh checklist. |
| python scripts/validate_logs.py | **100/100**; 123 records; 62 correlation IDs; 0 thiếu field, 0 thiếu enrichment, 0 PII leak | Ảnh 02 là snapshot cũ nhưng cùng điểm 100/100. |
| python scripts/validate_dashboard.py | **HỢP LỆ: 6/6 panel** | Khớp ảnh 03. |
| git status --short | Trống trước lần sửa report này | .env, config/challenge.json, data/logs.jsonl và .venv/ bị ignore, không được track. |
| git log -1 --oneline | bf98f7f Done CP34 | Cần lấy lại SHA sau commit nộp. |

CP0 trong [config SLO](../config/slo.yaml) ghi 10 requests, 0 failures và P95 1122 ms. File log CP0 đã chuyển khỏi repo, nên đây chỉ là baseline lưu trong config. Phần incident bên dưới dùng các request còn trong data/logs.jsonl để so sánh trực tiếp.

## 4. Logging và PII

- Middleware truyền correlation ID từ request qua response và structured log. Log có UTC timestamp, user_id_hash, session_id, feature, model, env và các event request_received/response_sent.
- Request tham chiếu req-4d97486a xuất hiện trong log lúc 2026-09-30T05:40:32.810876Z; response_sent lúc 05:40:32.984710Z, latency 156 ms. Cùng ID nằm trong metadata trace v1.
- Request kiểm tra PII dùng dữ liệu giả. Log req-8345994f chứa [REDACTED_EMAIL], [REDACTED_PHONE_VN], [REDACTED_CCCD], [REDACTED_CREDIT_CARD]. Validator trên 123 records báo 0 potential PII leaks. Evidence 05 cần chụp lại thành PNG rõ lệnh và output.

## 5. Tracing và prompt versioning

- Ảnh 06 cho thấy khoảng 132 root observations trong project cá nhân, vượt mức tối thiểu 10 trace. Hàng **12:40:32 giờ Việt Nam** tương ứng **05:40:32 UTC** trong log req-4d97486a.
- Ảnh 07 và 08 cùng trace 0bb93c2942f3dc8a9863cb5273c63edd. Root lab-agent-run có child retrieval và generation; UI ghi khoảng 0.17 s, 133 tokens, 0.001659 USD. Metadata cho thấy prompt_name=day13-chat, prompt_label=production, prompt_version=1.

| Version | Label khi request chạy | Trace ID | Correlation ID | Bắt đầu (UTC) | Nguồn |
|---|---|---|---|---|---|
| 1 | production | 0bb93c2942f3dc8a9863cb5273c63edd | req-4d97486a | 2026-09-30 05:40:32.810 | Ảnh 07–08 và log cục bộ |
| 2 | candidate | 423255e0a85edfacc8b988cb0274b0b7 | req-c2c00202 | 2026-09-30 04:06:37.125 | Dữ liệu Langfuse Observations API ghi ở lần rà soát trước; ảnh hiện có chưa hiển thị version của trace này |

Ảnh 09 và 10 chứng minh label production chuyển từ v1 sang v2. Chưa có ảnh trace request dùng production sau promote; chưa có ảnh rollback về v1. Hai trạng thái này cần evidence riêng nếu rubric yêu cầu cả promote và rollback. Mốc thời gian Langfuse trong ảnh trace là giờ Việt Nam (UTC+7); timestamp trong log/dashboard là UTC.

## 6. Dashboard, SLO và alerts

- [Cấu hình dashboard](../config/dashboard.yaml) có 6 panel: latency/TTFT, traffic, error/retrieval success, cost, tokens, quality. Cửa sổ 60 phút, refresh 30 giây. Ảnh 11a–11b hiển thị cả sáu panel. Ảnh 11a ghi P95 4099 ms ở đợt **08:46 UTC**, khác đợt incident 09:59 UTC trong mục 7.
- [SLO](../config/slo.yaml): 99.5% request thành công và latency ≤ 3000 ms trong 28 ngày; error budget 0.5%, tương đương **50 request không đạt trên 10.000 request tham chiếu**. Đây là ngân sách theo cấu hình, chưa phải số đã tiêu thụ trong 28 ngày.
- Guardrails: error rate ≤ 2%, daily cost ≤ 2.5 USD, quality trung bình ≥ 0.75, retrieval success ≥ 90%.
- [Ba alert](../config/alert_rules.yaml): ElevatedLatencyP95, HighRequestErrorRate, LowRetrievalSuccess; điều kiện, duration, severity, owner và [runbook](../docs/alerts.md) đã được cấu hình.

## 7. Điều tra challenge theo Metrics → Logs → Traces

- **Challenge ID:** day13-k4-l3b-monitoring-llmops-v1; feature chịu ảnh hưởng: monitoring; ngưỡng latency của challenge: **2000 ms**. Không công bố seed hoặc query.
- **Baseline cùng lần chạy:** 10 request từ 09:58:51.013Z đến 09:58:52.538Z có latency **153–223 ms**. Năm request challenge từ 09:59:17.482Z đến 09:59:28.154Z có latency **2653–2678 ms**, đều vượt ngưỡng challenge 2000 ms.
- **Metric:** Ảnh 12 hiển thị cửa sổ 09:00:39.660687Z–10:00:39.660687Z, P95 latency **2678 ms** và TTFT P95 **50 ms**. P95 này **dưới** ngưỡng SLO/dashboard 3000 ms, nên ảnh không chứng minh SLO P95 bị vi phạm. Bất thường được xác định qua baseline cùng lần chạy và ngưỡng challenge.
- **Log:** req-7f896a7a bắt đầu 09:59:22.800323Z, kết thúc 09:59:25.481287Z với response_sent, latency **2678 ms**, tool_name=retrieval, tool_success=true. Không có error event cho request này.
- **Trace:** Trace ebaf90f1b39ea70a37aaaf4366530aa6 có metadata correlation_id=req-7f896a7a. UI hiển thị bắt đầu **16:59:22.800 giờ Việt Nam**, đúng bằng **09:59:22.800 UTC**; root mất **2.68 s**, retrieval **2.50 s**, generation **0.16 s**.
- **Nguyên nhân:** Phần lớn thời gian request nằm ở retrieval. [Implementation retrieval](../app/mock_rag.py) có nhánh làm chậm 2.5 s khi chế độ incident bật; thời lượng span và log phù hợp với nhánh này.
- **Hành động xử lý:** Repo chưa có bằng chứng rằng incident đã được tắt và đo lại. Cần tắt chế độ làm chậm qua endpoint incident, chạy lại workload và ghi metric/log/trace sau xử lý. Alert P95 hiện đặt ở 3000 ms nên mức suy giảm 2.65–2.68 s này có thể không kích hoạt alert latency; nên đánh giá thêm ngưỡng cảnh báo riêng cho retrieval.

## 8. Giải thích và tự đánh giá

- **Quyết định kỹ thuật:** Dùng cùng correlation ID qua middleware, structured log và trace metadata; scrub PII trước khi log được serialize. Trace có span riêng cho retrieval và generation để định vị độ trễ.
- **Vấn đề lúc kiểm tra:** Python hệ thống thiếu dependencies nên pytest lỗi lúc collect; Python của .venv cho 24 tests passed. Evidence 05 thiếu PNG và ảnh 08/14 hiển thị public key, cần thay trước khi nộp.
- **Vai trò prompt/token/cost/SLO/rollback:** Prompt version gắn biến thể được dùng với trace; token/cost đo mức sử dụng; SLO và error budget đặt ngưỡng dịch vụ. Ảnh hiện có chứng minh promote label, chưa chứng minh rollback.
- **Điều rút ra:** Request có thể vượt ngưỡng challenge 2000 ms nhưng vẫn dưới SLO P95 3000 ms. So sánh baseline, log và span cho thấy sự suy giảm ở retrieval dù alert latency chưa chắc kích hoạt.

## 9. Việc còn lại trước khi nộp

- [ ] Chụp PNG evidence 05; chụp lại 04 để thấy đủ response_sent; chụp lại 08 và 14 để không hiển thị public key.
- [ ] Bổ sung evidence trace dùng production v2 sau promote và rollback nếu rubric yêu cầu cả hai hành động.
- [ ] Ghi nhận thao tác tắt incident và kết quả đo lại, hoặc giữ rõ giới hạn điều tra ở mục 7.
- [ ] Chạy python -m pytest -q trong .venv và hai validator trên trạng thái cuối; cập nhật ảnh và số liệu nếu kết quả thay đổi.
- [ ] Rà các ảnh còn lại về nguồn gốc và dữ liệu nhạy cảm; kiểm tra link tương đối trên GitHub; commit bài làm rồi cập nhật SHA nộp cuối.
