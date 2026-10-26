
# PostgreSQL connection settings loaded from environment variables.

import os
from typing import Any

from pydantic import (
    PostgresDsn,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_PASSWORD_FILE: str | None = None
    POSTGRES_DB: str

    @model_validator(mode="before")
    @classmethod
    def check_postgres_password(cls, data: Any) -> Any:
        if isinstance(data, dict):
            password_file = data.get("POSTGRES_PASSWORD_FILE")
            password = data.get("POSTGRES_PASSWORD")

            if password_file is None and password is None:
                raise ValueError(
                    "POSTGRES_PASSWORD or POSTGRES_PASSWORD_FILE must be set."
                )

        return data

    @field_validator("POSTGRES_PASSWORD_FILE", mode="before")
    @classmethod
    def read_password_from_file(cls, value: str | None) -> str | None:
        if value is not None:
            if os.path.exists(value):
                with open(value) as file:
                    return file.read().strip()

            raise ValueError(f"Password file {value} does not exist.")

        return value

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        url = MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=(
                self.POSTGRES_PASSWORD
                if self.POSTGRES_PASSWORD
                else self.POSTGRES_PASSWORD_FILE
            ),
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

        return PostgresDsn(url)


settings = Settings()  # type: ignore
