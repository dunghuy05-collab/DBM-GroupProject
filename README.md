# Project: Electricity Consumption Pattern Mining

## 1. Dataset sử dụng

Dataset chính của project là:

**UCI Individual Household Electric Power Consumption**

Link dataset:

https://archive.ics.uci.edu/dataset/235/individual%2Bhousehold%2Belectric%2Bpower%2Bconsumption

Dataset này ghi lại dữ liệu tiêu thụ điện của **một hộ gia đình** với tần suất **1 phút/lần** trong gần **4 năm**, từ tháng 12/2006 đến tháng 11/2010.

Mục tiêu của project là dùng dữ liệu này để:

- Phân tích thói quen sử dụng điện.
- Tìm các mẫu tiêu thụ điện phổ biến.
- Phát hiện ngày hoặc giờ tiêu thụ điện bất thường.
- Đề xuất cảnh báo khi mức dùng điện vượt ngưỡng bình thường.

---

## 2. Các cột dữ liệu gốc

File dữ liệu chính là:

```text
household_power_consumption.txt
```

Các cột trong dataset:

| Cột | Ý nghĩa |
|---|---|
| `Date` | Ngày ghi nhận dữ liệu, dạng `dd/mm/yyyy` |
| `Time` | Thời điểm ghi nhận dữ liệu, dạng `hh:mm:ss` |
| `Global_active_power` | Công suất tiêu thụ thực tế của hộ gia đình, đơn vị kW |
| `Global_reactive_power` | Công suất phản kháng, đơn vị kW |
| `Voltage` | Điện áp trung bình theo phút, đơn vị Volt |
| `Global_intensity` | Cường độ dòng điện, đơn vị Ampere |
| `Sub_metering_1` | Điện tiêu thụ nhóm thiết bị/khu vực 1 |
| `Sub_metering_2` | Điện tiêu thụ nhóm thiết bị/khu vực 2 |
| `Sub_metering_3` | Điện tiêu thụ nhóm thiết bị/khu vực 3 |

Trong project này, cột quan trọng nhất là:

```text
Global_active_power
```

Vì cột này cho biết hộ gia đình đang tiêu thụ bao nhiêu điện tại mỗi thời điểm.

---

## 3. Vấn đề của dữ liệu gốc

Dữ liệu gốc chưa thể dùng trực tiếp để phân tích hoặc chạy mô hình vì có một số vấn đề:

1. `Date` và `Time` đang bị tách thành hai cột riêng.
2. Một số cột số có thể đang được đọc dưới dạng text.
3. Dataset có missing values.
4. Dữ liệu theo từng phút nên rất lớn và khó phân tích trực tiếp.
5. Chưa có các biến thời gian như giờ, thứ, tháng, cuối tuần.
6. Chưa có cột điện năng tiêu thụ theo kWh.

Vì vậy, cần xử lý dữ liệu trước khi phân tích.

---

## 4. Quy trình xử lý dữ liệu

Pipeline xử lý dữ liệu dự kiến:

```text
Raw data
→ Gộp Date + Time
→ Chuyển dữ liệu sang numeric
→ Xử lý missing values
→ Tạo cột energy_kwh
→ Gom dữ liệu theo giờ và theo ngày
→ Tạo thêm feature mới
→ Lưu dữ liệu sạch
```

---

## 5. Bước 1: Gộp Date và Time

Dữ liệu gốc có hai cột riêng:

```text
Date = 16/12/2006
Time = 17:24:00
```

Ta sẽ gộp lại thành một cột mới:

```text
datetime = 2006-12-16 17:24:00
```

Lý do cần tạo `datetime`:

- Dễ sắp xếp dữ liệu theo thời gian.
- Dễ phân tích theo giờ, ngày, tháng.
- Dễ resampling dữ liệu từ phút sang giờ/ngày.
- Dễ vẽ biểu đồ time-series.

---

## 6. Bước 2: Chuyển dữ liệu sang dạng số

Các cột như:

```text
Global_active_power
Global_reactive_power
Voltage
Global_intensity
Sub_metering_1
Sub_metering_2
Sub_metering_3
```

cần được chuyển sang kiểu numeric.

Ví dụ:

```text
"4.216" → 4.216
"?" → missing value
```

Nếu không chuyển sang numeric, Python sẽ hiểu các giá trị này là chữ, khi đó không thể tính tổng, trung bình, độ lệch chuẩn hoặc chạy mô hình được.

---

## 7. Bước 3: Xử lý missing values

Dataset này có missing values. Missing values là các điểm dữ liệu bị thiếu.

Có hai cách xử lý phổ biến:

