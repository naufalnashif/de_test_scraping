import logging
import sys
from pathlib import Path
from typing import Optional
import colorlog

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = "app.log",
    log_dir: str = "logs"
) -> None:
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    logger.handlers.clear()

    # Format Console: Lebih minimalis dan rapi
    # [INFO] 10:30:00 | Pesan Anda
    console_format = colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(asctime)s%(reset)s | %(message)s',
        datefmt='%H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    )

    console_handler = colorlog.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_path / log_file, encoding='utf-8')
        # Format File: Lebih teknis untuk debugging
        file_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

class LoggerMixin:
    @property
    def logger(self):
        # Mengambil nama class agar log tahu pesan datang dari mana
        return get_logger(self.__class__.__name__)

if __name__ == "__main__":
    setup_logging()
    logger = get_logger(__name__)