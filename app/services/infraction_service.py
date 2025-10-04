from app.models.infraction import Infraction
from sqlalchemy.orm import Session
from datetime import date
from decimal import Decimal
from sqlalchemy import select, func


def get_infractions(
    db: Session, 
    *,
    skip: int = 0, 
    limit: int = 50,
    source_id: int | None = None,
    infraction_number: str | None = None,
    offender_name: str | None = None,
    offender_document: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    min_fine_value: Decimal | None = None,
    municipality: str | None = None,
    state: str | None = None,
    affected_biomes: str | None = None
) -> tuple[int, list[Infraction]]:
    
    stmt = select(Infraction)

    if source_id:
        stmt = stmt.where(Infraction.source_id == source_id)

    if infraction_number:
        stmt = stmt.where(Infraction.infraction_number == infraction_number)

    if offender_name:
        stmt = stmt.where(Infraction.offender_name.ilike(f"%{offender_name}%"))

    if offender_document:
        stmt = stmt.where(Infraction.offender_document == offender_document)

    if start_date:
        stmt = stmt.where(Infraction.infraction_datetime >= start_date)

    if end_date:
        stmt = stmt.where(Infraction.infraction_datetime <= end_date)

    if min_fine_value:
        stmt = stmt.where(Infraction.fine_value >= min_fine_value)

    if municipality:
        stmt = stmt.where(Infraction.municipality.ilike(f"%{municipality}%"))

    if state:
        stmt = stmt.where(Infraction.state == state)

    if affected_biomes:
        stmt = stmt.where(Infraction.affected_biomes.ilike(f"%{affected_biomes}%"))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.scalar(count_stmt) or 0

    result_stmt = stmt.order_by(Infraction.infraction_datetime.desc()).offset(skip).limit(limit)
    
    infractions = db.scalars(result_stmt).all()

    return total, list(infractions)

