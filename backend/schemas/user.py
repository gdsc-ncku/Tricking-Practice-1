from bcrypt import checkpw, gensalt, hashpw
from beanie import Document, Indexed
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
)

from typing import Annotated, Any, Optional

from config import INSTANCE_ID
from snowflake import SnowflakeGenerator, SnowflakeID

from .utils import optional

uid_generator = SnowflakeGenerator(INSTANCE_ID)


class UserBase(BaseModel):
    name: str = Field(
        title="Username",
        description="Username of user."
    )
    email: Optional[str] = Field(
        default=None,
        title="Email",
        description="User's email."
    )
    phone: Optional[str] = Field(
        default=None,
        title="Phone number",
        description="User's phone number."
    )
    gender: Optional[bool] = Field(
        default=None,
        title="Gender",
        description="User's gender, true rerepresent female."
    )
    age: Optional[int] = Field(
        default=None,
        title="Age",
        description="User's age."
    )


class UserWithPassword(UserBase):
    password: bytes = Field(
        title="Password(Hash)",
        description="Password of user after hash."
    )

    def check_password(self, password: str) -> bool:
        return checkpw(password.encode("utf-8"), self.password)


class UserWithUID(UserBase):
    uid: Annotated[SnowflakeID, Indexed(unique=True)] = Field(
        title="UID",
        description="UID of user, use snowflake format.",
        default_factory=uid_generator.next_id,
    )


class User(Document, UserWithUID, UserWithPassword):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "uid": 302774180611358720,
                    "name": "User",
                    "password": b"4fe3d2877cff0475",
                    "email": "contact@example.com",
                    "phone": None,
                    "gender": True,
                    "age": 24,
                }
            ]
        }
    )

    class Settings:
        name = "Users"
        bson_encoders = {
            SnowflakeID: str
        }


class UserView(UserWithUID):
    pass


class UserCreate(UserBase):
    password: str = Field(
        title="Password",
        description="Password of user."
    )

    @field_serializer("password")
    def password_auto_hash(self, value: str) -> Optional[bytes]:
        if value:
            return hashpw(value.encode("utf-8"), gensalt())
        return None


@optional
class UserUpdate(UserCreate):
    original_password: str = Field(
        title="Original Password",
        description="The original password is needed if user want to update their data."
    )
