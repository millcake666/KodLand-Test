import pgzrun
from pgzero.actor import Actor
from pgzero.constants import mouse
from pgzero.keyboard import keyboard
from pgzero.loaders import sounds
from pgzero.screen import Screen
from pygame.surface import Surface
from pgzero.animation import animate
from pgzero.clock import clock
from pgzero import music

from random import choice, randint
import os
import json

from actor_blocks import items

# settings
WIDTH = 1200  # Ширина окна
HEIGHT = 600  # Высота окна
TITLE = 'Dungeon game'  # Заголовок окна игры
FPS = 60  # Количество кадров в секунду
screen = Screen(Surface((WIDTH, HEIGHT)))
data: dict
music_after_game_flag = True
sound_door_open_flag = True

# open settings saved file
try:
    with open('settings.json', 'r+', encoding='utf-8') as file:
        data = json.load(file)

        # game element and sprites
        mode = 'menu'  # game / menu / lose / win
        door_open = False  # двери закрыты пока все зелья не собраны, для прохождения уровня надо их открыть и в них пройти
        sound_state = data['sound_state']
        music_state = data['music_state']
        enemy_count = data['enemy_count']

        doors = {'open': [Actor('door/door_left_open', topleft=(700, 100)), Actor('door/door_right_open', topleft=(750, 100))],
                 'close': [Actor('door/door_left_close', topleft=(700, 100)),
                           Actor('door/door_right_close', topleft=(750, 100))]}
        sands = [Actor('sand/sand', topleft=(x, y)) for x in range(0, 1201, 50) for y in range(0, 601, 50)]
        blocks = items
        attributes = [Actor('attribute/railway', topleft=(250, y)) for y in range(300, 451, 50)]

        # overgame screen button
        restart_overgame_button = Actor('overgame/restart', topleft=(332, 400))
        exit_overgame_button = Actor('overgame/exit', topleft=(618, 400))
        menu_overgame_button = Actor('overgame/menu', topleft=(475, 520))

        # menu screen button
        start_menu_button = Actor('menu/start', topleft=(100, 140))
        exit_menu_button = Actor('menu/exit', topleft=(100, 500))
        music_menu_button = {False: Actor('menu/enable_music', topleft=(100, 425)),
                             True: Actor('menu/disable_music', topleft=(100, 425))}
        sound_menu_button = {False: Actor('menu/enable_sound', topleft=(100, 365)),
                             True: Actor('menu/disable_sound', topleft=(100, 365))}
        plus_menu_button = Actor('menu/plus', topleft=(354, 305))
        minus_menu_button = Actor('menu/minus', topleft=(354, 333))
        monster_menu_button = Actor('menu/monsters', topleft=(100, 305))

        # menu animated logo
        menu_alien = Actor('menu/green_logo', topleft=(500, 250))
        menu_enemy = Actor('menu/red_logo', topleft=(964, 288))
        menu_spear = Actor('menu/spear_logo', topleft=(700, 320))  # x pos from 700 to 935

        if music_state:
            music.play('menu')
        else:
            music.play('empty')

        menu_background = Actor('menu/background', topleft=(0, 0))


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
                                    self.x += self.pixel_step
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
                                    self.y += self.pixel_step
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
                                    self.y -= self.pixel_step
                                    return

                self.state = 'move'

            def is_find_potion(self):
                global potions
                collide = self.collidelist(potions)
                if collide != -1:
                    if sound_state:
                        sounds.potion.play()
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
                self.target_direction = 0

                init_x, init_y = self._random_get_init_pos()

                super().__init__(os.path.join(self.img_directory, self.img_variants[self.enemy_color][self.direction][0]),
                                 topleft=(init_x, init_y))

            def update(self, dt):
                self.state = 'stay'

                if not self.move(self.target_direction):
                    self.target_direction = randint(0, 3)  # если враг больше не может идти в нужном направлении, меняем его

                self.animate(dt)

            def move(self, side: int) -> bool:
                global blocks

                match side:
                    case 0:
                        if self.right + self.pixel_step > WIDTH:
                            return False

                        self.x += self.pixel_step
                        for block in blocks:
                            if self.colliderect(block):
                                self.x -= self.pixel_step
                                return False
                        if len(potions) > 0:
                            for door in doors['close']:
                                if self.colliderect(door):
                                    self.x -= self.pixel_step
                                    return False
                        self.direction = 'right'

                    case 1:
                        if self.left - self.pixel_step < 0:
                            return False

                        self.x -= self.pixel_step
                        for block in blocks:
                            if self.colliderect(block):
                                self.x += self.pixel_step
                                return False
                        if len(potions) > 0:
                            for door in doors['close']:
                                if self.colliderect(door):
                                    self.x -= self.pixel_step
                                    return False
                        self.direction = 'left'

                    case 2:
                        if self.top - self.pixel_step < 0:
                            return False

                        self.y -= self.pixel_step
                        for block in blocks:
                            if self.colliderect(block):
                                self.y += self.pixel_step
                                return False
                        if len(potions) > 0:
                            for door in doors['close']:
                                if self.colliderect(door):
                                    self.x -= self.pixel_step
                                    return False

                    case 3:
                        if self.bottom + self.pixel_step > HEIGHT:
                            return False

                        self.y += self.pixel_step
                        for block in blocks:
                            if self.colliderect(block):
                                self.y -= self.pixel_step
                                return False
                        if len(potions) > 0:
                            for door in doors['close']:
                                if self.colliderect(door):
                                    self.x -= self.pixel_step
                                    return False

                self.state = 'move'
                return True

            def animate(self, dt):
                if self.state == 'stay':
                    self.dt_count = 0
                    if self.direction == 'right':
                        self.image = os.path.join(self.img_directory, self.img_variants[self.enemy_color]['right'][0])
                    else:
                        self.image = os.path.join(self.img_directory, self.img_variants[self.enemy_color]['left'][0])
                else:
                    self.dt_count += dt
                    if self.direction == 'right':
                        if self.old_y != self.y:
                            self.old_y = self.y
                            frame_index = int(self.y // 10) % 2
                            if self.dt_count >= self.animation_interval:
                                frame_index = (frame_index + 1) % 2
                                self.dt_count = 0
                            self.image = os.path.join(self.img_directory,
                                                      self.img_variants[self.enemy_color]['right'][frame_index])
                        else:
                            frame_index = int(self.x // 10) % 2
                            if self.dt_count >= self.animation_interval:
                                frame_index = (frame_index + 1) % 2
                                self.dt_count = 0
                            self.image = os.path.join(self.img_directory,
                                                      self.img_variants[self.enemy_color]['right'][frame_index])
                    else:
                        if self.old_y != self.y:
                            self.old_y = self.y
                            frame_index = int(self.y // 10) % 2
                            if self.dt_count >= self.animation_interval:
                                frame_index = (frame_index + 1) % 2
                                self.dt_count = 0
                            self.image = os.path.join(self.img_directory,
                                                      self.img_variants[self.enemy_color]['left'][frame_index])
                        else:
                            frame_index = int(self.x // 10) % 2
                            if self.dt_count >= self.animation_interval:
                                frame_index = (frame_index + 1) % 2
                                self.dt_count = 0
                            self.image = os.path.join(self.img_directory,
                                                      self.img_variants[self.enemy_color]['left'][frame_index])

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

                    if transparent_enemy.collidelist(blocks) == -1 and transparent_enemy.distance_to(alien) > 200 and \
                            transparent_enemy.collidelist(doors['open' if door_open else 'close']) == -1:
                        flag = False

                del transparent_enemy
                return init_x, init_y


        class Potion(Actor):
            def __init__(self, init_x: int | float, init_y: int | float):
                self.img_directory = 'potion'
                self.img_variants = ['blue', 'green', 'red']

                super().__init__(os.path.join(self.img_directory, choice(self.img_variants)), topleft=(init_x, init_y))


        alien = Alien(0, 550)
        enemies = [Enemy() for _ in range(enemy_count)]
        potions_x = [150, 1100, 850, 550, 800, 300, 1000]
        potions_y = [50, 50, 150, 250, 400, 500, 550]
        potions = [Potion(x, y) for x, y in zip(potions_x, potions_y)]
        spears = []


        def create_new_enemy():
            global enemies
            enemies.append(Enemy())


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


        def draw_menu():
            menu_background.draw()

            start_menu_button.draw()
            monster_menu_button.draw()
            screen.draw.text(str(enemy_count), topleft=(282, 309), fontname='rosencrantz_nbp.ttf',
                             fontsize=40, color='white')
            plus_menu_button.draw()
            minus_menu_button.draw()
            sound_menu_button[sound_state].draw()
            music_menu_button[music_state].draw()
            exit_menu_button.draw()

            menu_alien.draw()
            menu_enemy.draw()
            menu_spear.draw()


        def animate_menu_spear_home():
            if mode == 'menu':
                menu_spear.x = 700


        def animate_menu_spear_end():
            if mode == 'menu':
                animate(menu_spear, x=935, tween='accelerate', duration=1)


        clock.schedule_interval(animate_menu_spear_end, 2)
        clock.schedule_interval(animate_menu_spear_home, 2)


        def draw():
            global mode, music_after_game_flag

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
                screen.draw.text('You WIN!', center=(WIDTH // 2, HEIGHT // 3),
                                 color='green', fontsize=120, background='black', fontname='rosencrantz_nbp.ttf')
                restart_overgame_button.draw()
                exit_overgame_button.draw()
                menu_overgame_button.draw()

                if music_after_game_flag:
                    music_after_game_flag = False
                    if music_state:
                        music.play('menu')
                    else:
                        music.play('empty')

            elif mode == 'loose':
                screen.draw.text('Game OVER!', center=(WIDTH // 2, HEIGHT // 3),
                                 color='red', fontsize=120, background='black', fontname='rosencrantz_nbp.ttf')
                restart_overgame_button.draw()
                exit_overgame_button.draw()
                menu_overgame_button.draw()

                if music_after_game_flag:
                    music_after_game_flag = False
                    if music_state:
                        music.play('menu')
                    else:
                        music.play('empty')

            elif mode == 'menu':
                screen.clear()
                draw_menu()


        def on_mouse_down(button, pos):
            global door_open, alien, enemies, potions, start_menu_button, monster_menu_button, plus_menu_button
            global minus_menu_button, sound_menu_button, music_menu_button, exit_menu_button, sound_state, music_state
            global data, music_after_game_flag, mode, enemy_count

            if button == mouse.LEFT:
                if mode == 'loose' or mode == 'win':
                    if restart_overgame_button.collidepoint(pos):
                        mode = 'game'
                        if music_state:
                            music.play('game')
                        else:
                            music.play('empty')
                        if sound_state:
                            sounds.button.play()

                        alien.__init__(0, 550)

                        enemies.clear()
                        for _ in range(enemy_count):
                            create_new_enemy()

                        potions = [Potion(x, y) for x, y in zip(potions_x, potions_y)]

                        door_open = False
                        music_after_game_flag = True

                    if exit_overgame_button.collidepoint(pos):
                        if sound_state:
                            sounds.button.play()
                        quit(0)

                    if menu_overgame_button.collidepoint(pos):
                        mode = 'menu'
                        if music_state:
                            music.play('menu')
                        else:
                            music.play('empty')
                        if sound_state:
                            sounds.button.play()

                if mode == 'menu':
                    if start_menu_button.collidepoint(pos):
                        mode = 'game'
                        if music_state:
                            music.play('game')
                        else:
                            music.play('empty')
                        if sound_state:
                            sounds.button.play()

                        alien.__init__(0, 550)

                        enemies.clear()
                        for _ in range(enemy_count):
                            create_new_enemy()

                        potions = [Potion(x, y) for x, y in zip(potions_x, potions_y)]

                        door_open = False
                        music_after_game_flag = True

                    if exit_menu_button.collidepoint(pos):
                        if sound_state:
                            sounds.button.play()
                        quit(0)
                    if sound_menu_button[sound_state].collidepoint(pos):
                        sound_state = not sound_state
                        data['sound_state'] = sound_state
                        if sound_state:
                            sounds.button.play()
                        file.seek(0)
                        file.write(json.dumps(data))
                        file.truncate()
                    if music_menu_button[music_state].collidepoint(pos):
                        music_state = not music_state
                        if music_state:
                            music.play('menu')
                        else:
                            music.play('empty')
                        if sound_state:
                            sounds.button.play()
                        data['music_state'] = music_state
                        file.seek(0)
                        file.write(json.dumps(data))
                        file.truncate()
                    if plus_menu_button.collidepoint(pos):
                        if sound_state:
                            sounds.button.play()
                        if enemy_count < 9:
                            enemy_count += 1
                            data['enemy_count'] = enemy_count
                            file.seek(0)
                            file.write(json.dumps(data))
                            file.truncate()
                    if minus_menu_button.collidepoint(pos):
                        if sound_state:
                            sounds.button.play()
                        if enemy_count > 0:
                            enemy_count -= 1
                            data['enemy_count'] = enemy_count
                            file.seek(0)
                            file.write(json.dumps(data))
                            file.truncate()


        def on_key_down(key):
            if key == keys.W:
                if sound_state:
                    sounds.hit.play()
                spears.append(Spear('up', alien.x - alien.width / 4, alien.y - alien.height / 2))
            if key == keys.S:
                if sound_state:
                    sounds.hit.play()
                spears.append(Spear('down', alien.x - alien.width / 4, alien.y - alien.height / 2))
            if key == keys.A:
                if sound_state:
                    sounds.hit.play()
                spears.append(Spear('left', alien.x - alien.width / 2, alien.y - alien.height / 2))
            if key == keys.D:
                if sound_state:
                    sounds.hit.play()
                spears.append(Spear('right', alien.x - alien.width / 2, alien.y - alien.height / 2))


        def update(dt):
            global mode, door_open, alien, potions, sound_door_open_flag

            if mode == 'game':
                alien.update(dt)
                for spear in spears:
                    spear.update()

                while len(enemies) < enemy_count:
                    create_new_enemy()
                while len(enemies) > enemy_count:
                    enemies.pop(-1)

                for i, enemy in enumerate(enemies):
                    enemy.update(dt)
                    if enemy.collidelist(spears) != -1:
                        if sound_state:
                            sounds.enemy_dead.play()
                        enemies.pop(i)
                        create_new_enemy()

                if len(potions) == 0:
                    if sound_door_open_flag:
                        sound_door_open_flag = False
                        if sound_state:
                            sounds.door_open.play()
                    door_open = True

                if door_open:
                    if alien.collidelist(doors['open']) != -1:
                        mode = 'win'

                if alien.collidelist(enemies) != -1:
                    mode = 'loose'

        pgzrun.go()

except FileNotFoundError:
    raise Exception('Файл настроек не найден')
