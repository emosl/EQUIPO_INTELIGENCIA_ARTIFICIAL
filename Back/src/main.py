from fastapi import *
from schemas import *
from services import *
from sqlalchemy.orm import *

app = FastAPI()

create_database()

@app.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session=Depends(get_db())):
    db_user = get_user_by_email(db=db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="The entered email is already in use")  
    return create_user()