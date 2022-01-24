import os
import sys
import pygame
import pygame_gui
import requests

FPS = 20
SIZE = WIDTH, HEIGHT = 900, 900
clock = pygame.time.Clock()

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption('Labirinto')

background = pygame.Surface(SIZE)
manager = pygame_gui.UIManager(SIZE)

MOVE_ENEMIES_EVENT = 30
pygame.time.set_timer(MOVE_ENEMIES_EVENT, 500)
TIMER_QUIT = 1
pygame.time.set_timer(TIMER_QUIT, 10000)

req = 'https://ru.hitmotop.com/get/music/20180112/8-Bit_Misfits_-_Another_Brick_in_the_Wall_Pt_2_52587615.mp3'
response = requests.get(req)
# menu = pygame.mixer.Sound(response.content)
mus = 'data\Wantme.mp3'
menu = pygame.mixer.Sound(mus)
menu.set_volume(0.2)
pygame.mixer.Sound.play(menu)


def show_message(screen, message):
    font = pygame.font.Font(None, 50)
    text = font.render(message, 1, 'red')
    text_x = WIDTH // 2 - text.get_width() // 2
    text_y = HEIGHT // 2 - text.get_height() // 2
    text_w = text.get_width()
    text_h = text.get_height()
    pygame.draw.rect(screen, 'blue', (text_x - 10, text_y - 10, text_w + 20, text_h + 20))
    screen.blit(text, (text_x, text_y))


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


tile_images = {
    'wall': load_image('box.png', -1),
    'empty': load_image("grass.png", -1),
    'finish': load_image('fin.png', -1)
}
player_image = load_image('slimeBlock.png', -1)
enemy_image = load_image('saw.png', -1)
tile_width = 50
tile_height = 50


all_sprites = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()

