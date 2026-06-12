from pydantic import BaseModel, EmailStr, Field


class EmailRequest(BaseModel):
    to: EmailStr
    subject: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)


class EmailResponse(BaseModel):
    message: str
