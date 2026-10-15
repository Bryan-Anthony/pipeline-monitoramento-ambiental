
import logging
from pathlib import Path


class Logger:
    @staticmethod
    def configurar():
        # Diretório raiz do projeto
        raiz_projeto = Path(__file__).resolve().parents[2]
        pasta_logs = raiz_projeto / "logs"
        pasta_logs.mkdir(parents=True, exist_ok=True)

        arquivo_log = pasta_logs / "pipeline.log"

        logging.basicConfig(
            level=logging.INFO,
            format=(
                "%(asctime)s | %(levelname)s | "
                "%(name)s | %(message)s"
            ),
            handlers=[
                logging.FileHandler(
                    arquivo_log,
                    encoding="utf-8"
                ),
                logging.StreamHandler()
            ],
            force=True
        )

        return logging.getLogger("pipeline")
