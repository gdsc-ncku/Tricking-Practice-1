from beanie.operators import Or
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import decode
from pydantic import BaseModel

from typing import Annotated

from config import JWT_KEY
from schemas.jwt import JWT, JWTPayload
from schemas.user import User, UserCreate
from utils.generate_jwt import generate_jwt


class LoginData(BaseModel):
    account: str
    password: str
    # valid_code: str


AUTHORIZE_FAILED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Authorize failed"
)
ACCOUNT_ALREADY_EXIST = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="The account is already exist"
)
INVALIDE_AUTHENTICATION_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid authentication credentials"
)

SECURITY = HTTPBearer(
    scheme_name="JWT",
    description="JWT which get from posting discord oauth code to /auth/login."
)

router = APIRouter(
    prefix="/auth",
    tags=["Authorization"]
)

last_password_change_utc = {}


def valid_token(token: HTTPAuthorizationCredentials = Security(SECURITY)) -> JWTPayload:
    jwt = token.credentials
    try:
        decode_data = JWTPayload(**decode(
            jwt=jwt,
            key=JWT_KEY,
            algorithms=["HS256"],
            options={
                "require": ["exp", "iat"]
            }
        ))

        last_change = last_password_change_utc.get(decode_data.uid)
        if last_change is not None and decode_data.iat < last_change:
            raise INVALIDE_AUTHENTICATION_CREDENTIALS

        return decode_data
    except:
        raise INVALIDE_AUTHENTICATION_CREDENTIALS


user_depends = Depends(valid_token)
UserDepends = Annotated[JWTPayload, user_depends]


@router.post(
    path="/login",
    response_model=JWT,
    description="Login by account and password.",
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description": "The acocount or password are wrong."
        },
    }
)
async def login(data: LoginData) -> JWT:
    account = data.account
    password = data.password

    user = await User.find_one(Or(
        User.name == account,
        User.email == account,
        User.phone == account
    ))

    if user is None:
        raise AUTHORIZE_FAILED

    if not user.check_password(password):
        raise AUTHORIZE_FAILED

    return generate_jwt(user)


@router.post(
    path="/register",
    response_model=JWT,
    description="Register a new account and login.",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "description": "The account is already exist."
        }
    }
)
async def register(data: UserCreate) -> JWT:
    query_stats = [User.name == data.name]
    if data.email:
        query_stats.append(User.email == data.email)
    if data.phone:
        query_stats.append(User.phone == data.phone)

    if await User.find_one(Or(*query_stats)):
        raise ACCOUNT_ALREADY_EXIST

    new_user = User(**data.model_dump())

    await User.insert_one(new_user)

    return generate_jwt(new_user)


@router.put(
    path="/refresh",
    response_model=JWT,
    description="Update token.",
    status_code=status.HTTP_200_OK
)
def refresh_token(user: UserDepends) -> JWT:
    return generate_jwt(user)
