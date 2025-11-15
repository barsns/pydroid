import pygame
import sys
import math
import random
from pygame.locals import *

# Инициализация Pygame
pygame.init()

# Настройки экрана
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), FULLSCREEN)
pygame.display.set_caption("Эволюция ходьбы")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
BLUE = (50, 50, 255)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 50)
ORANGE = (255, 150, 50)
PURPLE = (150, 50, 255)
BROWN = (120, 70, 30)
GRAY = (150, 150, 150)

# Масштабирование
SCALE = min(WIDTH, HEIGHT) / 800
FONT_SIZE = int(28 * SCALE)
POINT_RADIUS = int(10 * SCALE)
LINE_WIDTH = int(4 * SCALE)

# Физика
GRAVITY = 0.5 * SCALE
FRICTION = 0.99
MUSCLE_STRENGTH = 0.5
STIFFNESS = 0.4
MIN_MUSCLE_LENGTH = 40 * SCALE
MAX_MUSCLE_LENGTH = 180 * SCALE

class Point:
    def __init__(self, x, y, fixed=False, color=YELLOW):
        self.x = x
        self.y = y
        self.prev_x = x
        self.prev_y = y
        self.fixed = fixed
        self.radius = POINT_RADIUS
        self.mass = 1.0
        self.color = RED if fixed else color
        self.highlight = False
        self.id = id(self)  # Уникальный идентификатор на основе id объекта
        
    def __hash__(self):
        return self.id  # Делаем объект хешируемым
        
    def __eq__(self, other):
        return self.id == other.id
        
    def update(self, dt):
        if not self.fixed:
            temp_x, temp_y = self.x, self.y
            vel_x = (self.x - self.prev_x) * FRICTION
            vel_y = (self.y - self.prev_y) * FRICTION
            
            self.x += vel_x
            self.y += vel_y + GRAVITY * dt * 50
            
            self.prev_x, self.prev_y = temp_x, temp_y
            
            self.x = max(self.radius, min(WIDTH-self.radius, self.x))
            self.y = max(self.radius, min(HEIGHT-self.radius, self.y))

class Muscle:
    def __init__(self, point1, point2, strength_mult=1.0):
        self.point1 = point1
        self.point2 = point2
        self.rest_length = self.get_length()
        self.target_length = self.rest_length
        self.contracting = False
        self.base_strength = MUSCLE_STRENGTH * strength_mult
        self.strength = self.base_strength
        self.phase = random.random() * 2 * math.pi
        self.speed = random.uniform(0.5, 1.5)
        self.color = BLUE
        self.highlight = False
        
    def get_length(self):
        dx = self.point2.x - self.point1.x
        dy = self.point2.y - self.point1.y
        return math.sqrt(dx*dx + dy*dy)
        
    def update(self, dt):
        if self.contracting:
            self.target_length = max(MIN_MUSCLE_LENGTH, self.rest_length * (0.6 + 0.1*math.sin(self.phase)))
        else:
            self.target_length = min(MAX_MUSCLE_LENGTH, self.rest_length * (1.0 + 0.2*math.sin(self.phase*0.5)))
            
        self.phase += dt * self.speed
        
        current_length = self.get_length()
        if current_length == 0:
            return
            
        dx = self.point2.x - self.point1.x
        dy = self.point2.y - self.point1.y
        direction_x = dx / current_length
        direction_y = dy / current_length
        
        force = (current_length - self.target_length) * self.strength
        
        if not self.point1.fixed:
            self.point1.x += direction_x * force * dt * 50 / self.point1.mass
            self.point1.y += direction_y * force * dt * 50 / self.point1.mass
            
        if not self.point2.fixed:
            self.point2.x -= direction_x * force * dt * 50 / self.point2.mass
            self.point2.y -= direction_y * force * dt * 50 / self.point2.mass
            
        stiffness_force = (current_length - self.rest_length) * STIFFNESS
        
        if not self.point1.fixed:
            self.point1.x += direction_x * stiffness_force * dt * 30
            self.point1.y += direction_y * stiffness_force * dt * 30
            
        if not self.point2.fixed:
            self.point2.x -= direction_x * stiffness_force * dt * 30
            self.point2.y -= direction_y * stiffness_force * dt * 30
            
        if self.contracting:
            self.color = GREEN
        else:
            ratio = current_length / self.rest_length
            self.color = ORANGE if ratio > 1.2 else PURPLE if ratio < 0.8 else BLUE

