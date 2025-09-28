from app.models.base import Base, bigintpk
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DECIMAL, DateTime, Date, TEXT, Index
from decimal import Decimal
from datetime import datetime, date

class Infraction(Base):
    __tablename__ = "infractions"

    id: Mapped[bigintpk] # Mapeado de: SEQ_AUTO_INFRACAO
    infraction_number: Mapped[str] = mapped_column(String(255), unique=True, nullable=False) # Mapeado de: NUM_AUTO_INFRACAO
    process_number: Mapped[str] = mapped_column(String(255), index=True, nullable=True) # Mapeado de: NU_PROCESSO_FORMATADO

    status: Mapped[str] = mapped_column(String(100), nullable=False) # Mapeado de: DES_STATUS_FORMULARIO
    sanction_type: Mapped[str] = mapped_column(String(100), nullable=True) # Mapeado de: TIPO_AUTO
    gravity: Mapped[str] = mapped_column(String(50), nullable=True) # Mapeado de: GRAVIDADE_INFRACAO

    fine_value: Mapped[Decimal] = mapped_column(DECIMAL(precision=12, scale=2), nullable=False, default=0.0) # Mapeado de: VAL_AUTO_INFRACAO

    infraction_datetime: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False) # Mapeado de: DAT_HORA_AUTO_INFRACAO
    fact_date: Mapped[date] = mapped_column(Date, nullable=True) # Mapeado de: DT_FATO_INFRACIONAL
    system_launch_date: Mapped[date] = mapped_column(Date, nullable=True) # Mapeado de: DT_LANCAMENTO
    last_updated_date: Mapped[datetime] = mapped_column(DateTime, nullable=True) # Mapeado de: DT_ULT_ALTERACAO

    offender_name: Mapped[str] = mapped_column(TEXT, nullable=False) # Mapeado de: NOME_INFRATOR
    offender_document: Mapped[str] = mapped_column(String(255), index=True, nullable=False) # Mapeado de: CPF_CNPJ_INFRATOR

    description: Mapped[str] = mapped_column(TEXT, nullable=True) # Mapeado de: DES_AUTO_INFRACAO
    infraction_type_description: Mapped[str] = mapped_column(TEXT, nullable=True) # Mapeado de: DES_INFRACAO

    municipality: Mapped[str] = mapped_column(String(255), nullable=True) # Mapeado de: MUNICIPIO
    state: Mapped[str] = mapped_column(String(2), nullable=False) # Mapeado de: UF
    location_description: Mapped[str] = mapped_column(TEXT, nullable=True) # Mapeado de: DES_LOCAL_INFRACAO
    longitude: Mapped[Decimal] = mapped_column(DECIMAL(11, 8), nullable=True) # Mapeado de: NUM_LONGITUDE_AUTO
    latitude: Mapped[Decimal] = mapped_column(DECIMAL(10, 8), nullable=True) # Mapeado de: NUM_LATITUDE_AUTO
    affected_biomes: Mapped[str] = mapped_column(TEXT, nullable=True) # Mapeado de: DS_BIOMAS_ATINGIDOS

    __table_args__ = (
        Index('ix_infractions_latitude_longitude', 'latitude', 'longitude'),
    )