| Cách xử lý | Ưu điểm | Nhược điểm |
|---|---|---|
| Xóa dòng bị thiếu | Đơn giản, dễ làm | Có thể mất dữ liệu |
| Nội suy theo thời gian | Giữ được chuỗi dữ liệu liên tục | Giá trị được ước lượng |

Trong project này, nên dùng:

```text
interpolation theo thời gian
```

Ví dụ:

```text
10:00 → 0.4 kW
10:01 → missing
10:02 → 0.6 kW
```

Sau khi nội suy:

```text
10:01 → khoảng 0.5 kW
```

Cách này phù hợp vì dữ liệu điện là dữ liệu time-series.

---

## 8. Bước 4: Tạo cột energy_kwh

Cột `Global_active_power` có đơn vị là kW.

Tuy nhiên, hóa đơn điện thường tính theo kWh. Vì dữ liệu được ghi mỗi phút, điện năng tiêu thụ trong một phút được tính như sau:

```text
energy_kwh = Global_active_power / 60
```

Ví dụ:

```text
Global_active_power = 1.2 kW
energy_kwh = 1.2 / 60 = 0.02 kWh
```

Cột `energy_kwh` sẽ được dùng để:

- Tính tổng điện tiêu thụ theo giờ.
- Tính tổng điện tiêu thụ theo ngày.
- Phát hiện ngày tiêu thụ điện bất thường.
- Làm dashboard và báo cáo.

---

## 9. Bước 5: Gom dữ liệu theo giờ và theo ngày

Dữ liệu gốc theo từng phút nên có hơn 2 triệu dòng. Nếu phân tích trực tiếp sẽ khá nặng.

Vì vậy, ta sẽ tạo thêm hai bảng dữ liệu sạch:

```text
hourly_consumption.csv
daily_consumption.csv
```

### 9.1. Dữ liệu theo giờ

Dữ liệu theo giờ được tạo bằng cách cộng tổng `energy_kwh` trong từng giờ.

Ví dụ:

```text
2006-12-16 17:00:00 → tổng kWh từ 17:00 đến 17:59
2006-12-16 18:00:00 → tổng kWh từ 18:00 đến 18:59
```

Dữ liệu theo giờ dùng để:

- Xem giờ nào dùng điện cao nhất.
- So sánh tiêu thụ điện giữa các khung giờ.
- Vẽ heatmap giờ trong ngày × thứ trong tuần.

### 9.2. Dữ liệu theo ngày

Dữ liệu theo ngày được tạo bằng cách cộng tổng `energy_kwh` trong từng ngày.

Ví dụ:

```text
2006-12-16 → tổng kWh trong ngày 16/12/2006
2006-12-17 → tổng kWh trong ngày 17/12/2006
```

Dữ liệu theo ngày dùng để:

- Xem ngày nào dùng điện cao nhất.
- So sánh ngày thường và cuối tuần.
- Phát hiện ngày tiêu thụ điện bất thường.
- Tính rolling mean 7 ngày.

---

## 10. Bước 6: Tạo feature mới

Sau khi có cột `datetime`, ta có thể tạo thêm các feature mới.

| Feature | Ý nghĩa |
|---|---|
| `hour` | Giờ trong ngày |
| `day_of_week` | Thứ trong tuần |
| `month` | Tháng |
| `is_weekend` | Có phải cuối tuần không |
| `daily_consumption` | Tổng điện tiêu thụ trong ngày |
| `evening_usage_ratio` | Tỷ lệ điện dùng vào buổi tối |
| `night_usage_ratio` | Tỷ lệ điện dùng vào ban đêm |
| `rolling_mean_7d` | Trung bình trượt 7 ngày |
| `z_score` | Điểm bất thường |

Các feature này sẽ giúp project trả lời các câu hỏi như:

- Nhà dùng điện nhiều vào giờ nào?
- Cuối tuần có dùng điện khác ngày thường không?
- Buổi tối có phải là thời điểm dùng điện cao nhất không?
- Ngày nào có mức tiêu thụ vượt xa bình thường?

---

## 11. Dữ liệu đầu ra sau xử lý

Sau bước xử lý dữ liệu, project sẽ có hai file chính:

```text
hourly_consumption.csv
daily_consumption.csv
```

### `hourly_consumption.csv`

File này chứa dữ liệu tiêu thụ điện theo giờ.

Dùng cho:

- EDA theo giờ.
- Heatmap giờ × thứ.
- Phân tích pattern theo khung giờ.

### `daily_consumption.csv`

File này chứa dữ liệu tiêu thụ điện theo ngày.

Dùng cho:

- EDA theo ngày/tháng.
- Phát hiện anomaly.
- Tạo luật pattern theo ngày.
- Làm dashboard tổng quan.

---

