from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.reader import Reader
from app.services.library_service import LibraryService

readers_bp = Blueprint('readers', __name__, url_prefix='/readers')

@readers_bp.route('/')
def index():
    search = request.args.get('q', '').strip()
    status = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)

    pagination = LibraryService.get_readers(
        search_query=search,
        status=status,
        page=page,
        per_page=10
    )
    return render_template(
        'readers/index.html',
        pagination=pagination,
        readers=pagination.items,
        search=search,
        status=status
    )

@readers_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        reader_code = request.form.get('reader_code', '').strip()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        registered_date = request.form.get('registered_date', '').strip()

        if not reader_code or not full_name or not email:
            flash('Vui lòng điền các trường bắt buộc (Mã độc giả, Họ và tên, Email).', 'danger')
            return render_template('readers/form.html', reader=None)

        try:
            reader = LibraryService.create_reader(
                reader_code=reader_code,
                full_name=full_name,
                email=email,
                phone=phone,
                address=address,
                registered_date=registered_date or None
            )
            flash(f"Thêm độc giả '{reader.full_name}' thành công!", 'success')
            return redirect(url_for('readers.index'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception:
            flash("Đã xảy ra lỗi hệ thống khi thêm độc giả.", 'danger')

    return render_template('readers/form.html', reader=None)

@readers_bp.route('/<int:reader_id>/edit', methods=['GET', 'POST'])
def edit(reader_id):
    reader = Reader.query.get_or_404(reader_id)
    if request.method == 'POST':
        reader_code = request.form.get('reader_code', '').strip()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        status = request.form.get('status', 'active').strip()

        if not reader_code or not full_name or not email:
            flash('Vui lòng điền các trường bắt buộc (Mã độc giả, Họ và tên, Email).', 'danger')
            return render_template('readers/form.html', reader=reader)

        try:
            LibraryService.update_reader(
                reader_id=reader.id,
                reader_code=reader_code,
                full_name=full_name,
                email=email,
                phone=phone,
                address=address,
                status=status
            )
            flash(f"Cập nhật độc giả '{reader.full_name}' thành công!", 'success')
            return redirect(url_for('readers.index'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception:
            flash("Đã xảy ra lỗi khi cập nhật độc giả.", 'danger')

    return render_template('readers/form.html', reader=reader)

@readers_bp.route('/<int:reader_id>/delete', methods=['POST'])
def delete(reader_id):
    try:
        msg = LibraryService.delete_or_deactivate_reader(reader_id)
        flash(msg, 'info')
    except ValueError as e:
        flash(str(e), 'warning')
    except Exception:
        flash("Không thể xử lý yêu cầu do phát sinh lỗi.", 'danger')

    return redirect(url_for('readers.index'))

@readers_bp.route('/<int:reader_id>')
def detail(reader_id):
    reader = Reader.query.get_or_404(reader_id)
    loans = reader.loans.order_by(Reader.created_at.desc()).all()
    return render_template('readers/detail.html', reader=reader, loans=loans)
