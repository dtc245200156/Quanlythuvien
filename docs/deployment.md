# HƯỚNG DẪN TRIỂN KHAI VÀ VẬN HÀNH HỆ THỐNG
### Đề tài: Hệ Thống Quản Lý Thư Viện

---

## 1. Yêu Cầu Môi Trường (System Prerequisites)

Để triển khai và chạy trơn tru toàn bộ hệ thống trên máy tính cá nhân hoặc máy chủ Ubuntu/Debian/Windows Server, cần chuẩn bị:

| Phần mềm / Công cụ | Phiên bản tối thiểu khuyến nghị | Ghi chú |
| :--- | :--- | :--- |
| **Hệ điều hành** | Windows 10/11 Pro (WSL2), Ubuntu 20.04+, macOS | Khuyên dùng hệ điều hành có hỗ trợ Docker native hoặc WSL2 |
| **Docker Desktop / Engine** | Docker 24.0+ hoặc mới hơn | Bắt buộc bật dịch vụ Docker daemon |
| **Docker Compose** | Docker Compose v2.20+ (`docker compose`) | Tích hợp sẵn trong Docker Desktop |
| **Git** | 2.30+ | Quản lý mã nguồn |
| **Python** (tùy chọn) | Python 3.10+ | Dùng để chạy script sinh certs / test độc lập trên host |
| **Tài nguyên phần cứng** | RAM >= 8GB, Ổ cứng trống >= 15GB | Đảm bảo đủ RAM cho 11 containers chạy đồng thời |

---

## 2. Quy Trình Cài Đặt Và Khởi Động Từ Đầu

### Bước 1: Sao chép mã nguồn từ GitHub
```bash
git clone https://github.com/[TÊN_TAI_KHOAN]/[TEN_REPO].git
cd Quanlythuvien
```

### Bước 2: Khởi tạo file cấu hình môi trường `.env`
Sao chép từ file mẫu `.env.example`:
```bash
# Trên Linux / macOS / Git Bash:
cp .env.example .env

# Trên Windows PowerShell:
Copy-Item .env.example .env

# Trên Windows Command Prompt (CMD):
copy .env.example .env
```
Mở file `.env` và tùy chỉnh các mật khẩu mạnh:
- `SECRET_KEY`: Khóa bí mật của Flask phiên làm việc
- `POSTGRES_PASSWORD`: Mật khẩu cơ sở dữ liệu PostgreSQL
- `PGADMIN_DEFAULT_PASSWORD`: Mật khẩu đăng nhập pgAdmin
- `GRAFANA_ADMIN_PASSWORD`: Mật khẩu tài khoản `admin` của Grafana

### Bước 3: Sinh chứng chỉ SSL tự ký cho Nginx (Local HTTPS)
Chạy script tự động tạo chứng chỉ bảo mật:
```bash
python scripts/generate_ssl.py
```
> [!TIP]
> Nếu máy host chưa cài đặt thư viện `cryptography`, script sẽ tự động tìm kiếm và sử dụng tiện ích `openssl` từ Git (`C:\Program Files\Git\usr\bin\openssl.exe`) để tạo cặp khóa. Cặp file `library.crt` và `library.key` sẽ được lưu trong `docker/nginx/certs/`.

### Bước 4: Xây dựng và khởi động toàn bộ cụm container
```bash
# Build image ứng dụng và kéo các image chính hãng
docker compose up -d --build

# Theo dõi tiến trình khởi động
docker compose ps
```

### Bước 5: Nạp dữ liệu mẫu (Database Seeding)
Sau khi container `library_postgres` chuyển sang trạng thái `healthy` (khoảng 10-15 giây), thực hiện lệnh nạp dữ liệu mẫu:
```bash
# Cách 1: Thực thi bên trong container web
docker compose exec web python scripts/seed.py

# Cách 2: Chạy trực tiếp từ máy host (nếu có Python và psycopg2)
python scripts/seed.py
```
Dữ liệu khởi tạo gồm:
- 11 đầu sách thuộc nhiều thể loại (CNTT, DevOps, Hệ điều hành, An toàn thông tin, AI).
- 6 hồ sơ độc giả (gồm độc giả hoạt động và độc giả tạm khóa).
- 1 phiếu mượn đang hoạt động (Active).
- 1 phiếu mượn đã hoàn tất trả (Returned).
- 1 phiếu mượn quá hạn (Overdue) để phục vụ demo trực quan trước giảng viên.

---

## 3. Danh Mục URL & Cổng Dịch Vụ Môi Trường Local

