# TÀI LIỆU BẢO MẬT VÀ GIA CỐ HỆ THỐNG (SECURITY HARDENING)
### Đồ án môn học: Triển khai và Quản trị Hệ thống Phần mềm

---

## 1. Phân Tích Nguy Cơ & Bề Mặt Tấn Công (Threat Analysis)

Trong môi trường triển khai ứng dụng web kết hợp cơ sở dữ liệu và hạ tầng phân tán, các rủi ro bảo mật chính gồm:
1. **Leo thang đặc quyền container (Container Privilege Escalation)**: Nếu tiến trình ứng dụng chạy với quyền `root` bên trong container, lỗ hổng thực thi mã từ xa (RCE) có thể giúp kẻ tấn công phá vỡ lớp cách ly container và chiếm quyền điều khiển máy chủ host (Container Escape).
2. **Xâm nhập ngang mạng (Lateral Movement)**: Nếu tất cả container cùng chia sẻ một Docker network duy nhất, kẻ tấn công chiếm được web server có thể tự do quét cổng, tấn công trực tiếp vào cơ sở dữ liệu, kho log hoặc hệ thống giám sát.
3. **Lộ lọt thông tin nhạy cảm (Information Disclosure & Secret Leaks)**: Hardcode mật khẩu cơ sở dữ liệu trong mã nguồn, commit private key lên Git, hoặc để ứng dụng hiển thị chi tiết stack trace khi phát sinh lỗi 500.
4. **Tấn công tầng ứng dụng (Application Attacks)**: Tấn công giả mạo yêu cầu chéo trang (Cross-Site Request Forgery - CSRF), tấn công tiêm nhiễm SQL (SQL Injection), tấn công Clickjacking hoặc nạp mã độc qua giao diện (Cross-Site Scripting - XSS).
5. **Cạn kiệt tài nguyên (Denial of Service - DoS)**: Không đặt giới hạn tài nguyên CPU/RAM khiến một dịch vụ bị tấn công hoặc memory leak kéo sập toàn bộ máy chủ.

---

## 2. Bảng Tổng Hợp Các Biện Pháp Hardening Đã Triển Khai

| STT | Biện Pháp Bảo Mật | Vị Trí Cấu Hình | Mục Đích Bảo Vệ | Cách Thức Kiểm Tra |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Chạy Non-Root User** | `Dockerfile` | Chặn đứng nguy cơ leo thang đặc quyền container ra máy chủ host. | `docker compose exec web whoami` -> trả về `appuser` (UID: 10001) |
| **2** | **Phân tách mạng (Network Isolation)** | `docker-compose.yml` | Áp dụng nguyên tắc đặc quyền tối thiểu: chia 4 mạng độc lập (`frontend`, `backend`, `monitoring`, `logging`). | Thử ping từ container `nginx` vào `db:5432` -> Bị chặn kết nối |
| **3** | **Quản lý Secrets qua Biến Môi Trường** | `.env.example`, `.gitignore` | Chống lộ mật khẩu, khóa bí mật lên GitHub. Chỉ lưu file mẫu không có dữ liệu thật. | `git status` -> `.env` không bị track |
| **4** | **Cô lập Cổng Database & Admin** | `docker-compose.yml` | PostgreSQL (5432) và pgAdmin (5050) chỉ bind trên `127.0.0.1`, không public ra mạng ngoài. | `netstat -ano \| findstr 5432` chỉ thấy listening trên `127.0.0.1` |
| **5** | **Bảo mật Nginx & TLS** | `docker/nginx/nginx.conf` | Mã hóa lưu lượng end-to-end (TLS 1.2/1.3), tự động chuyển hướng HTTP sang HTTPS. | Truy cập `http://localhost` tự động nhận mã phản hồi `301 Moved Permanently` sang HTTPS |
| **6** | **Nginx Security Headers** | `docker/nginx/nginx.conf` | Ngăn chặn Clickjacking, MIME-sniffing, XSS, ép buộc Content Security Policy (CSP). | Kiểm tra headers phản hồi qua `curl -kI https://localhost` |
| **7** | **Chống Leo Thang Đặc Quyền Linux** | `docker-compose.yml` (`no-new-privileges`) | Vô hiệu hóa bit SUID/SGID, ngăn tiến trình con giành thêm quyền. | Flag `security_opt: [no-new-privileges:true]` trên toàn bộ dịch vụ |
| **8** | **Giới hạn Tài Nguyên (Resource Limits)** | `docker-compose.yml` (`deploy.resources.limits`) | Ngăn chặn tấn công làm cạn kiệt tài nguyên máy chủ vật lý (DoS / Memory exhaustion). | `docker stats` hiển thị giới hạn CPU và Memory rõ ràng cho từng service |
| **9** | **Bảo vệ CSRF Toàn Diện** | `app/extensions.py`, `app/__init__.py` | Bắt buộc mã token CSRF hợp lệ đối với tất cả các thao tác thay đổi dữ liệu (POST). | Gửi form không có CSRF token -> Trả về lỗi 400 Bad Request |
| **10**| **Chống SQL Injection Tuyệt Đối** | `app/services/library_service.py` | Sử dụng SQLAlchemy ORM và Parameterized Queries, tuyệt đối không nối chuỗi thô. | Kiểm thử với payload `' OR '1'='1` -> Xử lý như chuỗi tìm kiếm thông thường |
| **11**| **Ẩn Stack Trace & Xử Lý Lỗi** | `app/templates/errors/` | Trả về giao diện lỗi 400, 404, 500 thân thiện, không làm lộ phiên bản, mã nguồn hay kết nối DB. | Truy cập URL không tồn tại -> Trả về giao diện 404 chuẩn, không lộ log hệ thống |
| **12**| **Proxy Header Trust Có Kiểm Soát** | `app/__init__.py` (`ProxyFix`) | Flask chỉ tin cậy 1 tầng proxy từ Nginx nội bộ (`x_for=1, x_proto=1`), chống giả mạo IP nguồn. | Kiểm tra header `X-Forwarded-For` trong Flask access log |

