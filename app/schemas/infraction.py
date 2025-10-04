from typing import TypeVar, Generic, Sequence
from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime, date

T = TypeVar("T")

class InfractionPublic(BaseModel):
    id: int
    source_id: int
    infraction_number: str
    process_number: str | None
    status: str
    sanction_type: str | None
    gravity: str | None
    fine_value: Decimal
    infraction_datetime: datetime
    fact_date: date | None
    system_launch_date: date | None
    last_updated_date: datetime | None
    offender_name: str
    offender_document: str
    description: str | None
    infraction_type_description: str | None
    municipality: str | None
    state: str
    location_description: str | None
    longitude: Decimal | None
    latitude: Decimal | None
    affected_biomes: str | None

    model_config = ConfigDict(from_attributes=True)

class Page(BaseModel, Generic[T]):
    total: int
    page: int
    size: int
    items: Sequence[T]