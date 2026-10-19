import uuid
from datetime import datetime, date
from sqlalchemy import func
from app.extensions import db
from app.models.book import Book
from app.models.reader import Reader
from app.models.loan import Loan, LoanDetail

class LibraryService:
    @staticmethod
    def get_dashboard_stats():
        """Retrieve dynamic dashboard statistics from PostgreSQL."""
        # Auto-update any overdue loans
        now_date = date.today()
        overdue_to_update = Loan.query.filter(
            Loan.status == 'borrowing',
            Loan.due_date < now_date
        ).all()
        if overdue_to_update:
            for l in overdue_to_update:
                l.status = 'overdue'
            db.session.commit()

        total_titles = Book.query.count()
        total_books_sum = db.session.query(func.sum(Book.total_quantity)).scalar() or 0
        total_available = db.session.query(func.sum(Book.available_quantity)).scalar() or 0
        total_readers = Reader.query.count()
        active_readers = Reader.query.filter_by(status='active').count()
        
        active_loans = Loan.query.filter(Loan.status.in_(['borrowing', 'overdue'])).count()
        overdue_count = Loan.query.filter_by(status='overdue').count()
        returned_count = Loan.query.filter_by(status='returned').count()

        recent_loans = Loan.query.order_by(Loan.created_at.desc()).limit(8).all()
        recent_books = Book.query.order_by(Book.created_at.desc()).limit(5).all()

        return {
            'total_titles': total_titles,
            'total_books_sum': total_books_sum,
            'total_available': total_available,
            'total_readers': total_readers,
            'active_readers': active_readers,
            'active_loans': active_loans,
            'overdue_count': overdue_count,
            'returned_count': returned_count,
            'recent_loans': recent_loans,
            'recent_books': recent_books
        }

    # ------------------ Books Service ------------------
    @staticmethod
    def get_books(search_query=None, category=None, page=1, per_page=10):
        query = Book.query
        if search_query:
            term = f"%{search_query.strip()}%"
            query = query.filter(
                (Book.title.ilike(term)) |
                (Book.author.ilike(term)) |
                (Book.isbn.ilike(term))
            )
        if category and category != 'all':
            query = query.filter(Book.category == category)
        return query.order_by(Book.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_all_categories():
        return [r[0] for r in db.session.query(Book.category).distinct().order_by(Book.category).all() if r[0]]

    @staticmethod
    def create_book(isbn, title, author, category, publisher=None, publish_year=None, total_quantity=1):
        total_qty = int(total_quantity)
        if total_qty < 0:
            raise ValueError("Số lượng sách không được là số âm.")

        # Check existing ISBN
        if Book.query.filter_by(isbn=isbn.strip()).first():
            raise ValueError(f"Mã ISBN '{isbn}' đã tồn tại trong hệ thống.")

        book = Book(
            isbn=isbn.strip(),
            title=title.strip(),
            author=author.strip(),
            category=category.strip() if category else 'Khác',
            publisher=publisher.strip() if publisher else None,
            publish_year=int(publish_year) if publish_year else None,
            total_quantity=total_qty,
            available_quantity=total_qty
        )
        db.session.add(book)
        db.session.commit()
        return book

    @staticmethod
    def update_book(book_id, isbn, title, author, category, publisher, publish_year, total_quantity):
        book = Book.query.get_or_404(book_id)
        new_total = int(total_quantity)
        if new_total < 0:
            raise ValueError("Số lượng tổng không thể âm.")

        # Check ISBN collision
        existing = Book.query.filter_by(isbn=isbn.strip()).first()
        if existing and existing.id != book.id:
            raise ValueError(f"Mã ISBN '{isbn}' đã được sử dụng cho một sách khác.")

        # Calculate currently borrowed books for this title
        currently_borrowed = book.total_quantity - book.available_quantity
        if new_total < currently_borrowed:
            raise ValueError(
                f"Không thể giảm tổng số lượng xuống {new_total} vì hiện có {currently_borrowed} cuốn đang được mượn."
            )

        new_available = new_total - currently_borrowed
        book.isbn = isbn.strip()
        book.title = title.strip()
        book.author = author.strip()
        book.category = category.strip() if category else 'Khác'
        book.publisher = publisher.strip() if publisher else None
        book.publish_year = int(publish_year) if publish_year else None
        book.total_quantity = new_total
        book.available_quantity = new_available
        
        db.session.commit()
        return book

    @staticmethod
    def delete_book(book_id):
        book = Book.query.get_or_404(book_id)
        # Check active unreturned loans
        active_count = LoanDetail.query.filter_by(book_id=book_id, returned=False).count()
        if active_count > 0:
            raise ValueError(f"Không thể xóa sách '{book.title}' vì đang có {active_count} cuốn đang được mượn chưa trả.")

        # Check total loan history
        history_count = LoanDetail.query.filter_by(book_id=book_id).count()
        if history_count > 0:
            raise ValueError(
                f"Không thể xóa sách '{book.title}' vì đã có lịch sử mượn trả ({history_count} lượt). "
                "Để bảo đảm tính toàn vẹn dữ liệu, hãy cập nhật số lượng về 0 thay vì xóa."
            )

        db.session.delete(book)
        db.session.commit()
        return True

    # ------------------ Readers Service ------------------
    @staticmethod
    def get_readers(search_query=None, status=None, page=1, per_page=10):
        query = Reader.query
        if search_query:
            term = f"%{search_query.strip()}%"
            query = query.filter(
                (Reader.full_name.ilike(term)) |
                (Reader.reader_code.ilike(term)) |
                (Reader.email.ilike(term)) |
                (Reader.phone.ilike(term))
            )
        if status and status != 'all':
            query = query.filter(Reader.status == status)
        return query.order_by(Reader.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def create_reader(reader_code, full_name, email, phone=None, address=None, registered_date=None):
        code = reader_code.strip().upper()
        if Reader.query.filter_by(reader_code=code).first():
            raise ValueError(f"Mã độc giả '{code}' đã tồn tại.")

        email_clean = email.strip().lower()
        if Reader.query.filter_by(email=email_clean).first():
            raise ValueError(f"Email '{email_clean}' đã được đăng ký.")

        reg_date = date.today()
        if registered_date:
            if isinstance(registered_date, str):
                reg_date = datetime.strptime(registered_date, '%Y-%m-%d').date()
            else:
                reg_date = registered_date

        reader = Reader(
            reader_code=code,
            full_name=full_name.strip(),
            email=email_clean,
            phone=phone.strip() if phone else None,
            address=address.strip() if address else None,
            registered_date=reg_date,
            status='active'
        )
        db.session.add(reader)
        db.session.commit()
        return reader

    @staticmethod
    def update_reader(reader_id, reader_code, full_name, email, phone, address, status):
        reader = Reader.query.get_or_404(reader_id)
        code = reader_code.strip().upper()
        email_clean = email.strip().lower()

        # Check code collision
        c_exist = Reader.query.filter_by(reader_code=code).first()
        if c_exist and c_exist.id != reader.id:
            raise ValueError(f"Mã độc giả '{code}' đã được sử dụng.")

        e_exist = Reader.query.filter_by(email=email_clean).first()
        if e_exist and e_exist.id != reader.id:
            raise ValueError(f"Email '{email_clean}' đã được sử dụng.")

        reader.reader_code = code
        reader.full_name = full_name.strip()
        reader.email = email_clean
        reader.phone = phone.strip() if phone else None
        reader.address = address.strip() if address else None
        reader.status = status
        db.session.commit()
        return reader

    @staticmethod
    def delete_or_deactivate_reader(reader_id):
        reader = Reader.query.get_or_404(reader_id)
        # Check active loans
        active_loans = Loan.query.filter_by(reader_id=reader_id).filter(Loan.status.in_(['borrowing', 'overdue'])).count()
        if active_loans > 0:
            raise ValueError(f"Không thể xóa/vô hiệu hóa độc giả '{reader.full_name}' vì đang có {active_loans} phiếu mượn chưa hoàn tất.")

        total_loans = Loan.query.filter_by(reader_id=reader_id).count()
        if total_loans > 0:
            # Soft delete to preserve history
            reader.status = 'inactive'
            db.session.commit()
            return "Độc giả đã có lịch sử mượn sách. Hệ thống đã chuyển trạng thái sang 'Ngừng hoạt động' để bảo toàn dữ liệu."
        else:
            db.session.delete(reader)
            db.session.commit()
            return "Đã xóa độc giả thành công."

    # ------------------ Loans & Returns Service ------------------
    @staticmethod
    def get_loans(search_query=None, status=None, page=1, per_page=10):
        # Update overdue
        now_date = date.today()
        Loan.query.filter(Loan.status == 'borrowing', Loan.due_date < now_date).update({'status': 'overdue'})
        db.session.commit()

        query = Loan.query.join(Reader)
        if search_query:
            term = f"%{search_query.strip()}%"
            query = query.filter(
                (Loan.loan_code.ilike(term)) |
                (Reader.full_name.ilike(term)) |
                (Reader.reader_code.ilike(term))
            )
        if status and status != 'all':
            query = query.filter(Loan.status == status)

        return query.order_by(Loan.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def create_loan(reader_id, book_items, borrow_date=None, due_date=None, notes=None):
        """
        Creates a loan ticket with transaction isolation and row locking.
        book_items: list of dicts [{'book_id': int, 'quantity': int}]
        """
        if not book_items:
            raise ValueError("Phiếu mượn phải có ít nhất một cuốn sách.")

        reader = Reader.query.get(reader_id)
        if not reader:
            raise ValueError("Độc giả không tồn tại.")
        if reader.status != 'active':
            raise ValueError(f"Độc giả '{reader.full_name}' đang ở trạng thái ngừng hoạt động, không thể mượn sách.")

        b_date = date.today()
        if borrow_date:
            b_date = datetime.strptime(borrow_date, '%Y-%m-%d').date() if isinstance(borrow_date, str) else borrow_date

        if not due_date:
            raise ValueError("Vui lòng chọn hạn trả sách.")
        d_date = datetime.strptime(due_date, '%Y-%m-%d').date() if isinstance(due_date, str) else due_date

        if d_date < b_date:
            raise ValueError("Hạn trả sách không thể trước ngày mượn.")

        # Generate unique loan code
        loan_code = f"PM-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        try:
            # Transaction block
            new_loan = Loan(
                loan_code=loan_code,
                reader_id=reader.id,
                borrow_date=b_date,
                due_date=d_date,
                notes=notes.strip() if notes else None,
                status='borrowing'
            )
            db.session.add(new_loan)
            db.session.flush()  # get new_loan.id

            for item in book_items:
                book_id = int(item['book_id'])
                qty = int(item.get('quantity', 1))
                if qty <= 0:
                    raise ValueError("Số lượng mượn phải lớn hơn 0.")

                # Row-level lock to prevent concurrent overdraft
                book = db.session.query(Book).filter_by(id=book_id).with_for_update().first()
                if not book:
                    raise ValueError(f"Không tìm thấy sách có ID {book_id}.")

                if book.available_quantity < qty:
                    raise ValueError(
                        f"Sách '{book.title}' chỉ còn {book.available_quantity} cuốn trong kho, "
                        f"không đủ để mượn {qty} cuốn."
                    )

                # Deduct inventory atomically
                book.available_quantity -= qty

                loan_detail = LoanDetail(
                    loan_id=new_loan.id,
                    book_id=book.id,
                    quantity=qty,
                    returned=False
                )
                db.session.add(loan_detail)

            db.session.commit()
            return new_loan

        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def return_loan_detail(loan_detail_id, notes=None):
        """
        Returns a specific book item in a loan ticket atomically.
        """
        try:
            # Lock the detail row
            detail = db.session.query(LoanDetail).filter_by(id=loan_detail_id).with_for_update().first()
            if not detail:
                raise ValueError("Bản ghi mượn sách không tồn tại.")

            if detail.returned:
                raise ValueError(f"Sách '{detail.book.title}' đã được trả vào ngày {detail.return_date}. Không thể trả lần hai.")

            # Lock the book row
            book = db.session.query(Book).filter_by(id=detail.book_id).with_for_update().first()
            book.available_quantity += detail.quantity
            if book.available_quantity > book.total_quantity:
                book.available_quantity = book.total_quantity

            detail.returned = True
            detail.return_date = date.today()
            if notes:
                detail.notes = notes.strip()

            # Check overall loan status
            loan = detail.loan
            loan.update_status()

            db.session.commit()
            return detail

        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def return_all_in_loan(loan_id):
        """Returns all remaining unreturned books in a loan ticket."""
        try:
            loan = db.session.query(Loan).filter_by(id=loan_id).with_for_update().first()
            if not loan:
                raise ValueError("Phiếu mượn không tồn tại.")

            unreturned_count = 0
            for detail in loan.details:
                if not detail.returned:
                    book = db.session.query(Book).filter_by(id=detail.book_id).with_for_update().first()
                    book.available_quantity += detail.quantity
                    if book.available_quantity > book.total_quantity:
                        book.available_quantity = book.total_quantity

                    detail.returned = True
                    detail.return_date = date.today()
                    unreturned_count += 1

            if unreturned_count == 0:
                raise ValueError("Tất cả sách trong phiếu mượn này đã được trả trước đó.")

            loan.status = 'returned'
            db.session.commit()
            return loan

        except Exception as e:
            db.session.rollback()
            raise e
