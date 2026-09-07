from typing import Any

from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)


class WidgetCreate(BaseModel):
    widget_type: str = Field(
        default="signup",
        pattern="^(signup|contact)$",
    )
    title: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    fields: list[str] = Field(min_length=1, max_length=10)
    button_text: str = Field(default="Submit", min_length=1, max_length=50)
    display_options: dict[str, Any] = Field(default_factory=dict)


class WidgetUpdate(BaseModel):
    widget_type: str | None = Field(
        default=None,
        pattern="^(signup|contact)$",
    )
    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    fields: list[str] | None = Field(default=None, min_length=1, max_length=10)
    button_text: str | None = Field(default=None, min_length=1, max_length=50)
    display_options: dict[str, Any] | None = None


class SubmissionRequest(BaseModel):
    widget_id: str
    data: dict[str, Any]
    honeypot: str = Field(default="", max_length=200)

    @field_validator("data")
    @classmethod
    def validate_data(cls, value):
        if len(value) > 20:
            raise ValueError("Too many fields")

        for key, item in value.items():
            if len(str(key)) > 100:
                raise ValueError("Field name too long")

            if len(str(item)) > 5000:
                raise ValueError("Field value too long")

        return value