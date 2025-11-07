import logging
import logging.handlers
import os


def setup_logging():
    """Настройка системы логирования"""
    # Создаем папку для логов
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Основной логгер
    logger = logging.getLogger("valutatrade")
    logger.setLevel(logging.INFO)
    
    # Форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Файловый обработчик с ротацией
    file_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, "actions.log"),
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Добавляем обработчики
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Создаем логгер при импорте
logger = setup_logging()