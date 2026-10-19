from datetime import datetime, date
from app.extensions import db

class Loan(db.Model):
    __tablename__ = 'loans'

    id = db.Column(db.Integer, primary_key=True)
    loan_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    reader_id = db.Column(db.Integer, db.ForeignKey('readers.id', ondelete='RESTRICT'), nullable=False, index=True)
    borrow_date = db.Column(db.Date, nullable=False, default=date.today)
    due_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='borrowing')  # 'borrowing', 'returned', 'overdue'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reader = db.relationship('Reader', back_populates='loans')
    details = db.relationship('LoanDetail', back_populates='loan', cascade='all, delete-orphan', lazy='joined')

    @property
    def is_overdue(self):
        if self.status == 'returned':
            return False
        return date.today() > self.due_date

    def update_status(self):
        """Re-evaluate loan status based on details and dates."""
        all_returned = all(detail.returned for detail in self.details)
        if all_returned and len(self.details) > 0:
            self.status = 'returned'
        elif date.today() > self.due_date:
            self.status = 'overdue'
        else:
            self.status = 'borrowing'

    def to_dict(self):
        return {
            'id': self.id,
            'loan_code': self.loan_code,
            'reader_id': self.reader_id,
            'reader_name': self.reader.full_name if self.reader else None,
            'borrow_date': self.borrow_date.isoformat() if self.borrow_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'is_overdue': self.is_overdue,
            'notes': self.notes,
            'details': [detail.to_dict() for detail in self.details]
        }

    def __repr__(self):
        return f'<Loan {self.loan_code} - Status: {self.status}>'


class LoanDetail(db.Model):
    __tablename__ = 'loan_details'

    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id', ondelete='CASCADE'), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete='RESTRICT'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    returned = db.Column(db.Boolean, nullable=False, default=False)
    return_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.String(255), nullable=True)

    # Relationships
    loan = db.relationship('Loan', back_populates='details')
    book = db.relationship('Book', back_populates='loan_details')

    def to_dict(self):
        return {
            'id': self.id,
            'loan_id': self.loan_id,
            'book_id': self.book_id,
            'book_title': self.book.title if self.book else None,
            'quantity': self.quantity,
            'returned': self.returned,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'notes': self.notes
        }

    def __repr__(self):
        return f'<LoanDetail #{self.id} Book:{self.book_id} Returned:{self.returned}>'
