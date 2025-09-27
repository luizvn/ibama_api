import logging
from sqlalchemy.orm import Session
from fastapi import UploadFile
import pandas as pd
from sqlalchemy import insert
from app.models.infraction import Infraction


logger = logging.getLogger(__name__)

class IngestionService:

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def process_csv(self, file: UploadFile):
        logger.info(f"Iniciando o processamento do arquivo: {file.filename}")

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
        
        chunk_size = 10000
        total_rows_inserted = 0

        try:          
            df = pd.read_csv(file.file, chunksize=chunk_size, low_memory=False, usecols=list(column_mapping.keys()))

            for chunk_df in df:            
                chunk_df.rename(columns=column_mapping, inplace=True)
                data_to_insert = chunk_df.to_dict(orient='records')
                
                if not data_to_insert:
                    continue

                self.db_session.execute(insert(Infraction), data_to_insert)
                self.db_session.commit()
                
                total_rows_inserted += len(data_to_insert)
                logger.info(f"Lote inserido. Total de linhas processadas: {total_rows_inserted}")
        
        except Exception as e:
            logger.error(f"Erro durante o processamento do CSV: {e}")
            self.db_session.rollback()
        finally:
            file.file.close()
            logger.info("Processamento do arquivo finalizado.")