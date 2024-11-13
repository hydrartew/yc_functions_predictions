from datetime import datetime
from typing import List, Optional, Any, Literal, Annotated, Callable

from pydantic import (BaseModel, field_validator, AfterValidator, Field, ConfigDict, HttpUrl, ValidationInfo,
                      computed_field)
from requests import Response
from requests.structures import CaseInsensitiveDict


# class YandexPassportData(BaseModel):
#     model_config = ConfigDict(arbitrary_types_allowed=True)
#
#     headers: CaseInsensitiveDict | dict
#     time_created: datetime
#     csrf_tokens: CsrfTokens = CsrfTokens()
#
#     @field_validator('headers')
#     @classmethod
#     def validate_headers(cls, v: CaseInsensitiveDict) -> CaseInsensitiveDict:
#         v['User-Agent'] = 'SuptechTaxi script by @amayammi'
#         return v
#
#     @computed_field
#     @property
#     def headers_expired(self) -> bool:
#         return (datetime.now() - self.time_created).total_seconds() > settings.yt_session_expired

class Prediction(BaseModel):
    accepted: bool = True
    author_tg_user_id: int
    author_staff_login: str
    dttm_created: datetime
    dttm_last_usage: datetime | None = None
    text: str

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        if 10 <= len(v) <= 256:
            return v
        raise ValueError('The length of the text should be from 10 to 256 characters (inclusive)')
