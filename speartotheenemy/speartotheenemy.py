

import pygame, sys, random, heapq

#      _____________________________
# ___/ Pygame İnit ve Temel Ayarlar \______________________________________ 
pygame.init()
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1024, 1024
TILE_SIZE = 32
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SPEAR TO ENEMY")

# Renkler
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
HIGHLIGHT_COLOR = (150, 150, 150)

clock = pygame.time.Clock()
FPS = 60

# Font tanımları
TITLE_FONT = pygame.font.Font(None, 100)
BUTTON_FONT = pygame.font.Font(None, 60)
CREDITS_FONT = pygame.font.Font(None, 40)

# Assetlerin yolu
ASSET_BASE_PATH = r'C:\Users\murat\Desktop\speartotheenemy\Assets' # Assetlerin nihai yolu, lütfen kendi bilgisayarınızda yolu doğru şekilde ayarlayın.
MUSIC_PATH = r'C:\Users\murat\Desktop\speartotheenemy\Music' #Music dosyasının nihai yolu, lütfen kendi bilgisayarınızda yolu doğru şekilde ayarlayın.
#__________________________________________________________________________________________________________________________________________________________________

#      ______________________
# ___/ Yardımcı Fonksiyonlar \______________________________________ 
def load_image(path, size=None, use_convert_alpha=True):
    try:
        image = pygame.image.load(path)
        if use_convert_alpha:
            image = image.convert_alpha()
        else:
            image = image.convert()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except pygame.error as e:
        print(f"Image load error: {path}\n{e}")
        sys.exit()

def draw_text(text, font, color, surface, x, y, center_align=True):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    if center_align:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)
    return text_rect

# Arkaplan resimleri yükleme
try:
    menu_background_image = load_image(f"{ASSET_BASE_PATH}/background0.png", (WIDTH, HEIGHT))
except Exception:
    menu_background_image = None
try:
    game_background_image = load_image(f"{ASSET_BASE_PATH}/black.jpg", (WIDTH, HEIGHT))
except Exception:
    game_background_image = None

