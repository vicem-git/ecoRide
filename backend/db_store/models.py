from geoalchemy2 import Geography
from typing import Any, List, Optional
from alchemy import Base, alchemy_db

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    PrimaryKeyConstraint,
    String,
    Table,
    Text,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import NullType
import datetime
import uuid


class AccountAccess(Base):
    __tablename__ = "account_access"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="account_access_pkey"),
        UniqueConstraint("name", name="account_access_name_key"),
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(50))

    accounts: Mapped[List["Accounts"]] = relationship(
        "Accounts", back_populates="account_access"
    )


class AccountStatus(Base):
    __tablename__ = "account_status"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="account_status_pkey"),
        UniqueConstraint("name", name="account_status_name_key"),
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(50))

    accounts: Mapped[List["Accounts"]] = relationship(
        "Accounts", back_populates="account_status_"
    )


class EnergyTypes(Base):
    __tablename__ = "energy_types"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="energy_types_pkey"),
        UniqueConstraint("name", name="energy_types_name_key"),
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(50))

    vehicles: Mapped[List["Vehicles"]] = relationship(
        "Vehicles", back_populates="energy_type"
    )


t_geography_columns = Table(
    "geography_columns",
    Base.metadata,
    Column("f_table_catalog", String),
    Column("f_table_schema", String),
    Column("f_table_name", String),
    Column("f_geography_column", String),
    Column("coord_dimension", Integer),
    Column("srid", Integer),
    Column("type", Text),
    schema="public",
)


t_geometry_columns = Table(
    "geometry_columns",
    Base.metadata,
    Column("f_table_catalog", String(256)),
    Column("f_table_schema", String),
    Column("f_table_name", String),
    Column("f_geometry_column", String),
    Column("coord_dimension", Integer),
    Column("srid", Integer),
    Column("type", String(30)),
    schema="public",
)


class Preferences(Base):
    __tablename__ = "preferences"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="preferences_pkey"),
        UniqueConstraint("name", name="preferences_name_key"),
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(50))

    driver: Mapped[List["DriverData"]] = relationship(
        "DriverData", secondary="public.driver_preferences", back_populates="preference"
    )


class ReviewStatus(Base):
    __tablename__ = "review_status"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="review_status_pkey"),
        UniqueConstraint("name", name="review_status_name_key"),
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(50))

    reviews: Mapped[List["Reviews"]] = relationship(
        "Reviews", back_populates="review_status"
    )


class Roles(Base):
    __tablename__ = "roles"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="roles_pkey"),
        UniqueConstraint("name", name="roles_name_key"),
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(50))

    user: Mapped[List["Users"]] = relationship(
        "Users", secondary="public.user_roles", back_populates="role"
    )


class SpatialRefSys(Base):
    __tablename__ = "spatial_ref_sys"
    __table_args__ = (
        CheckConstraint(
            "srid > 0 AND srid <= 998999", name="spatial_ref_sys_srid_check"
        ),
        PrimaryKeyConstraint("srid", name="spatial_ref_sys_pkey"),
        {"schema": "public"},
    )

    srid: Mapped[int] = mapped_column(Integer, primary_key=True)
    auth_name: Mapped[Optional[str]] = mapped_column(String(256))
    auth_srid: Mapped[Optional[int]] = mapped_column(Integer)
    srtext: Mapped[Optional[str]] = mapped_column(String(2048))
    proj4text: Mapped[Optional[str]] = mapped_column(String(2048))


class VehicleBrand(Base):
    __tablename__ = "vehicle_brand"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="vehicle_brand_pkey"),
        UniqueConstraint("name", name="vehicle_brand_name_key"),
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(50))

    vehicles: Mapped[List["Vehicles"]] = relationship(
        "Vehicles", back_populates="vehicle_brand"
    )


class Accounts(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        ForeignKeyConstraint(
            ["account_access_id"],
            ["public.account_access.id"],
            ondelete="CASCADE",
            name="accounts_account_access_id_fkey",
        ),
        ForeignKeyConstraint(
            ["account_status"],
            ["public.account_status.id"],
            ondelete="CASCADE",
            name="accounts_account_status_fkey",
        ),
        PrimaryKeyConstraint("id", name="accounts_pkey"),
        UniqueConstraint("email", name="accounts_email_key"),
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    email: Mapped[str] = mapped_column(String(100))
    password_hash: Mapped[str] = mapped_column(String(255))
    account_access_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    account_status: Mapped[uuid.UUID] = mapped_column(Uuid)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, server_default=text("now()")
    )

    account_access: Mapped["AccountAccess"] = relationship(
        "AccountAccess", back_populates="accounts"
    )
    account_status_: Mapped["AccountStatus"] = relationship(
        "AccountStatus", back_populates="accounts"
    )
    users: Mapped[List["Users"]] = relationship("Users", back_populates="account")


