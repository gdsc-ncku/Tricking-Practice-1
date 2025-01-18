from beanie.operators import And, Or
from fastapi import APIRouter, Body, HTTPException, Path, status

from datetime import datetime
try:
    from datetime import UTC
except ImportError:
    from datetime import timezone
    UTC = timezone.utc

from config import JWT_KEY
from schemas.jwt import JWT
from schemas.user import User, UserUpdate, UserView
from utils.generate_jwt import generate_jwt

from .auth import UserDepends, last_password_change_utc

USER_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found"
)
WRONG_PASSWORD = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Your password is wrong"
)
UPDATE_FAILED = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Some fields are conflict with others"
)
CANT_DELETE_OTHERS = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You can not delete data of others"
)

router = APIRouter(
    prefix="/user",
    tags=["User"]
)


@router.get(
    path="/{uid}",
    response_model=UserView,
    description="Get user information by uid.",
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "description": "User not found."
        }
    },
)
async def get_user(
    uid: str = Path(
        title="UID",
        description="UID of user you want to search",
    )
) -> UserView:
    user = await User.find_one(User.uid == uid).project(UserView)

    if user:
        return user
    raise USER_NOT_FOUND


@router.put(
    path="",
    response_model=JWT,
    description="Update user's data.",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "description": "Password is wrong."
        },
        403: {
            "description": "Update failed, some fields are conflict with others."
        }
    }
)
async def update_data(
    user: UserDepends,
    data: UserUpdate
) -> JWT:
    user_data = await User.find_one(User.uid == user.uid)
    if not user_data.check_password(data.original_password):
        raise WRONG_PASSWORD

    query_stats = []
    if data.name:
        query_stats.append(User.name == data.name)
    if data.email:
        query_stats.append(User.email == data.email)
    if data.phone:
        query_stats.append(User.phone == data.phone)

    if query_stats and await User.find_one(And(User.uid != user.uid, Or(*query_stats))):
        raise UPDATE_FAILED

    user_data = await user_data.set(data.model_dump(exclude_unset=True))

    if data.password is not None:
        last_password_change_utc[user.uid] = datetime.now(UTC)

    return generate_jwt(user_data)


@router.delete(
    path="",
    description="Delete user's data.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        400: {
            "description": "Password is wrong."
        },
        403: {
            "description": "You can only delete data of yourself."
        }
    }
)
async def delete_user(user: UserDepends, password: str = Body(example="passw0rd")) -> None:
    user_data = await User.find_one(User.uid == user.uid)
    if not user_data.check_password(password):
        raise WRONG_PASSWORD

    await user_data.delete()

    last_password_change_utc[user.uid] = datetime.now(UTC)

    return
