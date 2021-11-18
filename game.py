# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 16:23:26 2021

@author: User
"""
import pygame
import random
import os

FPS = 60 #一秒跑60次
WIDTH = 500
HEIGHT = 600

RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE= (255, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

#遊戲初始化 & 視窗
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))  #(寬,高)
pygame.display.set_caption("太空戰機") #更改標題
clock = pygame.time.Clock()

#載入圖片
background_img = pygame.image.load(os.path.join("D:\hank_python\pygame","background.png")).convert()
player_img = pygame.image.load(os.path.join("D:\hank_python\pygame","player.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
pygame.display.set_icon(player_mini_img)
bullet_img = pygame.image.load(os.path.join("D:\hank_python\pygame","bullet.png")).convert()
#rock_img = pygame.image.load(os.path.join("D:\hank_python\pygame","rock.png")).convert()
rock_imgs = []
for i in range(7):
    rock_imgs.append(pygame.image.load(os.path.join("D:\hank_python\pygame",f"rock{i}.png")).convert())

#爆炸特效
expl_anim = {}
expl_anim["lg"] = []
expl_anim['sm'] = []
expl_anim['player'] = []
for i in range(9):
    expl_img = pygame.image.load(os.path.join("D:\hank_python\pygame\exp",f"{i}.png")).convert()
    expl_img.set_colorkey(BLACK)
    expl_anim['lg'].append(pygame.transform.scale(expl_img, (75, 75)))
    expl_anim['sm'].append(pygame.transform.scale(expl_img, (30, 30)))
    
    player_expl_img = pygame.image.load(os.path.join("D:\hank_python\pygame\exp",f"{i}.png")).convert()
    player_expl_img.set_colorkey(BLACK)
    expl_anim['player'].append(player_expl_img)

#寶物
power_imgs = {}
power_imgs['shield'] = pygame.image.load(os.path.join("D:\hank_python\pygame","live.png")).convert()
power_imgs['gun'] = pygame.image.load(os.path.join("D:\hank_python\pygame","gun.png")).convert()

#載入音樂
shoot_sound = pygame.mixer.Sound(os.path.join("D:\hank_python\pygame","shoot.mp3"))
gun_sound = pygame.mixer.Sound(os.path.join("D:\hank_python\pygame","gun.wav"))
shield_sound = pygame.mixer.Sound(os.path.join("D:\hank_python\pygame","live.wav"))
die_sound = pygame.mixer.Sound(os.path.join("D:\hank_python\pygame","die.wav"))
expl_sounds = [
    pygame.mixer.Sound(os.path.join("D:\hank_python\pygame","exp.wav")),
    pygame.mixer.Sound(os.path.join("D:\hank_python\pygame","exp1.wav"))
    ]
pygame.mixer.music.load(os.path.join("D:\hank_python\pygame","background.mp3"))
pygame.mixer.music.set_volume(0.8)


font_name = os.path.join("D:\hank_python\pygame","font.ttf") #重電腦引入字體
def draw_text(surf, text, size, x, y): #劃分數
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)

def new_rock(): #新增石頭
     r = Rock()
     all_sprites.add(r)
     rocks.add(r)

def draw_health(surf, hp, x, y): #畫血條
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp/100)*BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect) #血條填滿
    pygame.draw.rect(surf, WHITE, outline_rect, 2) #外框

def draw_lives(surf, lives, img, x, y): #畫幾條命
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 35*i
        img_rect.y = y
        surf.blit(img, img_rect)

def draw_init():
    screen.blit(background_img, (0,0))
    draw_text(screen, '太空戰機!', 64 , WIDTH/2, HEIGHT/4)
    draw_text(screen, '← →:移動飛船 空白鍵:發射子彈', 22 , WIDTH/2, HEIGHT/2)
    draw_text(screen, '按任意鍵開始遊戲!', 18 , WIDTH/2, HEIGHT*3/4)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        #取得輸入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP: #假如有按鍵按下
                waiting = False
                return False
                
class Player(pygame.sprite.Sprite): #用類別去繼承pygame的sprite.Sprite
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
#       self.image = pygame.Surface((50,40)) #創造一個pygame的平面
#       self.image.fill((0,255,0)) #塗滿 綠色
        self.image = pygame.transform.scale(player_img, (57,55))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect() #將平面框起 
        self.radius = 25
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH/2  #定位平面在視窗位置
        self.rect.bottom = HEIGHT - 10
        self.speedx = 8 
        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hide_time = 0
        self.gun = 1
        self.gun_time = 0

    def update(self):
        now = pygame.time.get_ticks()
        if self.gun > 1 and now - self.gun_time > 3000: #假如強化時間過3秒
            self.gun -= 1
            self.gun_time = now
        
        if self.hidden and now - self.hide_time > 1000: #假如已經過一秒顯示出飛船
            self.hidden = False
            self.rect.centerx = WIDTH/2  
            self.rect.bottom = HEIGHT - 10
        
        key_pressed = pygame.key.get_pressed() #偵測鍵盤上有哪個鍵被按下
        if key_pressed[pygame.K_RIGHT]: #偵測右鍵是否被按下
            self.rect.x += self.speedx
        if key_pressed[pygame.K_LEFT]: #偵測左鍵是否被按下
            self.rect.x -= self.speedx
        
        if self.rect.right > WIDTH: #假如右平面跑出視窗右側則卡住
            self.rect.right = WIDTH
        if self.rect.left < 0: #假如左平面跑出視窗左側則卡住
            self.rect.left = 0 
            
    def shoot(self):
        if not(self.hidden):
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx , self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.gun >= 2:
                bullet1 = Bullet(self.rect.left , self.rect.centery)
                bullet2 = Bullet(self.rect.right , self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()
                
                
                
    def hide(self): #隱藏飛船
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2 ,HEIGHT+500)
        
    def gunup(self): #道具
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()  

class Rock(pygame.sprite.Sprite): #用類別去繼承pygame的sprite.Sprite
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_ori = random.choice(rock_imgs) #創造一個pygame的平面
        self.image = self.image_ori.copy()
        self.image_ori.set_colorkey(BLACK)
        self.rect = self.image.get_rect() #將平面框起 
        self.radius = int(self.rect.width / 2)
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)  #定位平面在視窗位置
        self.rect.y = random.randrange(-180, -100)
        self.speedy = random.randrange(2,10)
        self.speedx = random.randrange(-3,3) 
        self.total_degree = 0
        self.rot_degree = random.randrange(-3,3) 

    def rotate(self): #轉動石頭
        self.total_degree += self.rot_degree
        self.total_degree = self.total_degree % 360
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree)
        center = self.rect.center  #重新定位中心點
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.right > WIDTH or self.rect.left < 0: #假如石頭超過視窗就重置
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)  
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(2,10)
            self.speedx = random.randrange(-3,3) 
            
class Bullet(pygame.sprite.Sprite): #用類別去繼承pygame的sprite.Sprite
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img #創造一個pygame的平面
        self.image.set_colorkey(BLACK) 
        self.rect = self.image.get_rect() #將平面框起 
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10


    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0: #當子彈超出上方則刪除
            self.kill()
    
class Explosion(pygame.sprite.Sprite): #用類別去繼承pygame的sprite.Sprite
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_anim[self.size][0]
        self.rect = self.image.get_rect() #將平面框起 
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks() #回傳初始化到現在經過毫秒數
        self.frame_rate = 30 #動畫速度

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_anim[self.size]):
                self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center


class Power(pygame.sprite.Sprite): #用類別去繼承pygame的sprite.Sprite
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(["shield","gun"])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK) 
        self.rect = self.image.get_rect() #將平面框起 
        self.rect.center = center
        self.speedy = 3


    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT: 
            self.kill()
    
all_sprites = pygame.sprite.Group()
rocks = pygame.sprite.Group() #將石頭放入群組
bullets = pygame.sprite.Group() #將子彈放入群組
powers = pygame.sprite.Group() #將寶物放入群組
player = Player() #創建player
all_sprites.add(player) 
for i in range(8):
    new_rock()
score = 0

pygame.mixer.music.play(-1) #重複播放

# 遊戲迴圈
show_init = True #初始畫面
running = True
while running:
    if show_init:
        close = draw_init()
        if close:
            break
        show_init = False
        
        all_sprites = pygame.sprite.Group()
        rocks = pygame.sprite.Group() #將石頭放入群組
        bullets = pygame.sprite.Group() #將子彈放入群組
        powers = pygame.sprite.Group() #將寶物放入群組
        player = Player() #創建player
        all_sprites.add(player) 
        for i in range(8):
            new_rock()
        score = 0
    
    clock.tick(FPS)
    #取得輸入
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN: #假如有按鍵被輸入
            if event.key == pygame.K_SPACE: #假如輸入空白鍵呼叫shoot
                player.shoot()
    #更新遊戲
    all_sprites.update()  #執行update函式
    #判斷子彈 石頭相撞
    hits = pygame.sprite.groupcollide(rocks,bullets,True,True) #子彈碰到石頭會消除
    for hit in hits: #將消除的石頭加回
        random.choice(expl_sounds).play()
        score += hit.radius
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.9: #掉寶率
            poww = Power(hit.rect.center)
            all_sprites.add(poww)
            powers.add(poww)
        new_rock()
    
    #判斷石頭 飛船相撞
    hits = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_circle)
    for hit in hits: #假如碰到石頭扣血
        new_rock()
        player.health -= hit.radius
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        if player.health <= 0:
            death_expl = Explosion(player.rect.center, 'player')
            all_sprites.add(death_expl)
            die_sound.play()
            player.lives -= 1
            player.health = 100
            player.hide()
            
    #判斷寶物 飛船相撞
    hits = pygame.sprite.spritecollide(player, powers, True)
    for hit in hits:
        if hit.type == "shield":
            player.health += 20        
            if player.health > 100:
                player.health = 100
            shield_sound.play()
        elif hit.type == 'gun':
            player.gunup()
            gun_sound.play()
    
    if player.lives == 0 and not(death_expl.alive()):
        show_init = True   
    
    
    
    #畫面顯示                   
    screen.fill((0,0,0))  #(R,G,B)調色盤(黑色)
    screen.blit(background_img, (0,0)) #(畫上圖片,位置)
    all_sprites.draw(screen) #將all_sprite劃出至視窗
    draw_text(screen, str(score), 18 , WIDTH/2, 10)
    draw_health(screen, player.health, 5, 15)
    draw_lives(screen, player.lives, player_mini_img, WIDTH - 100, 15)
    pygame.display.update()
    

pygame.quit()