class Creature:
    def __init__(self, points, muscles):
        self.points = points
        self.muscles = muscles
        self.position = [WIDTH//2, HEIGHT//2]
        self.time_alive = 0
        self.distance_traveled = 0
        self.fitness = 0
        self.energy = 100
        self.age = 0
        self.color = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255)
        )
        self.brain = self.Brain(len(muscles))
        
    class Brain:
        def __init__(self, num_muscles):
            self.num_muscles = num_muscles
            self.commands = []
            self.current_command = 0
            self.command_timer = 0
            self.generate_commands()
            
        def generate_commands(self):
            patterns = [
                [True, False, True, False],
                [False, True, False, True],
                [True, True, False, False],
                [False, False, True, True],
                [True, False, False, True]
            ]
            
            for _ in range(15):
                pattern = random.choice(patterns)
                repeats = random.randint(2, 5)
                
                for _ in range(repeats):
                    self.commands.append({
                        'muscle_actions': [random.random() < 0.7 or p for p in pattern],
                        'duration': random.randint(8, 25)
                    })
        
        def update(self, creature, dt):
            if self.current_command >= len(self.commands):
                self.current_command = 0
                
            command = self.commands[self.current_command]
            
            for i, muscle in enumerate(creature.muscles):
                if random.random() < 0.05:
                    muscle.contracting = not muscle.contracting
                else:
                    muscle.contracting = command['muscle_actions'][i % len(command['muscle_actions'])]
            
            self.command_timer += dt * 60
            if self.command_timer >= command['duration']:
                self.current_command = (self.current_command + 1) % len(self.commands)
                self.command_timer = 0
        
        def mutate(self):
            for cmd in self.commands:
                if random.random() < 0.1:
                    idx = random.randint(0, len(cmd['muscle_actions'])-1)
                    cmd['muscle_actions'][idx] = not cmd['muscle_actions'][idx]
                    
                if random.random() < 0.05:
                    cmd['duration'] = max(5, cmd['duration'] + random.randint(-3, 3))
            
            if random.random() < 0.2:
                self.generate_commands()
    
    def update(self, dt):
        self.time_alive += dt
        self.age += dt * 0.01
        
        self.brain.update(self, dt)
        
        for point in self.points:
            point.update(dt)
            
        for muscle in self.muscles:
            muscle.update(dt)
            
        center_x = sum(p.x for p in self.points) / len(self.points)
        center_y = sum(p.y for p in self.points) / len(self.points)
        self.position = [center_x, center_y]
        
        self.distance_traveled = center_x - WIDTH//2
        
        movement_cost = sum(
            abs(m.get_length() - m.rest_length) * 0.001 
            for m in self.muscles
        )
        self.energy -= movement_cost * dt
        
        velocity = (center_x - self.position[0]) / dt if dt > 0 else 0
        height_penalty = abs(center_y - HEIGHT//2) * 0.2
        energy_bonus = self.energy * 0.01
        
        self.fitness = (
            self.distance_traveled * 0.2 + 
            velocity * 3 - 
            height_penalty + 
            energy_bonus -
            self.age
        )
        
        return center_x

class Evolution:
    def __init__(self, population_size=8):
        self.population_size = population_size
        self.population = []
        self.generation = 0
        self.best_fitness = 0
        self.best_creature = None
        self.initialize_population()
        
    def initialize_population(self):
        for _ in range(self.population_size):
            num_points = random.randint(4, 8)
            points = []
            
            center = Point(WIDTH//2, HEIGHT//2, True)
            points.append(center)
            
            for i in range(1, num_points):
                angle = random.random() * 2 * math.pi
                dist = random.randint(30, 100) * SCALE
                x = WIDTH//2 + math.cos(angle) * dist
                y = HEIGHT//2 + math.sin(angle) * dist
                color = (
                    random.randint(50, 255),
                    random.randint(50, 255),
                    random.randint(50, 255)
                )
                points.append(Point(x, y, False, color))
            
            muscles = []
            num_muscles = random.randint(num_points, num_points * 2)
            
            for _ in range(num_muscles):
                p1, p2 = random.sample(points, 2)
                dist = math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)
                if dist < 200 * SCALE:
                    strength_mult = random.uniform(0.7, 1.3)
                    muscles.append(Muscle(p1, p2, strength_mult))
            
            self.population.append(Creature(points, muscles))
    
    def evolve(self):
        self.generation += 1
        
        for creature in self.population:
            if creature.fitness > self.best_fitness:
                self.best_fitness = creature.fitness
                self.best_creature = creature
        
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        
        best_creatures = self.population[:int(self.population_size * 0.4)]
        new_population = []
        new_population.extend(best_creatures[:2])
        
        while len(new_population) < self.population_size:
            parent1 = random.choice(best_creatures)
            parent2 = random.choice(best_creatures)
            
            # Создаем копии точек для ребенка
            child_points = []
            point_map = {}  # Для отображения старых точек на новые
            
            # Копируем все точки родителей
            all_parent_points = list({p: None for p in parent1.points + parent2.points}.keys())
            for old_point in all_parent_points:
                new_point = Point(old_point.x, old_point.y, old_point.fixed, old_point.color)
                child_points.append(new_point)
                point_map[old_point] = new_point
            
            # Создаем мышцы ребенка
            child_muscles = []
            all_parent_muscles = parent1.muscles + parent2.muscles
            
            for muscle in all_parent_muscles:
                if random.random() < 0.6:  # Вероятность наследования мышцы
                    p1 = point_map.get(muscle.point1)
                    p2 = point_map.get(muscle.point2)
                    
                    if p1 and p2 and p1 != p2:
                        # Проверяем, нет ли уже такой мышцы
                        muscle_exists = any(
                            (m.point1 == p1 and m.point2 == p2) or 
                            (m.point1 == p2 and m.point2 == p1)
                            for m in child_muscles
                        )
                        
                        if not muscle_exists:
                            strength_mult = muscle.base_strength / MUSCLE_STRENGTH
                            child_muscles.append(Muscle(p1, p2, strength_mult))
            
            child = Creature(child_points, child_muscles)
            
            if random.random() < 0.8:
                self.mutate_creature(child)
            
            new_population.append(child)
        
        self.population = new_population
        return self.best_creature
    
    def mutate_creature(self, creature):
        creature.brain.mutate()
        
        if random.random() < 0.3:
            if random.random() < 0.5 and len(creature.points) < 10:
                # Добавляем новую точку
                angle = random.random() * 2 * math.pi
                dist = random.randint(30, 100) * SCALE
                x = WIDTH//2 + math.cos(angle) * dist
                y = HEIGHT//2 + math.sin(angle) * dist
                color = (
                    random.randint(50, 255),
                    random.randint(50, 255),
                    random.randint(50, 255)
                )
                new_point = Point(x, y, False, color)
                creature.points.append(new_point)
                
                # Соединяем с существующими точками
                num_connections = random.randint(1, 3)
                connected_points = random.sample([p for p in creature.points if p != new_point], 
                                                min(num_connections, len(creature.points)-1))
                for point in connected_points:
                    creature.muscles.append(Muscle(new_point, point))
                    
            elif len(creature.points) > 3:
                # Удаляем случайную точку (не фиксированную)
                non_fixed = [p for p in creature.points if not p.fixed]
                if non_fixed:
                    point_to_remove = random.choice(non_fixed)
                    creature.points.remove(point_to_remove)
                    creature.muscles = [
                        m for m in creature.muscles 
                        if m.point1 != point_to_remove and m.point2 != point_to_remove
                    ]
        
        if random.random() < 0.4:
            if random.random() < 0.7 and creature.muscles:
                # Удаляем случайную мышцу
                creature.muscles.pop(random.randint(0, len(creature.muscles)-1))
            
            if random.random() < 0.7 and len(creature.points) >= 2:
                # Добавляем новую мышцу
                p1, p2 = random.sample(creature.points, 2)
                dist = math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)
                if dist < 250 * SCALE:
                    # Проверяем, нет ли уже такой мышцы
                    muscle_exists = any(
                        (m.point1 == p1 and m.point2 == p2) or 
                        (m.point1 == p2 and m.point2 == p1)
                        for m in creature.muscles
                    )
                    
                    if not muscle_exists:
                        creature.muscles.append(Muscle(p1, p2))
        
        # Мутация параметров мышц
        for muscle in creature.muscles:
            if random.random() < 0.2:
                muscle.base_strength *= random.uniform(0.8, 1.2)
            if random.random() < 0.1:
                muscle.speed *= random.uniform(0.7, 1.3)