---

## 3. Chi Tiết Kỹ Thuật Các Biện Pháp Chính

### 3.1. Container Non-Root User
Trong `Dockerfile`, một người dùng và nhóm riêng biệt được khởi tạo trước khi chuyển quyền thực thi:
```dockerfile
# Tạo nhóm và người dùng chuyên biệt appuser (UID 10001)
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/false -m -d /home/appuser appuser

WORKDIR /app
COPY --chown=appuser:appgroup . /app

# Chuyển ngữ cảnh thực thi sang non-root
USER appuser
```
Lợi ích: Nếu ứng dụng web có lỗ hổng thực thi lệnh, kẻ tấn công chỉ có quyền của `appuser` bị giới hạn trong thư mục `/app`, không thể cài đặt gói phần mềm, sửa file cấu hình hệ thống `/etc`, hay tương tác với kernel.

### 3.2. Phân Tách Mạng Độc Lập (Network Segmentation)
Hệ thống tạo 4 mạng Docker bridge:
- `frontend`: Chỉ gồm `nginx` và `web`. Nginx là thành phần duy nhất lắng nghe kết nối từ bên ngoài trên cổng 80 và 443.
- `backend`: Chỉ gồm `web`, `db`, `pgadmin`, và `postgres-exporter`. Người dùng từ Internet không thể kết nối trực tiếp đến PostgreSQL.
- `monitoring`: Gồm `prometheus`, `grafana`, `cadvisor`, `node-exporter`, `postgres-exporter`, `web`. Tách biệt luồng cào dữ liệu giám sát với mạng sản xuất.
- `logging`: Gồm `promtail`, `loki`, `grafana`, `nginx`, `web`. Vận chuyển log khép kín.

### 3.3. Cấu Hình Nginx Security Headers
Trong `docker/nginx/nginx.conf`, các header chuẩn công nghiệp được bổ sung trong mọi phản hồi HTTP:
```nginx
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; font-src 'self' https://cdn.jsdelivr.net data:; img-src 'self' data: https:; connect-src 'self';" always;
```

---

## 4. Hướng Dẫn Kiểm Tra Thực Tế (Verification Steps)

### Kiểm tra 1: Xác nhận Web chạy với Non-Root
```bash
docker compose exec web whoami
# Kết quả kỳ vọng: appuser
docker compose exec web id
# Kết quả kỳ vọng: uid=10001(appuser) gid=10001(appgroup)
```

### Kiểm tra 2: Kiểm tra Security Headers qua cURL
```bash
curl -kI https://localhost
```
Kết quả hiển thị đầy đủ các tiêu đề:
- `Strict-Transport-Security` / TLS handshake
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `Content-Security-Policy`

### Kiểm tra 3: Kiểm tra chuyển hướng HTTP sang HTTPS
```bash
curl -I http://localhost
# Kết quả kỳ vọng: HTTP/1.1 301 Moved Permanently
# Location: https://localhost/
```

### Kiểm tra 4: Kiểm tra Giới hạn Tài nguyên Container
```bash
docker stats --no-stream
```
Quan sát cột `MEM LIMIT` hiển thị đúng ngưỡng cấu hình (512MB cho `web`, `db`, `prometheus`, `grafana`; 256MB cho `nginx`, `cadvisor`).

---

## 5. Giới Hạn Của Môi Trường Demo & Khuyến Nghị Cho Môi Trường Production

1. **Chứng chỉ SSL**: Trong môi trường demo cục bộ, dự án sử dụng chứng chỉ tự ký (`Self-Signed Certificate`). Khi đưa vào Production thực tế trên Internet, cần thay thế bằng chứng chỉ công khai hợp lệ từ **Let's Encrypt** (thông qua Certbot container) hoặc chứng chỉ thương mại được ký bởi CA tin cậy.
2. **Khóa ký Secrets**: Cần sử dụng các giải pháp quản lý secret chuyên nghiệp như **HashiCorp Vault**, AWS Secrets Manager hoặc Kubernetes Secrets thay vì lưu trong file `.env` trên đĩa cứng.
3. **Database Replication**: Trong production quy mô lớn, cần cấu hình PostgreSQL High Availability (HA) với cơ chế Streaming Replication (Primary - Replica) kết hợp PgBouncer làm Connection Pooler.
4. **WAF (Web Application Firewall)**: Nên bổ sung thêm ModSecurity hoặc AWS WAF trước Nginx để phát hiện và ngăn chặn các cuộc tấn công DDoS và quét lỗ hổng tự động.
