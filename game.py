"""
Модуль игры Лабиринт 3D.

Содержит логику генерации лабиринтов, raycasting рендеринг и игровой процесс.
"""

import pygame
import math
import random
import time
from logger import (
    log_error, log_info, log_game_start,
    log_game_completion, log_game_aborted
)

# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 800, 600

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
BROWN = (139, 69, 19)

# Константы игры
FOV = math.pi / 3
HALF_FOV = FOV / 2
MAX_DEPTH = 20
ROTATION_SPEED = 0.04
MINIMAP_SIZE = 150
WALL_HEIGHT_MULTIPLIER = 5
RAY_STEP_SIZE = 0.02

# Настройки сложности
EASY_CONFIG = {
    'map_size': 15,
    'move_speed': 0.1,
    'show_minimap': True
}

MEDIUM_CONFIG = {
    'map_size': 21,
    'move_speed': 0.08,
    'show_minimap': True
}

HARD_CONFIG = {
    'map_size': 25,
    'move_speed': 0.06,
    'show_minimap': False
}


def generate_maze(size):
    """Генерация случайного лабиринта с помощью алгоритма."""
    try:
        # Создаем сетку, где все клетки - стены
        maze = [[1 for _ in range(size)] for _ in range(size)]

        # Начинаем с центральной точки
        start_x, start_y = size // 2, size // 2
        maze[start_y][start_x] = 0

        # Список frontier клеток (тех, что можно расширять)
        frontiers = []

        # Добавляем соседей начальной точки
        for dx, dy in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
            nx, ny = start_x + dx, start_y + dy
            if 0 <= nx < size and 0 <= ny < size:
                frontiers.append((nx, ny, start_x, start_y))

        while frontiers:
            # Берем случайную frontier клетку
            fx, fy, px, py = frontiers.pop(
                random.randint(0, len(frontiers) - 1)
            )

            if maze[fy][fx] == 1:
                maze[fy][fx] = 0
                maze[(fy + py) // 2][(fx + px) // 2] = 0

                for dx, dy in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
                    nx, ny = fx + dx, fy + dy
                    if (0 <= nx < size and 0 <= ny < size
                            and maze[ny][nx] == 1):
                        frontiers.append((nx, ny, fx, fy))

        # Создаем вход и выход
        maze[1][1] = 0
        maze[size-2][size-2] = 0

        log_info(f"Лабиринт размером {size}x{size} успешно сгенерирован")
        return maze

    except Exception as e:
        log_error("Ошибка при генерации лабиринта", e)
        # Возвращаем простой лабиринт в случае ошибки
        simple_maze = [[0 for _ in range(size)] for _ in range(size)]
        for i in range(size):
            simple_maze[0][i] = 1
            simple_maze[size-1][i] = 1
            simple_maze[i][0] = 1
            simple_maze[i][size-1] = 1
        return simple_maze


def run_game(difficulty, player_name):
    """Запускает игру с заданной сложностью и возвращает время прохождения."""
    try:
        # Настройки в зависимости от сложности
        if difficulty == "easy":
            config = EASY_CONFIG
        elif difficulty == "medium":
            config = MEDIUM_CONFIG
        else:  # hard
            config = HARD_CONFIG

        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(
            f"Лабиринт - {player_name} - {difficulty}"
        )

        log_game_start(player_name, difficulty)

        # Генерация лабиринта
        maze = generate_maze(config['map_size'])
        exit_x, exit_y = config['map_size'] - 2, config['map_size'] - 2

        # Настройки игрока
        player_x, player_y = 1.5, 1.5
        player_angle = 0

        # Таймер
        start_time = time.time()
        completion_time = 0

        def cast_ray(angle):
            """Бросает луч и возвращает расстояние до стены."""
            try:
                ray_x, ray_y = player_x, player_y
                ray_cos = math.cos(angle) * RAY_STEP_SIZE
                ray_sin = math.sin(angle) * RAY_STEP_SIZE

                wall_distance = 0
                wall_hit = False

                while not wall_hit and wall_distance < MAX_DEPTH:
                    ray_x += ray_cos
                    ray_y += ray_sin
                    wall_distance = math.sqrt(
                        (ray_x - player_x)**2 + (ray_y - player_y)**2
                    )

                    map_x, map_y = int(ray_x), int(ray_y)
                    if (0 <= map_x < config['map_size'] and
                            0 <= map_y < config['map_size']):
                        if maze[map_y][map_x] == 1:
                            wall_hit = True
                    else:
                        break

                return wall_distance
            except Exception as e:
                log_error("Ошибка в raycasting", e)
                return MAX_DEPTH

        def draw_3d_view():
            """Отрисовывает 3D вид с помощью raycasting."""
            try:
                screen.fill(BLACK)

                # Рисуем пол и потолок
                pygame.draw.rect(screen, DARK_GRAY, (0, 0, WIDTH, HEIGHT // 2))
                pygame.draw.rect(
                    screen, BROWN, (0, HEIGHT // 2, WIDTH, HEIGHT // 2)
                )

                # Бросаем лучи для каждого столбца экрана
                for column in range(WIDTH):
                    ray_angle = (
                        player_angle - HALF_FOV + (column / WIDTH) * FOV
                    )
                    ray_angle %= 2 * math.pi

                    distance = cast_ray(ray_angle)
                    corrected_distance = distance * math.cos(
                        player_angle - ray_angle
                    )
                    wall_height = min(
                        int(HEIGHT / (corrected_distance + 0.0001)),
                        HEIGHT * WALL_HEIGHT_MULTIPLIER
                    )
                    wall_top = (HEIGHT - wall_height) // 2
                    wall_bottom = wall_top + wall_height

                    color_intensity = min(255, max(50, 255 - distance * 20))

                    if column % 3 == 0:
                        wall_color = (
                            color_intensity,
                            color_intensity // 3,
                            color_intensity // 3
                        )
                    elif column % 3 == 1:
                        wall_color = (
                            color_intensity // 3,
                            color_intensity,
                            color_intensity // 3
                        )
                    else:
                        wall_color = (
                            color_intensity // 3,
                            color_intensity // 3,
                            color_intensity
                        )

                    pygame.draw.line(
                        screen, wall_color, (column, wall_top),
                        (column, wall_bottom), 2
                    )
            except Exception as e:
                log_error("Ошибка при отрисовке 3D вида", e)
                screen.fill(BLACK)
                font = pygame.font.Font(None, 36)
                error_text = font.render("Ошибка отрисовки", True, RED)
                screen.blit(error_text, (WIDTH//2 - 100, HEIGHT//2))

        def draw_minimap():
            """Отрисовывает мини-карту и информацию."""
            if not config['show_minimap']:
                return

            try:
                cell_size = MINIMAP_SIZE // config['map_size']

                # Фон мини-карты
                pygame.draw.rect(
                    screen, (40, 40, 40),
                    (10, 10, MINIMAP_SIZE, MINIMAP_SIZE)
                )

                for y in range(config['map_size']):
                    for x in range(config['map_size']):
                        rect = pygame.Rect(
                            10 + x * cell_size,
                            10 + y * cell_size,
                            cell_size, cell_size
                        )
                        if maze[y][x] == 1:
                            pygame.draw.rect(screen, WHITE, rect)
                        else:
                            pygame.draw.rect(screen, BLACK, rect)
                        pygame.draw.rect(screen, GRAY, rect, 1)

                # Рисуем выход зеленым цветом
                exit_rect = pygame.Rect(
                    10 + exit_x * cell_size,
                    10 + exit_y * cell_size,
                    cell_size, cell_size
                )
                pygame.draw.rect(screen, GREEN, exit_rect)

                # Рисуем игрока
                player_minimap_x = 10 + int(player_x * cell_size)
                player_minimap_y = 10 + int(player_y * cell_size)
                pygame.draw.circle(
                    screen, RED, (player_minimap_x, player_minimap_y), 4
                )

                # Рисуем направление взгляда
                direction_x = (
                    player_minimap_x + math.cos(player_angle) * 15
                )
                direction_y = (
                    player_minimap_y + math.sin(player_angle) * 15
                )
                pygame.draw.line(
                    screen, GREEN,
                    (player_minimap_x, player_minimap_y),
                    (direction_x, direction_y), 2
                )

                # Информация
                font = pygame.font.Font(None, 24)
                info_text = [
                    f"Игрок: {player_name}",
                    f"Сложность: {difficulty}",
                    f"Время: {time.time() - start_time:.1f}с",
                    f"Цель: ({exit_x}, {exit_y})"
                ]

                for i, text in enumerate(info_text):
                    text_surface = font.render(text, True, WHITE)
                    screen.blit(
                        text_surface, (10, MINIMAP_SIZE + 20 + i * 25)
                    )
            except Exception as e:
                log_error("Ошибка при отрисовке мини-карты", e)

        def handle_movement():
            """Обрабатывает движение игрока."""
            nonlocal player_x, player_y, player_angle

            try:
                keys = pygame.key.get_pressed()

                move_x, move_y = 0, 0

                if keys[pygame.K_w] or keys[pygame.K_UP]:
                    move_x += math.cos(player_angle) * config['move_speed']
                    move_y += math.sin(player_angle) * config['move_speed']

                if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                    move_x -= math.cos(player_angle) * config['move_speed']
                    move_y -= math.sin(player_angle) * config['move_speed']

                if keys[pygame.K_q]:
                    move_x += math.cos(
                        player_angle - math.pi/2
                    ) * config['move_speed']
                    move_y += math.sin(
                        player_angle - math.pi/2
                    ) * config['move_speed']

                if keys[pygame.K_e]:
                    move_x += math.cos(
                        player_angle + math.pi/2
                    ) * config['move_speed']
                    move_y += math.sin(
                        player_angle + math.pi/2
                    ) * config['move_speed']

                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    player_angle -= ROTATION_SPEED

                if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    player_angle += ROTATION_SPEED

                if move_x != 0 or move_y != 0:
                    new_x = player_x + move_x
                    new_y = player_y + move_y

                    can_move_both = (
                        0 <= int(new_x) < config['map_size'] and
                        0 <= int(new_y) < config['map_size'] and
                        maze[int(new_y)][int(new_x)] == 0
                    )

                    if can_move_both:
                        player_x, player_y = new_x, new_y
                    else:
                        can_move_x = (
                            0 <= int(new_x) < config['map_size'] and
                            0 <= int(player_y) < config['map_size'] and
                            maze[int(player_y)][int(new_x)] == 0
                        )

                        can_move_y = (
                            0 <= int(player_x) < config['map_size'] and
                            0 <= int(new_y) < config['map_size'] and
                            maze[int(new_y)][int(player_x)] == 0
                        )

                        if can_move_x:
                            player_x = new_x

                        if can_move_y:
                            player_y = new_y
            except Exception as e:
                log_error("Ошибка при обработке движения", e)

        # Основной игровой цикл
        running = True
        clock = pygame.time.Clock()
        game_completed = False

        while running:
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False

                if not game_completed:
                    handle_movement()

                    # Проверка достижения выхода
                    if int(player_x) == exit_x and int(player_y) == exit_y:
                        completion_time = time.time() - start_time
                        game_completed = True

                        log_game_completion(
                            player_name, difficulty, completion_time
                        )

                        # Показываем экран победы
                        screen.fill(BLACK)
                        font_large = pygame.font.Font(None, 72)
                        font_medium = pygame.font.Font(None, 36)

                        win_text = font_large.render("ПОБЕДА!", True, GREEN)
                        time_text = font_medium.render(
                            f"Время: {completion_time:.2f} секунд", True, WHITE
                        )
                        player_text = font_medium.render(
                            f"Игрок: {player_name}", True, WHITE
                        )
                        diff_text = font_medium.render(
                            f"Сложность: {difficulty}", True, WHITE
                        )
                        continue_text = font_medium.render(
                            "Нажмите любую клавишу для выхода", True, GRAY
                        )

                        screen.blit(
                            win_text,
                            (WIDTH//2 - win_text.get_width()//2,
                             HEIGHT//2 - 100)
                        )
                        screen.blit(
                            time_text,
                            (WIDTH//2 - time_text.get_width()//2,
                             HEIGHT//2 - 20)
                        )
                        screen.blit(
                            player_text,
                            (WIDTH//2 - player_text.get_width()//2,
                             HEIGHT//2 + 20)
                        )
                        screen.blit(
                            diff_text,
                            (WIDTH//2 - diff_text.get_width()//2,
                             HEIGHT//2 + 60)
                        )
                        screen.blit(
                            continue_text,
                            (WIDTH//2 - continue_text.get_width()//2,
                             HEIGHT//2 + 120)
                        )

                        pygame.display.flip()

                        # Ждем нажатия любой клавиши
                        waiting = True
                        while waiting:
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    waiting = False
                                    running = False
                                elif event.type == pygame.KEYDOWN:
                                    waiting = False
                                    running = False

                if not game_completed:
                    draw_3d_view()
                    draw_minimap()

                    # Отображение управления
                    if config['show_minimap']:
                        font = pygame.font.Font(None, 24)
                        controls = [
                            "W/UP - вперед",
                            "S/DOWN - назад",
                            "A/LEFT - поворот влево",
                            "D/RIGHT - поворот вправо",
                            "Q/E - стрейф",
                            "ESC - выход в меню"
                        ]

                        for i, text in enumerate(controls):
                            control_text = font.render(text, True, WHITE)
                            screen.blit(control_text,
                                        (WIDTH - 200, 20 + i * 25))

                    pygame.display.flip()
                    clock.tick(60)

            except Exception as e:
                log_error("Ошибка в основном игровом цикле", e)
                running = False

        if not game_completed:
            log_game_aborted(player_name, difficulty)

        return completion_time if game_completed else -1

    except Exception as e:
        log_error("Критическая ошибка при запуске игры", e)
        return -1


# Для прямого запуска игры (если нужно)
if __name__ == "__main__":
    run_game("medium", "ТестовыйИгрок")
