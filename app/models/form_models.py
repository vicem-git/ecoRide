from typing_extensions import Self, Optional
import re
from typing import List
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    model_validator,
    constr,
    UUID4,
)
from datetime import datetime


class RegistrationData(BaseModel):
    email: EmailStr = Field(
        ...,
    )
    password: str = Field(
        ...,
    )
    confirm_password: str = Field(
        ...,
    )
    username: str = constr()
    roles: List[str] = Field(
        ...,
    )

    @field_validator("email")
    def validate_email(value):
        cleaned_email = value.strip().lower()
        if "@" not in cleaned_email or "." not in cleaned_email:
            raise ValueError("Veuillez fournir une adresse e-mail valide.")
        return cleaned_email

    @field_validator("username")
    def validate_username(value):
        min_length = 3
        max_length = 15
        cleaned_username = value.strip()
        if not re.match(r"^[a-zA-Z0-9_]+$", cleaned_username):
            raise ValueError(
                "Le nom d'utilisateur ne peut contenir que des lettres, des chiffres et des tirets bas."
            )
        if len(cleaned_username) < min_length or len(cleaned_username) > max_length:
            raise ValueError(
                f"Le nom d'utilisateur doit comporter entre {min_length} et {max_length} caractères."
            )
        return cleaned_username

    @field_validator("roles")
    def validate_roles(value):
        min_roles = 1
        if len(value) < min_roles:
            raise ValueError("Veuillez sélectionner au moins un rôle.")
        return value

    @field_validator("password")
    def validate_password(v):
        min_length = 8
        cleaned_password = v.strip()
        if len(cleaned_password) < min_length:
            raise ValueError(
                f"Le mot de passe doit comporter au moins {min_length} caractères."
            )
        return cleaned_password

    @model_validator(mode="after")
    def passwords_match(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Les mots de passe ne correspondent pas.")
        return self


class LoginData(BaseModel):
    email: EmailStr = Field(
        ...,
    )
    password: str = Field(
        ...,
    )

    @field_validator("email")
    def validate_email(value):
        cleaned_email = value.strip().lower()
        if "@" not in cleaned_email or "." not in cleaned_email:
            raise ValueError("Veuillez fournir une adresse e-mail valide.")
        return cleaned_email

    @field_validator("password")
    def validate_password(value):
        min_length = 8
        cleaned_password = value.strip()
        if len(cleaned_password) < min_length:
            raise ValueError(
                f"Le mot de passe il comporte au moins {min_length} caractères."
            )
        return cleaned_password


class TripSearchData(BaseModel):
    start_city: str = Field(
        ...,
    )
    end_city: str = Field(
        ...,
    )
    start_date: Optional[str] = None
    passenger_nr: Optional[int] = Field(default=1)
    max_price: Optional[int] = Field(default=25)
    driver_rating: Optional[int] = Field(default=3)
    eco_filter: bool = False

    @field_validator("passenger_nr", mode="before")
    def default_passenger_nr(v):
        return int(v) if v not in (None, "") else 1

    @field_validator("max_price", mode="before")
    def default_max_price(v):
        return int(v) if v not in (None, "") else 25

    @field_validator("driver_rating", mode="before")
    def default_driver_rating(v):
        return int(v) if v not in (None, "") else 3

    @field_validator("start_date")
    def validate_start_date(value):
        if not value:
            value = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return value.strip()

    @field_validator("start_city", "end_city")
    def validate_city(value):
        if not value or not value.strip():
            raise ValueError("veuillez choisir une ville de départ/ arrivée.")
        return value.strip()

    @property
    def energy_type(self):
        return "electrique" if self.eco_filter else None


class CreateTripData(BaseModel):
    start_city: str = Field(
        ...,
    )
    end_city: str = Field(
        ...,
    )
    start_datetime: datetime = Field(
        ...,
    )
    price: int = Field(
        ...,
    )
    vehicle_id: UUID4 = Field(
        ...,
    )

    @field_validator("start_city", "end_city")
    def not_empty(v):
        if not v.strip():
            raise ValueError("La ville de départ/ arrivée ne peut pas être vide.")
        return v

    @model_validator(mode="after")
    def validate_cities(self):
        if self.start_city == self.end_city:
            raise ValueError(
                "La ville de départ et d'arrivée ne peuvent pas être identiques."
            )
        return self


class CreateModeratorData(BaseModel):
    email: EmailStr = Field(
        ...,
    )
    password: str = Field(
        ...,
    )

    @field_validator("email")
    def validate_email(value):
        cleaned_email = value.strip().lower()
        if "@" not in cleaned_email or "." not in cleaned_email:
            raise ValueError("Veuillez fournir une adresse e-mail valide.")
        return cleaned_email

    @field_validator("password")
    def validate_password(value):
        min_length = 8
        cleaned_password = value.strip()
        if len(cleaned_password) < min_length:
            raise ValueError(
                f"Le mot de passe il comporte au moins {min_length} caractères."
            )
        return cleaned_password
