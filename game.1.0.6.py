import random
import time

import pygame
from pygame import mixer

pygame.init()  # Init pygame(khởi tạo tất cả các module cần thiết cho PyGame)
# Đặt fps
FPS = 60
fpsClock = pygame.time.Clock()

# Các đường dẫn
linkBackGround = './data/background 1.jpg'  # Đường dẫn ảnh background
linkEnemy = './data/enemy.png'  # Đường dẫn ảnh Enemy
linkPlanes = './data/player.png'  # Đường dẫn ảnh Planes
linkPlayerBullet = './data/bullet.png'  # Đường dẫn ảnh
linkPlayerLeftBullet = './data/bullet left.png'
linkPlayerRightBullet = './data/bullet right.png'
linkEnemyBullet_default = './data/bullet 2.png'
linkExplode = './data/explode 5.png'  # Đường dẫn ảnh vụ nổ

musicBullet = mixer.Sound('./data/laser.wav')
musicBackground = mixer.Sound('./data/Victory.wav')
musicTheme = mixer.Sound('./data/musictheme.wav')
musicEnd = mixer.Sound('./data/musicend.mp3')
explodeSound = mixer.Sound('./data/boom.wav')

player_ship = pygame.image.load(linkPlanes)
player_laser = pygame.image.load(linkPlayerBullet)
player_left_laser = pygame.image.load(linkPlayerLeftBullet)
player_right_laser = pygame.image.load(linkPlayerRightBullet)
enemy_ship = pygame.image.load(linkEnemy)
enemy_laser = pygame.image.load(linkEnemyBullet_default)

xScreen, yScreen = 627, 705  # Screen create
VBullet = 10  # Tốc độ Bullet
VPlayer = 8  # Tốc độ Planes
VEnemy = 3  # Tốc độ Enemy
scores = 0  # Điểm số

screen = pygame.display.set_mode((xScreen, yScreen))
pygame.display.set_caption("Group 15 - Space Invaders")
background = pygame.transform.scale(pygame.image.load(linkBackGround), (xScreen, yScreen))
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
FONT = pygame.font.Font(None, 32)
# Menu
button_1_x = xScreen / 2 - 100
button_1_y = yScreen / 2 - 25
button_2_x = xScreen / 2 - 100
button_2_y = yScreen / 2 + 75
button_3_x = xScreen / 2 - 100
button_3_y = yScreen / 2 + 175
button_1 = pygame.Rect(button_1_x, button_1_y, 200, 50)
button_2 = pygame.Rect(button_2_x, button_2_y, 200, 50)
button_3 = pygame.Rect(button_3_x, button_3_y, 200, 50)
paused = False
gameRunning = False
explode_img = pygame.transform.scale(pygame.image.load(linkExplode), (60, 60))


class Laser:
    def __init__(self, img, x, y, width, height):
        self.x = x
        self.y = y
        self.img = pygame.transform.scale(img, (width, height))  # change size image
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self):
        screen.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def moveClusterLeft(self, vel):
        self.y += vel
        self.x += int(vel / 2)

    def moveClusterRight(self, vel):
        self.y += vel
        self.x -= int(vel / 2)

    def off_screen(self, height):
        return self.y > height or self.y < 0

    def collision(self, obj):
        return collide(self, obj)


class Explode():
    def boom(self, x, y):
        # hiệu ứng tiếng nổ
        mixer.Channel(0).play(mixer.Sound(explodeSound))

        # hiển thị vụ nổ
        screen.blit(explode_img, (x, y))
        pygame.display.flip()
        pygame.event.pump()
        pygame.time.delay(20)


