from pydantic import BaseModel


class ExampleCreate(BaseModel):
    name: str


class ExampleOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
