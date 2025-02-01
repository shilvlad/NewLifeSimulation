import pygame
import random
import sys
from collections import deque

# Инициализация Pygame
pygame.init()

# Параметры окна
width, height = 200, 200
cell_size = 4
simulation_height = height * cell_size
graph_height = 400
window_size = (width * cell_size, simulation_height + graph_height)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("NewLife Simulation")

# Цвета
colors = {
    'GRASS': (255, 255, 0),  # Желтый
    'PEACEFUL': (0, 255, 0),  # Зеленый
    'PREDATOR': (255, 0, 0),  # Красный
    'BACKGROUND': (0, 0, 0),  # Черный
    'GRAPH_GRASS': (255, 255, 0),  # Желтый для графика
    'GRAPH_PEACEFUL': (0, 255, 0),  # Зеленый для графика
    'GRAPH_PREDATOR': (255, 0, 0),  # Красный для графика
    'GRAPH_AXIS': (255, 255, 255)  # Белый для осей графика
}

# Начальные параметры
initial_grass = 2000
initial_peaceful = 2000
initial_predator = 400
grass_growth_per_cycle = 200
max_cells_per_cycle = 500

# Классы клеток
class Grass:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Peaceful:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = 100

    def move_towards_grass(self, grass_list):
        if not grass_list:
            return
        closest_grass = min(grass_list, key=lambda g: (self.x - g.x) ** 2 + (self.y - g.y) ** 2)
        if self.x < closest_grass.x:
            self.x += 1
        elif self.x > closest_grass.x:
            self.x -= 1
        if self.y < closest_grass.y:
            self.y += 1
        elif self.y > closest_grass.y:
            self.y -= 1

    def reproduce(self, peaceful_list):
        if self.energy >= 30 and len(peaceful_list) < max_cells_per_cycle:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_x, new_y = self.x + dx, self.y + dy
                if 0 <= new_x < width and 0 <= new_y < height:
                    if not any(p.x == new_x and p.y == new_y for p in peaceful_list):
                        peaceful_list.append(Peaceful(new_x, new_y))
                        self.energy /= 2
                        break

class Predator:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = 100

    def move_towards_peaceful(self, peaceful_list):
        if not peaceful_list:
            return
        closest_peaceful = min(peaceful_list, key=lambda p: (self.x - p.x) ** 2 + (self.y - p.y) ** 2)
        if self.x < closest_peaceful.x:
            self.x += 1
        elif self.x > closest_peaceful.x:
            self.x -= 1
        if self.y < closest_peaceful.y:
            self.y += 1
        elif self.y > closest_peaceful.y:
            self.y -= 1

    def reproduce(self, predator_list):
        if self.energy >= 50 and len(predator_list) < max_cells_per_cycle:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_x, new_y = self.x + dx, self.y + dy
                if 0 <= new_x < width and 0 <= new_y < height:
                    if not any(pd.x == new_x and pd.y == new_y for pd in predator_list):
                        predator_list.append(Predator(new_x, new_y))
                        self.energy /= 2
                        break

# Инициализация клеток
grass = [Grass(random.randint(0, width - 1), random.randint(0, height - 1)) for _ in range(initial_grass)]
peaceful = [Peaceful(random.randint(0, width - 1), random.randint(0, height - 1)) for _ in range(initial_peaceful)]
predator = [Predator(random.randint(0, width - 1), random.randint(0, height - 1)) for _ in range(initial_predator)]

# Очередь для хранения истории состояний
history = deque(maxlen=1000)