| Dịch vụ | Địa chỉ URL | Thông tin xác thực mặc định |
| :--- | :--- | :--- |
| **Ứng dụng Quản lý Thư viện** | `https://localhost` | Truy cập trực tiếp qua HTTPS (Bỏ qua cảnh báo tự ký) |
| **Chuyển hướng HTTP sang HTTPS** | `http://localhost` | Tự động điều hướng về `https://localhost` (Mã 301) |
| **Healthcheck Endpoint** | `https://localhost/health` | Trả về JSON trạng thái hệ thống và database |
| **Prometheus Metrics Endpoint** | `https://localhost/metrics` | Chỉ số ứng dụng theo định dạng Prometheus |
| **pgAdmin 4 (Quản trị DB)** | `http://localhost:5050` | User: `admin@library.local`<br>Pass: `ChangePgAdminPassword123!` |
| **Grafana Monitoring** | `http://localhost:3000` | User: `admin`<br>Pass: `ChangeGrafanaAdmin123!` |
| **Prometheus Web UI** | `http://localhost:9090` | Truy cập trực tiếp (Status -> Targets) |

---

## 4. Hướng Dẫn Kết Nối PostgreSQL Trong pgAdmin 4

1. Truy cập `http://localhost:5050` và đăng nhập với tài khoản trong `.env`.
2. Chuột phải vào **Servers** -> Chọn **Register** -> **Server...**
3. Trong tab **General**: Đặt tên là `Library Production DB`.
4. Trong tab **Connection**:
   - **Host name/address**: `db` (Tên hostname dịch vụ trong Docker network `backend`)
   - **Port**: `5432`
   - **Maintenance database**: `library_db`
   - **Username**: `library_user`
   - **Password**: `ChangeThisSecurePassword123!` (mật khẩu trong file `.env`)
5. Nhấn **Save**. Bạn sẽ thấy cấu trúc cơ sở dữ liệu `library_db` cùng các bảng `books`, `readers`, `loans`, `loan_details`.

---

## 5. Quy Trình Sao Lưu Và Phục Hồi Dữ Liệu (Backup & Restore)

### Sao lưu (Backup Database)
Thực hiện trích xuất dữ liệu ra file SQL nén từ container đang chạy:
```bash
# Tạo thư mục lưu trữ backup
mkdir -p backups

# Thực hiện pg_dump từ container
docker compose exec -T db pg_dump -U library_user library_db > backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Trên Windows PowerShell:
docker compose exec -T db pg_dump -U library_user library_db | Out-File -FilePath backups/backup_latest.sql -Encoding utf8
```

### Phục hồi (Restore Database)
```bash
# Phục hồi dữ liệu vào database
docker compose exec -T db psql -U library_user -d library_db < backups/backup_latest.sql
```

---

## 6. Xử Lý Các Sự Cố Thường Gặp (Troubleshooting)

### Sự cố 1: Xung đột cổng (Port already allocated)
- **Triệu chứng**: Thông báo lỗi `Bind for 0.0.0.0:80 failed: port is already allocated` hoặc `port 443 is already in use`.
- **Nguyên nhân**: Dịch vụ IIS trên Windows, Skype, hoặc máy chủ web khác đang chiếm cổng 80/443.
- **Cách xử lý**:
  - Tắt IIS bằng lệnh PowerShell quyền Admin: `Stop-Service W3SVC`
  - Hoặc thay đổi cổng trong file `.env`: `HTTP_PORT=8080`, `HTTPS_PORT=8443`, sau đó chạy lại `docker compose up -d`.

### Sự cố 2: Trình duyệt cảnh báo chứng chỉ không tin cậy (NET::ERR_CERT_AUTHORITY_INVALID)
- **Nguyên nhân**: Chứng chỉ tự ký chưa được cài đặt vào kho chứng chỉ gốc của hệ điều hành.
- **Cách xử lý**: Đây là hiện tượng bình thường khi demo local. Nhấn **"Nâng cao" (Advanced)** -> **"Tiếp tục truy cập localhost" (Proceed to localhost)**.

### Sự cố 3: Docker Desktop không khởi động được trên Windows
- **Nguyên nhân**: WSL2 chưa được cài đặt hoặc ảo hóa (Virtualization) chưa được bật trong BIOS.
- **Cách xử lý**:
  - Mở PowerShell quyền Admin chạy: `wsl --install` và khởi động lại máy tính.
  - Bật Docker Desktop sau khi cài đặt xong WSL2.

---

## 7. Các Lệnh Quản Trị Hệ Thống Hữu Ích

```bash
# Xem logs của toàn bộ hệ thống
docker compose logs -f

# Xem logs của riêng dịch vụ web hoặc nginx
docker compose logs -f web
docker compose logs -f nginx

# Khởi động lại một dịch vụ cụ thể
docker compose restart web

# Dừng toàn bộ hệ thống (giữ nguyên dữ liệu persistent trong volumes)
docker compose down

# Dừng và xóa toàn bộ volumes (CẢNH BÁO: XÓA SẠCH DỮ LIỆU DATABASE VÀ LOGS)
docker compose down -v
```
