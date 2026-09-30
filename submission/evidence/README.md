# Chụp lại evidence thật từ 01 đến 14

## Quan trọng: ảnh hiện có không phải evidence

Một số PNG ban đầu trong thư mục này là ảnh dựng; các ảnh chụp thật đang được thay dần. Chỉ đưa vào báo cáo ảnh đã kiểm tra là chụp trực tiếp từ terminal, dashboard local hoặc project Langfuse cá nhân. Ảnh thật cần cho thấy ứng dụng/màn hình nguồn và output vừa tạo; không ghép nhiều ảnh, không vẽ số liệu lên ảnh, không dùng ảnh mẫu hoặc output của người khác.

Lưu ảnh mới dưới đúng tên hướng dẫn bên dưới. Với tên đã tồn tại, xác nhận ghi đè ảnh dựng bằng ảnh chụp thật. Ảnh 08 dùng đúng tên `08-trace-metadata.png`. Theo yêu cầu giảng viên vừa cung cấp, ảnh 10 có thể là một file `10-prompt-change.png` khi file đó, cùng ảnh 09, chứng minh được trạng thái trước/sau; nếu cần ghi cả promote và rollback, lưu thêm ảnh riêng cho từng trạng thái.

## A. Chuẩn bị workspace và công cụ

1. Mở PowerShell/Terminal tại thư mục gốc của repository này. Cài đặt và cấu hình project cá nhân theo [docs/SETUP.md](../../docs/SETUP.md). Tên project cần thấy trên ảnh Langfuse có dạng `day13-k4-l3b-<MSSV>`; không dùng project chung.
2. Nếu chưa cài dependencies, làm theo bước 1 trong `docs/SETUP.md`. Không đưa `.env`, API key, secret hoặc token lên ảnh. Không mở trang API Keys của Langfuse.
3. Chạy API trong Terminal 1:

   ```powershell
   uvicorn app.main:app --reload --env-file .env
   ```

   Chờ tới khi Uvicorn báo server đang chạy tại `127.0.0.1:8000`. Giữ terminal này mở. Nếu API dừng, khởi động lại bằng chính lệnh này.

4. Dùng Terminal 2 để gửi request, chạy tests/validators và lọc log. Dùng Terminal 3 cho dashboard. Chạy lệnh từ thư mục gốc repo để các đường dẫn `data/...` đúng.
5. Trước khi chụp, phóng to cửa sổ và đặt font terminal đủ lớn để đọc được cả lệnh quan trọng lẫn kết quả. Chờ request/validator/dashboard tải xong. Chụp cả tên ứng dụng/project, thời gian và ID cần đối chiếu; tránh để `.env`, key, terminal history bí mật hoặc PII thật lọt vào khung.
6. Chụp màn hình bằng công cụ của hệ điều hành:
   - **Windows:** `Win + Shift + S` → chọn vùng màn hình thật → chọn thông báo Snipping Tool → **Save as** PNG.
   - **macOS:** `Cmd + Shift + 4` → kéo vùng cần chụp; ảnh PNG thường được lưu trên Desktop, sau đó chuyển vào thư mục này.
   - **Ubuntu:** `Shift + PrtSc` → chọn vùng cần chụp và lưu PNG.

   Lưu trực tiếp vào `submission/evidence/` với đúng tên của từng mục. Không crop bỏ dữ liệu cần kiểm tra, thêm chữ/số lên ảnh, hoặc dựng lại màn hình bằng slide/HTML.

7. Làm theo thứ tự. Nếu một thao tác không chạy hoặc không tạo đúng dữ liệu cần chụp, dừng ở mục đó, ghi lỗi và bước còn thiếu trong report. Không thay bằng ảnh dựng. Nếu Langfuse hiển thị giờ Việt Nam, đối chiếu với timestamp UTC của log bằng cách cộng 7 giờ; kiểm tra thêm correlation ID và trace ID.

## B. Ảnh terminal và validator