def draw_ground(offset):
    ground_height = HEIGHT * 0.8
    pygame.draw.rect(screen, BROWN, (0, ground_height, WIDTH, HEIGHT-ground_height))
    
    for x in range(-100, WIDTH+100, 25):
        pygame.draw.line(screen, GREEN, 
                        (x + offset%25, ground_height),
                        (x + offset%25 - 12, ground_height-15), 3)
    
    pygame.draw.ellipse(screen, GRAY, 
                       (-100 + offset%50, ground_height-10, WIDTH+200, 20))

def draw_creature(creature, offset):
    for muscle in creature.muscles:
        width = LINE_WIDTH+2 if muscle.highlight else LINE_WIDTH
        pygame.draw.line(screen, muscle.color,
                       (muscle.point1.x - offset, muscle.point1.y),
                       (muscle.point2.x - offset, muscle.point2.y), 
                       width)
    
    for point in creature.points:
        color = point.color
        if point.highlight:
            color = (min(255, color[0]+100), min(255, color[1]+100), min(255, color[2]+100))
        
        pygame.draw.circle(screen, color, 
                         (int(point.x - offset), int(point.y)), 
                         point.radius + (2 if point.highlight else 0))
        
        if point.fixed:
            pygame.draw.circle(screen, BLACK, 
                             (int(point.x - offset), int(point.y)), 
                             point.radius + 4, 2)