#      _______________________________________
# ___/ Walls Sınıfı: Duvarlar ve Harita Verisi\______________________________________ 
class Walls:
    def __init__(self):
        self.wall_rects = []
        paris_sprite_info = {
            2: (f"{ASSET_BASE_PATH}/Wall1.png", 1),
            3: (f"{ASSET_BASE_PATH}/Wall1_Dik.png", 1),
            4: (f"{ASSET_BASE_PATH}/Wall2.png", 1),
            5: (f"{ASSET_BASE_PATH}/Wall3.png", 1),
            6: (f"{ASSET_BASE_PATH}/Mermer.png", 1),
            7: (f"{ASSET_BASE_PATH}/Mermer2.png", 1),
            8: (f"{ASSET_BASE_PATH}/Mermer3.png", 1),
            9: (f"{ASSET_BASE_PATH}/Mermer4.png", 1),
            10: (f"{ASSET_BASE_PATH}/Mermer_Red.png", 1),
            11: (f"{ASSET_BASE_PATH}/Mermer_Red_2.png", 1),
            12: (f"{ASSET_BASE_PATH}/Mermer_Red_4.png", 1),
            13: (f"{ASSET_BASE_PATH}/Mermer_Blue.png", 1),
            14: (f"{ASSET_BASE_PATH}/Mermer_Blue_2.png", 1),
        }
        self.paris_tiles = {}
        for code, (filename, width) in paris_sprite_info.items():
            try:
                image = pygame.image.load(filename).convert_alpha()
                image = pygame.transform.scale(image, (TILE_SIZE * width, TILE_SIZE))
                self.paris_tiles[code] = {"image": image, "width": width}
            except pygame.error as e:
                print(f"Hata: Duvar resmi yuklenemedi - {filename}\n{e}")
                fallback_image = pygame.Surface((TILE_SIZE * width, TILE_SIZE))
                fallback_image.fill(BLACK)
                self.paris_tiles[code] = {"image": fallback_image, "width": width}

        self.level_map = [
            [0,0,3,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,3],
            [0,0,3,7,7,7,7,7,7,7,7,7,7,3,14,14,14,14,3,7,7,7,7,7,7,7,7,7,7,3],
            [0,0,3,7,6,6,6,6,6,6,6,6,6,3,14,13,13,13,3,7,6,6,6,6,6,6,6,6,6,3],
            [0,0,3,7,6,2,2,2,2,2,2,6,6,3,14,13,13,13,3,7,6,2,2,2,2,2,2,9,6,3],
            [0,0,3,7,6,3,7,7,7,7,7,9,6,3,14,13,13,13,3,7,6,8,7,7,7,7,3,7,6,3],
            [0,0,3,7,6,3,7,6,6,6,6,6,6,8,7,9,6,8,7,7,6,6,6,6,6,8,3,7,6,3],
            [0,0,3,7,6,8,7,6,3,9,6,6,6,6,6,6,6,6,6,6,6,6,6,3,9,6,6,8,6,3],
            [0,0,3,7,6,6,6,6,3,7,6,6,6,6,6,6,6,6,6,6,6,6,6,3,7,6,6,6,6,3],
            [0,0,3,2,2,2,6,6,3,7,9,6,6,6,6,6,6,6,6,6,6,6,6,3,7,6,2,2,2,3],
            [0,0,3,7,7,7,9,6,2,2,2,6,6,2,2,2,2,2,2,6,6,2,2,2,7,6,8,7,7,3],
            [0,0,3,7,6,6,6,6,8,7,7,9,6,8,7,7,7,7,7,9,6,8,7,7,7,6,6,6,6,3],
            [0,0,3,7,6,3,9,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,3,9,6,3],
            [0,0,3,7,6,3,7,9,6,6,3,9,6,3,12,10,10,10,3,9,6,3,9,6,6,6,3,7,6,3],
            [0,0,3,7,6,2,2,2,6,6,3,7,6,3,11,10,10,10,3,7,6,3,7,6,2,2,2,7,6,3],
            [0,0,3,7,6,8,7,7,9,6,3,7,6,3,11,10,10,10,3,7,6,3,7,6,8,7,7,7,6,3],
            [0,0,3,7,6,6,6,6,6,6,3,7,6,3,11,10,10,10,3,7,6,3,7,9,6,6,6,6,6,3],
            [0,0,3,7,6,3,9,6,2,2,3,7,6,2,2,2,2,2,2,7,6,3,2,2,6,6,3,9,6,3],
            [0,0,3,7,6,3,7,6,8,7,7,7,6,8,7,7,7,7,7,7,6,8,7,7,9,6,3,7,6,3],
            [0,0,3,7,6,3,7,9,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,3,7,6,3],
            [0,0,3,7,6,2,2,2,6,6,2,2,2,2,6,6,6,6,2,2,2,2,9,6,2,2,2,7,6,3],
            [0,0,3,7,6,8,7,7,9,6,3,7,7,7,9,6,6,6,8,7,7,3,7,6,8,7,7,7,6,3],
            [0,0,3,7,6,6,6,6,6,6,3,7,6,6,6,6,6,6,6,6,6,3,7,6,6,6,6,6,6,3],
            [0,0,3,2,2,6,6,3,9,6,3,7,6,2,2,2,2,2,2,6,6,3,7,6,3,9,6,2,2,3],
            [0,0,3,7,6,6,6,3,7,6,6,8,6,8,7,7,7,7,7,9,6,8,7,6,3,7,6,8,7,3],
            [0,0,3,7,6,6,6,3,7,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,3,7,9,6,6,3],
            [0,0,3,7,6,2,2,2,7,6,3,2,2,2,6,6,6,6,2,2,2,3,9,6,2,2,2,6,6,3],
            [0,0,3,7,6,8,7,7,7,6,3,7,7,7,9,6,6,6,8,7,7,3,7,6,8,7,7,9,6,3],
            [0,0,3,7,6,6,6,6,6,6,3,7,6,6,6,6,6,6,6,6,6,3,7,6,6,6,6,6,6,3],
            [0,0,3,7,6,6,6,6,6,6,3,7,6,6,6,6,6,6,6,6,6,3,7,6,6,6,6,6,6,3],
            [0,0,3,7,6,6,6,6,6,6,3,7,6,6,6,6,6,6,6,6,6,3,7,6,6,6,6,6,6,3],
            [0,0,3,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,3]
        ]

        self.wall_rects.clear()
        collider_tile_codes = {2, 3, 4, 5}
        for row_index, row in enumerate(self.level_map):
            for col_index, tile_code in enumerate(row):
                if tile_code in collider_tile_codes:
                    width = self.paris_tiles[tile_code]["width"]
                    rect = pygame.Rect(
                        col_index * TILE_SIZE,
                        row_index * TILE_SIZE,
                        TILE_SIZE * width,
                        TILE_SIZE
                    )
                    self.wall_rects.append(rect)

    def draw(self, surface):
        for row_index, row in enumerate(self.level_map):
            for col_index, tile_code in enumerate(row):
                tile = self.paris_tiles.get(tile_code)
                if tile:
                    surface.blit(tile["image"], (col_index * TILE_SIZE, row_index * TILE_SIZE))