class Ship:

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.width = None
        self.height = None
        self.health = health
        self.shootSpeed = 3
        self.COOLDOWN = FPS / self.shootSpeed
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.dame = None
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw()

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(yScreen):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= self.dame
                if obj.health == 0:
                    # cho obj phát nổ
                    crash = Explode()
                    crash.boom(obj.x, obj.y)
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            soundBullet = mixer.Sound(musicBullet)
            soundBullet.set_volume(0.5)
            mixer.Channel(0).play(soundBullet)
            laser = Laser(self.laser_img, self.x + int(self.get_width() / 2) - 12, self.y - 30, 25, 60)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, width, height, health=100):
        super().__init__(x, y, health)
        self.ship_img = pygame.transform.scale(player_ship, (width, height))  # change size image
        self.laser_img = player_laser
        self.left_laser_img = pygame.transform.scale(player_left_laser, (25, 60))
        self.right_laser_img = pygame.transform.scale(player_right_laser, (25, 60))
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.straight = True
        self.cluster = True
        self.straightLasers = []
        self.leftLasers = []
        self.rightLasers = []
        self.max_health = health
        self.dame = 50

    def move_lasers(self, vel, objs):
        global scores
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(yScreen):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        obj.health -= self.dame
                        if obj.health == 0:
                            # cho obj phát nổ
                            crash = Explode()
                            crash.boom(obj.x, obj.y)
                            objs.remove(obj)
                            scores += 1
                        if laser in self.lasers:
                            self.lasers.remove(laser)
        for laser in self.straightLasers:
            laser.move(vel)
            if laser.off_screen(yScreen):
                self.straightLasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        obj.health -= self.dame
                        if obj.health == 0:
                            # cho obj phát nổ
                            crash = Explode()
                            crash.boom(obj.x, obj.y)
                            objs.remove(obj)
                            scores += 1
                        if laser in self.straightLasers:
                            self.straightLasers.remove(laser)
        for laser in self.leftLasers:
            laser.moveClusterLeft(vel)
            if laser.off_screen(yScreen):
                self.leftLasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        obj.health -= self.dame
                        if obj.health == 0:
                            # cho obj phát nổ
                            crash = Explode()
                            crash.boom(obj.x, obj.y)
                            objs.remove(obj)
                            scores += 1
                        if laser in self.leftLasers:
                            self.leftLasers.remove(laser)
        for laser in self.rightLasers:
            laser.moveClusterRight(vel)
            if laser.off_screen(yScreen):
                self.rightLasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        obj.health -= self.dame
                        if obj.health == 0:
                            # cho obj phát nổ
                            crash = Explode()
                            crash.boom(obj.x, obj.y)
                            objs.remove(obj)
                            scores += 1
                        if laser in self.rightLasers:
                            self.rightLasers.remove(laser)

    def clusterShoot(self):
        leftLaser = Laser(self.left_laser_img, self.x + int(self.get_width() / 2) - 12, self.y, 20, 30)
        rightLaser = Laser(self.right_laser_img, self.x + int(self.get_width() / 2) - 12, self.y, 20, 30)
        self.leftLasers.append(leftLaser)
        self.rightLasers.append(rightLaser)

    def straightShoot(self):
        laser = Laser(self.laser_img, self.x + int(self.get_width() / 2) - 17, self.y - 30, 25, 60)
        self.lasers.append(laser)
        laser = Laser(self.laser_img, self.x + int(self.get_width() / 2) - 5, self.y - 30, 25, 60)
        self.straightLasers.append(laser)

    def shoot(self):
        if self.cool_down_counter == 0:
            soundBullet = mixer.Sound(musicBullet)
            soundBullet.set_volume(0.5)
            mixer.Channel(0).play(soundBullet)
            if not self.straight:
                laser = Laser(self.laser_img, self.x + int(self.get_width() / 2) - 12, self.y - 30, 25, 60)
                self.lasers.append(laser)
            else:
                self.straightShoot()
            if self.cluster:
                self.clusterShoot()
            self.cool_down_counter = 1

    def draw(self, window):
        super().draw(window)
        if self.cluster:
            self.drawCluster()
        if self.straight:
            self.drawStraight()
        self.healthbar(window)

    def drawStraight(self):
        for laser in self.straightLasers:
            laser.draw()

    def drawCluster(self):
        for laser in self.leftLasers:
            laser.draw()
        for laser in self.rightLasers:
            laser.draw()

    def healthbar(self, window):
        pygame.draw.rect(window, (0, 0, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (
            self.x, self.y + self.ship_img.get_height() + 10,
            self.ship_img.get_width() * (self.health / self.max_health),
            10))


class Enemy(Ship):
    COLOR_MAP = {
        # "red": (RED_SPACE_SHIP, RED_LASER),
        # "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        # "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
        "default": (enemy_ship, enemy_laser)
    }

    def __init__(self, x, y, color, width, height, vel, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.ship_img = pygame.transform.scale(self.ship_img, (width, height))
        self.enemy_max_health = 100
        self.laser_vel = vel
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.dame = 10
        self.direction = random.choice((True, False))

    def move(self, vel):
        if self.x < 0 or self.x > xScreen - self.get_width():
            self.direction = not self.direction
        self.x = self.x + (- vel if self.direction else vel)
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.laser_img, self.x + int(self.get_width() / 2) - 5, self.y + self.get_height() - 12, 10,
                          30)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (0, 0, 0),
                         (self.x, self.y, self.ship_img.get_width(), 5))
        pygame.draw.rect(window, (255, 0, 0), (
            self.x, self.y, self.ship_img.get_width() * (self.health / self.enemy_max_health), 5))


