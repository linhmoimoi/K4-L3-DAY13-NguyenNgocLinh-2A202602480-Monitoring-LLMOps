# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> **Trạng thái evidence:** Một số PNG ban đầu là ảnh dựng; người học đang thay bằng ảnh chụp runtime/UI. Chỉ dẫn ảnh đã kiểm tra đúng nguồn, đọc được và không lộ key/PII. Theo [`evidence/README.md`](evidence/README.md), cập nhật kết quả và đường dẫn sau khi đối chiếu từng ảnh thật.

## 1. Thông tin học viên

- **Họ và tên:** Chưa xác minh — xác nhận cách viết chính thức.
- **MSSV:** `2A202602480`
- **Lớp:** K4-L3B
- **Repository URL:** [K4-L3-DAY13-NguyenNgocLinh-2A202602480-Monitoring-LLMOps](https://github.com/linhmoimoi/K4-L3-DAY13-NguyenNgocLinh-2A202602480-Monitoring-LLMOps)
- **Commit nộp cuối:** Chưa có. `git log -1 --oneline` hiện tại phải được chạy lại sau khi hoàn tất thay đổi và chụp evidence.
- **Challenge ID:** Chưa xác minh từ file challenge cá nhân. Ghi ID được Lab Coach cấp; không đưa nội dung challenge/query vào report.
- **Project Langfuse cá nhân:** `day13-k4-l3b-2A202602480` (đã thấy trong UI Tracing/Prompts và đối chiếu bằng Langfuse Observations API).

## 2. Evidence index

Evidence index dưới đây là checklist đang được cập nhật. File có mặt trong thư mục chưa đồng nghĩa ảnh đã đạt yêu cầu; kiểm tra nguồn, nội dung và key/PII trước khi thay trạng thái bằng link tương đối.

| Evidence | Đường dẫn ảnh chụp thật |
|---|---|
| 01 — pytest cuối | Chưa có ảnh thật: `evidence/01-pytest.png` |
| 02 — log validator | Chưa có ảnh thật: `evidence/02-log-validator.png` |
| 03 — dashboard validator | Chưa có ảnh thật: `evidence/03-dashboard-validator.png` |
| 04 — structured log | Chưa có ảnh thật: `evidence/04-structured-log.png` |
| 05 — PII redaction | Chưa có ảnh thật: `evidence/05-pii-redaction.png` |
| 06 — trace list | Chưa có ảnh thật: `evidence/06-trace-list.png` |
| 07 — trace waterfall | Chưa có ảnh thật: `evidence/07-trace-waterfall.png` |
| 08 — trace metadata, token/cost | Cần chụp lại `evidence/08-trace-metadata.png`: ảnh hiện có còn hiện `scope.attributes.public_key`; yêu cầu giảng viên dùng một ảnh 08 |
| 09 — prompt versions | [Ảnh 09](evidence/09-prompt-versions.png): v1 `production`/`baseline`, v2 `candidate`/`latest` |
| 10 — prompt promote | [Ảnh 10](evidence/10-prompt-rollback.png): v2 nhận label `production`, v1 còn `baseline`; tên file hiện tại là `rollback` nhưng nội dung ảnh là promote |
| 11 — dashboard runtime | Chưa có ảnh thật: `evidence/11-dashboard-overview.png`; nếu khó đọc, dùng ba ảnh `11a/11b/11c` như README |
| 12 — incident metric | Chưa có ảnh thật: `evidence/12-incident-metric.png` |
| 13 — incident log | Chưa có ảnh thật: `evidence/13-incident-log.png` |
| 14 — incident trace | Chưa có ảnh thật: `evidence/14-incident-trace.png` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nguồn / trạng thái |
|---|---|---|---|
| `validate_logs.py` | Chưa xác minh | Chưa chạy/chưa có ảnh thật | Chạy theo bước 02; ghi đúng Estimated Score và PII count từ output. |
| `validate_dashboard.py` | Chưa xác minh bằng output thật | Chưa chạy/chưa có ảnh thật | Chạy theo bước 03; ghi nguyên văn kết quả. |
| `pytest` | Chưa xác minh | Chưa chạy/chưa có ảnh thật | Chạy theo bước 01 trên trạng thái định nộp. |
| CP0 baseline | Config ghi 10 requests, 0 failures, latency P95 1122 ms | Chưa có kết quả mới | `config/slo.yaml` ghi nguồn `logs-cp0-baseline.jsonl`, file baseline đã chuyển khỏi repo nên không thể kiểm tra lại từ workspace này. |
| PII runtime | Chưa xác minh | Chưa có ảnh thật | Source có scrubber và test; cần chụp request dữ liệu giả cùng log đã scrub ở bước 05. |
| Tracing / prompt versions | Chưa có baseline đo độc lập | Đã xác minh trace dùng v1 và v2 trong project cá nhân | Trace IDs, label, correlation ID và thời điểm UTC ở mục 5 lấy từ Langfuse Observations API; ảnh 08 hiện có cần chụp lại để không hiện public key. |
| Dashboard runtime | Config định nghĩa 6 panel, cửa sổ 60 phút, refresh 30 giây | Chưa có ảnh thật | `config/dashboard.yaml`; mở dashboard local theo bước 11. |
| Challenge | Chưa xác minh | Chưa điều tra lại bằng bằng chứng thật | Cần file challenge riêng của Lab Coach và cùng một incident metric → log → trace. |

Chỉ dùng số liệu, timestamp, correlation ID, trace ID hoặc kết luận đã kiểm tra trực tiếp từ runtime, log hay Langfuse; không lấy ảnh dựng trước đó làm nguồn xác minh. Sau khi chạy thật, thay các ô “Chưa xác minh” bằng output và ID lấy trực tiếp từ lần chạy đó.

## 4. Logging và PII

- **Theo source:** middleware nhận `x-request-id` hợp lệ dạng `req-<8 hex>` hoặc tự tạo ID; ID được gắn vào context và response header.
- **Theo source:** log API gắn `user_id_hash`, `session_id`, `feature`, `model`, `env`; các event gồm `request_received`, `response_sent` và `request_failed`. Timestamp được ghi UTC.
- **Theo source:** PII scrubber nằm trong pipeline logging. Ảnh runtime phải chứng minh bằng request dữ liệu giả và log ra các nhãn `[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]`, `[REDACTED_CCCD]`, `[REDACTED_CREDIT_CARD]`.
- **Correlation ID để đối chiếu log và trace:** `req-4d97486a` trong log ảnh 04 khớp metadata trace v1 ở mục 5. Ảnh 04 cần kiểm tra lại độ đầy đủ của dòng `response_sent` trước khi dẫn làm evidence cuối.

## 5. Tracing và prompt versioning

- **Project Langfuse:** `day13-k4-l3b-2A202602480`, đã thấy trong UI cá nhân; không chụp trang API Keys.
- **Observation tree theo source:** trace `day13-agent-request` có root `lab-agent-run`, child `retrieval` và `generation`; các decorator trong `app/agent.py`, `app/mock_rag.py`, `app/mock_llm.py` tạo observations. Xác nhận cây thật trong UI trước khi ghi kết quả.
- **Metadata prompt theo source:** root span cập nhật `correlation_id`, `prompt_name`, `prompt_label`, `prompt_version`, `prompt_source`. Generation cập nhật model, token usage, cost và managed prompt. Không chụp raw Input/Output.
- **Prompt:** `day13-chat`; màn hình Prompts đã cho thấy v1 và v2 cùng các label `baseline`, `candidate`, `production`.

| Prompt version | Label khi request chạy | Trace ID | Correlation ID | Bắt đầu (UTC) |
|---|---|---|---|---|
| v1 | `production` | `0bb93c2942f3dc8a9863cb5273c63edd` | `req-4d97486a` | 2026-09-30 05:40:32.810 |
| v2 | `candidate` | `423255e0a85edfacc8b988cb0274b0b7` | `req-c2c00202` | 2026-09-30 04:06:37.125 |

Hai hàng trên được đối chiếu từ các observation `lab-agent-run` trong project Langfuse bằng API đọc dữ liệu; trace v1 còn hiện trong ảnh 08 đang cần chụp lại an toàn. Trace v2 là request `candidate` trước lần chụp promote hiện tại, nên không được dùng riêng nó để khẳng định ảnh 10 đã tạo request `production` v2.
- **Promote label `production`:** Ảnh 09 cho thấy label ở v1, còn ảnh 10 cho thấy label đã chuyển sang v2. Hai ảnh chứng minh thay đổi label; chưa có trace mới được xác minh sau lần promote này. Nếu rollback tiếp về v1, ghi hành động và evidence bổ sung.
- **Múi giờ:** log/dashboard hiển thị UTC. Nếu Langfuse UI hiển thị giờ Việt Nam, ghi giờ UTC+7 và đối chiếu thêm correlation ID/trace ID.

## 6. Dashboard, SLO và alerts

- **Sáu panel theo config:** Latency percentiles and TTFT, Request traffic, Error rate and retrieval success, Cost over time, Input and output tokens, Quality proxy. Dashboard local đọc `data/logs.jsonl`; để thấy dữ liệu, cần chạy API/workload trước, sau đó mở `python scripts/dashboard.py` và vào `http://127.0.0.1:8501`.
- **SLO theo `config/slo.yaml`:** 99.5% request thành công và latency không quá 3000 ms trong cửa sổ 28 ngày; error budget 0.5%. Với volume tham chiếu 10,000 request, ngân sách tham chiếu là 50 request không đạt (`10,000 × 0.005`). Đây là giá trị cấu hình, không phải kết quả runtime mới.
- **Guardrails cấu hình:** error rate tối đa 2%, daily cost tối đa 2.5 USD, quality trung bình tối thiểu 0.75, retrieval success tối thiểu 90%.
- **Alerts cấu hình:** `ElevatedLatencyP95`, `HighRequestErrorRate`, `LowRetrievalSuccess`; xem điều kiện, duration, severity, owner, Slack channel và runbook tại `config/alert_rules.yaml` và `docs/alerts.md`.
- **Runtime dashboard:** Chưa chụp thật; điền time range, đơn vị, threshold và các số liệu nhìn thấy sau bước 11.

## 7. Điều tra challenge

- **Challenge ID:** Chưa xác minh. Điền đúng ID từ challenge cá nhân, không sao chép nội dung/seed/query vào report.
- **Khoảng thời gian:** Chưa có. Ghi start/end UTC đọc từ dashboard/log, kèm giờ Langfuse UTC+7 nếu khác.
- **Metric bất thường:** Chưa có. Ghi metric, giá trị baseline, giá trị trong incident và cửa sổ đo từ ảnh 12.
- **Log request:** Chưa có. Chọn correlation ID trong output lọc ở ảnh 13; ghi event, timestamp UTC và trường bất thường.
- **Trace/span:** Chưa có. Tìm trace cùng correlation ID, ghi trace ID, tên span và duration thật từ ảnh 14.
- **Root cause:** Chưa xác minh. Chỉ kết luận sau khi metric, log và trace cùng trỏ tới request/khoảng sự cố.
- **Fix action / preventive measure:** Chưa xác minh. Ghi hành động đã thực hiện và biện pháp phòng ngừa có thể kiểm chứng; không ghi hành động giả định như đã hoàn thành.

## 8. Giải thích và tự đánh giá

- **Quyết định kỹ thuật (theo source hiện có):** truyền cùng correlation ID qua middleware, structured log và trace metadata để tìm đúng request; scrub PII trước khi log được serialize.
- **Blocker đã gặp và cách xử lý:** Chưa xác minh từ trải nghiệm thực tế của học viên. Ghi lỗi thật, cách tìm nguyên nhân và thao tác đã xử lý sau khi chạy CP4.
- **Metrics → Logs → Traces:** metric khoanh triệu chứng/khoảng thời gian; log chọn request qua correlation ID; trace phân rã duration theo span để xác định bước gây ảnh hưởng.
- **Vai trò prompt/token/cost/SLO/rollback:** prompt version cho biết request dùng biến thể nào; token/cost thể hiện mức sử dụng; SLO/error budget định nghĩa ngưỡng dịch vụ; rollback chuyển production về version đã biết ổn định khi có căn cứ.
- **Điều học được:** Chưa ghi — hoàn thiện sau khi tự chạy và điều tra incident.
- **Hạn chế còn lại:** Hiện chưa có evidence runtime thật. Các kết luận và số liệu CP1–CP3 cần điền lại theo ảnh chụp thật và artifact có thể đối chiếu.

## 9. Checklist trước khi nộp

- [ ] Kiểm tra/thay ảnh dựng bằng evidence chụp thật 01–14 theo `submission/evidence/README.md`; chụp lại ảnh 08 để không hiện `public_key`.
- [ ] Lưu ảnh thật cùng tên, cập nhật Evidence index và chèn liên kết tương đối tới các file đã tồn tại.
- [ ] Ghi kết quả validator/test, trace IDs, correlation IDs, prompt versions, challenge ID và incident timestamps từ output/UI thật.
- [ ] Xác nhận họ tên, project Langfuse cá nhân và commit cuối.
- [ ] Rà secret/PII, đảm bảo ảnh Langfuse không mở API Keys và không có raw prompt/input/output nhạy cảm.
- [ ] Kiểm tra log UTC ↔ Langfuse UTC+7, liên kết metric → log → trace và các đường dẫn trên GitHub.
