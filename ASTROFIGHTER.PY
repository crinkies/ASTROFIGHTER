import os as shell
from os import path
from os import environ
import random
import time

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

try:
    import pygame
except ModuleNotFoundError:
    shell.system('pip install pygame')

asset_dir = path.join(path.dirname(__file__), 'ASSET')

WIDTH = 480
HEIGHT = 600
FPS = 60
POWERUP_TIME = 3000
colors = {
"BLACK" : (0,0,0),
"WHITE" : (255,255,255),
"GOLD"  : (255,204,0,0),
"BROWN" : (89,62,26,0)}
score = 0
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(20)
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("ASTROFIGHTER")
clock = pygame.time.Clock()

font_name = pygame.font.match_font('arial')

def spawn():
    enemies = Mob()
    sprites.add(enemies)
    mobs.add(enemies)
    
def shield(surface, x, y, percentage):
    if percentage < 0:
        percentage = 0
    LENGTH = 480
    HEIGHT = 10
    fill = (percentage/100*LENGTH)
    outline = pygame.Rect(x, y, LENGTH, HEIGHT)
    filled = pygame.Rect(x, y, fill, HEIGHT)
    pygame.draw.rect(surface, colors['GOLD'],filled)
    pygame.draw.rect(surface, colors['BROWN'], outline, 2)
    
def text(surface, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, False, colors["GOLD"])
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)
    
def life(surface, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surface.blit(img, img_rect)
        
class Player(pygame.sprite.Sprite):
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_image, (62, 62))
        self.image.set_colorkey(colors["BLACK"])

        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT-10
        self.speedx = 0
        self.speedy = 0
        self.shield = 100
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()

        
    def powerup(self):
        self.power +=1
        self.power_time = pygame.time.get_ticks()
        
    def update(self):
        if self.power == 1:
            self.shot_delay = 150
        if self.power == 2:
            self.shot_delay = 75
        if self.power == 3:
            self.shot_delay = 35
        if self.power >= 1 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            if not self.power == 1:
                self.power -= 1
            if self.power > 3:
                self.power = 3
            self.power_time = pygame.time.get_ticks()
            
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT -10
            
        self.speedx = 0
        self.speedy = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -10
        if keystate[pygame.K_RIGHT]:
            self.speedx = 10
        if keystate[pygame.K_UP]:
            self.speedy = -10
        if keystate[pygame.K_DOWN]:
            self.speedy = 10
        if keystate[pygame.K_SPACE] and not self.hidden:
            self.shoot()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if not self.hidden and self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 0:
            self.rect.top = 0
            
    def nuke(self):
        for sprite in mobs:
            explosion = Explode(sprite.rect.center, 'nuke')
            sprites.add(explosion)
            sprite.kill()
            pygame.mixer.find_channel(True).play(random.choice(explosion_sounds))
            nuke_mob = Mob()
            nuke_mob.hide()
            spawn()
            nuke_sound.play()
            
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shot_delay:
            self.last_shot = now
            bullet_1 = Bullet(self.rect.centerx+20, self.rect.top)
            bullet_2 = Bullet(self.rect.centerx-20, self.rect.top)
            sprites.add(bullet_1,bullet_2)
            bullets.add(bullet_1,bullet_2)
            pygame.mixer.find_channel(True).play(laser_sound)
    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        
class Mob(pygame.sprite.Sprite):
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(mob_images)
        self.image_orig.set_colorkey(colors["BLACK"])
        self.image = self.image_orig.copy()

        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width*.8/2)
        self.rect.x = random.randrange(WIDTH-self.rect.width)
        self.rect.y = random.randrange(-150,-100)
        self.speedy = random.randrange(1, 7)
        self.speedx = random.randrange(-3,3) 
        self.rot = 0
        self.rot_speed = random.randrange(-8,8)
        self.last_update = pygame.time.get_ticks()
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        
    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2,HEIGHT+200)  
            
    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y+= self.speedy
        if self.rect.top > HEIGHT +10 or self.rect.left < -10 or self.rect.right > WIDTH+10:
            self.rect.x = random.randrange(WIDTH-self.rect.width)
            self.rect.y = random.randrange(-100,-40)
            self.speedy = random.randrange(1, 14)
        