class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)


def show_texts(x, y, texts, size):  # In chữ
    font = pygame.font.SysFont("comicsans", size)
    text = font.render(str(texts), True, (255, 255, 255))
    screen.blit(text, (x, y))


def show_texts_middle(y, texts, size):  # In chữ ở giữa
    font = pygame.font.SysFont("comicsans", size)
    text = font.render(str(texts), True, (255, 255, 255))
    screen.blit(text, (xScreen / 2 - text.get_width() / 2, y))


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def show_text_menu(x, y, text, size):  # x,y là toạ độ tâm của hcn chứa text
    font = pygame.font.SysFont("comicsansms", size)
    text = font.render(text, True, (255, 255, 0))
    text_rect = text.get_rect(center=(x, y))
    screen.blit(text, text_rect)


def pause():
    global paused
    global gameRunning
    while paused:
        screen.blit(background, (0, 0))
        pygame.draw.rect(screen, (0, 0, 0), button_1)
        show_text_menu(xScreen / 2, 25, "Paused", 30)
        show_text_menu(xScreen / 2, button_1_y + (button_1.height / 2), "Continue", 25)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mixer.stop()
                    paused = False
                    gameRunning = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    if button_1.collidepoint((mx, my)):
                        paused = False
                        mixer.unpause()
                        continue
        pygame.display.update()  # Update


def main_menu():
    global gameRunning
    menu_run = True
    while menu_run:
        screen.blit(background, (0, 0))
        # if self.button_2.collidepoint((self.mx, self.my)):
        #     if self.click:
        #         self.highscores()
        # if self.button_3.collidepoint((self.mx, self.my)):
        #     if self.click:
        #         self.options()

        pygame.draw.rect(screen, (0, 0, 0), button_1)
        pygame.draw.rect(screen, (0, 0, 0), button_2)
        pygame.draw.rect(screen, (0, 0, 0), button_3)
        show_text_menu(xScreen / 2, button_1_y + (button_1.height / 2), "Start", 25)
        show_text_menu(xScreen / 2, button_2_y + (button_2.height / 2), "Highscores", 25)
        show_text_menu(xScreen / 2, button_3_y + (button_3.height / 2), "Options", 25)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    if button_1.collidepoint((mx, my)):
                        gameRunning = True
                        run()
                        continue

        pygame.display.update()  # Update
    pygame.display.update()  # Update
    # Khởi tạo màn hình


