import logging
from app.db.session import SessionLocal
import pandas as pd
from sqlalchemy import insert
from app.models.infraction import Infraction
import os
import numpy as np


logger = logging.getLogger(__name__)

class IngestionService:

    def process_csv(self, file_path: str) -> None:
        logger.info(f"Iniciando o processamento do arquivo: {file_path}")

        with SessionLocal() as db_session:
            try:
                column_mapping = {
                    'SEQ_AUTO_INFRACAO': 'id',
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
                total_rows_inserted = 0
         
                with pd.read_csv(
                    file_path, 
                    chunksize=chunk_size, 
                    low_memory=False, 
                    usecols=list(column_mapping.keys()),
                    delimiter=";",
                    encoding="latin-1"
                ) as df:
                    for chunk_df in df:            
                        chunk_df.rename(columns=column_mapping, inplace=True)

                        required_columns = [
                            'infraction_number',
                            'status',
                            'infraction_datetime',
                            'offender_name',
                            'offender_document',
                            'state'
                        ]
                        chunk_df.dropna(subset=required_columns, inplace=True)

                        if chunk_df.empty:
                            logger.info("Nenhuma nova infração para inserir neste lote.")
                            continue

                        chunk_df['fine_value'] = pd.to_numeric(
                            chunk_df['fine_value'].str.replace(',', '.', regex=False),
                            errors='coerce'
                        )

                        chunk_df['infraction_datetime'] = pd.to_datetime(chunk_df['infraction_datetime'], errors='coerce')
                        chunk_df['last_updated_date'] = pd.to_datetime(chunk_df['last_updated_date'], errors='coerce')

                        processed_chunk = chunk_df.replace({np.nan: None, pd.NaT: None})

                        data_to_insert = processed_chunk.to_dict(orient='records')
                        if not data_to_insert:
                            continue

                        stmt = insert(Infraction).values(data_to_insert)

                        stmt = stmt.prefix_with("IGNORE")

                        db_session.execute(stmt)
                        
                        total_rows_inserted += len(data_to_insert)
                        logger.info(f"Total de linhas processadas: {total_rows_inserted}")
                        
                    db_session.commit()
                    logger.info(f"Commit finalizado com sucesso para o arquivo '{os.path.basename(file_path)}'.")
                
            except Exception as e:
                logger.error(f"Erro durante o processamento do CSV: {e}")
                db_session.rollback()
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Arquivo temporário '{file_path}' removido.")

                logger.info("Processamento do arquivo finalizado.")
        