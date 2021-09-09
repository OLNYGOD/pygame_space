import pygame
import random
from pygame import font
from pygame.constants import K_SPACE
import os
from pygame.draw import rect
from pygame.event import get

from pygame.sprite import collide_circle_ratio


WIDTH = 1000         #視窗大小
HEIGHT = 800    

#圖片大小
player_size = (75,50)


WHITE = (255,255,255)
GREEN = (0,255,0)
RED = (255,0,0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

PFS = 60           #更新頻率


#遊戲初始化$創建視窗
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))  #設定視窗
clock = pygame.time.Clock()

#載入圖片
background_img = pygame.image.load(os.path.join('img', 'background.png')).convert()
background_img = pygame.transform.scale2x(background_img)                           #圖片放大兩倍
player_img = pygame.image.load(os.path.join('img', 'player.png')).convert()
player_mini_img = pygame.transform.scale(player_img, (25,19))
player_mini_img.set_colorkey(BLACK)
#rock_img = pygame.image.load(os.path.join('img', 'rock.png')).convert()
bullet_img = pygame.image.load(os.path.join('img', 'bullet.png')).convert()
rock_images = []
for i in range(7):
    rock_images.append(pygame.image.load(os.path.join('img', f'rock{i}.png')).convert())
power_img = {}
power_img['shield'] = pygame.image.load(os.path.join('img', 'shield.png')).convert()
power_img['gun'] = pygame.image.load(os.path.join('img', 'gun.png')).convert()

"""resurrections_img = []
for i in range(3):
    resurrection_img = pygame.image.load(os.path.join('img', f'resurrection{i}.png')).convert()
    resurrection_img.set_colorkey(BLACK)
    resurrections_img.append(pygame.transform.scale(resurrection_img, (75,75)))"""


#載入爆炸圖片
expl_imgtotal = {}          #rock &player &bullet
expl_imgtotal['lg'] = []    #大爆炸
expl_imgtotal['sm'] = []    #小爆炸
expl_imgtotal['player'] = []    #player爆炸
for i in range(9):
    expl_img = pygame.image.load(os.path.join('img', f'expl{i}.png')).convert()
    expl_playerimg = pygame.image.load(os.path.join('img', f'player_expl{i}.png')).convert()
    expl_img.set_colorkey(BLACK)
    expl_playerimg.set_colorkey(BLACK)
    expl_imgtotal['lg'].append(pygame.transform.scale(expl_img, (75, 75)))
    expl_imgtotal['sm'].append(pygame.transform.scale(expl_img, (30, 30)))
    expl_imgtotal['player'].append(pygame.transform.scale(expl_playerimg, (75, 75)))

#載入字體
font_name = pygame.font.match_font("arial")
#字體位置、字型、大小
def draw_text(surf, text , size , x , y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)

#產生新石頭
def new_rock():
    rock = Rock()
    all_sprites.add(rock)
    rocks.add(rock)

#劃生命條
def draw_health(surf, hp, x, y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp/100)*BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)   

#劃小飛船
def draw_lives(surf,lives, img, x, y):
    for i in range(lives):
        live_rect = img.get_rect()
        live_rect.x = x + 30*i
        live_rect.y = y
        surf.blit(img, live_rect)



#載入音效
shoot_sound = pygame.mixer.Sound(os.path.join('sound', 'shoot.wav'))
expl_sound = [
    pygame.mixer.Sound(os.path.join('sound', 'expl0.wav')),
    pygame.mixer.Sound(os.path.join('sound', 'expl1.wav'))
]
pygame.mixer.music.load(os.path.join('sound', 'background.ogg'))
expl_sound = [
    pygame.mixer.Sound(os.path.join('sound', 'pow0.wav')),
    pygame.mixer.Sound(os.path.join('sound', 'pow1.wav'))
]
playerexpl_sound = pygame.mixer.Sound(os.path.join('sound', 'rumble.ogg'))

#sprite 遊戲畫面精靈製作 飛艇
class Player(pygame.sprite.Sprite):                 #https://ithelp.ithome.com.tw/articles/10232278
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, player_size)    #調整圖片大小
        self.image.set_colorkey(BLACK)                              #去除黑色
        self.rect = self.image.get_rect()                           #定位
        self.radius = self.rect.width*0.8/2                        #碰撞半徑判斷
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH/2                 #圖片位置
        self.rect.bottom = HEIGHT-20
        self.speedx = 8
        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hidden_time = 0
        self.gun = 1
        self.guntime = 0
        
        #飛船圖片移動更新
    def update(self):
        if self.hidden and pygame.time.get_ticks() - self.hidden_time > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH/2
            self.rect.bottom = HEIGHT -20
        
        #按鍵移動
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_RIGHT] or key_pressed[pygame.K_d]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_LEFT] or key_pressed[pygame.K_a]:
            self.rect.x -= self.speedx

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

        if self.rect.left < 0 :
            self.rect.left = 0

    def shoot(self):
        if not(self.hidden):
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            if self.gun > 1:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.rigjt, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hidden_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2 , HEIGHT+500)

    def gunup(self):
        self.gun += 1
        self.guntime = pygame.time.get_ticks()
            
    