### 01 — `01-pytest.png`: commit và pytest cuối

Chỉ chụp sau khi các chỉnh sửa source cuối cùng đã xong. Từ Terminal 2, chạy lần lượt:

```powershell
git log -1 --oneline
python -m pytest -q
```

Đợi pytest kết thúc. Chụp terminal thật có dòng `git log` và tổng kết pytest với số `passed`, cùng số failed/skipped nếu có. Ghi chính xác kết quả và SHA trong report. Nếu có lỗi, không che lỗi hay ghi số pass dự kiến.

### 02 — `02-log-validator.png`: tạo log mới và chạy validator

Validator đọc tất cả `data/logs.jsonl`; để dùng workload mới, cần đưa log cũ ra ngoài repo trước khi chạy. Dừng API ở Terminal 1 bằng `Ctrl+C`. Trong Terminal 2 chạy:

```powershell
if (Test-Path 'data/logs.jsonl') {
  $backup = Join-Path $env:TEMP ("day13-logs-before-cp4-" + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.jsonl')
  Move-Item -LiteralPath 'data/logs.jsonl' -Destination $backup
  Write-Output "Old log moved outside repository: $backup"
}
```

Khởi động lại API bằng lệnh ở mục A. Sau khi API sẵn sàng, trong Terminal 2 chạy:

```powershell
python scripts/load_test.py
python scripts/validate_logs.py
```

Đợi load test và validator hoàn tất. Chụp **output thật** có Grading Scorecard, tổng số log/PII leak và dòng `Estimated Score`. Chỉ report đạt nếu kết quả thực tế từ validator ít nhất 80/100; nếu thấp hơn, ghi điểm thật và nguyên nhân, không tạo ảnh “đạt”.

### 03 — `03-dashboard-validator.png`: kiểm tra cấu hình 6 panel

```powershell
python scripts/validate_dashboard.py
```

Đợi lệnh kết thúc. Chụp lệnh và dòng output thật; kết quả đạt phải hiện `HỢP LỆ: 6/6 panel`. Validator này xác nhận dashboard contract/config, còn ảnh 11 mới xác nhận dashboard local có runtime data.

## C. Ảnh request log và PII

### 04 — `04-structured-log.png`: gửi một request và in log của nó

Đảm bảo API ở Terminal 1 đang chạy. Trong Terminal 2 gửi request dùng dữ liệu giả không nhạy cảm và ID ngẫu nhiên theo format `req-` + 8 ký tự hex:

```powershell
$rid = 'req-' + [guid]::NewGuid().ToString('N').Substring(0,8)
$message = 'How should alerts be designed?'
$body = @{user_id='evidence-user-04'; session_id='cp4-evidence-04'; feature='qa'; message=$message} | ConvertTo-Json -Compress
$headers = @{'x-request-id'=$rid}
$response = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/chat' -Method Post -Headers $headers -ContentType 'application/json' -Body $body
$response | Select-Object correlation_id,latency_ms,ttft_ms | Format-List
Select-String -Path 'data/logs.jsonl' -Pattern $rid
```

Chụp command và kết quả mới tại terminal. Phải thấy đúng correlation ID trong response/log và cả `request_received`/`response_sent`. JSON cần đọc được `ts`, `event`, `correlation_id`, `user_id_hash`, `session_id`, `feature`, `model`, `env`, `latency_ms`. Ghi lại `$rid` trong report. Giữ request này làm request tham chiếu cho bước 07–08 nếu nó xuất hiện trong Langfuse.

### 05 — `05-pii-redaction.png`: gửi PII giả và xem log đã scrub

Chạy request riêng với đúng dữ liệu giả được yêu cầu:

