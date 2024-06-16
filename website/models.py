from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column


class Role(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(64), nullable=False, unique=True)

    users: Mapped[list["User"]] = db.relationship(back_populates="role", uselist=True)


class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(db.String(128), nullable=True)
    last_name: Mapped[str] = mapped_column(db.String(128), nullable=True)
    username: Mapped[str] = mapped_column(db.String(128), nullable=False)
    photo_url: Mapped[str] = mapped_column(db.String(128), nullable=True)
    auth_date: Mapped[str] = mapped_column(db.String(128), nullable=True)
    hash: Mapped[str] = mapped_column(db.String(128), nullable=False)
    balance: Mapped[int] = mapped_column(nullable=False, default=10)
    subsciption_end: Mapped[str] = mapped_column(db.TIMESTAMP, nullable=True)
    role_id: Mapped[int] = mapped_column(db.ForeignKey("role.id"))

    role: Mapped["Role"] = db.relationship(back_populates="users", uselist=False)
    payments: Mapped[list["Payments"]] = db.relationship(
        back_populates="user", uselist=True
    )


class Payments(db.Model):
    id: Mapped[str] = mapped_column(db.String(36), primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"))
    status: Mapped[str] = mapped_column(db.String(64), nullable=False)
    amount: Mapped[str] = mapped_column(db.String(16), nullable=False)
    created_at: Mapped[int] = mapped_column(db.TIMESTAMP, default=func.now())

    user: Mapped["User"] = db.relationship(back_populates="payments", uselist=False)