class Vehicles(Base):
    __tablename__ = "vehicles"
    __table_args__ = (
        ForeignKeyConstraint(
            ["brand"],
            ["public.vehicle_brand.id"],
            ondelete="CASCADE",
            name="vehicles_brand_fkey",
        ),
        ForeignKeyConstraint(
            ["energy_type_id"],
            ["public.energy_types.id"],
            ondelete="CASCADE",
            name="vehicles_energy_type_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="vehicles_pkey"),
        UniqueConstraint("plate_number", name="vehicles_plate_number_key"),
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    plate_number: Mapped[str] = mapped_column(String(20))
    registration_date: Mapped[datetime.date] = mapped_column(Date)
    brand: Mapped[uuid.UUID] = mapped_column(Uuid)
    model: Mapped[str] = mapped_column(String(50))
    color: Mapped[str] = mapped_column(String(30))
    number_of_seats: Mapped[int] = mapped_column(Integer)
    energy_type_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    photo_url: Mapped[Optional[str]] = mapped_column(String(255))

    vehicle_brand: Mapped["VehicleBrand"] = relationship(
        "VehicleBrand", back_populates="vehicles"
    )
    energy_type: Mapped["EnergyTypes"] = relationship(
        "EnergyTypes", back_populates="vehicles"
    )
    user: Mapped[List["Users"]] = relationship(
        "Users", secondary="public.driver_vehicles", back_populates="vehicle"
    )


class Users(Base):
    __tablename__ = "users"
    __table_args__ = (
        ForeignKeyConstraint(
            ["account_id"],
            ["public.accounts.id"],
            ondelete="CASCADE",
            name="users_account_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="users_pkey"),
        UniqueConstraint("username", name="users_username_key"),
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    account_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    username: Mapped[str] = mapped_column(String(30))
    photo_url: Mapped[Optional[str]] = mapped_column(String(255))
    credits: Mapped[Optional[int]] = mapped_column(Integer, server_default=text("20"))

    role: Mapped[List["Roles"]] = relationship(
        "Roles", secondary="public.user_roles", back_populates="user"
    )
    account: Mapped["Accounts"] = relationship("Accounts", back_populates="users")
    vehicle: Mapped[List["Vehicles"]] = relationship(
        "Vehicles", secondary="public.driver_vehicles", back_populates="user"
    )
    driver_data: Mapped[List["DriverData"]] = relationship(
        "DriverData", back_populates="user"
    )
    trips: Mapped[List["Trips"]] = relationship("Trips", back_populates="driver")
    trip: Mapped[List["Trips"]] = relationship(
        "Trips", secondary="public.trip_passengers", back_populates="user"
    )
    reviews: Mapped[List["Reviews"]] = relationship("Reviews", back_populates="author")


class DriverData(Base):
    __tablename__ = "driver_data"
    __table_args__ = (
        CheckConstraint("rating >= 0 AND rating <= 5", name="driver_data_rating_check"),
        ForeignKeyConstraint(
            ["user_id"],
            ["public.users.id"],
            ondelete="CASCADE",
            name="driver_data_user_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="driver_data_pkey"),
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    rating: Mapped[Optional[int]] = mapped_column(Integer, server_default=text("0"))

    user: Mapped["Users"] = relationship("Users", back_populates="driver_data")
    preference: Mapped[List["Preferences"]] = relationship(
        "Preferences", secondary="public.driver_preferences", back_populates="driver"
    )


t_driver_vehicles = Table(
    "driver_vehicles",
    Base.metadata,
    Column("user_id", Uuid, primary_key=True, nullable=False),
    Column("vehicle_id", Uuid, primary_key=True, nullable=False),
    ForeignKeyConstraint(
        ["user_id"],
        ["public.users.id"],
        ondelete="CASCADE",
        name="driver_vehicles_user_id_fkey",
    ),
    ForeignKeyConstraint(
        ["vehicle_id"],
        ["public.vehicles.id"],
        ondelete="CASCADE",
        name="driver_vehicles_vehicle_id_fkey",
    ),
    PrimaryKeyConstraint("user_id", "vehicle_id", name="driver_vehicles_pkey"),
    schema="public",
)


class Trips(Base):
    __tablename__ = "trips"
    __table_args__ = (
        ForeignKeyConstraint(
            ["driver_id"],
            ["public.users.id"],
            ondelete="CASCADE",
            name="trips_driver_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="trips_pkey"),
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    driver_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    vehicle_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    start_location: Mapped[Any] = mapped_column(
        Geography(geometry_type="POINT", srid=4326)
    )
    end_location: Mapped[Any] = mapped_column(
        Geography(geometry_type="POINT", srid=4326)
    )
    start_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    price: Mapped[int] = mapped_column(Integer)
    status: Mapped[Optional[str]] = mapped_column(
        String(50), server_default=text("'pending'::character varying")
    )
    rating: Mapped[Optional[int]] = mapped_column(Integer, server_default=text("0"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, server_default=text("now()")
    )
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, server_default=text("now()")
    )

    driver: Mapped["Users"] = relationship("Users", back_populates="trips")
    user: Mapped[List["Users"]] = relationship(
        "Users", secondary="public.trip_passengers", back_populates="trip"
    )
    reviews: Mapped[List["Reviews"]] = relationship("Reviews", back_populates="trip")


t_user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Uuid, primary_key=True, nullable=False),
    Column("role_id", Uuid, primary_key=True, nullable=False),
    ForeignKeyConstraint(
        ["role_id"],
        ["public.roles.id"],
        ondelete="CASCADE",
        name="user_roles_role_id_fkey",
    ),
    ForeignKeyConstraint(
        ["user_id"],
        ["public.users.id"],
        ondelete="CASCADE",
        name="user_roles_user_id_fkey",
    ),
    PrimaryKeyConstraint("user_id", "role_id", name="user_roles_pkey"),
    schema="public",
)


t_driver_preferences = Table(
    "driver_preferences",
    Base.metadata,
    Column("driver_id", Uuid, primary_key=True, nullable=False),
    Column("preference_id", Uuid, primary_key=True, nullable=False),
    ForeignKeyConstraint(
        ["driver_id"],
        ["public.driver_data.id"],
        ondelete="CASCADE",
        name="driver_preferences_driver_id_fkey",
    ),
    ForeignKeyConstraint(
        ["preference_id"],
        ["public.preferences.id"],
        ondelete="CASCADE",
        name="driver_preferences_preference_id_fkey",
    ),
    PrimaryKeyConstraint("driver_id", "preference_id", name="driver_preferences_pkey"),
    schema="public",
)


class Reviews(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating >= 0 AND rating <= 5", name="reviews_rating_check"),
        ForeignKeyConstraint(
            ["author_id"],
            ["public.users.id"],
            ondelete="CASCADE",
            name="reviews_author_id_fkey",
        ),
        ForeignKeyConstraint(
            ["review_status_id"],
            ["public.review_status.id"],
            ondelete="CASCADE",
            name="reviews_review_status_id_fkey",
        ),
        ForeignKeyConstraint(
            ["trip_id"],
            ["public.trips.id"],
            ondelete="CASCADE",
            name="reviews_trip_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="reviews_pkey"),
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    trip_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    author_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    rating: Mapped[int] = mapped_column(Integer)
    review_status_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    comments: Mapped[Optional[str]] = mapped_column(Text)

    author: Mapped["Users"] = relationship("Users", back_populates="reviews")
    review_status: Mapped["ReviewStatus"] = relationship(
        "ReviewStatus", back_populates="reviews"
    )
    trip: Mapped["Trips"] = relationship("Trips", back_populates="reviews")


t_trip_passengers = Table(
    "trip_passengers",
    Base.metadata,
    Column("trip_id", Uuid, primary_key=True, nullable=False),
    Column("user_id", Uuid, primary_key=True, nullable=False),
    ForeignKeyConstraint(
        ["trip_id"],
        ["public.trips.id"],
        ondelete="CASCADE",
        name="trip_passengers_trip_id_fkey",
    ),
    ForeignKeyConstraint(
        ["user_id"],
        ["public.users.id"],
        ondelete="CASCADE",
        name="trip_passengers_user_id_fkey",
    ),
    PrimaryKeyConstraint("trip_id", "user_id", name="trip_passengers_pkey"),
    schema="public",
)
