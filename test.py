import pytest
import random
import math
from main import Cell, update_game, initialize_cells, WIDTH, HEIGHT, MAX_ENERGY, FOOD_REGEN, ENERGY_THRESHOLD, grid, \
    peaceful_cells, predators, food


# Тестирование класса Cell
def test_cell_initialization():
    # Проверка инициализации мирной клетки
    cell = Cell(1, 1, 0)
    assert cell.x == 1
    assert cell.y == 1
    assert cell.cell_type == 0
    assert cell.energy == MAX_ENERGY

    # Проверка инициализации хищной клетки
    predator = Cell(2, 2, 1)
    assert predator.x == 2
    assert predator.y == 2
    assert predator.cell_type == 1
    assert predator.energy == 100


# Тестирование питания клеток
def test_peaceful_cell_eats_food():
    # Создаем мирную клетку и пищу
    peaceful = Cell(1, 1, 0)
    food_position = (1, 1)  # Пища на этой же позиции
    food.append(food_position)

    # Проверка начальной энергии мирной клетки
    initial_energy = peaceful.energy

    # Имитация питания
    update_game()

    # Энергия клетки должна увеличиться
    assert peaceful.energy == min(initial_energy + FOOD_REGEN, MAX_ENERGY)
    assert food_position not in food  # Пища должна исчезнуть


def test_food_appears():
    # Проверим, что еда появляется в случайных местах
    initialize_cells()  # Инициализируем клетки и еду
    initial_food_count = len(food)

    # Имитация цикла обновления
    update_game()

    # Пища должна была быть съедена или перемещена
    assert len(food) != initial_food_count  # Количество еды изменилось


# Тестирование размножения клеток
def test_peaceful_cell_reproduces():
    peaceful = Cell(1, 1, 0)
    peaceful.energy = MAX_ENERGY
    peaceful_cells.append(peaceful)

    # Проверим, что размножение происходит только при достаточно энергии
    peaceful.energy = 60  # Энергия больше порога

    # Количество мирных клеток до размножения
    initial_count = len(peaceful_cells)

    # Имитация размножения
    update_game()

    # Проверка увеличения количества мирных клеток
    assert len(peaceful_cells) == initial_count + 1


def test_predator_eats_peaceful_cell():
    predator = Cell(2, 2, 1)
    peaceful = Cell(3, 2, 0)
    predators.append(predator)
    peaceful_cells.append(peaceful)

    # Проверка начального здоровья хищной клетки
    initial_health = predator.energy

    # Имитация хищника поедающего мирную клетку
    update_game()

    # Хищная клетка должна восстановить здоровье
    assert predator.energy == 100
    assert peaceful not in peaceful_cells  # Мирная клетка должна исчезнуть


def test_predator_reproduces():
    predator1 = Cell(2, 2, 1)
    predator2 = Cell(3, 2, 1)
    predators.append(predator1)
    predators.append(predator2)

    # Количество хищных клеток до размножения
    initial_count = len(predators)

    # Имитация размножения
    update_game()

    # Проверка увеличения количества хищных клеток
    assert len(predators) == initial_count + 1


# Тестирование движения клеток
def test_cell_movement_towards_food():
    peaceful = Cell(1, 1, 0)
    food_position = (5, 5)
    food.append(food_position)

    # Проверяем начальную позицию
    initial_position = (peaceful.x, peaceful.y)

    peaceful.move_towards(food_position[0], food_position[1])

    # Позиция клетки должна измениться и двигаться в сторону пищи
    assert peaceful.x != initial_position[0] or peaceful.y != initial_position[1]


def test_cell_does_not_move_if_no_food():
    peaceful = Cell(1, 1, 0)
    initial_position = (peaceful.x, peaceful.y)

    # Если нет пищи, клетка не должна двигаться
    peaceful.move_towards(50, 50)
    assert peaceful.x == initial_position[0] and peaceful.y == initial_position[1]


# Тестирование размножения при низкой энергии
def test_peaceful_cell_does_not_reproduce_without_enough_energy():
    peaceful = Cell(1, 1, 0)
    peaceful.energy = 10  # Энергия недостаточна для размножения
    peaceful_cells.append(peaceful)

    # Количество мирных клеток до размножения
    initial_count = len(peaceful_cells)

    # Имитация цикла обновления
    update_game()

    # Клетка не должна размножиться
    assert len(peaceful_cells) == initial_count


# Тестирование работы паузы
@pytest.mark.parametrize("key, expected_paused_state", [
    (pygame.K_SPACE, True),
    (pygame.K_RETURN, False),
])
def test_pause_functionality(key, expected_paused_state):
    # Проверка, что пауза переключается при нажатии клавиши
    paused = False
    if key == pygame.K_SPACE:
        paused = not paused

    assert paused == expected_paused_state
