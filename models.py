from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey


db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    stats = db.relationship("Stats", back_populates="user",
                            uselist=False, cascade="all, delete-orphan")


class Stats(db.Model):
    __tablename__ = "stats"
    id = db.Column(db.Integer, ForeignKey(User.id), primary_key=True)
    money = db.Column(db.BigInteger, nullable=False)
    prestiges = db.Column(db.BigInteger, nullable=False)
    producers = db.Column(db.Text, nullable=False)
    user = db.relationship("User", back_populates="stats")
