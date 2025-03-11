from bson import ObjectId
from pydantic import BaseModel, Field, ValidationError
from typing import Optional


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value, values=None, field=None):
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler):
        schema.update(type="string")
        return schema

    def __str__(self):
        return str(self)


class OCRText(BaseModel):
    id: Optional[str] = Field(None)
    file_name: str
    recognized_text: str
    detected_language: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class OCRUpdateRequest(BaseModel):
    document_id: str
    original_text: str
    updated_text: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
