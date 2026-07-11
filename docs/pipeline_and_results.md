# Luồng Chạy Project Và Kết Quả Phân Tích

## 1. Tổng quan project

Tên project:

```text
Electricity Consumption Pattern Mining for Household Anomaly Detection
```

Mục tiêu của project là phân tích dữ liệu tiêu thụ điện của một hộ gia đình để:

- Hiểu thói quen sử dụng điện theo giờ, ngày, tháng.
- Tìm các ngày tiêu thụ điện bất thường.
- Khai phá các mẫu tiêu thụ điện phổ biến bằng Apriori.
- Tạo output dạng bảng và biểu đồ để dùng cho báo cáo hoặc dashboard.

Dataset sử dụng:

```text
UCI Individual Household Electric Power Consumption
```

Đặc điểm dataset:

| Thuộc tính | Giá trị |
|---|---|
| Số dòng gốc | 2,075,259 |
| Số cột gốc | 9 |
| Tần suất ghi nhận | 1 phút/lần |
| Khoảng thời gian | 12/2006 đến 11/2010 |
| Đối tượng | 1 hộ gia đình |

---

## 2. Cấu trúc luồng chạy

Toàn bộ project được chạy theo pipeline:

```text
Raw data
-> Inspect data
-> Clean data
-> Resample hourly/daily
-> EDA
-> Anomaly detection
-> Pattern mining
-> Output tables/figures
```

File chạy toàn bộ pipeline:

```text
src/run_pipeline.py
```

Lệnh chạy:

```powershell
python src/run_pipeline.py
```

---

## 3. Bước 1: Đọc và kiểm tra dữ liệu gốc

File code:

```text
src/load_data.py
```

Mục tiêu:

- Đọc file `household_power_consumption.txt`.
- Kiểm tra số dòng, số cột.
- Kiểm tra tên cột.
- Kiểm tra kiểu dữ liệu.
- Kiểm tra missing values.

Kết quả:

```text
Rows: 2,075,259
Columns: 9
```

Các cột:

```text
Date
Time
Global_active_power
Global_reactive_power
Voltage
Global_intensity
Sub_metering_1
Sub_metering_2
Sub_metering_3
```

Missing values ban đầu:

| Cột | Missing values |
|---|---:|
| Global_active_power | 25,979 |
| Global_reactive_power | 25,979 |
| Voltage | 25,979 |
| Global_intensity | 25,979 |
| Sub_metering_1 | 25,979 |
| Sub_metering_2 | 25,979 |
| Sub_metering_3 | 25,979 |

Nhận xét:

Dữ liệu có missing values ở các cột đo điện. Vì đây là dữ liệu chuỗi thời gian, project xử lý missing values bằng nội suy theo thời gian.

---

## 4. Bước 2: Làm sạch dữ liệu

File code:

```text
src/preprocess_data.py
```

Các xử lý chính:

1. Gộp `Date` và `Time` thành `datetime`.
2. Chuyển các cột đo điện sang numeric.
3. Sắp xếp dữ liệu theo thời gian.
4. Đặt `datetime` làm index.
5. Nội suy missing values theo thời gian.
6. Tạo cột `energy_kwh`.
7. Tạo feature thời gian: `hour`, `day_of_week`, `month`, `is_weekend`.

Công thức tạo điện năng tiêu thụ:

```text
energy_kwh = Global_active_power / 60
```

Lý do:

`Global_active_power` có đơn vị kW và dữ liệu được ghi mỗi phút. Vì 1 giờ có 60 phút, điện năng tiêu thụ trong 1 phút là `kW / 60`.

Kết quả:

```text
Rows after cleaning: 2,075,259
Columns after cleaning: 14
Missing values after cleaning: 0
```

File output local:

```text
data/processed/clean_power_consumption.csv
```

---

## 5. Bước 3: Gom dữ liệu theo giờ và theo ngày

File code:

```text
src/resample_data.py
```

Mục tiêu:

Dữ liệu gốc theo phút quá lớn và khó phân tích trực tiếp, nên project gom dữ liệu thành:

```text
hourly_consumption.csv
daily_consumption.csv
```

Kết quả:

| Bảng | Số dòng |
|---|---:|
| Hourly data | 34,589 |
| Daily data | 1,442 |

File output local:

```text
data/processed/hourly_consumption.csv
data/processed/daily_consumption.csv
```

Các feature quan trọng trong daily data:

| Feature | Ý nghĩa |
|---|---|
| `daily_consumption` | Tổng điện tiêu thụ trong ngày |
| `avg_hourly_consumption` | Điện tiêu thụ trung bình mỗi giờ |
| `max_hourly_consumption` | Giờ có mức tiêu thụ cao nhất trong ngày |
| `evening_usage_ratio` | Tỷ lệ điện dùng buổi tối |
| `night_usage_ratio` | Tỷ lệ điện dùng ban đêm |
| `rolling_mean_7d` | Trung bình trượt 7 ngày |
| `is_weekend` | Có phải cuối tuần không |