```powershell
$rid = 'req-' + [guid]::NewGuid().ToString('N').Substring(0,8)
$message = 'a@b.vn 0901234567 001099012345 4111 1111 1111 1111'
$body = @{user_id='evidence-user-05'; session_id='cp4-evidence-05'; feature='qa'; message=$message} | ConvertTo-Json -Compress
$headers = @{'x-request-id'=$rid}
$response = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/chat' -Method Post -Headers $headers -ContentType 'application/json' -Body $body
$response | Select-Object correlation_id | Format-List
Select-String -Path 'data/logs.jsonl' -Pattern $rid
```

Chụp command chứa chuỗi **giả** và JSON output thực tế có đủ `[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]`, `[REDACTED_CCCD]`, `[REDACTED_CREDIT_CARD]`. Không gửi PII thật. Nếu log còn nguyên giá trị, không chụp như thể đạt; sửa xử lý theo source/runbook, xóa log cũ ra ngoài repo, khởi động API lại và lặp lại request.

## D. Ảnh Tracing và prompt trong Langfuse

### Tạo đủ traces cho mục 06

Trong Terminal 2, chạy workload bằng API đã cấu hình key cá nhân:

```powershell
python scripts/load_test.py
```

Đợi các request hoàn tất. Mở project cá nhân trong Langfuse Cloud và chọn thời gian gần nhất bao gồm lần chạy này. Nếu chưa thấy trace, đợi ingestion một chút rồi refresh; nếu vẫn không có, kiểm tra `.env`/project trong terminal riêng, không chụp `.env`. Cách đọc trace tree/metadata có thể xem [Langfuse Observability Best Practices](https://langfuse.com/docs/observability/best-practices).

### 06 — `06-trace-list.png`: danh sách trace thật

1. Mở Langfuse Cloud và chọn project cá nhân `day13-k4-l3b-<MSSV>`.
2. Vào **Tracing** (tên mục có thể đổi nhẹ theo phiên bản UI), chọn time range bao phủ workload vừa chạy.
3. Chờ bảng nạp trace. Chụp UI Langfuse thật có project, time range và ít nhất 10 trace `day13-agent-request`.
4. Để Input/Output không lộ nội dung: chụp bảng danh sách, không mở raw payload. Không dùng ảnh export/dựng lại làm ảnh UI.

### 07 — `07-trace-waterfall.png`: mở một trace có log đối chiếu

1. Trong tracing table, tìm trace có `correlation_id` khớp ID ở ảnh 04. Nếu trường này không hiện trong bảng, mở trace và kiểm tra Metadata; so khớp với log rồi mới chọn.
2. Mở trace detail, chọn chế độ **Tree**/trace tree hoặc bật nhãn observation nếu UI cung cấp.
3. Chụp UI Langfuse có project/time, trace ID và cây `lab-agent-run` → `retrieval` + `generation`; cần đọc được duration từng observation.
4. Nếu thiếu observation hoặc quan hệ cha-con, chưa có evidence hợp lệ cho ảnh 07; ghi nhận thiếu sót và xử lý implementation trước. Không vẽ cây bằng tay.

### 08 — `08-trace-metadata.png`: metadata, usage và cost của trace

Giảng viên yêu cầu **một ảnh 08**. Trong trace cùng request với ảnh 04, chọn `lab-agent-run` ở cây bên trái → **Attributes** → **Formatted**. Chụp vùng UI thật có tên project, trace ID, số token và cost ở phần đầu, cùng metadata `correlation_id`, `model`, `prompt_name`, `prompt_label`, `prompt_version`. Correlation ID phải khớp ảnh 04; không để lộ raw PII. Nếu cost không có, giữ nguyên giá trị UI thực tế vì yêu cầu là “cost nếu có”.

Ảnh 08 đang lưu trong thư mục đã hiện `scope.attributes.public_key` ở phần dưới, nên cần chụp lại: dùng công cụ chụp vùng màn hình từ đầu trang đến hết các trường prompt cần chấm, dừng trước hàng `public_key`. Không sửa ảnh để xóa key sau khi chụp. Nếu token/cost không xuất hiện cùng metadata trên `lab-agent-run`, mở observation `generation` để kiểm tra usage/cost và lưu thêm ảnh phụ; ảnh 08 chính vẫn cần cho thấy correlation ID cùng prompt name/label/version. Xem [tài liệu Langfuse về usage và cost](https://langfuse.com/docs/observability/features/token-and-cost-tracking).

### Tạo prompt v1/v2 để chụp mục 09–10

Thực hiện trong project Langfuse cá nhân, theo [Prompt Version Control của Langfuse](https://langfuse.com/docs/prompt-management/features/prompt-version-control):

1. Vào **Prompts** → tạo text prompt `day13-chat` nếu chưa có. Giữ các biến `{{feature}}`, `{{docs}}`, `{{message}}` theo `docs/PROMPT_VERSIONING.md`.
2. Lưu version 1; gắn labels `baseline` và `production`.
3. Tạo version 2 với thay đổi prompt nhỏ có chủ đích; gắn label `candidate`. `latest` có thể được Langfuse tự gắn.
4. Trong `.env` đặt `LANGFUSE_PROMPT_LABEL=baseline`, restart API, gửi một request test và ghi lại correlation ID/trace ID; sau đó đổi label sang `candidate`, restart API, gửi request thứ hai và ghi ID. Không để `.env` lọt vào ảnh. Mở hai trace và xác minh metadata thể hiện đúng version/label trước khi ghi vào report.
5. Tên/version/label trong UI có thể bố trí khác; yêu cầu bằng chứng là project cá nhân, version thực tế và label đang trỏ tới version đó.

### 09 — `09-prompt-versions.png`: danh sách versions/labels

Bạn đang ở trang **Tracing**. Đi tới prompt theo các bước sau:

1. Nhìn thanh trên cùng, xác nhận project là `day13-k4-l3b-2A202602480`. Ở góc trên bên trái, bấm biểu tượng mở thanh điều hướng (ô nhỏ cạnh tên tổ chức) nếu menu đang thu gọn.
2. Trong menu bên trái, tìm **Prompts** hoặc **Prompt Management**; có thể phải cuộn menu xuống. Bấm vào đó để mở danh sách prompt của **cùng project**.
3. Tại ô tìm kiếm của danh sách prompt, nhập chính xác `day13-chat` (không gõ `v1` hoặc `production` vào tên). Bấm vào hàng `day13-chat`.
4. Trên trang chi tiết, tìm bảng/danh sách **Versions** hoặc nút chọn version. Bạn cần nhìn thấy version **1** và **2**, cùng các nhãn: v1 có `baseline` và, trước promote/sau rollback, `production`; v2 có `candidate`. Nhãn `latest` trên v2 là bình thường.
5. Nếu trang chỉ hiện một version, kiểm tra bộ lọc/ô chọn version. Nếu thực sự mới có v1, tạo v2 theo mục **Tạo prompt v1/v2** ngay phía trên rồi quay lại. Không chụp ảnh 09 như thể đã có hai version.
6. Khi tên project, `day13-chat`, cả hai version và các label cùng đọc được trên UI, chụp màn hình thật và lưu `09-prompt-versions.png`. Nếu chữ quá nhỏ, mở trang toàn màn hình hoặc thu gọn menu bên trái trước khi chụp; không ghép ảnh.

Ảnh 08 của request bạn vừa kiểm tra đã hiện `prompt_name=day13-chat`, `prompt_source=langfuse`, `prompt_version=1`. Vì vậy `day13-chat` đã tồn tại trong project của trace đó; nếu không thấy ở bước 3, hãy kiểm tra lại project và các bộ lọc trên trang Prompts. Một đường khác là mở observation `generation` của trace đó và bấm liên kết prompt `day13-chat` nếu UI có hiển thị.

### 10 — `10-prompt-change.png`: chứng minh label/version đã đổi

Một ảnh chỉ đạt khi người chấm có thể đối chiếu **hai trạng thái**; ảnh chỉ thấy `production` đang ở một version chưa chứng minh có thay đổi. Có hai cách theo yêu cầu giảng viên:

1. **Ảnh trước/sau:** ảnh 09 bạn đã chụp là trạng thái trước, với `production` ở v1. Trong UI prompt `day13-chat`, chuyển `production` sang v2, chờ UI cập nhật, rồi chụp trạng thái sau vào `10-prompt-change.png`. Ghi trong report rằng ảnh 09 là trước promote (v1) và ảnh 10 là sau promote (v2). Như vậy mục 10 chỉ cần **một PNG mới**, nhưng bằng chứng so sánh gồm cả ảnh 09. Nếu sau đó rollback về v1, ghi lại hành động và có thể lưu thêm ảnh sau rollback.
2. **So sánh trace IDs:** dùng một ảnh màn hình Langfuse hiển thị hai trace thực tế với trace ID, thời điểm và prompt version khác nhau trước/sau đổi label. Cả hai request nên có `prompt_label=production` để chứng minh chính label đó đã chuyển version. Ghi hai ID và version tương ứng trong report. Không ghép hai ảnh riêng thành một ảnh dựng.

Sau khi đổi label, restart API để bỏ cache prompt cũ, gửi một request dùng label `production`, rồi mở trace xác nhận version được dùng thật. Nếu quyền project không cho sửa label hoặc thao tác thất bại, ghi blocker và trạng thái thật; không sửa ảnh để giả promote/rollback.

## E. Ảnh dashboard

### Khởi động dashboard local

Đảm bảo API đã nhận workload và `data/logs.jsonl` có log mới. Giữ API chạy ở Terminal 1; tại Terminal 3 từ thư mục gốc chạy:

```powershell
python scripts/dashboard.py
```

Chờ terminal báo dashboard tại `http://127.0.0.1:8501`; mở địa chỉ đó trong trình duyệt. Chờ đủ sáu panel và refresh dữ liệu. Dashboard đọc cửa sổ 60 phút gần nhất, nên phải có request trong khoảng đó.

### 11 — `11-dashboard-overview.png` hoặc ba ảnh `11a/11b/11c`

Chụp trực tiếp trình duyệt dashboard local, có tiêu đề dashboard, khoảng thời gian UTC và cả 6 panel có dữ liệu. Cần đọc được tên panel, unit, threshold; Latency phải có TTFT và Errors phải có retrieval success.

Nếu một ảnh khiến chữ nhỏ, lưu thành ba ảnh thật:

- `11a-dashboard-latency-traffic.png`: Latency và Traffic.
- `11b-dashboard-errors-cost.png`: Errors và Cost.
- `11c-dashboard-tokens-quality.png`: Tokens và Quality.

Mỗi ảnh phải giữ tiêu đề/dashboard hoặc time range và toàn bộ panel liên quan. Sau đó cập nhật evidence index trong report để dẫn đủ ba ảnh.

## F. Ảnh challenge: chỉ dùng challenge được Lab Coach cấp

### Điều kiện trước khi làm

Chỉ dùng challenge chính thức sau khi Lab Coach đã cấp file riêng cho lớp và file `config/challenge.json` hiện có trong máy cá nhân. Không tạo, sửa, chia sẻ hoặc chụp file này. Nếu chưa có challenge file, dừng tại đây: không dùng practice scenario hoặc dữ liệu giả thay cho incident evidence CP3.

Giữ log baseline để so sánh. Mở dashboard ở bước E trước hoặc sau workload, miễn time range 60 phút bao trùm cả baseline và incident.

Chạy đúng các lệnh challenge từ thư mục gốc, với API đang chạy:

```powershell
python scripts/inject_incident.py
python scripts/load_test.py --challenge --concurrency 5
```

Đợi toàn bộ request xong, rồi dùng dashboard để xác định metric và khoảng bất thường. Tắt incident theo hướng dẫn của Lab Coach/runbook sau khi thu thập dữ liệu cần thiết. Không đưa query, seed hoặc raw challenge input lên ảnh/report.

### 12 — `12-incident-metric.png`: dashboard sau challenge

1. Refresh dashboard thật ở `http://127.0.0.1:8501`.
2. Xác nhận cửa sổ UTC hiển thị có cả baseline lẫn thời gian challenge.
3. Chụp panel metric có điểm bất thường và đường/tham chiếu baseline trên cùng trục thời gian. Giữ tên panel, unit, threshold và time range trong ảnh.
4. Ghi số đo và khoảng thời gian đúng như dashboard; không tự vẽ điểm hoặc khẳng định một spike không hiển thị.

### 13 — `13-incident-log.png`: một log line của request bất thường

Ảnh 13 chỉ cần một request đại diện, nằm gần thời điểm metric bất thường trong ảnh 12. Với sự cố chậm, chọn event `response_sent` có `latency_ms` cao; nếu ảnh 12 cho thấy lỗi, chọn `request_failed` và `error_type`/`tool_success` tương ứng. Không lấy một request chậm ở ngoài khoảng challenge chỉ vì nó có latency lớn hơn. Ví dụ trong ảnh dashboard bạn vừa chụp, đợt challenge nằm khoảng **08:51–08:52 UTC**; request 4099 ms lúc 08:45 UTC thuộc đợt trước, không đại diện cho đợt đó. Nếu bạn chạy challenge lại, dùng thời gian mới trong ảnh 12.

1. Giữ API và file `data/logs.jsonl` từ lần chạy đã chụp ảnh 12. Trong PowerShell tại thư mục gốc repo, nhập khoảng UTC bao quanh đợt bất thường. Ví dụ dưới đây dành cho ảnh 12 hiện tại; thay hai mốc nếu ảnh của bạn khác:

   ```powershell
   $fromUtc = [DateTimeOffset]::Parse('2026-09-30T08:51:00Z')
   $toUtc   = [DateTimeOffset]::Parse('2026-09-30T08:53:00Z')
   $rows = Get-Content 'data/logs.jsonl' | ForEach-Object { $_ | ConvertFrom-Json }
   $candidates = $rows | Where-Object {
     $_.event -in @('response_sent','request_failed') -and
     [DateTimeOffset]::Parse($_.ts) -ge $fromUtc -and
     [DateTimeOffset]::Parse($_.ts) -lt $toUtc
   }
   $candidates | Select-Object ts,event,correlation_id,latency_ms,error_type,tool_name,tool_success | Format-Table -AutoSize
   ```

2. Chọn **một** `correlation_id` có metric/log field bất thường và đúng khoảng UTC. Chép ID từ output, không tự tạo ID cho ảnh này. `req-aa61e703` trong lệnh dưới chỉ là ví dụ từ log lần chạy 08:51 UTC; **chỉ dùng làm evidence cuối khi tìm thấy trace cùng ID trong Langfuse**. Nếu bạn chạy lại challenge, thay ID ở dòng đầu bằng ID mới. Dán **từng dòng lệnh** sau vào PowerShell, không dán dấu nhắc `PS ...>` hoặc `>>`. Lệnh đọc các field an toàn từ **dòng gốc** trong `data/logs.jsonl`, kèm số dòng; không in payload hay query challenge:

   ```powershell
   $rid = 'req-aa61e703'
   $matches = Select-String -Path 'data/logs.jsonl' -SimpleMatch -Pattern $rid
   $match = $matches | Where-Object { ($_.Line | ConvertFrom-Json).event -in @('response_sent','request_failed') } | Select-Object -Last 1
   $record = $match.Line | ConvertFrom-Json
   "Source: data/logs.jsonl:$($match.LineNumber)"
   $record | Select-Object ts,event,correlation_id,latency_ms,error_type,tool_name,tool_success | Format-List
   ```

   Nếu PowerShell hiện dấu nhắc `>>` liên tục, nhấn `Ctrl+C` để hủy câu lệnh chưa hoàn tất rồi dán lại từ dòng `$rid = ...`. `Read-Host 'Nhap correlation_id...'` (nếu dùng) chỉ đặt **câu hỏi** trên màn hình; ID phải nhập sau khi nhấn Enter ở câu hỏi đó. Không đặt ID bên trong dấu nháy của `Read-Host`.

3. Chụp terminal thật sao cho đọc được `source`, `ts`, `event`, `correlation_id` và `latency_ms` hoặc field lỗi bất thường. `ts` phải gần khoảng bất thường trong ảnh 12. Giá trị trống ở field không áp dụng (ví dụ `error_type` của `response_sent`) là bình thường; không điền số giả. Lưu ảnh thành `submission/evidence/13-incident-log.png`.

4. Ghi lại đúng `$rid` và dùng nó tìm trace trong project Langfuse cá nhân cho ảnh 14. Trước khi chụp ảnh 14, mở metadata trace và xác nhận `correlation_id` khớp ảnh 13. Nếu trace chưa xuất hiện, chờ ingestion/refresh và kiểm tra time range (Langfuse UI có thể hiện giờ Việt Nam, tức UTC+7). Nếu vẫn không tìm được trace của **bất kỳ** request nào trong đợt challenge, kiểm tra việc xuất trace từ API rồi chạy lại baseline và challenge; chụp lại ảnh 12–13 theo thời gian/ID mới trước khi chụp ảnh 14. Không ghép ảnh 13 cũ với trace ID khác. Trong report, ghi cùng ID, timestamp UTC và giá trị bất thường; không đưa raw challenge input, query hay seed vào ảnh/report.

### 14 — `14-incident-trace.png`: trace của cùng request

1. Mở đúng project Langfuse cá nhân → **Tracing**.
2. Tìm trace theo correlation ID đã chọn ở ảnh 13. Mở trace và kiểm tra ID metadata trùng khớp.
3. Chụp trace detail thật có tên project, trace ID, correlation ID, timestamp và tree/duration các span.
4. Span được nêu trong report phải là span UI cho thấy duration/status bất thường. Không mở raw Input/Output hoặc API Keys.

## G. Tên file, kiểm tra và link report

Lưu ảnh chụp thật theo danh sách:

```text
01-pytest.png
02-log-validator.png
03-dashboard-validator.png
04-structured-log.png
05-pii-redaction.png
06-trace-list.png
07-trace-waterfall.png
08-trace-metadata.png
09-prompt-versions.png
10-prompt-change.png  (ảnh 09 là trạng thái trước; có thể bổ sung ảnh rollback)
11-dashboard-overview.png  (hoặc 11a-dashboard-latency-traffic.png,
                             11b-dashboard-errors-cost.png,
                             11c-dashboard-tokens-quality.png)
12-incident-metric.png
13-incident-log.png
14-incident-trace.png
```

Mở lại từng file PNG vừa lưu để kiểm tra ảnh đọc được và đúng nguồn. Sau đó cập nhật Evidence index và các giá trị trong `submission/REPORT.md`. Chỉ dẫn ảnh bằng đường dẫn tương đối, ví dụ:

```markdown
![Trace waterfall](evidence/07-trace-waterfall.png)
```

Không ghi `C:\Users\...` hoặc đường dẫn máy cá nhân vào report. Tham khảo thêm yêu cầu evidence tại [docs/SUBMISSION.md](../../docs/SUBMISSION.md). Langfuse UI và tên menu có thể thay đổi theo phiên bản; bằng chứng vẫn phải là project cá nhân và dữ liệu thật. Tài liệu chính thức: [trace tree và metadata](https://langfuse.com/docs/observability/best-practices), [trace metadata](https://langfuse.com/docs/observability/features/metadata), [prompt version labels](https://langfuse.com/docs/prompt-management/features/prompt-version-control).
