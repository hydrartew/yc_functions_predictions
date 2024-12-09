from datetime import datetime

from pydantic import BaseModel, field_validator


class Prediction(BaseModel):
    prediction_id: int
    accepted: bool = True
    author_staff_login: str = 'admin'
    dttm_created: datetime
    text: str
    issue_key: str | None = None

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        if 10 <= len(v) <= 256:
            return v
        raise ValueError('The length of the text should be from 10 to 256 characters (inclusive)')