def draw_ui(generation, best_dist, speed, creature_fitness):
    font = pygame.font.SysFont(None, FONT_SIZE)
    small_font = pygame.font.SysFont(None, int(FONT_SIZE*0.8))
    
    s = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)
    s.fill((150, 150, 150, 150))
    screen.blit(s, (0, 0))
    
    stats = [
        f"Поколение: {generation}",
        f"Рекорд: {best_dist:.1f}",
        f"Скорость: {speed}x",
        f"Фитнес: {creature_fitness:.1f}"
    ]
    
    for i, text in enumerate(stats):
        text_surface = font.render(text, True, WHITE)
        screen.blit(text_surface, (10, 10 + i*(FONT_SIZE+5)))
    
    button_w = WIDTH // 4
    button_h = 50
    
    pygame.draw.rect(screen, (100, 100, 200), (10, HEIGHT-button_h-10, button_w, button_h), border_radius=10)
    pause_text = small_font.render("Пауза", True, WHITE)
    screen.blit(pause_text, (10 + button_w//2 - pause_text.get_width()//2, HEIGHT-button_h-10 + button_h//2 - pause_text.get_height()//2))
    
    pygame.draw.rect(screen, (100, 200, 100), (20 + button_w, HEIGHT-button_h-10, button_w, button_h), border_radius=10)
    speed_text = small_font.render(f"Скорость: {speed}x", True, WHITE)
    screen.blit(speed_text, (20 + button_w + button_w//2 - speed_text.get_width()//2, HEIGHT-button_h-10 + button_h//2 - speed_text.get_height()//2))
    
    pygame.draw.rect(screen, (200, 100, 100), (30 + button_w*2, HEIGHT-button_h-10, button_w, button_h), border_radius=10)
    reset_text = small_font.render("Сброс", True, WHITE)
    screen.blit(reset_text, (30 + button_w*2 + button_w//2 - reset_text.get_width()//2, HEIGHT-button_h-10 + button_h//2 - reset_text.get_height()//2))

def check_button_click(pos):
    button_w = WIDTH // 4
    button_h = 50
    buttons = [
        pygame.Rect(10, HEIGHT-button_h-10, button_w, button_h),
        pygame.Rect(20 + button_w, HEIGHT-button_h-10, button_w, button_h),
        pygame.Rect(30 + button_w*2, HEIGHT-button_h-10, button_w, button_h)
    ]
    
    for i, button in enumerate(buttons):
        if button.collidepoint(pos):
            return i
    return -1

def create_initial_creature():
    points = [
        Point(WIDTH//2, HEIGHT//2, True),
        Point(WIDTH//2-60, HEIGHT//2+40, color=BLUE),
        Point(WIDTH//2+60, HEIGHT//2+40, color=BLUE),
        Point(WIDTH//2-90, HEIGHT//2+90, color=GREEN),
        Point(WIDTH//2+90, HEIGHT//2+90, color=GREEN),
        Point(WIDTH//2, HEIGHT//2-60, color=ORANGE)
    ]
    
    muscles = [
        Muscle(points[0], points[1], 1.2),
        Muscle(points[0], points[2], 1.2),
        Muscle(points[1], points[2], 0.8),
        Muscle(points[1], points[3], 1.0),
        Muscle(points[2], points[4], 1.0),
        Muscle(points[3], points[4], 1.1),
        Muscle(points[0], points[5], 0.9),
        Muscle(points[5], points[1], 0.7),
        Muscle(points[5], points[2], 0.7)
    ]
    
    return Creature(points, muscles)

def main():
    clock = pygame.time.Clock()
    evolution = Evolution()
    best_creature = create_initial_creature()
    current_creature = best_creature
    
    # Инициализация переменных состояния
    simulating = True
    speed_multiplier = 1
    current_generation = 0
    best_distance = 0
    world_offset = 0
    last_touch_pos = None
    touch_start_time = 0
    
    while True:
        dt = 0.05 * speed_multiplier
        
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
                
            elif event.type == FINGERDOWN:
                pos = (event.x * WIDTH, event.y * HEIGHT)
                last_touch_pos = pos
                touch_start_time = pygame.time.get_ticks()
                
                button_idx = check_button_click(pos)
                if button_idx == 0:
                    simulating = not simulating
                elif button_idx == 1:
                    speed_multiplier = speed_multiplier % 3 + 1
                elif button_idx == 2:
                    evolution = Evolution()
                    best_creature = create_initial_creature()
                    current_creature = best_creature
                    current_generation = 0
                    best_distance = 0
                    world_offset = 0
                    simulating = True
            
            elif event.type == FINGERMOTION and last_touch_pos:
                if pygame.time.get_ticks() - touch_start_time > 500:
                    dx = event.x * WIDTH - last_touch_pos[0]
                    world_offset += dx * 0.5
                    last_touch_pos = (event.x * WIDTH, event.y * HEIGHT)
            
            elif event.type == FINGERUP:
                last_touch_pos = None
        
        if simulating:
            center_x = current_creature.update(dt)
            target_offset = WIDTH//2 - center_x
            world_offset += (target_offset - world_offset) * 0.1 * speed_multiplier
            
            if current_creature.time_alive > 10 or current_creature.energy <= 0:
                best_creature = evolution.evolve()
                current_creature = best_creature
                current_generation = evolution.generation
                best_distance = max(best_distance, current_creature.distance_traveled)
                world_offset = 0
        
        screen.fill(WHITE)
        pygame.draw.rect(screen, (240, 240, 255), (0, 0, WIDTH, HEIGHT*0.8))
        draw_ground(world_offset)
        
        if current_creature:
            draw_creature(current_creature, world_offset)
            
            for muscle in current_creature.muscles:
                muscle.highlight = muscle.contracting and random.random() < 0.3
            
            for point in current_creature.points:
                point.highlight = random.random() < 0.05
        
        fitness = current_creature.fitness if current_creature else 0
        draw_ui(current_generation, best_distance, speed_multiplier, fitness)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()