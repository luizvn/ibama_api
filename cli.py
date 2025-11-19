import typer
import asyncio
import httpx
import logging
import sys
from typing import Optional, List
import aiofiles.os as aio_os
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

try:
    from app.core.logging_config import setup_logging
    from app.services.crawler_service import CrawlerService
    from app.services.ingestion_service import IngestionService
except ImportError as e:
    print(
        "Erro Crítico: Não foi possível importar os módulos da 'app'.", file=sys.stderr
    )
    print(f"Detalhe: {e}", file=sys.stderr)
    sys.exit(1)

setup_logging()
logger = logging.getLogger(__name__)

app = typer.Typer()


async def run_etl_pipeline():
    logger.info("--- INICIANDO PIPELINE DE ETL DO IBAMA ---")

    csv_path_list: Optional[List[str]] = None

    try:
        async with httpx.AsyncClient() as client:
            logger.info("Instanciando CrawlerService...")
            crawler = CrawlerService(client=client)

            logger.info("Executando Crawler: fetch_and_extract_all_csvs()...")
            csv_path_list = await crawler.fetch_and_extract_all_csvs()

        if not csv_path_list:
            logger.error("Crawler falhou ou não retornou arquivos. Encerrando.")
            return

        logger.info(
            f"Crawler concluído. {len(csv_path_list)} arquivos prontos para ingestão."
        )

        ingestion_service = IngestionService()

        files_processed = 0
        files_failed = 0

        for csv_path in csv_path_list:
            try:
                logger.info(f"[Ingestion] Processando arquivo: {csv_path}...")

                await ingestion_service.process_csv(csv_path)

                logger.info(f"[Ingestion] Arquivo {csv_path} processado com sucesso.")
                files_processed += 1

            except Exception as e:
                logger.error(
                    f"[Ingestion] FALHA ao processar o arquivo {csv_path}: {e}",
                    exc_info=True,
                )
                files_failed += 1

        logger.info("--- PIPELINE DE ETL CONCLUÍDO ---")
        logger.info(
            f"Resumo: {files_processed} arquivos processados, {files_failed} falharam."
        )

    except Exception as e:
        logger.error(f"Erro fatal no orquestrador do pipeline: {e}", exc_info=True)

    finally:
        if csv_path_list:
            logger.info("Verificando limpeza de arquivos...")
            remaining_files = []
            for path in csv_path_list:
                if await aio_os.path.exists(path):
                    logger.info(f"Limpando arquivo órfão: {path}")
                    await aio_os.remove(path)
                    remaining_files.append(path)
            if not remaining_files:
                logger.info("Limpeza final concluída. Nenhum arquivo órfão encontrado.")

        logger.info("--- FIM DA EXECUÇÃO ---")


@app.command()
def run():
    logger.info("Typer: Recebido comando 'run'. Iniciando loop asyncio...")
    asyncio.run(run_etl_pipeline())


if __name__ == "__main__":
    app()
