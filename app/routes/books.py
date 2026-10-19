from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from app.models.book import Book
from app.services.library_service import LibraryService

books_bp = Blueprint('books', __name__, url_prefix='/books')

@books_bp.route('/')
def index():
    search = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    page = request.args.get('page', 1, type=int)
    
    pagination = LibraryService.get_books(
        search_query=search,
        category=category,
        page=page,
        per_page=10
    )
    categories = LibraryService.get_all_categories()
    
    return render_template(
        'books/index.html',
        pagination=pagination,
        books=pagination.items,
        search=search,
        category=category,
        categories=categories
    )

@books_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        isbn = request.form.get('isbn', '').strip()
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        category = request.form.get('category', '').strip()
        publisher = request.form.get('publisher', '').strip()
        publish_year = request.form.get('publish_year', '').strip()
        total_quantity = request.form.get('total_quantity', '1').strip()

        if not isbn or not title or not author:
            flash('Vui lòng điền đầy đủ các thông tin bắt buộc (ISBN, Tên sách, Tác giả).', 'danger')
            return render_template('books/form.html', book=None, categories=LibraryService.get_all_categories())

        try:
            book = LibraryService.create_book(
                isbn=isbn,
                title=title,
                author=author,
                category=category,
                publisher=publisher,
                publish_year=int(publish_year) if publish_year else None,
                total_quantity=int(total_quantity)
            )
            flash(f"Thêm sách '{book.title}' thành công!", 'success')
            return redirect(url_for('books.index'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception:
            flash("Đã xảy ra lỗi hệ thống khi thêm sách.", 'danger')

    return render_template('books/form.html', book=None, categories=LibraryService.get_all_categories())

@books_bp.route('/<int:book_id>/edit', methods=['GET', 'POST'])
def edit(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        isbn = request.form.get('isbn', '').strip()
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        category = request.form.get('category', '').strip()
        publisher = request.form.get('publisher', '').strip()
        publish_year = request.form.get('publish_year', '').strip()
        total_quantity = request.form.get('total_quantity', '1').strip()

        if not isbn or not title or not author:
            flash('Vui lòng điền đầy đủ các thông tin bắt buộc (ISBN, Tên sách, Tác giả).', 'danger')
            return render_template('books/form.html', book=book, categories=LibraryService.get_all_categories())

        try:
            LibraryService.update_book(
                book_id=book.id,
                isbn=isbn,
                title=title,
                author=author,
                category=category,
                publisher=publisher,
                publish_year=int(publish_year) if publish_year else None,
                total_quantity=int(total_quantity)
            )
            flash(f"Cập nhật sách '{book.title}' thành công!", 'success')
            return redirect(url_for('books.index'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception:
            flash("Đã xảy ra lỗi khi cập nhật sách.", 'danger')

    return render_template('books/form.html', book=book, categories=LibraryService.get_all_categories())

@books_bp.route('/<int:book_id>/delete', methods=['POST'])
def delete(book_id):
    try:
        LibraryService.delete_book(book_id)
        flash("Đã xóa sách khỏi thư viện thành công.", 'success')
    except ValueError as e:
        flash(str(e), 'warning')
    except Exception:
        flash("Không thể xóa sách do phát sinh lỗi.", 'danger')

    return redirect(url_for('books.index'))

@books_bp.route('/<int:book_id>')
def detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('books/detail.html', book=book)
