from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime

router = APIRouter(prefix='/auth', tags=['auth'])

KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
ALG = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_berear = OAuth2PasswordBearer(tokenUrl='auth/token')


class CreateUser(BaseModel):
    user_name: str
    first_name: str
    last_name: str
    password: str
    role: str
    email: str


class Token(BaseModel):
    acsses_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def auth_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(user_name: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': user_name, 'id': user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, KEY, algorithm=ALG)


async def get_current_user(token: Annotated[str, Depends(oauth2_berear)]):
    try:
        payload = jwt.decode(token, KEY, algorithms=[ALG])
        username: str = payload.get('sub')
        id: int = payload.get('id')
        if username is None or id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Not Authorized')

        return {'username': username, "id": id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='JWT ERROR')


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user: CreateUser):
    create_user_model = Users(
        username=create_user.user_name,
        first_name=create_user.first_name,
        email=create_user.email,
        last_name=create_user.last_name,
        hashed_password=bcrypt_context.hash(create_user.password),
        role=create_user.role,
        is_active=True)

    db.add(create_user_model)
    db.commit()


@router.post("/token", response_model=Token)
async def loing_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                      db: db_dependency):
    user = auth_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Not Authorized')
    token = create_access_token(user.username, user.id, timedelta(minutes=20))

    return {'acsses_token': token, 'token_type': 'bearer'}
