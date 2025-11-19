import httpx
import logging
import zipfile
import tempfile
import os
import shutil
from typing import Optional, List
import asyncio
import aiofiles
import aiofiles.os as aio_os


DATA_URL = "https://dadosabertos.ibama.gov.br/dados/SIFISC/auto_infracao/auto_infracao/auto_infracao_csv.zip"

logger = logging.getLogger(__name__)


class CrawlerService:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    def extract_zip(self, zip_path: str) -> List[str]:
        # initialize here so exception handlers and finally blocks can safely
        # reference the variable without causing "possibly unbound" warnings.
        extracted_csv_paths: List[str] = []
        try:
            logger.info("Iniciando extração dos CSVs do arquivo ZIP...")

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                csv_files_in_zip = [
                    f.filename
                    for f in zip_ref.infolist()
                    if not f.is_dir() and f.filename.lower().endswith(".csv")
                ]

                if not csv_files_in_zip:
                    logger.error("Nenhum arquivo CSV encontrado dentro do ZIP.")
                    return []

                logger.info(
                    f"Encontrados {len(csv_files_in_zip)} arquivos CSV: {csv_files_in_zip}"
                )

                for csv_name in csv_files_in_zip:
                    logger.debug(f"Extraindo arquivo: {csv_name}")

                    with zip_ref.open(csv_name) as extracted_csv_stream:
                        with tempfile.NamedTemporaryFile(
                            suffix=".csv", delete=False
                        ) as temp_csv_file:
                            shutil.copyfileobj(extracted_csv_stream, temp_csv_file)

                            extracted_csv_paths.append(temp_csv_file.name)
                            logger.debug(
                                f"Arquivo {csv_name} extraído para {temp_csv_file.name}"
                            )

            logger.info(
                f"Extração concluída. Total de CSVs prontos: {len(extracted_csv_paths)}"
            )
            return extracted_csv_paths

        except zipfile.BadZipFile:
            logger.error("Erro: O arquivo ZIP está corrompido ou é inválido.")
            return []
        except Exception as e:
            logger.error(f"Erro inesperado durante a extração: {e}")

            for path in extracted_csv_paths:
                if os.path.exists(path):
                    os.remove(path)
            return []

    async def fetch_and_extract_all_csvs(self) -> Optional[List[str]]:
        # ensure this is defined before the try so finally can reference it
        temp_zip_file_path: Optional[str] = None

        try:
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=True) as temp_file:
                temp_zip_file_path = temp_file.name

            logger.info(f"Iniciando pipeline de crawler para: {DATA_URL}")

            async with aiofiles.open(temp_zip_file_path, "wb") as temp_zip_file:
                logger.info(f"Criado arquivo temporário para ZIP: {temp_zip_file_path}")

                async with self.client.stream(
                    "GET", DATA_URL, follow_redirects=True, timeout=400.0
                ) as response:
                    response.raise_for_status()

                    async for chunk in response.aiter_bytes():
                        await temp_zip_file.write(chunk)

                    await temp_zip_file.flush()

                logger.info(
                    f"Download do ZIP concluído. Bytes: {os.path.getsize(temp_zip_file_path)}"
                )

                extracted_paths = await asyncio.to_thread(
                    self.extract_zip, temp_zip_file_path
                )

                if not extracted_paths:
                    logger.error("Nenhum CSV foi extraído do arquivo ZIP.")
                    return None

                return extracted_paths

        except httpx.RequestError as e:
            logger.error(f"Erro de HTTP (rede/timeout) ao tentar baixar o arquivo: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado no processamento do crawler: {e}")
            return None
        finally:
            if temp_zip_file_path and await aio_os.path.exists(temp_zip_file_path):
                await aio_os.remove(temp_zip_file_path)
                logger.info(f"Arquivo ZIP temporário removido: {temp_zip_file_path}")
