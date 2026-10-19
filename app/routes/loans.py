from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.loan import Loan, LoanDetail
from app.models.reader import Reader
from app.models.book import Book
from app.services.library_service import LibraryService

loans_bp = Blueprint('loans', __name__, url_prefix='/loans')

@loans_bp.route('/')
def index():
    search = request.args.get('q', '').strip()
    status = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)

    pagination = LibraryService.get_loans(
        search_query=search,
        status=status,
        page=page,
        per_page=10
    )
    return render_template(
        'loans/index.html',
        pagination=pagination,
        loans=pagination.items,
        search=search,
        status=status
    )

@loans_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        reader_id = request.form.get('reader_id', type=int)
        borrow_date = request.form.get('borrow_date', date.today().isoformat())
        due_date = request.form.get('due_date')
        notes = request.form.get('notes', '').strip()

        # Parse selected books
        selected_books = request.form.getlist('book_ids')
        if not selected_books:
            flash("Vui lòng chọn ít nhất một cuốn sách để tạo phiếu mượn.", "danger")
            readers = Reader.query.filter_by(status='active').order_by(Reader.full_name).all()
            books = Book.query.filter(Book.available_quantity > 0).order_by(Book.title).all()
            return render_template('loans/form.html', readers=readers, books=books, default_due=date.today() + timedelta(days=14))

        book_items = []
        for b_id in selected_books:
            qty_key = f'qty_{b_id}'
            qty = int(request.form.get(qty_key, 1))
            book_items.append({'book_id': int(b_id), 'quantity': qty})

        try:
            loan = LibraryService.create_loan(
                reader_id=reader_id,
                book_items=book_items,
                borrow_date=borrow_date,
                due_date=due_date,
                notes=notes
            )
            flash(f"Tạo phiếu mượn '{loan.loan_code}' thành công!", 'success')
            return redirect(url_for('loans.detail', loan_id=loan.id))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception:
            flash("Đã xảy ra lỗi trong quá trình tạo phiếu mượn.", 'danger')

    readers = Reader.query.filter_by(status='active').order_by(Reader.full_name).all()
    books = Book.query.filter(Book.available_quantity > 0).order_by(Book.title).all()
    default_due = date.today() + timedelta(days=14)
    return render_template('loans/form.html', readers=readers, books=books, default_due=default_due)

@loans_bp.route('/<int:loan_id>')
def detail(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    return render_template('loans/detail.html', loan=loan)

@loans_bp.route('/return-item/<int:detail_id>', methods=['POST'])
def return_item(detail_id):
    detail = LoanDetail.query.get_or_404(detail_id)
    loan_id = detail.loan_id
    notes = request.form.get('notes', '')
    try:
        LibraryService.return_loan_detail(detail_id, notes=notes)
        flash(f"Đã trả sách '{detail.book.title}' thành công!", 'success')
    except ValueError as e:
        flash(str(e), 'warning')
    except Exception:
        flash("Không thể xử lý trả sách do phát sinh lỗi.", 'danger')

    return redirect(url_for('loans.detail', loan_id=loan_id))

@loans_bp.route('/<int:loan_id>/return-all', methods=['POST'])
def return_all(loan_id):
    try:
        LibraryService.return_all_in_loan(loan_id)
        flash("Đã hoàn tất trả toàn bộ sách trong phiếu mượn!", 'success')
    except ValueError as e:
        flash(str(e), 'warning')
    except Exception:
        flash("Không thể xử lý trả sách do phát sinh lỗi.", 'danger')

    return redirect(url_for('loans.detail', loan_id=loan_id))
