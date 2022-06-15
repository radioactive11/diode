from pydantic import BaseModel


class Details(BaseModel):
    token: str
