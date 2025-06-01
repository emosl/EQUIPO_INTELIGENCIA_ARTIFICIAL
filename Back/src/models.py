import datetime as _dt
import sqlalchemy as _sql
import sqlalchemy.orm as _orm

import database as _database

class User(_database.Base):
    __tablename__ = "users"
    user_id: Mapped[int] = _sql.Column(_sql.Integer, primary_key=True, index=True)
    email = _sql.Column(_sql.String, unique=True)
    password = _sql.Column(_sql.String)
    is_active = _sql.Column(_sql.Boolean, default=True)

class Patient(_database.Base):
    __tablename__ = "patients"
    patient_id: Mapped[int] = _sql.Column(_sql.Integer, primary_key=True, index=True)
    name = _sql.Column(_sql.String)
    father_surname = _sql.Column(_sql.String)
    mother_surname = _sql.Column(_sql.String)
    age = _sql.Column(_sql.String)
    sex = _sql.Column(_sql.String)

class Session(_database.Base):
    __tablename__ = "sessions"
    session_id: Mapped[int] = _sql.Column(_sql.Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = _sql.Column(_sql.Integer, foreign_key=True)
    user_id: Mapped[int] = _sql.Column(_sql.Integer, foreign_key=True)
    session_timestamp = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)

class EegData(_database.Base):
    __tablename__ = "eeg_data"
    session_id: Mapped[int] = _sql.Column(_sql.Integer, foreign_key=True)
    af3 = _sql.Column(_sql.Float)
    f7 = _sql.Column(_sql.Float)
    f3 = _sql.Column(_sql.Float)
    fc5 = _sql.Column(_sql.Float)
    t7 = _sql.Column(_sql.Float)
    p7 = _sql.Column(_sql.Float)
    o1 = _sql.Column(_sql.Float)
    o2 = _sql.Column(_sql.Float)
    p8 = _sql.Column(_sql.Float)
    t8 = _sql.Column(_sql.Float)
    fc6 = _sql.Column(_sql.Float)
    f4 = _sql.Column(_sql.Float)
    f8 = _sql.Column(_sql.Float)
    af4 = _sql.Column(_sql.Float)