class Bullet(pygame.sprite.Sprite):
    
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bullet_image, (22,22))
        self.image.set_colorkey(colors["BLACK"])
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()
            
class Powerup(pygame.sprite.Sprite):
    
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield','gun','life_powerup','nuke'])
        self.image = powerup_images[self.type]
        self.image = pygame.transform.scale(self.image, (22,22))
        self.image.set_colorkey(colors["BLACK"])
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 4

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()
            
class Explode(pygame.sprite.Sprite):
    
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_animations[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last = pygame.time.get_ticks()
        self.fps = 30
        
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last > self.fps:
            self.last = now
            self.frame +=1
            if self.frame == len(explosion_animations[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_animations[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center
                
def game_over_screen(score):
    screen.blit(background, background_rect)
    if score == 0:
        text(screen, "NO SCORE", 35, WIDTH/2, HEIGHT*3/5)
    elif score > 0:
        text(screen, f"Score: {score}", 35, WIDTH/2, HEIGHT*3/5)
    text(screen, "ASTROFIGHTER", 50, WIDTH/2,HEIGHT/4)
    text(screen, "Arrow keys to move, space to fire, esc to exit", 15, WIDTH/2, HEIGHT*6/7)
    text(screen, "Press any key to begin", 18, WIDTH/2, HEIGHT*3/4)
    pygame.display.flip()
    key_wait = True
    while key_wait:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                key_wait = False
    
background = pygame.image.load(path.join(asset_dir,"background.png")).convert()
background_rect = background.get_rect()
player_image = pygame.image.load(path.join(asset_dir, "ship_01.png")).convert()
hearts = pygame.image.load(path.join(asset_dir, "heart.png")).convert()
hearts = pygame.transform.scale(hearts, (25, 25))
hearts.set_colorkey(colors['BLACK'])
bullet_image = pygame.image.load(path.join(asset_dir, "bullet.png")).convert()
mob_images = []
mob_list = ['mob_01.png', 'mob_02.png','mob_03.png','mob_04.png','mob_05.png','mob_06.png']

for mob in mob_list:
    mob_images.append(pygame.image.load(path.join(asset_dir, mob)).convert())
    
explosion_animations = {}
explosion_animations['nuke'] = []
explosion_animations['large'] = []
explosion_animations['small'] = []
explosion_animations['player'] = []

for i in range(8):
    filename = 'explosion_0{}.png'.format(i)
    explosion_image = pygame.image.load(path.join(asset_dir, filename)).convert()
    explosion_image.set_colorkey(colors['BLACK'])
    image_large = pygame.transform.scale(explosion_image, (150,150))
    explosion_animations['nuke'].append(image_large)
    image_large = pygame.transform.scale(explosion_image, (75,75))
    explosion_animations['large'].append(image_large)
    image_small = pygame.transform.scale(explosion_image, (32, 32))
    explosion_animations['small'].append(image_small)
    filename = 'player_explosion_0{}.png'.format(i)
    image = pygame.image.load(path.join(asset_dir, filename)).convert()
    image.set_colorkey(colors['BLACK'])
    explosion_animations['player'].append(image)
powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(asset_dir, 'shield_01.png'))
powerup_images['gun'] = pygame.image.load(path.join(asset_dir, 'gun_01.png'))
powerup_images['life_powerup'] = pygame.image.load(path.join(asset_dir, 'heart.png'))
powerup_images['nuke'] = pygame.image.load(path.join(asset_dir, 'nuke.png'))    
laser_sound = pygame.mixer.Sound(path.join(asset_dir, 'laser_01.wav'))
pygame.mixer.Sound.set_volume(laser_sound, 0.3)
shield_sound = pygame.mixer.Sound(path.join(asset_dir, 'shield_01.wav'))
pygame.mixer.Sound.set_volume(laser_sound, 0.3)
powerup_sound_shield = pygame.mixer.Sound(path.join(asset_dir, 'powerup_01.wav'))
pygame.mixer.Sound.set_volume(laser_sound, 0.3)
powerup_sound_gun = pygame.mixer.Sound(path.join(asset_dir, 'powerup_02.wav'))
pygame.mixer.Sound.set_volume(laser_sound, 0.3)
powerup_heart = pygame.mixer.Sound(path.join(asset_dir, 'heart_01.wav'))
pygame.mixer.Sound.set_volume(laser_sound, 0.3)
explosion_sound_player = pygame.mixer.Sound(path.join(asset_dir, 'explosion_03.ogg'))
pygame.mixer.Sound.set_volume(explosion_sound_player, 0.3)
nuke_sound = pygame.mixer.Sound(path.join(asset_dir, 'explosion_03.ogg'))
pygame.mixer.Sound.set_volume(explosion_sound_player, 0.3)
explosion_sounds = []
for sound in ['explosion_01.wav', 'explosion_02.wav']:
    explosion_sounds.append(pygame.mixer.Sound(path.join(asset_dir, sound)))
    for Sounds in explosion_sounds:
        Sounds.set_volume(0.2)
        

pygame.mixer.music.load(path.join(asset_dir, 'song_03.ogg'))
pygame.mixer.music.set_volume(.8)


pygame.mixer.music.play(loops=-1)
game_over = True
level = 0
running = True
while running:
    if game_over:
        game_over_screen(score)
        score = 0
        game_over = False
        sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        sprites.add(player)

        for i in range(20):
            spawn()
            
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    sprites.update()

    colissions = pygame.sprite.groupcollide(mobs, bullets, True, True)
    
    for colission in colissions:
        score += 50 - colission.radius
        pygame.mixer.find_channel(True).play(random.choice(explosion_sounds))
        explosion = Explode(colission.rect.center, 'large')
        sprites.add(explosion)
        if random.random() > 0.98:
            powerup = Powerup(colission.rect.center)
            sprites.add(powerup)
            powerups.add(powerup)
        spawn()
        
    colissions = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for colission in colissions:
        player.shield-=colission.radius *2
        pygame.mixer.find_channel(True).play(shield_sound)
        explosion = Explode(colission.rect.center, 'small')
        sprites.add(explosion)
        spawn()
        if player.shield <= 0:
            death = Explode(player.rect.center, 'player')
            sprites.add(death)
            pygame.mixer.find_channel(True).play(explosion_sound_player)
            player.hide()
            player.lives -=1
            player.shield = 100
    colissions = pygame.sprite.spritecollide(player, powerups, True)
    for colission in colissions:
        if colission.type == 'shield':
            score+=1000
            pygame.mixer.find_channel(True).play(powerup_sound_shield)
            player.shield += random.randrange(5,20)
            if player.shield >= 100:
                player.shield = 100
        if colission.type == 'gun':
            score+=1000
            pygame.mixer.find_channel(True).play(powerup_sound_gun)
            player.powerup()
        if colission.type == 'life_powerup':
            score+=1000
            pygame.mixer.find_channel(True).play(powerup_heart)
            player.lives +=1
            if player.lives >= 3:
                player.lives = 3
        if colission.type == 'nuke':
            score+=1000
            player.nuke()
                
    if player.lives == 0 and not death.alive():
        game_over = True
        
    screen.fill(colors["BLACK"])
    screen.blit(background,background_rect)

    sprites.draw(screen)
    text(screen, str(score), 18, WIDTH/2, 10)
    shield(screen, 0, 0, player.shield)
    life(screen, 10, 10, player.lives, hearts)
    pygame.display.flip()
    
pygame.quit()
