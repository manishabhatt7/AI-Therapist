from pydantic import BaseModel
import uuid

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str | None = None

class RegisterResponse(BaseModel):
    message: str