#      _______________________________________
# ___/ Player Sınıfı: Oyuncu Hareket ve Çizim \_____________________________________________________
class Player:
    def __init__(self):
        self.image_right = load_image(f"{ASSET_BASE_PATH}/Character_right.png", (30, 54))
        self.pos = pygame.Vector2(WIDTH // 2, HEIGHT // 1.15)
        self.speed = 200 # Oyuncunun hızını arttırmak oyundan daha farklı şeyleri zorlaştırabilir.
        self.facing_left = False
        self.rect = self.image_right.get_rect(center=self.pos)
        self.surface = self.image_right

    def update(self, dt, keys, wall_rects):
        direction = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction.x += 1

        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.pos.x += direction.x * self.speed * dt
            self.rect.centerx = self.pos.x
            for wall in wall_rects:
                if self.rect.colliderect(wall):
                    if direction.x > 0:
                        self.rect.right = wall.left
                    elif direction.x < 0:
                        self.rect.left = wall.right
                    self.pos.x = self.rect.centerx

            self.pos.y += direction.y * self.speed * dt
            self.rect.centery = self.pos.y
            for wall in wall_rects:
                if self.rect.colliderect(wall):
                    if direction.y > 0:
                        self.rect.bottom = wall.top
                    elif direction.y < 0:
                        self.rect.top = wall.bottom
                    self.pos.y = self.rect.centery

            if direction.x < 0:
                self.facing_left = True
            elif direction.x > 0:
                self.facing_left = False

        self.surface = pygame.transform.flip(self.image_right, True, False) if self.facing_left else self.image_right
        self.rect.center = self.pos

    def draw(self, screen):
        screen.blit(self.surface, self.rect.topleft)

#      _________________________________________
# ___/ Money Sınıfı: Toplanabilir Para Objeleri \______________________________ 
class Money:
    def __init__(self, position):
        self.image = load_image(f"{ASSET_BASE_PATH}/Money.png", (12, 12))
        self.rect = pygame.Rect(position[0], position[1], 24, 24)

    def draw(self, screen):
        screen.blit(self.image, self.rect.center)


#      ______________________________________
# ___/ Spear Sınıfı: Mızrak Hareketi ve Çizim \_________________________________________________________________________
class Spear:
    def __init__(self):
        self.image_original = load_image(f"{ASSET_BASE_PATH}/spear_c.png", (62, 30))
        self.thrown = False
        self.timer = 0.0
        self.pos = pygame.Vector2(0, 0)
        self.movement_direction = pygame.Vector2(0, 0)
        self.speed = 400
        self.visual_angle = 0.0
        self.lifetime = 1.5

    def throw(self, start_pos, target_pos, facing_left):
        self.thrown = True
        self.timer = 0.0
        self.pos = start_pos.copy()
        direction = pygame.Vector2(target_pos) - start_pos

        if direction.length_squared() > 0:
            self.movement_direction = direction.normalize()
        else:
            self.movement_direction = pygame.Vector2(-1, 0) if facing_left else pygame.Vector2(1, 0)

        self.visual_angle = direction.angle_to(pygame.Vector2(1, 0))

    def update(self, dt, player_pos):
        if self.thrown:
            self.timer += dt
            self.pos += self.movement_direction * self.speed * dt
            if self.timer >= self.lifetime:
                self.thrown = False
        else:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dir_to_mouse = pygame.Vector2(mouse_x - player_pos.x, mouse_y - player_pos.y)
            if dir_to_mouse.length_squared() > 0:
                self.visual_angle = dir_to_mouse.angle_to(pygame.Vector2(1, 0))

    def draw(self, screen, player_pos):
        center_pos = self.pos if self.thrown else player_pos
        rotated_surface = pygame.transform.rotate(self.image_original, self.visual_angle)
        rect = rotated_surface.get_rect(center=center_pos)
        screen.blit(rotated_surface, rect.topleft)


#      ___________________________________________
# ___/ Enemy Sınıfı: Düşman Yapay Zekası ve Çizim \_______________________________________________________________________________ 
class Enemy:
    def __init__(self, pos, speed, color_type="red"):
        self.pos = pygame.Vector2(pos)
        self.speed = speed
        self.color_type = color_type
        if color_type == "red":
            self.image_right = load_image(f"{ASSET_BASE_PATH}/Enemy_Red_Image.png", (30, 54))
            self.image_left = load_image(f"{ASSET_BASE_PATH}/Enemy_Red_Image2.png", (30, 54))
        else:
            self.image_right = load_image(f"{ASSET_BASE_PATH}/Enemy_Blue_Image.png", (30, 54))
            self.image_left = load_image(f"{ASSET_BASE_PATH}/Enemy_Blue_Image2.png", (30, 54))
        self.current_image = self.image_right
        self.rect = self.image_right.get_rect(center=self.pos)
        self.facing_right = True
        self.path = []
        self.path_index = 0
        self.repath_timer = 0

    def grid_pos(self):
        # Düşmanın bulunduğu tile koordinatları
        return (int(self.pos.x // TILE_SIZE), int(self.pos.y // TILE_SIZE))

    def find_path(self, target_pos, walls):
        # A* algoritması ile yol bulma (temel hareket: dört yönlü)
        start = self.grid_pos()
        end = (int(target_pos.x // TILE_SIZE), int(target_pos.y // TILE_SIZE))
        wall_set = set((rect.x // TILE_SIZE, rect.y // TILE_SIZE) for rect in walls.wall_rects)
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: abs(start[0] - end[0]) + abs(start[1] - end[1])}

        while open_set:
            _, current = heapq.heappop(open_set)
            if current == end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if (0 <= neighbor[0] < WIDTH // TILE_SIZE and 0 <= neighbor[1] < HEIGHT // TILE_SIZE and neighbor not in wall_set):
                    tentative_g = g_score[current] + 1
                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f_score[neighbor] = tentative_g + abs(neighbor[0] - end[0]) + abs(neighbor[1] - end[1])
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return []

    def update(self, player_pos, player_rect, dt, walls):
        # Yol güncelleme
        self.repath_timer += dt
        if self.repath_timer > 0.5 or not self.path:
            self.path = self.find_path(player_pos, walls)
            self.path_index = 0
            self.repath_timer = 0
        
        # Yolun sonraki noktasına hareket et
        if self.path and self.path_index < len(self.path):
            target_tile = self.path[self.path_index]
            target_pixel = pygame.Vector2(target_tile[0] * TILE_SIZE + TILE_SIZE//2, target_tile[1] * TILE_SIZE + TILE_SIZE//2)
            direction = target_pixel - self.pos
            if direction.length_squared() > 4:
                move = direction.normalize() * self.speed * dt
                if move.length_squared() > direction.length_squared():
                    self.pos = target_pixel
                else:
                    self.pos += move
            else:
                self.path_index += 1
        else:
            # Hedef oyuncu ise doğrudan hareket
            direction = player_pos - self.pos
            if direction.length_squared() > 4:
                self.pos += direction.normalize() * self.speed * dt

        # Yüzü hedefe dön
        if self.path and self.path_index < len(self.path):
            direction_check = pygame.Vector2(self.path[self.path_index][0] * TILE_SIZE, self.path[self.path_index][1] * TILE_SIZE) - self.pos
        else:
            direction_check = player_pos - self.pos

        if direction_check.x > 0:
            self.facing_right = True
            self.current_image = self.image_right
        else:
            self.facing_right = False
            self.current_image = self.image_left

        self.rect = self.current_image.get_rect(center=self.pos)

    def draw(self, screen):
        screen.blit(self.current_image, self.rect.topleft)


#      ______________________________________
# ___/ UIManager Tekil Sınıfı: Skor Yönetimi \__________________________ 
class UIManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UIManager, cls).__new__(cls)
            cls._instance.score = 0
        return cls._instance

    def add_score(self, amount):
        self.score += amount

    def get_score(self):
        return self.score

    def reset_score(self):
        self.score = 0

#      _________________________________________________________
# ___/ GameState Abstract Sınıfı: Diğer Durumların Temel Sınıfı \_________
class GameState:
    def __init__(self, controller):
        self.controller = controller

    def handle_events(self, events):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass


#      __________________________________________
# ___/ MainMenu Sınıfı: Ana Menü durumu ve Müzik \________________________________________________________________________________________________________
class MainMenu(GameState):
    def __init__(self, controller):
        super().__init__(controller)
        self.button_y_start = HEIGHT // 1.68
        self.button_spacing = 100
        self.play_button_rect = pygame.Rect(0, 0, 1, 1)
        self.credits_button_rect = pygame.Rect(0, 0, 1, 1)
        self.exit_button_rect = pygame.Rect(0, 0, 1, 1)
        self.music_loaded = False
        self.init_music()

    def init_music(self):
        try:
            pygame.mixer.music.load(f"{MUSIC_PATH}/menu-music.wav")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            self.music_loaded = True
        except Exception as e:
            print(f"Muzik yuklenemedi: {e}\nAna menu muzik olmadan baslatiliyor.")
            self.music_loaded = False

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.QUIT:
                self.controller.quit_game()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.play_button_rect.collidepoint(mouse_pos):
                    if self.music_loaded:
                        pygame.mixer.music.stop()  # Müzik durduruluyor
                    self.controller.start_game()
                elif self.credits_button_rect.collidepoint(mouse_pos):
                    self.controller.show_credits()
                elif self.exit_button_rect.collidepoint(mouse_pos):
                    self.controller.quit_game()
            elif event.type == pygame.KEYDOWN:
                if self.music_loaded:
                    if event.key == pygame.K_PLUS:
                        current_volume = pygame.mixer.music.get_volume()
                        new_volume = min(current_volume + 0.1, 1.0)
                        pygame.mixer.music.set_volume(new_volume)
                    elif event.key == pygame.K_MINUS:
                        current_volume = pygame.mixer.music.get_volume()
                        new_volume = max(current_volume - 0.1, 0.0)
                        pygame.mixer.music.set_volume(new_volume)

    def update(self, dt):
        pass

    def draw(self, screen):
        if menu_background_image:
            screen.blit(menu_background_image, (0, 0))
        else:
            screen.fill(DARK_GRAY)

        mouse_pos = pygame.mouse.get_pos()
        play_color = HIGHLIGHT_COLOR if self.play_button_rect.collidepoint(mouse_pos) else WHITE
        self.play_button_rect = draw_text("Play", BUTTON_FONT, play_color, screen, WIDTH // 2, self.button_y_start)

        credits_color = HIGHLIGHT_COLOR if self.credits_button_rect.collidepoint(mouse_pos) else WHITE
        self.credits_button_rect = draw_text("Credits", BUTTON_FONT, credits_color, screen, WIDTH // 2, self.button_y_start + self.button_spacing)

        exit_color = HIGHLIGHT_COLOR if self.exit_button_rect.collidepoint(mouse_pos) else WHITE
        self.exit_button_rect = draw_text("Exit", BUTTON_FONT, exit_color, screen, WIDTH // 2, self.button_y_start + self.button_spacing * 2)


#      ______________________________________
# ___/ Credits Sınıfı: Geliştirici Bilgileri \____________________________________________________________________________________
class Credits(GameState):
    def __init__(self, controller):
        super().__init__(controller)
        self.back_button_rect = pygame.Rect(0, 0, 1, 1)

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.QUIT:
                self.controller.quit_game()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.controller.back_to_menu()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.back_button_rect.collidepoint(mouse_pos):
                self.controller.back_to_menu()

    def update(self, dt):
        pygame.mixer.music.stop()
        #pass

    def draw(self, screen):
        screen.fill(DARK_GRAY)
        title_y = HEIGHT // 4
        line_height = CREDITS_FONT.get_linesize() + 10
        draw_text("Credits", TITLE_FONT, WHITE, screen, WIDTH // 2, title_y)

        current_y = HEIGHT // 2 - line_height * 1.5
        draw_text("Developers: Kerem Kekulluoglu, Muratcan Sariyildiz", CREDITS_FONT, WHITE, screen, WIDTH // 2, current_y)
        current_y += line_height
        draw_text("Designer: Ege Alpogan", CREDITS_FONT, WHITE, screen, WIDTH // 2, current_y)
        current_y += line_height
        draw_text("Theme: Medieval", CREDITS_FONT, WHITE, screen, WIDTH // 2, current_y)

        mouse_pos = pygame.mouse.get_pos()
        back_color = HIGHLIGHT_COLOR if self.back_button_rect.collidepoint(mouse_pos) else WHITE
        self.back_button_rect = draw_text("Back to Main Menu (ESC)", BUTTON_FONT, back_color, screen, WIDTH // 2, HEIGHT * 3 // 4 + 50)


#      ________________________________________________
# ___/ GameOver Sınıfı: Oyun Kaybetme Durumu ve Arayüz \_______________________________________________________
class GameOver(GameState):
    def __init__(self, controller):
        self.ui_manager = UIManager()
        super().__init__(controller)
        self.retry_button_rect = pygame.Rect(0, 0, 1, 1)
        self.menu_button_rect = pygame.Rect(0, 0, 1, 1)

        try:
            self.background = load_image(f"{ASSET_BASE_PATH}/game_over_bg.png", (WIDTH, HEIGHT))
        except (pygame.error, FileNotFoundError) as e:
            print(f"Game over background image not loaded: {ASSET_BASE_PATH}/game_over_bg.png\nError: {e}")
            self.background = None

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.QUIT:
                self.controller.quit_game()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.retry_button_rect.collidepoint(mouse_pos):
                    self.controller.start_game()
                    self.ui_manager.reset_score()
                elif self.menu_button_rect.collidepoint(mouse_pos):
                    self.controller.back_to_menu()
                    self.ui_manager.reset_score()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.controller.back_to_menu()
                self.ui_manager.reset_score()

    def update(self, dt):
        pass

    def draw(self, screen):
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(DARK_GRAY)

        score_text = f"Score: {self.ui_manager.get_score()}"
        draw_text(score_text, BUTTON_FONT, WHITE, screen, 375, 475, center_align=False)

        mouse_pos = pygame.mouse.get_pos()
        color = HIGHLIGHT_COLOR if self.retry_button_rect.collidepoint(mouse_pos) else WHITE
        self.retry_button_rect = draw_text("Try Again", BUTTON_FONT, color, screen, WIDTH // 2, HEIGHT // 2 + 75)

        color = HIGHLIGHT_COLOR if self.menu_button_rect.collidepoint(mouse_pos) else WHITE
        self.menu_button_rect = draw_text("Back Main Menu", BUTTON_FONT, color, screen, WIDTH // 2, HEIGHT // 2 + 200)

        hint_text = "Increasing my score fills me with determination"
        hint_img_path = f"{ASSET_BASE_PATH}/tip_icon.png"

        try:
            hint_image = load_image(hint_img_path, (74, 74))
            img_x = WIDTH // 2 - 342
            img_y = HEIGHT // 2 + 275
            screen.blit(hint_image, (img_x, img_y))
            text_x = img_x + 74 + 10
            text_y = img_y + 32
            draw_text(hint_text, CREDITS_FONT, WHITE, screen, text_x, text_y, center_align=False)
        except Exception:
            draw_text(hint_text, CREDITS_FONT, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 275)


#      _____________________________________________
# ___/ YouWin Sınıfı: Oyun Kazanma Durumu ve Arayüz \___________________________________________________
class YouWin(GameState):
    def __init__(self, controller):
        self.ui_manager = UIManager()
        super().__init__(controller)
        self.menu_button_rect = pygame.Rect(0, 0, 1, 1)

        try:
            self.background = load_image(f"{ASSET_BASE_PATH}/you_win_bg.png", (WIDTH, HEIGHT))
        except (pygame.error, FileNotFoundError) as e:
            print(f"You win background image not loaded: {ASSET_BASE_PATH}/you_win_bg.png\nError: {e}")
            self.background = None

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.QUIT:
                self.controller.quit_game()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_button_rect.collidepoint(mouse_pos):
                    self.controller.back_to_menu()
                    self.ui_manager.reset_score()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.controller.back_to_menu()

    def update(self, dt):
        pass

    def draw(self, screen):
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(DARK_GRAY)

        mouse_pos = pygame.mouse.get_pos()
        color = HIGHLIGHT_COLOR if self.menu_button_rect.collidepoint(mouse_pos) else WHITE
        self.menu_button_rect = draw_text("Back Main Menu", BUTTON_FONT, color, screen, WIDTH // 2, HEIGHT // 2 + 200)

        score_text = f"Score: {self.ui_manager.get_score()}"
        draw_text(score_text, BUTTON_FONT, WHITE, screen, 375, 475, center_align=False)

        hint_text = "Winning the game fills me with determination"
        hint_img_path = f"{ASSET_BASE_PATH}/tip_icon.png"

        try:
            hint_image = load_image(hint_img_path, (74, 74))
            img_x = WIDTH // 2 - 342
            img_y = HEIGHT // 2 + 275
            screen.blit(hint_image, (img_x, img_y))
            text_x = img_x + 74 + 10
            text_y = img_y + 32
            draw_text(hint_text, CREDITS_FONT, WHITE, screen, text_x, text_y, center_align=False)
        except Exception:
            draw_text(hint_text, CREDITS_FONT, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 275)


        congratulations_text = "CONGRATULATIONS!! Murat Can will treat you to any coffee you want."
        draw_text(congratulations_text, CREDITS_FONT, YELLOW, screen, WIDTH // 2, img_y + 100, center_align=True)

#      __________________________________________________
# ___/ Playing Sınıfı: Oyun içi İşlemler, Mantık ve Çizim \_________
class Playing(GameState):
    def __init__(self, controller):
        super().__init__(controller)
        self.player = Player()
        self.spear = Spear()
        self.walls = Walls()
        self.enemies = []
        self.num_enemies = 8
        self.enemy_speed_default = 120
        self.init_enemies()
        self.spawn_timer = 0
        self.spawn_interval = 5
        self.game_time = 0
        self.last_spawn_interval_update = 0
        self.ui_manager = UIManager()
        self.money_objects = []
        self.spawn_money_objects()
        self.pending_game_over = False
        self.game_over_timer = 0
        self.pending_you_win = False
        self.you_win_timer = 0
        self.music_loaded = False
        self.init_music()

    def init_music(self):
        try:
            pygame.mixer.music.load(f"{MUSIC_PATH}/playing-music.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            self.music_loaded = True
        except Exception as e:
            print(f"Muzik yuklenemedi: {e}\nPlaying sinifi müzik olmadan baslatiliyor.")
            self.music_loaded = False

    def spawn_money_objects(self):
        self.money_objects.clear()
        tile_size = TILE_SIZE
        for row_index, row in enumerate(self.walls.level_map):
            for col_index, value in enumerate(row):
                if value in (6, 7, 8, 9):
                    x = col_index * tile_size
                    y = row_index * tile_size
                    money = Money((x, y))
                    self.money_objects.append(money)

    def check_money_collisions(self):
        for money in self.money_objects[:]:
            if self.player.rect.colliderect(money.rect):
                self.money_objects.remove(money)
                self.ui_manager.add_score(25)

    def spawn_enemy(self):
        spawn_points = [
            ((512, 450), "red"),
            ((512, 50), "blue")
        ]
        for point, color in spawn_points:
            speed = self.enemy_speed_default + random.randint(-10, 10)
            new_enemy = Enemy(point, speed, color_type=color)
            self.enemies.append(new_enemy)

    def init_enemies(self):
        self.enemies.clear()
        half = self.num_enemies // 2
        for _ in range(half):
            spawn_point = (512, 450)
            speed = self.enemy_speed_default + random.randint(-10, 10)
            self.enemies.append(Enemy(spawn_point, speed, color_type="red"))
        for _ in range(self.num_enemies - half):
            spawn_point = (512, 50)
            speed = self.enemy_speed_default + random.randint(-10, 10)
            self.enemies.append(Enemy(spawn_point, speed, color_type="blue"))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.controller.quit_game()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.controller.back_to_menu()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.spear.thrown:
                    mouse_pos = pygame.mouse.get_pos()
                    self.spear.throw(self.player.pos, mouse_pos, self.player.facing_left)
            elif event.type == pygame.KEYDOWN:
                if self.music_loaded:
                    if event.key == pygame.K_PLUS:
                        current_volume = pygame.mixer.music.get_volume()
                        new_volume = min(current_volume + 0.1, 1.0)
                        pygame.mixer.music.set_volume(new_volume)
                    elif event.key == pygame.K_MINUS:
                        current_volume = pygame.mixer.music.get_volume()
                        new_volume = max(current_volume - 0.1, 0.0)
                        pygame.mixer.music.set_volume(new_volume)

    def update(self, dt):
        if self.pending_game_over and pygame.time.get_ticks() >= self.game_over_timer:
            self.controller.current_state = self.controller.states['game_over']
            self.pending_game_over = False
            pygame.mixer.music.stop()
        if self.pending_you_win and pygame.time.get_ticks() >= self.you_win_timer:
            self.controller.current_state = self.controller.states['you_win']
            self.pending_you_win = False
            pygame.mixer.music.stop()
        if self.pending_game_over or self.pending_you_win:
            return

        self.game_time += dt
        keys = pygame.key.get_pressed()
        self.player.update(dt, keys, self.walls.wall_rects)
        self.check_money_collisions()
        self.spear.update(dt, self.player.pos)

        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                self.pending_game_over = True
                self.game_over_timer = pygame.time.get_ticks() + 1000
                break

        if not self.money_objects:
            self.pending_you_win = True
            self.you_win_timer = pygame.time.get_ticks() + 1000
            return

        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_enemy()
            self.spawn_timer = 0

        for enemy in self.enemies:
            enemy.update(self.player.pos, self.player.rect, dt, self.walls)

        if self.spear.thrown:
            spear_pos = self.spear.pos
            enemies_to_remove = []
            for enemy in self.enemies:
                if enemy.rect.collidepoint(spear_pos.x, spear_pos.y):
                    enemies_to_remove.append(enemy)
            for enemy in enemies_to_remove:
                self.enemies.remove(enemy)
                self.ui_manager.add_score(100)

        if self.game_time - self.last_spawn_interval_update >= 30 and self.spawn_interval > 1:
            self.spawn_interval -= 1
            self.last_spawn_interval_update = self.game_time

    def draw_money_objects(self, screen):
        for money in self.money_objects:
            money.draw(screen)

    def draw_score(self, screen):
        score_text = f"Score: {self.ui_manager.get_score()}"
        draw_text(score_text, BUTTON_FONT, WHITE, screen, 20, 20, center_align=False)

    def draw(self, screen):
        if game_background_image:
            screen.blit(game_background_image, (0, 0))
        else:   
            screen.fill(LIGHT_GRAY)

        self.walls.draw(screen)
        self.player.draw(screen)
        self.spear.draw(screen, self.player.pos)
        for enemy in self.enemies:
            enemy.draw(screen)
        self.draw_money_objects(screen)
        self.draw_score(screen)

#      _______________________________________________
# ___/ GameController Sınıfı: Durum Yönetimi ve Döngü \________
class GameController:
    def __init__(self):
        self.states = {
            'main_menu': MainMenu(self),
            'playing': None,
            'credits': Credits(self),
            'game_over': GameOver(self),
            'you_win': YouWin(self)
        }
        self.current_state = self.states['main_menu']
        self.running = True

    def start_game(self):
        self.states['playing'] = Playing(self)
        self.current_state = self.states['playing']

    def show_credits(self):
        self.current_state = self.states['credits']

    def back_to_menu(self):
        self.current_state = self.states['main_menu']
        if hasattr(self.current_state, "init_music"):
            self.current_state.init_music()

    def quit_game(self):
        self.running = False

    def game_loop(self):
        while self.running:
            dt = clock.tick(FPS) / 1000.0
            events = pygame.event.get()
            self.current_state.handle_events(events)
            self.current_state.update(dt)
            self.current_state.draw(screen)
            pygame.display.update()


#      _______________________
# ___/ Ana Program Başlangıcı \_______
if __name__ == "__main__":
    game = GameController()
    game.game_loop()
    if pygame.get_init():
        pygame.quit()
    sys.exit()