# Функция для отрисовки клеток
def draw_cells():
    screen.fill(colors['BACKGROUND'])
    for g in grass:
        pygame.draw.rect(screen, colors['GRASS'], (g.x * cell_size, g.y * cell_size, cell_size, cell_size))
    for p in peaceful:
        pygame.draw.circle(screen, colors['PEACEFUL'], (p.x * cell_size + cell_size // 2, p.y * cell_size + cell_size // 2), cell_size // 2)
    for pd in predator:
        pygame.draw.circle(screen, colors['PREDATOR'], (pd.x * cell_size + cell_size // 2, pd.y * cell_size + cell_size // 2), cell_size // 2)

# Функция для отрисовки графика
def draw_graph():
    graph_surface = pygame.Surface((width * cell_size, graph_height))
    graph_surface.fill(colors['BACKGROUND'])

    if len(history) < 2:
        return graph_surface

    # Отрисовка осей
    pygame.draw.line(graph_surface, colors['GRAPH_AXIS'], (50, graph_height - 50), (width * cell_size - 50, graph_height - 50), 2)  # Ось X
    pygame.draw.line(graph_surface, colors['GRAPH_AXIS'], (50, 50), (50, graph_height - 50), 2)  # Ось Y

    # Масштабирование графика
    max_count = max(max(h[0], h[1], h[2]) for h in history)
    if max_count == 0:
        return graph_surface

    # Отрисовка линий графика
    for i in range(1, len(history)):
        x1 = 50 + (i - 1) * (width * cell_size - 100) // len(history)
        x2 = 50 + i * (width * cell_size - 100) // len(history)

        # Трава
        y1_grass = graph_height - 50 - (history[i - 1][0] * (graph_height - 100) // max_count)
        y2_grass = graph_height - 50 - (history[i][0] * (graph_height - 100) // max_count)
        pygame.draw.line(graph_surface, colors['GRAPH_GRASS'], (x1, y1_grass), (x2, y2_grass), 2)

        # Мирные клетки
        y1_peaceful = graph_height - 50 - (history[i - 1][1] * (graph_height - 100) // max_count)
        y2_peaceful = graph_height - 50 - (history[i][1] * (graph_height - 100) // max_count)
        pygame.draw.line(graph_surface, colors['GRAPH_PEACEFUL'], (x1, y1_peaceful), (x2, y2_peaceful), 2)

        # Хищные клетки
        y1_predator = graph_height - 50 - (history[i - 1][2] * (graph_height - 100) // max_count)
        y2_predator = graph_height - 50 - (history[i][2] * (graph_height - 100) // max_count)
        pygame.draw.line(graph_surface, colors['GRAPH_PREDATOR'], (x1, y1_predator), (x2, y2_predator), 2)

    return graph_surface

# Основной цикл игры
clock = pygame.time.Clock()
cycle = 0
paused = False
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused

    if not paused:
        # Логика игры
        # Трава растет
        for _ in range(grass_growth_per_cycle):
            if len(grass) < width * height:
                x, y = random.randint(0, width - 1), random.randint(0, height - 1)
                if not any(g.x == x and g.y == y for g in grass):
                    grass.append(Grass(x, y))

        # Мирные клетки двигаются и едят траву
        for p in peaceful[:]:  # Используем копию списка для безопасного удаления
            p.energy -= 1
            if p.energy <= 0:
                peaceful.remove(p)
                continue
            p.move_towards_grass(grass)
            for g in grass[:]:  # Используем копию списка для безопасного удаления
                if p.x == g.x and p.y == g.y:
                    grass.remove(g)
                    p.energy = 100
                    break
            p.reproduce(peaceful)

        # Хищные клетки двигаются и едят мирных
        for pd in predator[:]:  # Используем копию списка для безопасного удаления
            pd.energy -= 1
            if pd.energy <= 0:
                predator.remove(pd)
                continue
            pd.move_towards_peaceful(peaceful)
            for p in peaceful[:]:  # Используем копию списка для безопасного удаления
                if pd.x == p.x and pd.y == p.y:
                    peaceful.remove(p)
                    pd.energy = 100
                    break
            pd.reproduce(predator)

        # Ограничение размножения
        if len(peaceful) > max_cells_per_cycle:
            peaceful = peaceful[:max_cells_per_cycle]
        if len(predator) > max_cells_per_cycle:
            predator = predator[:max_cells_per_cycle]

        # Сохранение истории
        history.append((len(grass), len(peaceful), len(predator)))

        # Отрисовка
        draw_cells()
        graph_surface = draw_graph()
        screen.blit(graph_surface, (0, simulation_height))

        # Отображение информации
        font = pygame.font.SysFont("Arial", 18)
        text = font.render(f"Cycle: {cycle}, Grass: {len(grass)}, Peaceful: {len(peaceful)}, Predator: {len(predator)}", True, (255, 255, 255))
        screen.blit(text, (10, 10))

        # Пауза и отображение здоровья
        if paused:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            cell_x, cell_y = mouse_x // cell_size, mouse_y // cell_size
            for p in peaceful:
                if p.x == cell_x and p.y == cell_y:
                    health_text = font.render(f"Peaceful Energy: {p.energy}", True, (255, 255, 255))
                    screen.blit(health_text, (mouse_x, mouse_y))
            for pd in predator:
                if pd.x == cell_x and pd.y == cell_y:
                    health_text = font.render(f"Predator Energy: {pd.energy}", True, (255, 255, 255))
                    screen.blit(health_text, (mouse_x, mouse_y))

        pygame.display.flip()
        clock.tick(1)
        cycle += 1

# Завершение Pygame
pygame.quit()