from . import db
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column

class Role(db.Model):
    id : Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(db.String(64), nullable=False, unique=True)

    users : Mapped[list['User']] = db.relationship(back_populates='role', uselist=True)

class User(db.Model, UserMixin):
    id : Mapped[int] = mapped_column(primary_key=True)
    login : Mapped[str] = mapped_column(db.String(32), unique=True, nullable=False)
    password_hash : Mapped[str] = mapped_column(db.String(300), nullable=False)
    balance : Mapped[int] = mapped_column(nullable=False, default=10)
    role_id : Mapped[int] = mapped_column(db.ForeignKey('role.id'))

    role : Mapped['Role'] = db.relationship(back_populates='users', uselist=False)