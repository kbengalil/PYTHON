from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(prefix='/auth',tags=['auth'])

SECRET_KEY = 'dhh384jd93mdkkj#kej^^#3jewje92js&***4jwjwE39EKDNEWLASNSkskdjkdi03030'
ALGO = 'HS256'


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oath2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


class CreatUserrequest(BaseModel):
    user_name: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str

class Token(BaseModel):
    access_token:str
    token_type: str



@router.post('/', status_code=status.HTTP_201_CREATED)
def create_user(db: db_dependency,
                create_user: CreatUserrequest):
    create_user = Users(
        email=create_user.email,
        username=create_user.user_name,
        first_name=create_user.first_name,
        last_name=create_user.last_name,
        hashed_password=bcrypt_context.hash(create_user.password),
        role=create_user.role,
        is_active=True)

    db.add(create_user)
    db.commit()



async def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


async def create_access_token(username: str, user_id: int, expire_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + expire_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY,algorithm=ALGO)


async def get_current_user(token: Annotated[str, Depends(OAuth2PasswordBearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY,algorithms=[ALGO])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="not validated")
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="not validated")




@router.post('/token', response_model=Token)
async def login_for_accsses_token(form_data: Annotated[OAuth2PasswordRequestForm,
Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="not validated")

    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}


