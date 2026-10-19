# TÀI LIỆU KIẾN TRÚC HỆ THỐNG QUẢN LÝ THƯ VIỆN
### Triển khai và Quản trị Hệ thống Phần mềm

---

## 1. Tổng Quan Kiến Trúc (Architecture Overview)

Hệ thống Quản lý Thư viện được xây dựng theo kiến trúc phân tầng dạng vi dịch vụ (Microservices-ready containerized architecture) được điều phối thông qua **Docker Compose**. Mô hình phân tách rõ ràng giữa 4 phân hệ:

1. **Phân hệ Proxy & Trình diễn (Edge & Presentation Layer)**: Nginx Reverse Proxy tiếp nhận lưu lượng HTTP/HTTPS, chấm dứt SSL (TLS Termination), áp dụng các chính sách bảo mật Security Headers và chuyển tiếp an toàn vào Flask App.
2. **Phân hệ Ứng dụng & Dữ liệu (Application & Persistence Layer)**: Flask WSGI Application kết nối với PostgreSQL 15, hỗ trợ công cụ quản trị web pgAdmin 4.
3. **Phân hệ Giám sát (Monitoring Layer)**: Prometheus thực hiện cào (scrape) chỉ số định kỳ từ Flask `/metrics`, `postgres_exporter`, `cAdvisor` và `node_exporter`. Grafana trực quan hóa dữ liệu qua các dashboard tự động nạp.
4. **Phân hệ Thu thập Log Tập Trung (Centralized Logging Layer)**: Promtail thu thập log file từ container và Nginx, đẩy dữ liệu về Loki, cho phép truy vấn LogQL thời gian thực.

---

## 2. Sơ Đồ Kiến Trúc Chi Tiết (Mermaid Diagram)

```mermaid
graph TB
    subgraph Internet_User ["Môi Trường Client / Trình Duyệt"]
        User["Người Dùng / Độc Giả<br>(Web Browser)"]
        Admin["Quản Trị Viên / Giảng Viên<br>(DevOps Engineer)"]
    end

    subgraph Host_Network ["Host Gateway / Port Mapping"]
        Port443["0.0.0.0:443 (HTTPS)"]
        Port80["0.0.0.0:80 (HTTP Redirect)"]
        Port5050["127.0.0.1:5050 (pgAdmin)"]
        Port3000["0.0.0.0:3000 (Grafana)"]
        Port9090["127.0.0.1:9090 (Prometheus)"]
    end

    User -->|HTTPS:443| Port443
    User -->|HTTP:80| Port80
    Port80 -.->|HTTP 301 Redirect| Port443
    Admin -->|Admin Access| Port5050
    Admin -->|Dashboards| Port3000
    Admin -->|Metrics Check| Port9090

    subgraph Docker_Network_Frontend ["Docker Network: frontend (Bridge)"]
        Nginx["Nginx 1.25 Alpine<br>(Reverse Proxy + SSL + Security Headers)"]
    end
    Port443 --> Nginx

    subgraph Docker_Network_Backend ["Docker Network: backend (Bridge, Internal)"]
        Flask["Flask App (Gunicorn)<br>Port 5000 (Non-root user)"]
        Postgres[("PostgreSQL 15 Alpine<br>Port 5432 (Data Persistent)")]
        pgAdmin["pgAdmin 4 Container<br>Port 80 (Internal)"]
    end
    Nginx -->|proxy_pass: web:5000| Flask
    Flask -->|Database Query| Postgres
    pgAdmin -->|DB Management| Postgres
    Port5050 --> pgAdmin

    subgraph Docker_Network_Monitoring ["Docker Network: monitoring (Bridge)"]
        Prometheus["Prometheus Server<br>Port 9090"]
        Grafana["Grafana Server<br>Port 3000"]
        PGExporter["postgres_exporter<br>Port 9187"]
        cAdvisor["cAdvisor Container<br>Port 8080"]
        NodeExporter["node_exporter<br>Port 9100"]
    end
    Port3000 --> Grafana
    Port9090 --> Prometheus
    Prometheus -->|Scrape /metrics| Flask
    Prometheus -->|Scrape :9187| PGExporter
    Prometheus -->|Scrape :8080| cAdvisor
    Prometheus -->|Scrape :9100| NodeExporter
    PGExporter -->|Metrics Query| Postgres
    Grafana -->|PromQL Query| Prometheus

    subgraph Docker_Network_Logging ["Docker Network: logging (Bridge)"]
        Promtail["Promtail Log Shipper"]
        Loki["Loki Log Database<br>Port 3100"]
    end
    Nginx -.->|Access/Error Logs| Promtail
    Flask -.->|App Logs| Promtail
    Promtail -->|Push Log Batches| Loki
    Grafana -->|LogQL Query| Loki
```

---

## 3. Thiết Kế Mạng Docker & Nguyên Tắc Đặc Quyền Tối Thiểu

Dự án phân bổ 4 Docker Network riêng biệt:

