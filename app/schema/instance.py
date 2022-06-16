from pydantic import BaseModel


class CreateInstance(BaseModel):
    token: str
    instance_type: str
    region: str
    image: str


class DeleteInstance(BaseModel):
    token: str
    instance_id: str