---

## 6. Bước 4: EDA

File code:

```text
src/eda_analysis.py
```

EDA được dùng để hiểu dữ liệu trước khi chạy mô hình hoặc thuật toán khai phá.

### 6.1. Điện tiêu thụ trung bình theo giờ

Công thức:

```text
avg_energy_kwh_by_hour = mean(energy_kwh) theo từng hour
```

Top 5 giờ tiêu thụ điện trung bình cao nhất:

| Giờ | kWh trung bình |
|---:|---:|
| 20:00 | 1.890 |
| 21:00 | 1.867 |
| 19:00 | 1.725 |
| 07:00 | 1.494 |
| 08:00 | 1.454 |

Nhận xét:

Hộ gia đình dùng điện nhiều nhất vào buổi tối, đặc biệt khoảng 20:00-21:00. Điều này phù hợp với hành vi sinh hoạt gia đình sau giờ làm/học.

### 6.2. Điện tiêu thụ trung bình theo tháng

Công thức:

```text
avg_daily_consumption_by_month = mean(daily_consumption) theo từng month
```

Top 5 tháng có điện tiêu thụ trung bình/ngày cao nhất:

| Tháng | kWh/ngày trung bình |
|---:|---:|
| 12 | 35.522 |
| 1 | 35.219 |
| 2 | 31.208 |
| 11 | 30.967 |
| 3 | 29.437 |

Nhận xét:

Các tháng mùa lạnh như 12, 1, 2 có mức tiêu thụ cao hơn. Điều này có thể liên quan đến nhu cầu sưởi ấm hoặc sinh hoạt trong nhà nhiều hơn.

### 6.3. So sánh ngày thường và cuối tuần

Công thức:

```text
mean(daily_consumption) theo is_weekend
```

Kết quả:

| Loại ngày | kWh/ngày trung bình |
|---|---:|
| Weekday | 24.888 |
| Weekend | 29.309 |

Nhận xét:

Cuối tuần có mức tiêu thụ điện cao hơn ngày thường. Điều này hợp lý vì các thành viên có thể ở nhà nhiều hơn.

### 6.4. Top 10 ngày tiêu thụ điện cao nhất

| Ngày | kWh |
|---|---:|
| 2006-12-23 | 79.556 |
| 2007-02-03 | 67.162 |
| 2006-12-26 | 65.568 |
| 2007-02-18 | 63.829 |
| 2007-02-04 | 59.932 |
| 2007-02-11 | 59.520 |
| 2007-03-31 | 58.492 |
| 2006-12-31 | 58.237 |
| 2007-03-11 | 58.011 |
| 2008-11-23 | 56.790 |

Output EDA:

```text
outputs/tables/avg_consumption_by_hour.csv
outputs/tables/avg_daily_consumption_by_month.csv
outputs/tables/weekday_vs_weekend.csv
outputs/tables/top_10_consumption_days.csv
outputs/tables/usage_heatmap_day_hour.csv
outputs/figures/avg_consumption_by_hour.png
outputs/figures/avg_daily_consumption_by_month.png
outputs/figures/usage_heatmap_day_hour.png
```

---

## 7. Bước 5: Phát hiện bất thường bằng Z-score

File code:

```text
src/anomaly_detection.py
```

Mục tiêu:

Tìm các ngày có mức tiêu thụ điện lệch xa so với mức tiêu thụ bình thường.

Công thức:

```text
z_score = (x - mean) / std
```

Trong đó:

| Thành phần | Ý nghĩa |
|---|---|
| `x` | Điện tiêu thụ của một ngày |
| `mean` | Điện tiêu thụ trung bình/ngày |
| `std` | Độ lệch chuẩn |

Quy tắc:

```text
Nếu |z_score| > 3 -> Abnormal
Ngược lại -> Normal
```

Kết quả:

```text
Total days: 1,442
Abnormal days: 13
```

Top ngày bất thường:

| Ngày | kWh | Z-score |
|---|---:|---:|
| 2006-12-23 | 79.556 | 5.324 |
| 2007-02-03 | 67.162 | 4.088 |
| 2006-12-26 | 65.568 | 3.929 |
| 2007-02-18 | 63.829 | 3.756 |
| 2007-02-04 | 59.932 | 3.368 |

Nhận xét:

Các ngày bất thường chủ yếu là các ngày có tổng điện tiêu thụ rất cao so với trung bình. Ngày 2006-12-23 là ngày bất thường mạnh nhất với z-score khoảng 5.324.

Output:

```text
outputs/tables/daily_consumption_with_zscore.csv
outputs/tables/zscore_anomalies.csv
```

---

## 8. Bước 6: Pattern Mining bằng Apriori

File code:

```text
src/pattern_mining.py
```

Mục tiêu:

