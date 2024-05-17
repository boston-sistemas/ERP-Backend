from sqlmodel import SQLModel


class LoginForm(SQLModel):
    username: str
    password: str
