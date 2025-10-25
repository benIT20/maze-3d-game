"""
Главное меню игры Лабиринт 3D.

Содержит интерфейс пользователя, навигацию по меню и управление экранами.
"""

import pygame
import sys
from game import run_game
from statistics import add_statistic, get_sorted_statistics, clear_statistics
from logger import (
    log_error, log_info, log_warning, log_screen_transition,
    log_statistics_viewed, log_statistics_loaded, log_statistics_cleared
)

# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Лабиринт - Главное меню")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Шрифты
title_font = pygame.font.Font(None, 64)
menu_font = pygame.font.Font(None, 36)
input_font = pygame.font.Font(None, 32)
stats_font = pygame.font.Font(None, 24)
small_font = pygame.font.Font(None, 20)


def load_background():
    """Загружает фоновое изображение для меню."""
    try:
        background = pygame.image.load('maze.jpg')
        # Масштабируем изображение под размер окна
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        log_info("Фоновое изображение успешно загружено")
        return background
    except (pygame.error, FileNotFoundError) as e:
        log_error("Ошибка загрузки фонового изображения", e)
        log_info("Будет использован черный фон")
        return None


def create_overlay_surface():
    """Создает полупрозрачную поверхность для улучшения читаемости текста."""
    try:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Черный с прозрачностью
        return overlay
    except Exception as e:
        log_error("Ошибка создания overlay поверхности", e)
        return None


def update_button_colors(buttons, mouse_pos):
    """Обновляет цвета кнопок при наведении мыши."""
    try:
        for button in buttons:
            button.current_color = (
                button.hover_color if button.is_hovered(mouse_pos)
                else button.color
            )
    except Exception as e:
        log_error("Ошибка при обновлении цветов кнопок", e)


class InputBox:
    """Класс для поля ввода текста."""

    def __init__(self, x, y, w, h, text=''):
        """Инициализирует поле ввода."""
        try:
            self.rect = pygame.Rect(x, y, w, h)
            self.color = GRAY
            self.text = text
            self.txt_surface = input_font.render(text, True, WHITE)
            self.active = False
        except Exception as e:
            log_error("Ошибка инициализации InputBox", e)

    def handle_event(self, event):
        """Обрабатывает события поля ввода."""
        try:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.active = self.rect.collidepoint(event.pos)
                self.color = BLUE if self.active else GRAY
            if event.type == pygame.KEYDOWN:
                if self.active:
                    if event.key == pygame.K_RETURN:
                        return True
                    elif event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                    else:
                        self.text += event.unicode
                    self.txt_surface = input_font.render(self.text, True,
                                                         WHITE)
            return False
        except Exception as e:
            log_error("Ошибка обработки события InputBox", e)
            return False

    def draw(self, screen):
        """Отрисовывает поле ввода на экране."""
        try:
            screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
            pygame.draw.rect(screen, self.color, self.rect, 2)
        except Exception as e:
            log_error("Ошибка отрисовки InputBox", e)


class Button:
    """Класс для кнопок интерфейса."""

    def __init__(self, x, y, w, h, text, color=GRAY, hover_color=LIGHT_GRAY,
                 text_color=WHITE):
        """Инициализирует кнопку."""
        try:
            self.rect = pygame.Rect(x, y, w, h)
            self.text = text
            self.color = color
            self.hover_color = hover_color
            self.text_color = text_color
            self.current_color = color
        except Exception as e:
            log_error("Ошибка инициализации Button", e)

    def draw(self, screen):
        """Отрисовывает кнопку на экране."""
        try:
            pygame.draw.rect(screen, self.current_color, self.rect)
            pygame.draw.rect(screen, WHITE, self.rect, 2)
            text_surf = menu_font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)
        except Exception as e:
            log_error("Ошибка отрисовки Button", e)

    def is_hovered(self, pos):
        """Проверяет, находится ли курсор над кнопкой."""
        try:
            return self.rect.collidepoint(pos)
        except Exception as e:
            log_error("Ошибка проверки hover кнопки", e)
            return False

    def is_clicked(self, event):
        """Проверяет, была ли нажата кнопка."""
        try:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return self.rect.collidepoint(event.pos)
            return False
        except Exception as e:
            log_error("Ошибка проверки клика кнопки", e)
            return False


