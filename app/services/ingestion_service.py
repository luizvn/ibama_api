import logging
from app.db.session import AsyncSessionLocal
import pandas as pd
from sqlalchemy.dialects.mysql import insert
from app.models.infraction import Infraction
import os
import numpy as np
import asyncio
import aiofiles
from unidecode import unidecode


logger = logging.getLogger(__name__)

class IngestionService:

    def process_chunk(
        self, 
        chunk_df: pd.DataFrame, 
        column_mapping: dict
    ) -> list[dict]:

        logger.info(f"Iniciando o processamento do chunk com {len(chunk_df)} linhas em uma thread.")

        chunk_df.rename(columns=column_mapping, inplace=True)

        required_columns = [
            'infraction_number',
            'source_id',
            'status',
            'infraction_datetime',
            'offender_name',
            'offender_document',
            'state'
        ]
        chunk_df.dropna(subset=required_columns, inplace=True)

        if chunk_df.empty:
            logger.info("Nenhuma nova infração para inserir neste lote.")
            return []

        chunk_df['fine_value'] = pd.to_numeric(
            chunk_df['fine_value'].str.replace(',', '.', regex=False),
            errors='coerce'
        ).fillna(0.0)

        chunk_df['infraction_datetime'] = pd.to_datetime(chunk_df['infraction_datetime'], errors='coerce')
        chunk_df['last_updated_date'] = pd.to_datetime(chunk_df['last_updated_date'], errors='coerce')

        text_columns_to_clean = [
            'offender_name',
            'description',
            'infraction_type_description',
            'municipality',
            'location_description',
            'affected_biomes',
        ]
        def safe_unidecode(text: str | None) -> str | None:
            if pd.isna(text):
                return None
            return unidecode(str(text), 'utf-8', errors='ignore')

        logger.info(f"Normalizando {len(text_columns_to_clean)} colunas de texto com unidecode...")
        for col in text_columns_to_clean:
            if col in chunk_df.columns:
                chunk_df[col] = chunk_df[col].apply(safe_unidecode)

        chunk_df.drop_duplicates(subset=['infraction_number'], keep='last', inplace=True)
        processed_chunk = chunk_df.replace({np.nan: None, pd.NaT: None})

        logger.info(f"Chunk processado com {len(processed_chunk)} linhas válidas para inserção/atualização.")
        return processed_chunk.to_dict(orient='records')

    async def process_csv(
        self, 
        file_path: str
    ) -> None:
        logger.info(f"Iniciando o processamento do arquivo: {file_path}")

        async with AsyncSessionLocal() as db_session:
            try:
                column_mapping = {
                    'SEQ_AUTO_INFRACAO': 'source_id',
                    'NUM_AUTO_INFRACAO': 'infraction_number',
                    'NU_PROCESSO_FORMATADO': 'process_number',
                    'DES_STATUS_FORMULARIO': 'status',
                    'TIPO_AUTO': 'sanction_type',
                    'GRAVIDADE_INFRACAO': 'gravity',
                    'VAL_AUTO_INFRACAO': 'fine_value',
                    'DAT_HORA_AUTO_INFRACAO': 'infraction_datetime',
                    'DT_FATO_INFRACIONAL': 'fact_date',
                    'DT_LANCAMENTO': 'system_launch_date',
                    'DT_ULT_ALTERACAO': 'last_updated_date',
                    'NOME_INFRATOR': 'offender_name',
                    'CPF_CNPJ_INFRATOR': 'offender_document',
                    'DES_AUTO_INFRACAO': 'description',
                    'DES_INFRACAO': 'infraction_type_description',
                    'MUNICIPIO': 'municipality',
                    'UF': 'state',
                    'DES_LOCAL_INFRACAO': 'location_description',
                    'NUM_LONGITUDE_AUTO': 'longitude',
                    'NUM_LATITUDE_AUTO': 'latitude',
                    'DS_BIOMAS_ATINGIDOS': 'affected_biomes',
                }
                
                chunk_size = 5000
                total_rows_affected = 0
         
                with pd.read_csv(
                    file_path, 
                    chunksize=chunk_size, 
                    low_memory=False, 
                    usecols=list(column_mapping.keys()),
                    delimiter=";",
                    encoding="latin-1"
                ) as df:
                    for chunk_df in df:

                        data_to_insert = await asyncio.to_thread(
                            self.process_chunk, 
                            chunk_df, 
                            column_mapping
                        )
                        if not data_to_insert:
                            continue

                        stmt_base = insert(Infraction.__table__) # type: ignore
                        stmt_upsert = stmt_base.on_duplicate_key_update(
                            source_id=stmt_base.inserted.source_id,
                            process_number=stmt_base.inserted.process_number,
                            status=stmt_base.inserted.status,
                            sanction_type=stmt_base.inserted.sanction_type,
                            gravity=stmt_base.inserted.gravity,
                            fine_value=stmt_base.inserted.fine_value,
                            infraction_datetime=stmt_base.inserted.infraction_datetime,
                            fact_date=stmt_base.inserted.fact_date,
                            system_launch_date=stmt_base.inserted.system_launch_date,
                            last_updated_date=stmt_base.inserted.last_updated_date,
                            offender_name=stmt_base.inserted.offender_name,
                            offender_document=stmt_base.inserted.offender_document,
                            description=stmt_base.inserted.description,
                            infraction_type_description=stmt_base.inserted.infraction_type_description,
                            municipality=stmt_base.inserted.municipality,
                            state=stmt_base.inserted.state,
                            location_description=stmt_base.inserted.location_description,
                            longitude=stmt_base.inserted.longitude,
                            latitude=stmt_base.inserted.latitude,
                            affected_biomes=stmt_base.inserted.affected_biomes
                        )

                        result = await db_session.execute(stmt_upsert, data_to_insert)
                        
                        total_rows_affected += result.rowcount
                        logger.info(f"Lote processado. Total de linhas afetadas (inseridas/atualizadas) até agora: {total_rows_affected}")
                        
                    await db_session.commit()
                    logger.info(f"Commit finalizado com sucesso para o arquivo '{os.path.basename(file_path)}'.")
                
            except Exception as e:
                logger.error(f"Erro durante o processamento do CSV: {e}")
                await db_session.rollback()
            finally:
                if os.path.exists(file_path):
                    await aiofiles.os.remove(file_path)
                    logger.info(f"Arquivo temporário '{file_path}' removido.")

                logger.info("Processamento do arquivo finalizado.")
        