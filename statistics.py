"""
Модуль статистики игры Лабиринт 3D.

Обеспечивает сохранение, загрузку и отображение результатов игроков.
"""

import json
import os
import datetime
from logger import log_error, log_info, log_warning

STATS_FILE = "game_statistics.json"

# Порядок сложностей для сортировки (от самой сложной к самой легкой)
DIFFICULTY_ORDER = {"Сложная": 3, "Средняя": 2, "Легкая": 1}


def load_statistics():
    """Загружает статистику из файла."""
    try:
        if not os.path.exists(STATS_FILE):
            log_info("Файл статистики не найден, создается новый")
            return []

        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            statistics = json.load(f)
            log_info(f"Статистика загружена: {len(statistics)} записей")
            return statistics

    except (json.JSONDecodeError, FileNotFoundError) as e:
        log_error("Ошибка загрузки статистики", e)
        return []
    except Exception as e:
        log_error("Неожиданная ошибка при загрузке статистики", e)
        return []


def save_statistics(statistics):
    """Сохраняет статистику в файл."""
    try:
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(statistics, f, ensure_ascii=False, indent=2)
        log_info(f"Статистика сохранена: {len(statistics)} записей")
        return True
    except Exception as e:
        log_error("Ошибка сохранения статистики", e)
        return False


def add_statistic(player_name, completion_time, difficulty):
    """Добавляет запись в статистику и сохраняет в файл."""
    try:
        statistics = load_statistics()

        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        new_record = {
            'player': player_name,
            'date': current_date,
            'time': completion_time,
            'difficulty': difficulty
        }

        statistics.append(new_record)

        if save_statistics(statistics):
            log_info(
                f"Добавлена запись: {player_name}, {difficulty}, "
                f"{completion_time:.2f}с"
            )
            return True
        else:
            log_error("Не удалось сохранить статистику")
            return False

    except Exception as e:
        log_error("Ошибка добавления записи в статистику", e)
        return False


def get_sorted_statistics():
    """Возвращает отсортированную статистику."""
    try:
        statistics = load_statistics()

        # Сортируем сначала по сложности (сложная -> средняя -> легкая),
        # затем по времени
        sorted_stats = sorted(
            statistics,
            key=lambda x: (-DIFFICULTY_ORDER.get(x['difficulty'], 0),
                           x['time'])
        )

        log_info(f"Статистика отсортирована: {len(sorted_stats)} записей")
        return sorted_stats

    except Exception as e:
        log_error("Ошибка сортировки статистики", e)
        return []


def clear_statistics():
    """Очищает всю статистику."""
    try:
        if os.path.exists(STATS_FILE):
            os.remove(STATS_FILE)
            log_info("Статистика полностью очищена")
            return True
        else:
            log_warning("Попытка очистки несуществующего файла статистики")
            return True
    except Exception as e:
        log_error("Ошибка очистки статистики", e)
        return False


def get_player_statistics(player_name):
    """Возвращает статистику конкретного игрока."""
    try:
        statistics = load_statistics()
        player_stats = [
            stat for stat in statistics if stat['player'] == player_name
        ]

        # Сортируем по сложности и времени
        sorted_stats = sorted(
            player_stats,
            key=lambda x: (-DIFFICULTY_ORDER.get(x['difficulty'], 0),
                           x['time'])
        )

        log_info(
            f"Загружена статистика игрока {player_name}: "
            f"{len(sorted_stats)} записей"
        )
        return sorted_stats

    except Exception as e:
        log_error(f"Ошибка загрузки статистики игрока {player_name}", e)
        return []


def get_difficulty_statistics(difficulty):
    """Возвращает статистику по конкретной сложности."""
    try:
        statistics = load_statistics()
        diff_stats = [
            stat for stat in statistics if stat['difficulty'] == difficulty
        ]

        # Сортируем по времени
        sorted_stats = sorted(diff_stats, key=lambda x: x['time'])

        log_info(
            f"Загружена статистика сложности {difficulty}: "
            f"{len(sorted_stats)} записей"
        )
        return sorted_stats

    except Exception as e:
        log_error(f"Ошибка загрузки статистики сложности {difficulty}", e)
        return []