def run():
    global gameRunning
    global paused
    global scores
    listEnemy = []
    wave_length = 5
    level = 0
    lives = 5
    lost = False
    player = Player(280, 600, 80, 80)
    i = 0

    while gameRunning:
        fpsClock.tick(FPS)
        screen.blit(background, [0, i])  # tạo cuộn dọc(nền chuyển động)
        screen.blit(background, [0, -yScreen + i])
        if i == yScreen:
            i = 0
        i += 1
        show_texts(10, 10, f"Scores: {scores}", 30)
        show_texts(10, 50, f"Lives: {lives}", 30)
        show_texts(xScreen - 135, 10, f"Level: {level}", 30)
        show_texts(xScreen - 135, 50, f"Enemys left:{len(listEnemy)}", 25)
        for enemy in listEnemy:
            enemy.draw(screen)

        player.draw(screen)
        pygame.display.update()  # Update

        if lives <= 0 or player.health <= 0:
            lost = True

        if len(listEnemy) == 0:
            show_texts_middle(yScreen / 2 - 100, f"Level: {level + 1}", 100)
            pygame.display.update()
            time.sleep(0.7)
            lives = 5
            level += 1
            wave_length += 5

            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, xScreen - 100), random.randrange(-1500, -100),
                              random.choice(["default"]), 80, 80, VBullet)
                listEnemy.append(enemy)
        mixer.Sound.play(musicBackground)

        for event in pygame.event.get():  # Bắt các sự kiện
            if event.type == pygame.QUIT:  # sự kiện nhấn thoát
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:  # sự kiện có phím nhấn xuống
                if event.key == pygame.K_ESCAPE:
                    mixer.pause()
                    paused = True
                    pause()
                    continue

        keys = pygame.key.get_pressed()  # sự kiện đè phím
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player.x - VPlayer > 0:  # left
            player.x -= VPlayer
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player.x + VPlayer + player.get_width() < xScreen:  # right
            player.x += VPlayer
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and player.y - VPlayer > 0:  # up
            player.y -= VPlayer
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player.y + VPlayer + player.get_height() < yScreen:  # down
            player.y += VPlayer
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in listEnemy[:]:  # Địch di chuyển và bắn
            enemy.move(VEnemy)
            enemy.move_lasers(enemy.laser_vel, player)

            if random.randrange(0, 2 * FPS) == 1:
                enemy.shoot()

            if collide(enemy, player):  # xử lý khi va chạm với địch
                player.health -= enemy.dame
                # cho obj phát nổ
                crash = Explode()
                crash.boom(enemy.x, enemy.y)
                listEnemy.remove(enemy)
            elif enemy.y + enemy.get_height() > yScreen:
                lives -= 1
                listEnemy.remove(enemy)

        player.move_lasers(-VBullet, listEnemy)

        if lost:  # Nếu thua
            input_box = InputBox(200, yScreen / 2, 140, 32)
            newGame = False
            mixer.stop()
            musicEnd.play(1000000)
            while True:
                for event in pygame.event.get():  # Nếu nhấn
                    if event.type == pygame.QUIT:  # Thoát
                        gameRunning = False
                        newGame = True
                        mixer.stop()
                        break
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:  # Thoát
                        newGame = True
                        mixer.stop()
                        break
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # If the user clicked on the input_box rect.
                        if input_box.rect.collidepoint(event.pos):
                            # Toggle the active variable.
                            input_box.active = not input_box.active
                        else:
                            input_box.active = False
                        # Change the current color of the input box.
                        input_box.color = COLOR_ACTIVE if input_box.active else COLOR_INACTIVE
                    if event.type == pygame.KEYDOWN:
                        if input_box.active:
                            if event.key == pygame.K_RETURN:
                                print(input_box.text)
                                gameRunning = False
                                break
                            elif event.key == pygame.K_BACKSPACE:
                                input_box.text = input_box.text[:-1]
                            else:
                                input_box.text += event.unicode
                            # Re-render the text.
                            input_box.txt_surface = FONT.render(input_box.text, True, input_box.color)
                input_box.update()
                screen.blit(background, (0, 0))  # vẽ lại background
                show_texts_middle(100, "Scores:{}".format(scores), 60)  # In điểm
                show_texts_middle(yScreen / 2 - 100, "GAME OVER", 70)  # In Thông báo thua
                show_texts_middle(yScreen / 2, "Do you want to save your score?", 40)
                input_box.draw(screen)
                # show_texts_middle(yScreen / 2, "Press Space to play again", 40)
                pygame.display.update()
                fpsClock.tick(FPS)
                if newGame or not gameRunning:  # Thoát vòng while để vào game mới
                    break

            scores = 0  # Trả các biến về giá trị ban đầu
            listEnemy = []
            wave_length = 5
            level = 0
            lives = 5
            lost = False
            player = Player(280, 600, 80, 80)


if __name__ == "__main__":
    main_menu()
