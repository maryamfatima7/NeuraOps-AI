from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str | None = Field(default=None, min_length=8)
    full_name: str = Field(..., min_length=2)

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, value: str, info):
        values = info.data
        if value is not None and "password" in values and value != values["password"]:
            raise ValueError("Passwords do not match")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    plan: str = "FREE"
    plan_status: str = "ACTIVE"

    class Config:
        from_attributes = True
