.PHONY: help init cert build up down restart logs ps seed test report clean

help:
	@echo "======================================================================"
	@echo " HỆ THỐNG QUẢN LÝ THƯ VIỆN - CÁC LỆNH ĐIỀU PHỐI DEVOPS"
	@echo "======================================================================"
	@echo " make init     - Khởi tạo file .env và sinh chứng chỉ SSL tự ký"
	@echo " make cert     - Sinh lại chứng chỉ SSL cho Nginx (HTTPS demo)"
	@echo " make build    - Xây dựng images với Docker Compose"
	@echo " make up       - Khởi chạy toàn bộ 11 container ở chế độ chạy ngầm"
	@echo " make down     - Dừng toàn bộ hệ thống (giữ nguyên dữ liệu persistent)"
	@echo " make restart  - Khởi động lại toàn bộ các dịch vụ"
	@echo " make logs     - Theo dõi nhật ký (logs) thời gian thực của hệ thống"
	@echo " make ps       - Kiểm tra trạng thái và sức khỏe của các container"
	@echo " make seed     - Nạp dữ liệu mẫu vào cơ sở dữ liệu PostgreSQL"
	@echo " make test     - Chạy bộ kiểm thử tự động với Pytest (20 ca kiểm thử)"
	@echo " make report   - Tạo file báo cáo đồ án DOCX chuyên nghiệp"
	@echo "======================================================================"

init:
	@if not exist .env (copy .env.example .env) else (echo [.env already exists])
	python scripts/generate_ssl.py

cert:
	python scripts/generate_ssl.py

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

ps:
	docker compose ps

seed:
	docker compose exec web python scripts/seed.py

test:
	python -m pytest tests/ -v

report:
	python scripts/generate_report_docx.py
