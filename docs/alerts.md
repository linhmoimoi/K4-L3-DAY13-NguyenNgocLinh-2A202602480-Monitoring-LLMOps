# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: `ElevatedLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: P95 latency của `response_sent.latency_ms`; SLO 3000 ms.
- Điều kiện và thời gian duy trì: P95 vượt 3000 ms liên tục trong 5 phút.
- Ảnh hưởng tới người dùng: câu trả lời mất nhiều thời gian hơn ngưỡng dịch vụ.
- Ba bước kiểm tra đầu tiên:
  1. **Metrics:** xem P50/P95/P99 và TTFT P95 trong 60 phút, xác định phút bắt đầu tăng.
  2. **Logs:** lọc `response_sent` ở khoảng đó, sắp theo `latency_ms` giảm dần và lấy `correlation_id` của request chậm.
  3. **Traces:** mở trace cùng `correlation_id`, so sánh thời lượng `retrieval` và `generation` để định vị bước chậm.
- Mitigation tạm thời: nếu generation/prompt gây tăng latency, rollback label `production` về version đã biết tốt; nếu retrieval chậm, giảm tải hoặc khôi phục dịch vụ retrieval.
- Owner: `student-2A202602480`.

## Alert 2

- Tên: `HighRequestErrorRate`
- Severity: `critical`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: tỷ lệ `request_failed` trên `request_received`; tối đa 2%.
- Điều kiện và thời gian duy trì: error rate vượt 2% liên tục trong 5 phút.
- Ảnh hưởng tới người dùng: một phần request không nhận được câu trả lời.
- Ba bước kiểm tra đầu tiên:
  1. **Metrics:** xác nhận error rate và breakdown theo `error_type` trong cửa sổ 60 phút.
  2. **Logs:** lọc event `request_failed`, nhóm theo `error_type`, kiểm tra `tool_name`, `tool_success` và correlation ID.
  3. **Traces:** mở trace theo correlation ID lỗi; tìm observation đầu tiên có level/status lỗi và xác định dịch vụ gây lỗi.
- Mitigation tạm thời: nếu lỗi retrieval tăng, khôi phục backend hoặc tạm giảm tải; nếu lỗi liên quan prompt/model, rollback prompt `production` về version ổn định.
- Owner: `student-2A202602480`.

## Alert 3

- Tên: `LowRetrievalSuccess`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: retrieval success tối thiểu 90%, tính trên mọi event có `tool_success` trong `response_sent` và `request_failed`.
- Điều kiện và thời gian duy trì: số event `tool_success=true` chia cho toàn bộ event có `tool_success` nhỏ hơn 90% liên tục 5 phút.
- Ảnh hưởng tới người dùng: câu trả lời có thể thiếu ngữ cảnh hoặc request có thể thất bại.
- Ba bước kiểm tra đầu tiên:
  1. **Metrics:** xem retrieval success và error rate cùng thời gian để phân biệt retrieval lỗi với lỗi tổng quát.
  2. **Logs:** lọc `response_sent` và `request_failed` có `tool_name=retrieval`; so sánh `tool_success` và correlation ID.
  3. **Traces:** mở các trace tương ứng, so sánh duration/status của observation `retrieval` với `generation`.
- Mitigation tạm thời: khôi phục index/backend retrieval hoặc tắt nguồn truy xuất lỗi nếu có fallback; không phát hành prompt mới cho tới khi retrieval success ổn định.
- Owner: `student-2A202602480`.
