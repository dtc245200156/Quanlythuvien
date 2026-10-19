import os
import sys
from datetime import date, timedelta

# Add parent directory to path so script can run directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.book import Book
from app.models.reader import Reader
from app.models.loan import Loan, LoanDetail

def seed_database():
    app = create_app()
    with app.app_context():
        # Ensure database tables exist
        db.create_all()
        print("Initializing seed data for Library Management System...")

        # 1. Seed Books (>= 10 books)
        books_data = [
            {
                "isbn": "978-604-0-00101-1",
                "title": "Thiết Kế Hệ Thống Phân Tán (Designing Data-Intensive Applications)",
                "author": "Martin Kleppmann",
                "category": "Công nghệ thông tin",
                "publisher": "NXB Thông tin & Truyền thông",
                "publish_year": 2021,
                "total_quantity": 10
            },
            {
                "isbn": "978-604-0-00102-8",
                "title": "Lập Trình Mạng Với Python và Docker",
                "author": "Dr. Brandon Rhodes",
                "category": "Công nghệ thông tin",
                "publisher": "NXB Bách Khoa Hà Nội",
                "publish_year": 2022,
                "total_quantity": 8
            },
            {
                "isbn": "978-604-0-00103-5",
                "title": "Site Reliability Engineering (SRE) Toàn Tập",
                "author": "Betsy Beyer, Niall Richard Murphy",
                "category": "DevOps & Cloud",
                "publisher": "NXB Thống Kê",
                "publish_year": 2020,
                "total_quantity": 6
            },
            {
                "isbn": "978-604-0-00104-2",
                "title": "Quản Trị Cơ Sở Dữ Liệu PostgreSQL Chuyên Sâu",
                "author": "Hans-Jürgen Schönig",
                "category": "Cơ sở dữ liệu",
                "publisher": "NXB Khoa Học & Kỹ Thuật",
                "publish_year": 2023,
                "total_quantity": 7
            },
            {
                "isbn": "978-604-0-00105-9",
                "title": "Clean Code - Nghệ Thuật Viết Mã Sạch",
                "author": "Robert C. Martin (Uncle Bob)",
                "category": "Công nghệ thông tin",
                "publisher": "NXB Tri Thức",
                "publish_year": 2019,
                "total_quantity": 12
            },
            {
                "isbn": "978-604-0-00106-6",
                "title": "Kiến Trúc Microservices Thực Chiến",
                "author": "Sam Newman",
                "category": "DevOps & Cloud",
                "publisher": "NXB Thông tin & Truyền thông",
                "publish_year": 2023,
                "total_quantity": 5
            },
            {
                "isbn": "978-604-0-00107-3",
                "title": "An Toàn Thông Tin và Phòng Thủ Mạng",
                "author": "William Stallings",
                "category": "An toàn thông tin",
                "publisher": "NXB Bưu Điện",
                "publish_year": 2022,
                "total_quantity": 6
            },
            {
                "isbn": "978-604-0-00108-0",
                "title": "Cấu Trúc Dữ Liệu và Giải Thuật Ứng Dụng",
                "author": "PGS. TS. Đinh Mạnh Tường",
                "category": "Khoa học máy tính",
                "publisher": "NXB Giáo Dục",
                "publish_year": 2021,
                "total_quantity": 15
            },
            {
                "isbn": "978-604-0-00109-7",
                "title": "Trí Tuệ Nhân Tạo: Cách Tiếp Cận Hiện Đại",
                "author": "Stuart Russell, Peter Norvig",
                "category": "Trí tuệ nhân tạo",
                "publisher": "NXB Đại Học Quốc Gia",
                "publish_year": 2024,
                "total_quantity": 9
            },
            {
                "isbn": "978-604-0-00110-3",
                "title": "DevOps Handbook: Vận Hành và Phát Triển Phần Mềm",
                "author": "Gene Kim, Jez Humble, Patrick Debois",
                "category": "DevOps & Cloud",
                "publisher": "NXB Bách Khoa",
                "publish_year": 2022,
                "total_quantity": 10
            },
            {
                "isbn": "978-604-0-00111-0",
                "title": "Giám Sát Hệ Thống Thực Tiễn Với Prometheus",
                "author": "Brian Brazil",
                "category": "DevOps & Cloud",
                "publisher": "NXB Khoa Học & Kỹ Thuật",
                "publish_year": 2023,
                "total_quantity": 5
            }
        ]

        book_objects = {}
        for b in books_data:
            existing = Book.query.filter_by(isbn=b['isbn']).first()
            if not existing:
                book = Book(
                    isbn=b['isbn'],
                    title=b['title'],
                    author=b['author'],
                    category=b['category'],
                    publisher=b['publisher'],
                    publish_year=b['publish_year'],
                    total_quantity=b['total_quantity'],
                    available_quantity=b['total_quantity']
                )
                db.session.add(book)
                db.session.flush()
                book_objects[b['isbn']] = book
                print(f" [+] Added Book: {b['title']}")
            else:
                book_objects[b['isbn']] = existing

        db.session.commit()

        # 2. Seed Readers (>= 5 readers)
        readers_data = [
            {
                "code": "DG2025001",
                "name": "Nguyễn Hoàng Nam",
                "email": "nam.nh@library.local",
                "phone": "0912345671",
                "address": "Lớp K21-CNTT, Đại học Công nghệ",
                "status": "active"
            },
            {
                "code": "DG2025002",
                "name": "Trần Thị Mai Anh",
                "email": "maianh.tt@library.local",
                "phone": "0912345672",
                "address": "Lớp K22-HTTT, Đại học Công nghệ",
                "status": "active"
            },
            {
                "code": "DG2025003",
                "name": "Lê Văn Hùng",
                "email": "hung.lv@library.local",
                "phone": "0912345673",
                "address": "Lớp K21-KTPM, Đại học Bách Khoa",
                "status": "active"
            },
            {
                "code": "DG2025004",
                "name": "Phạm Minh Tuấn",
                "email": "tuan.pm@library.local",
                "phone": "0912345674",
                "address": "Lớp K20-ATTT, Học viện Kỹ thuật",
                "status": "active"
            },
            {
                "code": "DG2025005",
                "name": "Vũ Thu Trang",
                "email": "trang.vt@library.local",
                "phone": "0912345675",
                "address": "Lớp K22-KHMT, Đại học Quốc Gia",
                "status": "active"
            },
            {
                "code": "DG2025006",
                "name": "Đỗ Quang Huy",
                "email": "huy.dq@library.local",
                "phone": "0912345676",
                "address": "Lớp Cựu sinh viên K19",
                "status": "inactive"
            }
        ]

        reader_objects = {}
        for r in readers_data:
            existing = Reader.query.filter_by(reader_code=r['code']).first()
            if not existing:
                reader = Reader(
                    reader_code=r['code'],
                    full_name=r['name'],
                    email=r['email'],
                    phone=r['phone'],
                    address=r['address'],
                    status=r['status'],
                    registered_date=date.today() - timedelta(days=60)
                )
                db.session.add(reader)
                db.session.flush()
                reader_objects[r['code']] = reader
                print(f" [+] Added Reader: {r['name']}")
            else:
                reader_objects[r['code']] = existing

        db.session.commit()

        # 3. Seed Loans: Active, Returned, and Overdue case
        today = date.today()

        # Case A: Active Loan (Đang mượn - chưa đến hạn)
        loan_a_code = "PM-DEMO-ACTIVE-01"
        if not Loan.query.filter_by(loan_code=loan_a_code).first():
            reader = reader_objects["DG2025001"]
            b1 = book_objects["978-604-0-00101-1"]
            b2 = book_objects["978-604-0-00103-5"]

            loan_a = Loan(
                loan_code=loan_a_code,
                reader_id=reader.id,
                borrow_date=today - timedelta(days=3),
                due_date=today + timedelta(days=11),
                notes="Mượn nghiên cứu đồ án hệ thống phân tán",
                status="borrowing"
            )
            db.session.add(loan_a)
            db.session.flush()

            # Details
            d1 = LoanDetail(loan_id=loan_a.id, book_id=b1.id, quantity=1, returned=False)
            d2 = LoanDetail(loan_id=loan_a.id, book_id=b2.id, quantity=1, returned=False)
            b1.available_quantity -= 1
            b2.available_quantity -= 1
            db.session.add_all([d1, d2])
            print(f" [+] Added Active Loan: {loan_a_code}")

        # Case B: Returned Loan (Đã trả hoàn tất)
        loan_b_code = "PM-DEMO-RETURNED-02"
        if not Loan.query.filter_by(loan_code=loan_b_code).first():
            reader = reader_objects["DG2025002"]
            b3 = book_objects["978-604-0-00105-9"]

            loan_b = Loan(
                loan_code=loan_b_code,
                reader_id=reader.id,
                borrow_date=today - timedelta(days=20),
                due_date=today - timedelta(days=6),
                notes="Đã trả đầy đủ, sách nguyên vẹn",
                status="returned"
            )
            db.session.add(loan_b)
            db.session.flush()

            d3 = LoanDetail(
                loan_id=loan_b.id,
                book_id=b3.id,
                quantity=1,
                returned=True,
                return_date=today - timedelta(days=7),
                notes="Đã trả đúng hạn"
            )
            db.session.add(d3)
            print(f" [+] Added Returned Loan: {loan_b_code}")

        # Case C: Overdue Loan for Demo (Quá hạn mượn)
        loan_c_code = "PM-DEMO-OVERDUE-03"
        if not Loan.query.filter_by(loan_code=loan_c_code).first():
            reader = reader_objects["DG2025003"]
            b4 = book_objects["978-604-0-00104-2"]

            loan_c = Loan(
                loan_code=loan_c_code,
                reader_id=reader.id,
                borrow_date=today - timedelta(days=30),
                due_date=today - timedelta(days=5),  # Due 5 days ago!
                notes="Trường hợp quá hạn để demo giảng viên",
                status="overdue"
            )
            db.session.add(loan_c)
            db.session.flush()

            d4 = LoanDetail(
                loan_id=loan_c.id,
                book_id=b4.id,
                quantity=1,
                returned=False,
                notes="Chưa nộp lại sách, đã gửi email nhắc nhở"
            )
            b4.available_quantity -= 1
            db.session.add(d4)
            print(f" [+] Added Overdue Loan: {loan_c_code}")

        db.session.commit()
        print(" Seed data initialization completed successfully!")

if __name__ == '__main__':
    seed_database()
