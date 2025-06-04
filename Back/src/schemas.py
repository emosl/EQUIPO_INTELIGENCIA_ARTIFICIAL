from datetime import date, datetime
from pydantic import BaseModel

# User Classes
class UserBase(BaseModel):
    name: str
    father_surname: str
    mother_surname: str
    medical_department: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
    


#Patient Classes
class PatientBase(BaseModel):
    name: str
    father_surname: str
    mother_surname: str
    birth_date: date
    sex: str
    email: str

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# Session Classes
class SessionBase(BaseModel):
    patient_id: int

class SessionCreate(SessionBase):
    pass

class Session(SessionBase):
    id: int
    patient_id: int
    session_timestamp: datetime

    class Config:
        from_attributes = True

# EEGData Classes
class EegDataBase(BaseModel):
    af3: float
    f7: float
    f3: float
    fc5: float
    t7: float
    p7: float
    o1: float
    o2: float
    p8: float
    t8: float
    fc6: float
    f4: float
    f8: float
    af4: float

class EegDataCreate(EegDataBase):
    pass

class EegData(EegDataBase):
    session_id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None