| Tên Network | Driver | Các Container Tham Gia | Mục Đích & Ràng Buộc Bảo Mật |
| :--- | :--- | :--- | :--- |
| `frontend` | bridge | `nginx`, `web` | Tiếp nhận và xử lý lưu lượng HTTP/S người dùng. Chỉ Nginx mở port ra ngoài. |
| `backend` | bridge | `web`, `db`, `pgadmin`, `postgres-exporter` | Lưu lượng truy vấn dữ liệu nhạy cảm. Không thể truy cập trực tiếp từ Internet. |
| `monitoring` | bridge | `prometheus`, `grafana`, `postgres-exporter`, `cadvisor`, `node-exporter`, `web` | Thu thập chỉ số định kỳ, cách ly luồng dữ liệu giám sát với luồng nghiệp vụ. |
| `logging` | bridge | `promtail`, `loki`, `grafana` | Vận chuyển log từ các dịch vụ về kho lưu trữ tập trung. |

---

## 4. Danh Sách Dịch Vụ Và Phân Bổ Tài Nguyên (Resource Limits)

| Tên Dịch Vụ | Docker Image | CPU Limit | Memory Limit | Restart Policy | Volume Gắn Kết |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `web` | Custom (Dockerfile) | 1.0 CPU | 512 MB | unless-stopped | `instance`, `logs` |
| `db` | `postgres:15-alpine` | 1.0 CPU | 512 MB | unless-stopped | `pg_data` |
| `pgadmin` | `dpage/pgadmin4:8.14` | 0.5 CPU | 384 MB | unless-stopped | `pgadmin_data` |
| `nginx` | `nginx:1.25-alpine` | 0.5 CPU | 256 MB | unless-stopped | `nginx.conf`, `certs`, `nginx_logs` |
| `prometheus`| `prom/prometheus:v2.50.1`| 0.5 CPU | 512 MB | unless-stopped | `prometheus.yml`, `prom_data` |
| `grafana` | `grafana/grafana:10.3.3` | 0.5 CPU | 512 MB | unless-stopped | `provisioning`, `dashboards`, `grafana_data` |
| `postgres-exporter`| `prometheuscommunity/postgres-exporter:v0.15.0` | 0.2 CPU | 128 MB | unless-stopped | - |
| `cadvisor` | `gcr.io/cadvisor/cadvisor:v0.49.1` | 0.5 CPU | 256 MB | unless-stopped | `/sys`, `/var/lib/docker` (ro) |
| `node-exporter`| `prom/node-exporter:v1.7.0` | 0.2 CPU | 128 MB | unless-stopped | `/proc`, `/sys` (ro) |
| `loki` | `grafana/loki:2.9.4` | 0.5 CPU | 512 MB | unless-stopped | `loki-config.yml`, `loki_data` |
| `promtail` | `grafana/promtail:2.9.4`| 0.2 CPU | 256 MB | unless-stopped | `promtail-config.yml`, `nginx_logs` |

---

## 5. Quy Trình Mượn Và Trả Sách (Transaction & Row Locking)

```mermaid
sequenceDiagram
    autonumber
    actor User as Độc giả / Thủ thư
    participant Web as Nginx & Flask Web
    participant Svc as LibraryService
    participant DB as PostgreSQL Database

    Note over User, DB: QUY TRÌNH MƯỢN SÁCH (BORROW FLOW)
    User->>Web: POST /loans/create (reader_id, book_ids, quantities)
    Web->>Svc: create_loan(reader_id, book_items, due_date)
    Svc->>DB: BEGIN TRANSACTION
    Svc->>DB: SELECT * FROM readers WHERE id = :id (Check Active)
    loop Với từng sách được chọn
        Svc->>DB: SELECT * FROM books WHERE id = :book_id FOR UPDATE (Row Lock)
        alt available_quantity < quantity
            Svc-->>Web: Rollback & Ném lỗi "Hết sách khả dụng"
            Web-->>User: Hiển thị thông báo lỗi (Flash Error)
        else available_quantity >= quantity
            Svc->>DB: UPDATE books SET available_quantity = available_quantity - :qty
            Svc->>DB: INSERT INTO loan_details (loan_id, book_id, quantity, returned=False)
        end
    end
    Svc->>DB: INSERT INTO loans (loan_code, reader_id, due_date, status='borrowing')
    Svc->>DB: COMMIT TRANSACTION
    Web-->>User: Thông báo tạo phiếu mượn thành công

    Note over User, DB: QUY TRÌNH TRẢ SÁCH (RETURN FLOW)
    User->>Web: POST /loans/return-item/{detail_id}
    Web->>Svc: return_loan_detail(detail_id)
    Svc->>DB: BEGIN TRANSACTION
    Svc->>DB: SELECT * FROM loan_details WHERE id = :detail_id FOR UPDATE
    alt returned == True
        Svc-->>Web: Ném lỗi "Sách đã được trả trước đó"
    else returned == False
        Svc->>DB: UPDATE loan_details SET returned=True, return_date=CURRENT_DATE
        Svc->>DB: SELECT * FROM books WHERE id = :book_id FOR UPDATE
        Svc->>DB: UPDATE books SET available_quantity = available_quantity + :qty
        Svc->>DB: Kiểm tra tất cả chi tiết phiếu mượn -> nếu đều returned=True thì cập nhật loans.status='returned'
        Svc->>DB: COMMIT TRANSACTION
        Web-->>User: Trả sách thành công
    end
```