Tìm các mẫu tiêu thụ điện thường xuất hiện trong dữ liệu theo ngày.

### 8.1. Chuyển dữ liệu thành transaction

Apriori không xử lý trực tiếp số liên tục, nên project chuyển dữ liệu thành nhãn.

Ví dụ:

```text
daily_consumption = 35.2
```

có thể được chuyển thành:

```text
total_usage_high
```

Một transaction đại diện cho một ngày:

```text
weekend_yes, total_usage_high, evening_usage_high, night_usage_low, peak_hour_usage_high
```

Các nhóm nhãn:

| Nhóm | Ý nghĩa |
|---|---|
| `total_usage_low/medium/high` | Tổng điện tiêu thụ trong ngày |
| `evening_usage_low/medium/high` | Tỷ lệ điện dùng buổi tối |
| `night_usage_low/medium/high` | Tỷ lệ điện dùng ban đêm |
| `peak_hour_usage_low/medium/high` | Mức tiêu thụ cao nhất trong một giờ |
| `weekend_yes/weekend_no` | Có phải cuối tuần không |

### 8.2. Chỉ số đánh giá luật

Công thức:

```text
support(A -> B) = count(A and B) / total_transactions
confidence(A -> B) = count(A and B) / count(A)
lift(A -> B) = confidence(A -> B) / support(B)
```

Ý nghĩa:

| Chỉ số | Ý nghĩa |
|---|---|
| `support` | Pattern xuất hiện thường xuyên đến mức nào |
| `confidence` | Nếu có A thì khả năng có B là bao nhiêu |
| `lift` | A và B có liên quan mạnh hơn ngẫu nhiên không |

Nếu `lift > 1`, vế trái và vế phải có quan hệ tích cực.

### 8.3. Kết quả Pattern Mining

Kết quả:

```text
Transactions: 1,442
Frequent itemsets: 114
Association rules: 178
```

Một số luật có lift cao:

| Antecedents | Consequents | Support | Confidence | Lift |
|---|---|---:|---:|---:|
| evening_usage_low, total_usage_low | night_usage_high, peak_hour_usage_low, weekend_no | 0.087 | 0.525 | 3.659 |
| night_usage_high, peak_hour_usage_low, weekend_no | evening_usage_low, total_usage_low | 0.087 | 0.604 | 3.659 |
| evening_usage_low, total_usage_low | night_usage_high, peak_hour_usage_low | 0.117 | 0.710 | 3.495 |
| night_usage_high, peak_hour_usage_low | evening_usage_low, total_usage_low | 0.117 | 0.577 | 3.495 |
| evening_usage_low, total_usage_low, weekend_no | night_usage_high, peak_hour_usage_low | 0.087 | 0.694 | 3.418 |

Nhận xét:

Các luật có lift cao cho thấy một số nhóm hành vi có xu hướng đi cùng nhau. Ví dụ, các ngày có tổng tiêu thụ thấp và dùng điện buổi tối thấp thường đi kèm với mức peak-hour thấp. Những luật này giúp mô tả pattern hành vi tiêu thụ điện theo ngày.

Output:

```text
outputs/tables/daily_transactions.csv
outputs/tables/frequent_itemsets.csv
outputs/tables/association_rules.csv
```

---

## 9. Tổng hợp kết quả chính

| Nội dung | Kết quả |
|---|---|
| Số dòng dữ liệu gốc | 2,075,259 |
| Missing values ban đầu | 25,979 ở các cột đo điện |
| Missing values sau clean | 0 |
| Số dòng hourly data | 34,589 |
| Số dòng daily data | 1,442 |
| Giờ tiêu thụ cao nhất | 20:00 |
| Tháng tiêu thụ cao nhất | Tháng 12 |
| Trung bình ngày thường | 24.888 kWh/ngày |
| Trung bình cuối tuần | 29.309 kWh/ngày |
| Số ngày bất thường | 13 |
| Frequent itemsets | 114 |
| Association rules | 178 |

---

## 10. Kết luận

Qua pipeline phân tích, project rút ra một số kết luận chính:

1. Hộ gia đình có xu hướng dùng điện cao vào buổi tối, đặc biệt khoảng 20:00-21:00.
2. Cuối tuần tiêu thụ điện cao hơn ngày thường.
3. Các tháng mùa lạnh như tháng 12 và tháng 1 có mức tiêu thụ trung bình/ngày cao nhất.
4. Z-score phát hiện được 13 ngày tiêu thụ điện bất thường.
5. Apriori tìm được các luật kết hợp mô tả quan hệ giữa tổng điện tiêu thụ, mức dùng buổi tối, ban đêm, peak-hour và cuối tuần.

Project hiện đã có đủ các phần cốt lõi cho một bài Data Mining/DBM:

```text
Data understanding
Data preprocessing
Feature engineering
EDA
Anomaly detection
Pattern mining
Result interpretation
```