## 12. Tóm tắt phần xử lý data

Nói ngắn gọn, phần xử lý data sẽ biến dữ liệu gốc:

```text
Dữ liệu theo phút, nhiều dòng, có missing values
```

thành:

```text
Dữ liệu sạch theo giờ và theo ngày
```

Từ đó, project có thể tiếp tục làm:

- EDA.
- Pattern discovery.
- Anomaly detection.
- Dashboard.

---

## 13. Bước hiện tại của project

Hiện tại project đang ở bước:

```text
Bước 2: Đọc và kiểm tra dữ liệu gốc
```

Mục tiêu của bước này chưa phải là làm sạch dữ liệu. Mục tiêu chỉ là kiểm tra:

- File dataset có đọc được không.
- Dataset có bao nhiêu dòng và bao nhiêu cột.
- Tên các cột là gì.
- 5 dòng đầu tiên trông như thế nào.
- Kiểu dữ liệu ban đầu của từng cột.
- Cột nào có missing values.

Các file/thư mục đã tạo cho bước này:

```text
data/raw/.gitkeep
data/processed/.gitkeep
src/load_data.py
requirements.txt
.gitignore
```

Trong đó:

| File/thư mục | Ý nghĩa |
|---|---|
| `data/raw/` | Nơi đặt file dữ liệu gốc |
| `data/processed/` | Nơi lưu dữ liệu sau khi xử lý ở các bước sau |
| `src/load_data.py` | Code đọc và kiểm tra dữ liệu gốc |
| `requirements.txt` | Danh sách thư viện Python cần cài |
| `.gitignore` | Không đẩy file data lớn lên GitHub |

Lưu ý: file dữ liệu gốc khá lớn nên không nên commit lên GitHub.

---

## 14. Cách chạy bước đọc dữ liệu

Trước tiên, tải dataset từ UCI và giải nén file:

```text
household_power_consumption.txt
```

Sau đó đặt file vào:

```text
data/raw/household_power_consumption.txt
```

Cài thư viện cần thiết:

```powershell
pip install -r requirements.txt
```

Chạy script kiểm tra dữ liệu:

```powershell
python src/load_data.py
```

Kết quả mong đợi là chương trình sẽ in ra:

- Số dòng, số cột.
- Danh sách cột.
- 5 dòng đầu.
- Kiểu dữ liệu.
- Số missing values ở từng cột.

---

## 15. Bước 3: Làm sạch dữ liệu

Sau khi đã đọc được dữ liệu gốc, bước tiếp theo là làm sạch dữ liệu.

File code cho bước này:

```text
src/preprocess_data.py
```

Bước này làm các việc sau:

1. Gộp `Date` và `Time` thành một cột thời gian tên là `datetime`.
2. Chuyển các cột số sang dạng numeric.
3. Sắp xếp dữ liệu theo thời gian.
4. Đưa `datetime` thành index của bảng dữ liệu.
5. Xử lý missing values bằng nội suy theo thời gian.
6. Tạo cột `energy_kwh`.
7. Tạo thêm các feature thời gian: `hour`, `day_of_week`, `month`, `is_weekend`.

### 15.1. Vì sao cần gộp Date và Time?

Dữ liệu gốc có:

```text
Date = 16/12/2006
Time = 17:24:00
```

Sau khi xử lý sẽ thành:

```text
datetime = 2006-12-16 17:24:00
```

Nhờ đó ta có thể phân tích dữ liệu theo giờ, ngày, tuần, tháng.

### 15.2. Vì sao xử lý missing values bằng nội suy?

Dữ liệu điện là dữ liệu theo thời gian. Nếu một vài phút bị thiếu, ta có thể ước lượng giá trị bị thiếu dựa vào giá trị trước và sau nó.

Ví dụ:

```text
10:00 → 0.4 kW
10:01 → missing
10:02 → 0.6 kW
```

Sau nội suy:

```text
10:01 → khoảng 0.5 kW
```

### 15.3. Vì sao tạo energy_kwh?

`Global_active_power` có đơn vị kW. Nhưng khi tính điện tiêu thụ, ta thường dùng kWh.

Vì dữ liệu được ghi mỗi phút:

```text
energy_kwh = Global_active_power / 60
```

Ví dụ:

```text
Global_active_power = 1.2 kW
energy_kwh = 1.2 / 60 = 0.02 kWh
```

### 15.4. Cách chạy bước clean data

Chạy lệnh:

```powershell
python src/preprocess_data.py
```

Sau khi chạy thành công, file dữ liệu sạch sẽ được tạo tại:

```text
data/processed/clean_power_consumption.csv
```

File này không được commit lên GitHub vì dữ liệu khá lớn.
