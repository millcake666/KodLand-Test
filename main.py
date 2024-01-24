import pgzrun
from pgzero.actor import Actor
from pgzero.keyboard import keyboard
from pgzero.screen import Screen
from pygame.surface import Surface

from random import choice, randint
import os

from actor_blocks import items

WIDTH = 1200  # Ширина окна
HEIGHT = 600  # Высота окна
TITLE = 'Dungeon game'  # Заголовок окна игры
FPS = 60  # Количество кадров в секунду
screen = Screen(Surface((WIDTH, HEIGHT)))

mode = 'game'  # game / menu / exit / lose / win
door_open = False  # двери закрыты пока все зелья не собраны, для прохождения уровня надо их открыть и в них пройти

doors = {'open': [Actor('door/door_left_open', topleft=(700, 100)), Actor('door/door_right_open', topleft=(750, 100))],
         'close': [Actor('door/door_left_close', topleft=(700, 100)),
                   Actor('door/door_right_close', topleft=(750, 100))]}
sands = [Actor('sand/sand', topleft=(x, y)) for x in range(0, 1201, 50) for y in range(0, 601, 50)]
blocks = items
attributes = [Actor('attribute/railway', topleft=(250, y)) for y in range(300, 451, 50)]


class Alien(Actor):
    def __init__(self, init_x: int | float, init_y: int | float):
        self.img_directory = 'alien'
        self.img_right = ['right_1', 'right_2']
        self.img_left = ['left_1', 'left_2']
        self.pixel_step = 2
        self.direction = 'right'  # right / left
        self.old_y = 0
        self.dt_count = 0
        self.animation_interval = 0.2
        self.state = 'stay'  # stay / move

        super().__init__(os.path.join(self.img_directory, self.img_right[0]), topleft=(init_x, init_y))

    def update(self, dt):
        self.is_find_potion()
        self.state = 'stay'

        if keyboard.RIGHT:
            self.move('right')
        if keyboard.LEFT:
            self.move('left')
        if keyboard.UP:
            self.move('up')
        if keyboard.DOWN:
            self.move('down')

        self.animate(dt)

    def move(self, side: str):
        global blocks

        match side:
            case 'right':
                if self.right + self.pixel_step > WIDTH:
                    return

                self.x += self.pixel_step
                for block in blocks:
                    if self.colliderect(block):
                        self.x -= self.pixel_step
                        return
                if len(potions) > 0:
                    for door in doors['close']:
                        if self.colliderect(door):
                            self.x -= self.pixel_step
                            return
                self.direction = 'right'

            case 'left':
                if self.left - self.pixel_step < 0:
                    return

                self.x -= self.pixel_step
                for block in blocks:
                    if self.colliderect(block):
                        self.x += self.pixel_step
                        return
                if len(potions) > 0:
                    for door in doors['close']:
                        if self.colliderect(door):
                            self.x -= self.pixel_step
                            return
                self.direction = 'left'

            case 'up':
                if self.top - self.pixel_step < 0:
                    return

                self.y -= self.pixel_step
                for block in blocks:
                    if self.colliderect(block):
                        self.y += self.pixel_step
                        return
                if len(potions) > 0:
                    for door in doors['close']:
                        if self.colliderect(door):
                            self.x -= self.pixel_step
                            return

            case 'down':
                if self.bottom + self.pixel_step > HEIGHT:
                    return

                self.y += self.pixel_step
                for block in blocks:
                    if self.colliderect(block):
                        self.y -= self.pixel_step
                        return
                if len(potions) > 0:
                    for door in doors['close']:
                        if self.colliderect(door):
                            self.x -= self.pixel_step
                            return

        self.state = 'move'

    def is_find_potion(self):
        global potions
        collide = self.collidelist(potions)
        if collide != -1:
            potions.pop(collide)

    def animate(self, dt):
        if self.state == 'stay':
            self.dt_count = 0
            if self.direction == 'right':
                self.image = os.path.join(self.img_directory, self.img_right[0])
            else:
                self.image = os.path.join(self.img_directory, self.img_left[0])
        else:
            self.dt_count += dt
            if self.direction == 'right':
                if self.old_y != self.y:
                    self.old_y = self.y
                    frame_index = int(self.y // 10) % 2
                    if self.dt_count >= self.animation_interval:
                        frame_index = (frame_index + 1) % 2
                        self.dt_count = 0
                    self.image = os.path.join(self.img_directory, self.img_right[frame_index])
                else:
                    frame_index = int(self.x // 10) % 2
                    if self.dt_count >= self.animation_interval:
                        frame_index = (frame_index + 1) % 2
                        self.dt_count = 0
                    self.image = os.path.join(self.img_directory, self.img_right[frame_index])
            else:
                if self.old_y != self.y:
                    self.old_y = self.y
                    frame_index = int(self.y // 10) % 2
                    if self.dt_count >= self.animation_interval:
                        frame_index = (frame_index + 1) % 2
                        self.dt_count = 0
                    self.image = os.path.join(self.img_directory, self.img_left[frame_index])
                else:
                    frame_index = int(self.x // 10) % 2
                    if self.dt_count >= self.animation_interval:
                        frame_index = (frame_index + 1) % 2
                        self.dt_count = 0
                    self.image = os.path.join(self.img_directory, self.img_left[frame_index])


class Spear(Actor):
    def __init__(self, direction: str, init_x: int | float, init_y: int | float):
        if direction not in ['up', 'down', 'right', 'left']:
            raise Exception('Неправильное название направления копья!')

        self.pixel_step = 15
        self.direction = direction

        match direction:
            case 'up':
                super().__init__('attribute/spear', topleft=(init_x, init_y))
                self.angle = 0
            case 'down':
                super().__init__('attribute/spear', topleft=(init_x, init_y))
                self.angle = 180
            case 'right':
                super().__init__('attribute/spear', topleft=(init_x, init_y))
                self.angle = 270
            case 'left':
                super().__init__('attribute/spear', topleft=(init_x, init_y))
                self.angle = 90

    def update(self):
        match self.direction:
            case 'up':
                self.y -= self.pixel_step
            case 'down':
                self.y += self.pixel_step
            case 'right':
                self.x += self.pixel_step
            case 'left':
                self.x -= self.pixel_step


class Enemy(Actor):
    def __init__(self):
        self.img_directory = 'enemy'
        self.img_variants = {1: {'right': ['1_right_1', '1_right_2'], 'left': ['1_left_1', '1_left_2']},
                             2: {'right': ['2_right_1', '2_right_2'], 'left': ['2_left_1', '2_left_2']}}
        self.enemy_color = randint(1, 2)
        self.pixel_step = 1.5
        self.direction = 'right'  # right / left
        self.old_y = 0
        self.dt_count = 0
        self.animation_interval = 0.4
        self.state = 'stay'  # stay / move

        init_x, init_y = self._random_get_init_pos()
        print(init_x, init_y)

        super().__init__(os.path.join(self.img_directory, self.img_variants[self.enemy_color][self.direction][0]),
                         topleft=(init_x, init_y))

    def update(self):
        pass

    def animate(self):
        pass

    @staticmethod
    def _random_get_init_pos():
        global alien, enemies, blocks

        pos_list_x = range(0, 1151, 50)
        pos_list_y = range(0, 551, 50)
        transparent_enemy: Actor
        init_x = 0
        init_y = 0
        flag = True

        while flag:
            transparent_enemy = Actor('enemy/transparent', topleft=(choice(pos_list_x), choice(pos_list_y)))
            init_x = transparent_enemy.left
            init_y = transparent_enemy.top

            if transparent_enemy.collidelist(blocks) == -1 and transparent_enemy.distance_to(alien) > 200:
                flag = False

        del transparent_enemy
        return init_x, init_y


class Potion(Actor):
    def __init__(self, init_x: int | float, init_y: int | float):
        self.img_directory = 'potion'
        self.img_variants = ['blue', 'green', 'red']

        super().__init__(os.path.join(self.img_directory, choice(self.img_variants)), topleft=(init_x, init_y))


alien = Alien(0, 550)
enemies = [Enemy(), Enemy(), Enemy()]
potions_x = [150, 1100, 850, 550, 800, 300, 1000]
potions_y = [50, 50, 150, 250, 400, 500, 550]
potions = [Potion(x, y) for x, y in zip(potions_x, potions_y)]
spears = []


def draw_map():
    for sand in sands:
        sand.draw()
    for attribute in attributes:
        attribute.draw()
    for block in blocks:
        block.draw()
    if len(potions) > 0:
        for door in doors['close']:
            door.draw()
    else:
        for door in doors['open']:
            door.draw()


def draw():
    global mode

    if mode == 'game':
        screen.clear()
        draw_map()

        for potion in potions:
            potion.draw()

        for i, spear in enumerate(spears):
            if spear.x > WIDTH or spear.x < 0 or spear.y > HEIGHT or spear.y < 0:
                spears.pop(i)
            elif spear.collidelist(blocks) != -1:
                spears.pop(i)
            else:
                spear.draw()

        alien.draw()

        for enemy in enemies:
            enemy.draw()

    elif mode == 'win':
        pass


def on_key_down(key):
    if key == keys.W:
        spears.append(Spear('up', alien.x - alien.width / 4, alien.y - alien.height / 2))
    if key == keys.S:
        spears.append(Spear('down', alien.x - alien.width / 4, alien.y - alien.height / 2))
    if key == keys.A:
        spears.append(Spear('left', alien.x - alien.width / 2, alien.y - alien.height / 2))
    if key == keys.D:
        spears.append(Spear('right', alien.x - alien.width / 2, alien.y - alien.height / 2))


def update(dt):
    global mode, door_open, alien, potions

    if mode == 'game':
        alien.update(dt)
        for spear in spears:
            spear.update()

        for enemy in enemies:
            enemy.update()

        if len(potions) == 0:
            door_open = True

        if door_open:
            if alien.collidelist(doors['open']) != -1:
                mode = 'win'

        if alien.collidelist(enemies) != -1:
            mode = 'loose'

    elif mode == 'win':
        print('победа победа вместо обеда!')

    elif mode == 'loose':
        print('вы проиграли(((')


pgzrun.go()