#石頭
class Rock(pygame.sprite.Sprite):                 #https://ithelp.ithome.com.tw/articles/10232278
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #self.image = pygame.transform.scale(rock_img, rock_size)
        self.image_ori = random.choice(rock_images) 
        self.image_ori.set_colorkey(BLACK)
        self.image = self.image_ori.copy()
        self.rect = self.image.get_rect()
        self.radius = self.rect.width*0.8/2
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)        #圖片位置
        self.rect.y = random.randrange(-200, -100)
        self.speedy = random.randrange(3, 6)
        self.speedx = random.randrange(-3, 3)
        self.total_degree = 0
        self.rot_degree = random.randrange(-3, 3)

    def rotate(self):
        self.total_degree += self.rot_degree
        self.total_degree = self.total_degree % 360
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)        #圖片位置
            self.rect.y = random.randrange(-200, 0)
            self.speedy = random.randrange(2,5)
            self.speedx = random.randrange(-3,3)

#子彈
class Bullet(pygame.sprite.Sprite):                 #https://ithelp.ithome.com.tw/articles/10232278
    def __init__(self, x , y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x          #圖片位置
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

#爆炸(碰撞偵測)
class Explosion(pygame.sprite.Sprite):                 #https://ithelp.ithome.com.tw/articles/10232278
    def __init__(self, size, center):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_imgtotal[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center        #圖片位置
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_imgtotal[self.size]):
                self.kill()
            else : 
                self.image = expl_imgtotal[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center

#寶物
class Power(pygame.sprite.Sprite):                 #https://ithelp.ithome.com.tw/articles/10232278
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type 
        self.power_chose = random.choice(['shield', 'gun'])
        self.image = power_img[self.power_chose]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center          #圖片位置
        self.speedy = 5

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

#復活
"""class Resurrection(pygame.sprite.Sprite):                 #https://ithelp.ithome.com.tw/articles/10232278
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = resurrections_img[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH/2                 #圖片位置
        self.rect.bottom = HEIGHT-20
        self.speedx = 8
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 5000
        self.stop = False

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(resurrections_img):
                self.stop = True
                self.kill()
            else : 
                self.image = resurrections_img[self.frame]
                self.rect = self.image.get_rect()"""
                
all_sprites = pygame.sprite.Group()
powers = pygame.sprite.Group()
rocks = pygame.sprite.Group()
bullets = pygame.sprite.Group()
players = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
players.add(player)
for i in range(8):
    new_rock()
score = 0
pygame.mixer.music.play(-1)         #背景音樂循環撥放
pygame.mixer.music.set_volume(0.1)

#遊戲迴圈
running = True
while running:
    rock = Rock()
    clock.tick(PFS)

    #取得輸入
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == K_SPACE:
                player.shoot()

    #更新畫面
    all_sprites.update()
    hits = pygame.sprite.groupcollide(rocks, bullets, True, True)      #回傳字典型態碰到的rock&bullet
    for hit in hits:    #hit 表示碰到的石頭
        expl = Explosion('lg', hit.rect.center)
        all_sprites.add(expl)
        random.choice(expl_sound).play()    #音效
        score += int(hit.radius)    #依石頭半徑計分
        if random.random() > 0.1:
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            powers.add(pow)
        new_rock()
    hits = pygame.sprite.spritecollide(player ,powers, True, pygame.sprite.collide_circle)      #回傳字典碰到的rock&players
    for hit in hits:
        if hit.type == 'shield':
            player.health += 20
            if player.health > 100:
                player.health = 100
        elif hit.type == 'gun':
            player.gunup()

    hits = pygame.sprite.groupcollide(players ,rocks, False, True, pygame.sprite.collide_circle)      #回傳字典碰到的rock&players
    for hit in hits:
        expl = Explosion('sm', hit.rect.center)
        all_sprites.add(expl)
        player.health -= rock.radius*10
        new_rock()
        if player.health <= 0:
            death_expl = Explosion('player', hit.rect.center)
            all_sprites.add(death_expl)
            playerexpl_sound.play()
            player.lives -= 1
            player.health = 100
            player.hide()
            #running = False
    

    if player.lives == 0 and not(death_expl.alive()):
        running = False

    #畫面顯示
    screen.fill(BLACK)
    screen.blit(background_img, (0,0))
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH/2, 10)
    draw_health(screen, player.health, 5, 10)
    draw_lives(screen, player.lives, player_mini_img, 150, 10)
    pygame.display.update()

pygame.quit