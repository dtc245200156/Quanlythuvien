from datetime import datetime
from app.extensions import db
from sqlalchemy import CheckConstraint

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(30), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    author = db.Column(db.String(255), nullable=False, index=True)
    category = db.Column(db.String(100), nullable=False, default='Khác')
    publisher = db.Column(db.String(150), nullable=True)
    publish_year = db.Column(db.Integer, nullable=True)
    total_quantity = db.Column(db.Integer, nullable=False, default=1)
    available_quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint('total_quantity >= 0', name='check_total_quantity_non_negative'),
        CheckConstraint('available_quantity >= 0', name='check_available_quantity_non_negative'),
        CheckConstraint('available_quantity <= total_quantity', name='check_available_le_total'),
    )

    # Relationships
    loan_details = db.relationship('LoanDetail', back_populates='book', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'isbn': self.isbn,
            'title': self.title,
            'author': self.author,
            'category': self.category,
            'publisher': self.publisher,
            'publish_year': self.publish_year,
            'total_quantity': self.total_quantity,
            'available_quantity': self.available_quantity,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Book {self.isbn} - {self.title}>'
