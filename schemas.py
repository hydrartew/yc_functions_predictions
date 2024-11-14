from datetime import datetime
from typing import List, Optional, Any, Literal, Annotated, Callable

from pydantic import (BaseModel, field_validator, AfterValidator, Field, ConfigDict, HttpUrl, ValidationInfo,
                      computed_field)
from requests import Response
from requests.structures import CaseInsensitiveDict


class Prediction(BaseModel):
    prediction_id: int
    accepted: bool = True
    author_tg_user_id: int = 0
    author_staff_login: str = 'admin'
    dttm_created: datetime
    dttm_last_usage: datetime = datetime(1970, 1, 1)
    text: str

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        if 10 <= len(v) <= 256:
            return v
        raise ValueError('The length of the text should be from 10 to 256 characters (inclusive)')
