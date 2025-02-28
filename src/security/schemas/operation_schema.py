from pydantic import BaseModel, Field


class OperationBase(BaseModel):
    operation_id: int = Field(validation_alias="id")
    name: str

    class Config:
        from_attributes = True


class OperationSchema(OperationBase):
    pass


class OperationListSchema(BaseModel):
    operations: list[OperationSchema]
