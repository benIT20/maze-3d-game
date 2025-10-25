"""
Модуль логирования для игры Лабиринт 3D.

Обеспечивает централизованное логирование ошибок и событий.
"""

import logging
import os
from datetime import datetime

# Создаем папку для логов если ее нет
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


# Настройка логирования
def setup_logger():
    """Настраивает и возвращает логгер."""
    logger = logging.getLogger('maze_game')
    logger.setLevel(logging.DEBUG)

    # Форматтер для логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Файловый обработчик
    log_filename = datetime.now().strftime("maze_game_%Y%m%d_%H%M%S.log")
    log_path = os.path.join(LOG_DIR, log_filename)

    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Добавляем обработчики к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Создаем глобальный логгер
logger = setup_logger()


def log_error(error_message, exception=None):
    """Логирует ошибку с дополнительной информацией об исключении."""
    if exception:
        logger.error(f"{error_message}: {str(exception)}", exc_info=True)
    else:
        logger.error(error_message)


def log_info(info_message):
    """Логирует информационное сообщение."""
    logger.info(info_message)


def log_debug(debug_message):
    """Логирует отладочное сообщение."""
    logger.debug(debug_message)


def log_warning(warning_message):
    """Логирует предупреждение."""
    logger.warning(warning_message)


def log_game_start(player_name, difficulty):
    """Логирует начало игры."""
    logger.info(f"Начало игры - Игрок: {player_name}, Сложность: {difficulty}")


def log_game_completion(player_name, difficulty, completion_time):
    """Логирует завершение игры."""
    logger.info(
        f"Завершение игры - Игрок: {player_name}, "
        f"Сложность: {difficulty}, Время: {completion_time:.2f}с"
    )


def log_game_aborted(player_name, difficulty):
    """Логирует прерывание игры."""
    logger.info(
        f"Игра прервана - Игрок: {player_name}, "
        f"Сложность: {difficulty}"
    )


def log_screen_transition(from_screen, to_screen, additional_info=""):
    """Логирует переход между экранами."""
    message = f"Переход экрана: {from_screen} -> {to_screen}"
    if additional_info:
        message += f" ({additional_info})"
    logger.info(message)


def log_statistics_viewed():
    """Логирует просмотр статистики."""
    logger.info("Просмотр статистики")


def log_statistics_loaded(record_count):
    """Логирует загрузку статистики."""
    logger.info(f"Статистика загружена: {record_count} записей")


def log_statistics_cleared():
    """Логирует очистку статистики."""
    logger.info("Статистика очищена")