class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.obj_pos = (self.rect.x, self.rect.y)
        if tile_type == 'finish':
            self.finish = pos_x, pos_y


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.pos = (pos_x, pos_y)

    def move(self, x, y):
        self.pos = (x, y)
        self.rect = self.image.get_rect().move(tile_width * x, tile_height * y)
        self.rect.move(tile_width * x, tile_height * y)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(enemy_group)
        self.image = enemy_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.obj_pos = (self.rect.x, self.rect.y)
        self.pos_in_cube = (self.rect.x // tile_width, self.rect.y // tile_height)
        self.width = len(lev[0])
        self.height = len(lev)

    def get_tile_id(self, position):
        return lev[position[1]][position[0]]

    def is_free(self, position):
        return self.get_tile_id(position) in ('.', '@')

    def find_path_step(self):
        start = self.pos_in_cube
        target = player.pos
        from collections import deque
        import math
        x, y = start
        dist = [[math.inf] * self.width for _ in range(self.height)]
        dist[y][x] = 0
        queue = deque()
        queue.append(start)
        prev = [[None] * self.width for _ in range(self.height)]
        while queue:
            x, y = queue.popleft()
            for dx, dy in (1, 0), (0, 1), (-1, 0), (0, -1):
                next_x, next_y = x + dx, y + dy
                if 0 <= next_x < self.width and 0 <= next_y < self.height and \
                        self.is_free((next_x, next_y)) and dist[next_y][next_x] == math.inf:
                    dist[next_y][next_x] = dist[y][x] + 1
                    prev[next_y][next_x] = (x, y)
                    queue.append((next_x, next_y))
        x, y = target
        if dist[y][x] == math.inf or start == target:
            return start
        while prev[y][x] != start:
            x, y = prev[y][x]
        return x, y

    def move_enemy(self):
        x, y = self.find_path_step()
        self.rect = self.image.get_rect().move(tile_width * x, tile_height * y)
        self.rect.move(tile_width * x, tile_height * y)
        self.pos_in_cube = (self.rect.x // tile_width, self.rect.y // tile_height)


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "                   Правила игры:",
                  "Правил нет",
                  "да и вообще у вас нет прав в этой игре",
                  "поэтому даже если захотите что-то сделать, ",
                  "то ничего не получится("
                  ]

    fon = pygame.transform.scale(load_image('fon.jpg'), SIZE)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_hero, new_enemy, finish, x, y = None, None, None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('empty', x, y)
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_hero = Player(x, y)
            elif level[y][x] == '%':
                finish = Tile('finish', x, y)
            elif level[y][x] == '$':
                Tile('empty', x, y)
                new_enemy = Enemy(x, y)
    return new_hero, new_enemy, finish, x, y


def move(player, movement):
    x, y = player.pos
    if movement == "u":
        if lev[y - 1][x] != "#":
            player.move(x, y - 1)
    elif movement == "d":
        if lev[y + 1][x] != "#":
            player.move(x, y + 1)
    elif movement == "l":
        if lev[y][x - 1] != "#":
            player.move(x - 1, y)
    elif movement == "r":
        if lev[y][x + 1] != "#":
            player.move(x + 1, y)


difficulty = pygame_gui.elements.ui_drop_down_menu.UIDropDownMenu(
    options_list=['map_1', 'map_2'], starting_option='map_0',
    relative_rect=pygame.Rect((800, 10), (100, 25)), manager=manager
)
difficulty_l = pygame_gui.elements.ui_drop_down_menu.UIDropDownMenu(
    options_list=['HARD', 'NORMAL', 'EASY'], starting_option='NORMAL',
    relative_rect=pygame.Rect((800, 50), (100, 25)), manager=manager
)
start_screen()
lev = load_level('map_0')
player, evil, end, level_x, level_y = generate_level(lev)
running = True
game_over = False
while running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            confirmation_dialog = pygame_gui.windows.UIConfirmationDialog(
                rect=pygame.Rect((250, 200), (300, 200)), manager=manager,
                window_title='Подтвердите действие',
                action_long_desc="Вы уверенны, что хотите выйти?",
                action_short_name='OK',
                blocking=True
            )
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                running = False
            if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == difficulty:
                    screen.fill("black")

                    all_sprites = pygame.sprite.Group()
                    enemy_group = pygame.sprite.Group()
                    player_group = pygame.sprite.Group()

                    lev = load_level(str(event.text))
                    player, evil, end, level_x, level_y = generate_level(lev)
                    pygame.display.flip()

                    all_sprites.draw(screen)
                    player_group.draw(screen)
                    enemy_group.draw(screen)

                if event.ui_element == difficulty_l:
                    if event.text == 'HARD':
                        pygame.time.set_timer(MOVE_ENEMIES_EVENT, 100)
                    if event.text == 'NORMAL':
                        pygame.time.set_timer(MOVE_ENEMIES_EVENT, 500)
                    if event.text == 'EASY':
                        pygame.time.set_timer(MOVE_ENEMIES_EVENT, 1000)

        if pygame.key.get_pressed()[pygame.K_LEFT]:
            move(player, 'l')
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            move(player, 'r')
        if pygame.key.get_pressed()[pygame.K_UP]:
            move(player, 'u')
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            move(player, 'd')

        manager.process_events(event)

        if not game_over:
            if event.type == MOVE_ENEMIES_EVENT:
                evil.move_enemy()

            screen.fill("black")
            manager.update(time_delta)
            screen.blit(background, (0, 0))

            all_sprites.draw(screen)
            player_group.draw(screen)
            enemy_group.draw(screen)

            manager.draw_ui(screen)
            if end.finish == player.pos:
                show_message(screen, 'U won')
                game_over = True
            if evil.pos_in_cube == player.pos:
                show_message(screen, 'U lose noob')
                game_over = True
        else:
            pygame.time.set_timer(MOVE_ENEMIES_EVENT, 0)
            if event.type == TIMER_QUIT:
                pygame.quit()
    clock.tick(FPS)
    pygame.display.flip()
pygame.quit()