def draw_main_menu(background, overlay, input_box, play_button, stats_button,
                   clear_button, exit_button, mouse_pos):
    """Отрисовывает главное меню."""
    try:
        # Отрисовка фона
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill(BLACK)

        # Отрисовка полупрозрачного overlay для читаемости
        if overlay:
            screen.blit(overlay, (0, 0))

        # Заголовок
        title_text = title_font.render("ЛАБИРИНТ", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH//2, 80))
        screen.blit(title_text, title_rect)

        # Поле ввода имени
        name_label = menu_font.render("Введите имя:", True, WHITE)
        screen.blit(name_label, (WIDTH//2 - 150, 150))
        input_box.draw(screen)

        # Обновляем цвета кнопок
        update_button_colors(
            [play_button, stats_button, clear_button, exit_button], mouse_pos
        )

        # Отрисовываем кнопки
        play_button.draw(screen)
        stats_button.draw(screen)
        clear_button.draw(screen)
        exit_button.draw(screen)
    except Exception as e:
        log_error("Ошибка отрисовки главного меню", e)


def draw_difficulty_menu(background, overlay, back_button, easy_button,
                         medium_button, hard_button, mouse_pos):
    """Отрисовывает меню выбора сложности."""
    try:
        # Отрисовка фона
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill(BLACK)

        # Отрисовка полупрозрачного overlay
        if overlay:
            screen.blit(overlay, (0, 0))

        # Заголовок
        title_text = title_font.render("ВЫБЕРИТЕ СЛОЖНОСТЬ", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH//2, 80))
        screen.blit(title_text, title_rect)

        # Описания сложностей
        easy_desc = [
            "ЛЕГКАЯ:",
            "- Маленький лабиринт 15x15",
            "- Есть мини-карта",
            "- Высокая скорость движения",
            "- Быстрое прохождение"
        ]

        medium_desc = [
            "СРЕДНЯЯ:",
            "- Средний лабиринт 21x21",
            "- Есть мини-карта",
            "- Стандартная скорость",
            "- Нормальная сложность"
        ]

        hard_desc = [
            "СЛОЖНАЯ:",
            "- Большой лабиринт 25x25",
            "- Нет мини-карты",
            "- Медленная скорость",
            "- Сложная навигация"
        ]

        # Отображение описаний
        y_pos = 150
        for line in easy_desc:
            text = small_font.render(line, True, GREEN)
            screen.blit(text, (WIDTH//4 - 120, y_pos))
            y_pos += 30

        y_pos = 150
        for line in medium_desc:
            text = small_font.render(line, True, YELLOW)
            screen.blit(text, (WIDTH//2 - 120, y_pos))
            y_pos += 30

        y_pos = 150
        for line in hard_desc:
            text = small_font.render(line, True, RED)
            screen.blit(text, (3*WIDTH//4 - 120, y_pos))
            y_pos += 30

        # Обновляем цвета кнопок
        update_button_colors(
            [back_button, easy_button, medium_button, hard_button], mouse_pos
        )

        # Отрисовываем кнопки
        back_button.draw(screen)
        easy_button.draw(screen)
        medium_button.draw(screen)
        hard_button.draw(screen)
    except Exception as e:
        log_error("Ошибка отрисовки меню сложности", e)


def draw_statistics_menu(background, overlay, back_button, mouse_pos,
                         statistics=None):
    """Отрисовывает экран статистики."""
    try:
        # Отрисовка фона
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill(BLACK)

        # Отрисовка полупрозрачного overlay
        if overlay:
            screen.blit(overlay, (0, 0))

        # Заголовок
        title_text = title_font.render("СТАТИСТИКА", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH//2, 50))
        screen.blit(title_text, title_rect)

        # Заголовки таблицы
        headers = ["№", "Игрок", "Сложность", "Время", "Дата"]
        x_positions = [50, 120, 220, 350, 480]

        for i, header in enumerate(headers):
            text = stats_font.render(header, True, YELLOW)
            screen.blit(text, (x_positions[i], 100))

        # Используем переданную статистику или загружаем заново
        if statistics is None:
            statistics = get_sorted_statistics()

        if not statistics:
            no_data = menu_font.render(
                "Нет данных о прохождениях", True, GRAY
            )
            screen.blit(no_data, (WIDTH//2 - 180, 200))
        else:
            # Показываем топ-15 результатов
            for i, stat in enumerate(statistics[:15]):
                y_pos = 130 + i * 25

                # Цвет в зависимости от сложности
                if stat['difficulty'] == "Сложная":
                    color = RED
                elif stat['difficulty'] == "Средняя":
                    color = YELLOW
                else:
                    color = GREEN

                # Номер
                num_text = stats_font.render(str(i+1), True, WHITE)
                screen.blit(num_text, (x_positions[0], y_pos))

                # Игрок (обрезаем если слишком длинный)
                player_name = (
                    stat['player'][:12] + "..."
                    if len(stat['player']) > 12
                    else stat['player']
                )
                player_text = stats_font.render(player_name, True, WHITE)
                screen.blit(player_text, (x_positions[1], y_pos))

                # Сложность
                diff_text = stats_font.render(stat['difficulty'], True, color)
                screen.blit(diff_text, (x_positions[2], y_pos))

                # Время
                time_text = stats_font.render(f"{stat['time']:.2f}с", True,
                                              WHITE)
                screen.blit(time_text, (x_positions[3], y_pos))

                # Дата (только дата, без времени)
                date_only = stat['date'].split(' ')[0]
                date_text = stats_font.render(date_only, True, WHITE)
                screen.blit(date_text, (x_positions[4], y_pos))

            # Общая информация
            total_text = small_font.render(
                f"Всего записей: {len(statistics)}", True, GRAY
            )
            screen.blit(total_text, (50, HEIGHT - 60))

        # Обновляем цвет кнопки назад
        update_button_colors([back_button], mouse_pos)
        back_button.draw(screen)
    except Exception as e:
        log_error("Ошибка отрисовки экрана статистики", e)


def draw_clear_confirmation(background, overlay, back_button, confirm_button,
                            cancel_button, mouse_pos):
    """Отрисовывает экран подтверждения очистки статистики."""
    try:
        # Отрисовка фона
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill(BLACK)

        # Отрисовка полупрозрачного overlay
        if overlay:
            screen.blit(overlay, (0, 0))

        # Заголовок
        title_text = title_font.render("ОЧИСТКА СТАТИСТИКИ", True, RED)
        title_rect = title_text.get_rect(center=(WIDTH//2, 150))
        screen.blit(title_text, title_rect)

        # Предупреждение
        warning_text = menu_font.render(
            "Вы уверены, что хотите удалить всю статистику?", True, WHITE
        )
        warning_rect = warning_text.get_rect(center=(WIDTH//2, 250))
        screen.blit(warning_text, warning_rect)

        # Обновляем цвета кнопок
        update_button_colors(
            [back_button, confirm_button, cancel_button], mouse_pos
        )

        # Отрисовываем кнопки
        back_button.draw(screen)
        confirm_button.draw(screen)
        cancel_button.draw(screen)
    except Exception as e:
        log_error("Ошибка отрисовки экрана подтверждения очистки", e)


def main():
    """Главная функция, запускающая приложение."""
    try:
        log_info("Запуск главного меню")

        # Загрузка фона и создание overlay
        background = load_background()
        overlay = create_overlay_surface()

        # Создание элементов интерфейса
        input_box = InputBox(WIDTH//2 - 100, 200, 200, 40)

        # Кнопки главного меню
        play_button = Button(WIDTH//2 - 100, 260, 200, 50, "ИГРАТЬ", GREEN)
        stats_button = Button(WIDTH//2 - 100, 330, 200, 50, "СТАТИСТИКА", BLUE)
        clear_button = Button(
            WIDTH//2 - 100, 400, 200, 50, "ОЧИСТИТЬ СТАТИСТИКУ", (150, 0, 0)
        )
        exit_button = Button(
            WIDTH//2 - 100, 470, 200, 50, "ВЫХОД", (100, 100, 100)
        )

        # Кнопки меню сложности
        back_button = Button(WIDTH//2 - 100, 500, 200, 50, "НАЗАД")
        easy_button = Button(WIDTH//4 - 75, 350, 150, 50, "ЛЕГКО", GREEN)
        medium_button = Button(
            WIDTH//2 - 75, 350, 150, 50, "СРЕДНЕ", YELLOW, text_color=BLACK
        )
        hard_button = Button(3*WIDTH//4 - 75, 350, 150, 50, "СЛОЖНО", RED)

        # Кнопки подтверждения очистки
        confirm_button = Button(
            WIDTH//2 - 220, 350, 200, 50, "ДА, ОЧИСТИТЬ", color=(200, 0, 0)
        )
        cancel_button = Button(WIDTH//2 + 20, 350, 200, 50, "ОТМЕНА")

        # Состояния меню "main", "difficulty", "statistics", "clear_confirm"
        current_screen = "main"
        player_name = ""
        statistics_data = None  # Кэш для статистики

        clock = pygame.time.Clock()

        while True:
            try:
                mouse_pos = pygame.mouse.get_pos()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        log_info("Выход из приложения")
                        pygame.quit()
                        sys.exit()

                    if current_screen == "main":
                        if input_box.handle_event(event):
                            player_name = input_box.text

                        if play_button.is_clicked(event):
                            if input_box.text.strip():
                                player_name = input_box.text.strip()
                                current_screen = "difficulty"
                                log_screen_transition(
                                    "main", "difficulty",
                                    f"Игрок: {player_name}"
                                )
                            else:
                                log_warning(
                                    "Попытка начать игру без имени игрока"
                                )

                        if stats_button.is_clicked(event):
                            current_screen = "statistics"
                            log_screen_transition("main", "statistics")
                            log_statistics_viewed()
                            # Загружаем статистику один раз при переходе
                            statistics_data = get_sorted_statistics()
                            log_statistics_loaded(len(statistics_data))

                        if clear_button.is_clicked(event):
                            current_screen = "clear_confirm"
                            log_screen_transition("main",
                                                  "clear_confirmation")

                        if exit_button.is_clicked(event):
                            log_info("Выход из приложения по кнопке")
                            pygame.quit()
                            sys.exit()

                    elif current_screen == "difficulty":
                        if back_button.is_clicked(event):
                            current_screen = "main"
                            log_screen_transition("difficulty", "main")

                        if easy_button.is_clicked(event):
                            log_info(
                                f"Запуск игры: {player_name}, "
                                f"сложность: Легкая"
                            )
                            completion_time = run_game("easy", player_name)
                            if completion_time > 0:
                                add_statistic(player_name, completion_time,
                                              "Легкая")
                                log_info(
                                    f"Статистика сохранена: {player_name}, "
                                    f"Легкая, {completion_time:.2f}с"
                                )
                            current_screen = "main"
                            log_screen_transition("difficulty", "main",
                                                  "после игры")

                        if medium_button.is_clicked(event):
                            log_info(
                                f"Запуск игры: {player_name}, "
                                f"сложность: Средняя"
                            )
                            completion_time = run_game("medium", player_name)
                            if completion_time > 0:
                                add_statistic(player_name, completion_time,
                                              "Средняя")
                                log_info(
                                    f"Статистика сохранена: {player_name}, "
                                    f"Средняя, {completion_time:.2f}с"
                                )
                            current_screen = "main"
                            log_screen_transition("difficulty", "main",
                                                  "после игры")

                        if hard_button.is_clicked(event):
                            log_info(
                                f"Запуск игры: {player_name}, "
                                f"сложность: Сложная"
                            )
                            completion_time = run_game("hard", player_name)
                            if completion_time > 0:
                                add_statistic(player_name, completion_time,
                                              "Сложная")
                                log_info(
                                    f"Статистика сохранена: {player_name}, "
                                    f"Сложная, {completion_time:.2f}с"
                                )
                            current_screen = "main"
                            log_screen_transition("difficulty", "main",
                                                  "после игры")

                    elif current_screen == "statistics":
                        if back_button.is_clicked(event):
                            current_screen = "main"
                            log_screen_transition("statistics", "main")

                    elif current_screen == "clear_confirm":
                        if back_button.is_clicked(event):
                            current_screen = "main"
                            log_screen_transition("clear_confirmation", "main")

                        if confirm_button.is_clicked(event):
                            if clear_statistics():
                                log_statistics_cleared()
                                statistics_data = []  # Очищаем кэш
                            else:
                                log_error("Не удалось очистить статистику")
                            current_screen = "main"
                            log_screen_transition("clear_confirmation", "main")

                        if cancel_button.is_clicked(event):
                            current_screen = "main"
                            log_screen_transition("clear_confirmation",
                                                  "main", "отмена")

                # Отрисовка текущего экрана
                if current_screen == "main":
                    draw_main_menu(
                        background, overlay, input_box, play_button,
                        stats_button, clear_button, exit_button, mouse_pos
                    )
                elif current_screen == "difficulty":
                    draw_difficulty_menu(
                        background, overlay, back_button, easy_button,
                        medium_button, hard_button, mouse_pos
                    )
                elif current_screen == "statistics":
                    draw_statistics_menu(
                        background, overlay, back_button, mouse_pos,
                        statistics_data
                    )
                elif current_screen == "clear_confirm":
                    draw_clear_confirmation(
                        background, overlay, back_button,
                        confirm_button, cancel_button, mouse_pos
                    )

                pygame.display.flip()
                clock.tick(60)

            except Exception as e:
                log_error("Ошибка в основном цикле меню", e)

    except Exception as e:
        log_error("Критическая ошибка в главной функции", e)
    finally:
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()
