import pygame
import os
import random
import csv
import button
from pygame import mixer

mixer.init()
pygame.init()


SCREEN_WIDTH = 500
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('platformer')

# set frame rate
clock = pygame.time.Clock()
FPS = 60

# define game variables
GRAVITY = 0.8

ROWS = 20
COLS = 100
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
MAX_LEVELS = 5

level = 1
screen_scroll = 0
bg_scroll = 0
SCROLL_THRESH = 100
start_game = False
start_intro = False


# define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False
main_music_started = False

#load audio
main_music = mixer.Sound("audio/main music.mp3")
main_music.set_volume(0.3)
jump_fx = mixer.Sound("audio/jump.wav")
jump_fx.set_volume(0.3)
shot_fx = mixer.Sound("audio/shoot.wav")
shot_fx.set_volume(0.5)
grenade_fx = mixer.Sound("audio/explosion.wav")
grenade_fx.set_volume(0.5)
pickup_fx = mixer.Sound("audio/pickup.wav")
pickup_fx.set_volume(0.5)
hurt_fx = mixer.Sound("audio/hurt.wav")
hurt_fx.set_volume(0.5)
health_pickup_fx = mixer.Sound("audio/health-pickup.wav")
health_pickup_fx.set_volume(0.5)


#button images
start_img = pygame.image.load('img/start_btn2.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn2.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn2.png').convert_alpha()

#store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/tile/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
#bullet
bullet_img = pygame.image.load("img/icons/bullet.png").convert_alpha()
bullet_img_icon = pygame.image.load("img/icons/bullet2.png").convert_alpha()
#grenade
grenade_img = pygame.image.load("img/icons/grenade.png").convert_alpha()
#pick up boxes
health_box_img = pygame.image.load("img/icons/health_box.png").convert_alpha()
ammo_box_img = pygame.image.load("img/icons/ammo_box.png").convert_alpha()
grenade_box_img = pygame.image.load("img/icons/grenade_box.png").convert_alpha()

item_boxes = { 
              
               "Health" : health_box_img,
              "Ammo": ammo_box_img,
              "Grenade" : grenade_box_img    
}

#define colours
BLACK = pygame.color.Color('black')
RED = pygame.color.Color('red')
WHITE = pygame.color.Color('white')
GREEN = pygame.color.Color('green')
ORANGE = (245, 197, 66)
BLUE = (50, 168, 158)
BLUE_WHITE = (195, 214, 213)
PINK = (235, 65, 54)
YELLOW = pygame.color.Color('yellow')

#define font
font = pygame.font.SysFont('Arial', 12)

def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x,y))

def draw_bg():
    screen.fill(BLACK)
    
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()
    
    #create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)
    return data


class Soldier(pygame.sprite.Sprite):
    # speed determines how many pixels character will move each time display updates
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.ammo = ammo
        self.start_ammo = ammo
        self.grenades = grenades
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        #ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 100, 20) # view distance
        self.idling = False
        self.idling_counter = 0
        
        # load all images for players
        animation_types = ['Idle','Run', 'Jump', 'Death']
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
    def update(self):
        self.update_animation()
        
        self.check_alive()
              
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
       
        
    def move(self, moving_left, moving_right):
        
        
        #essentially you just move the rect. Better to draw a rect around an img and move that for convention
        screen_scroll = 0
        dx = 0
        dy = 0
        # we declare these variables in order to calculate their displacement after they move in order to make collisions possible
        if moving_left:
            dx -= self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx += self.speed
            self.flip = False
            self.direction = 1
            
        # jump
        if self.jump == True and self.in_air == False:
            jump_fx.play()
            self.vel_y = -10 # moving up is in the negative y direction with this coordinate system
            self.jump = False
            self.in_air = True
            
        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10 # declaring a terminal gravtiy
        dy += self.vel_y
        
        #check collision 
        for tile in world.obstacle_list:
            #check collision in x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #check if below the ground, i.e. jumping
                
                if self.vel_y < 0: 
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                
                #check if above the ground, i.e. falling
                elif self.vel_y >= 0: 
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom
                    
        #water collision
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0
            
        #check collision with exit
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True
    
        # fall off map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0                    
                    
        #check if going off edge
        if self.char_type == "player":
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0
                     
        #update rectangle position  
        self.rect.x += dx
        self.rect.y += dy
        
        #update scroll based on player position
        if self.char_type == "player":
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH) \
            or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx
                
        
                
        return screen_scroll, level_complete
        
    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 10
            bullet = Bullet(self.rect.centerx + (0.8 * self.rect.size[0] * self.direction),self.rect.centery, 0.75, self.direction)
            bullet_group.add(bullet)
            # reduce ammo
            self.ammo -= 1
            shot_fx.play()
            
    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0) #idle
                self.idling = True
                self.idling_counter = 50 
                # check if ai is near the player
            if self.vision.colliderect(player.rect):
                #stop running and face player
                self.update_action(0) 
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1) # ai runs
                    self.move_counter += 1
                    #update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 50 * self.direction, self.rect.centery) # 75 is half of vision rect
                    
                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter-=1
                    if self.idling_counter<=0:
                        self.idling = False
            
            
        self.rect.x += screen_scroll

            
    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        #update img depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index+=1
            
        # if the animation has run out, the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
        
    def update_action(self, new_action):
        # check if new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
            
    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)
            
    
    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False) ,self.rect)
        
class World():
    def __init__(self):
        self.obstacle_list = []
    
    def process_data(self, data):
        self.level_length = len(data[0])
        
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10: #water
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15: # create a player
                        player = Soldier("player", x * TILE_SIZE, y * TILE_SIZE, 1, 4 , 30, 5)
                        health_bar = HealthBar(10, 10, player.health, player.max_health)
                    elif tile == 16:#create enemies
                        enemy = Soldier("enemy", x * TILE_SIZE, y * TILE_SIZE, 1, 3, 30, 0)
                        enemy_group.add(enemy)
                    elif tile == 17: # create ammo box
                        item_box = ItemBox("Ammo", x * TILE_SIZE, y * TILE_SIZE, 0.5)
                        item_box_group.add(item_box)
                        
                    elif tile == 19: # create ammo box
                        item_box = ItemBox("Health", x * TILE_SIZE, y * TILE_SIZE, 0.5)
                        item_box_group.add(item_box)
                        
                    elif tile == 18: # create ammo box
                        item_box = ItemBox("Grenade", x * TILE_SIZE, y * TILE_SIZE, 0.5)
                        item_box_group.add(item_box)
                    elif tile == 20: #create exit
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)
                    
        return player, health_bar               
                        
    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])                                        




class Decoration(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
        
    def update(self):
        self.rect.x += screen_scroll
        

class Water(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
        
    def update(self):
        self.rect.x += screen_scroll
        
class Exit(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    
    def update(self):
        self.rect.x += screen_scroll

                    
class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        img = item_boxes[self.item_type]
        self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)) )
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE// 2, y + (TILE_SIZE - self.image.get_height()))
        
    def update(self):
        
        self.rect.x += screen_scroll
        #check if player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            #check item box type
            if self.item_type == "Health":
                player.health += 25
                health_pickup_fx.play()
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == "Ammo":
                player.ammo += 15
                pickup_fx.play()
            elif self.item_type == "Grenade":
                player.grenades += 3
                pickup_fx.play()
            #delete item box after collision
            self.kill()
                
class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health
        
    def draw(self, health):
        # update with new health
        self.health = health
    
        pygame.draw.rect(screen, RED, (self.x, self.y, 100, 10))
   
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 100 * ratio, 10))
        
        

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y,scale, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = pygame.transform.scale(bullet_img, (int(bullet_img.get_width() * scale), int(bullet_img.get_height() * scale)) )
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        
    def update(self):
        # move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill() 
            
        # check with collsion with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
            
        # check collision with characters
        # might have to change player collision with bullets as it is causing a bug. Code a manual system so we have more control
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                hurt_fx.play()
                self.kill()
        for enemy in enemy_group:    
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()
                
                    


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -10
        self.speed = 5
        self.image = pygame.transform.scale(grenade_img, (int(grenade_img.get_width() * scale), int(grenade_img.get_height() * scale)) )
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction      
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y
        
        # check with collision with level
        for tile in world.obstacle_list:
            # grenade collision with walls
            # x direction collision
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            # y direction collision
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                #check if below the ground, i.e. jumping
                if self.vel_y < 0: 
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                
                #check if above the ground, i.e. falling
                elif self.vel_y >= 0: 
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom
                     
        
        
        # move grenade
        self.rect.x += dx + screen_scroll
        self.rect.y += dy
        
        # grenade timer
        
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 1)
            explosion_group.add(explosion)
            #grenade damage based on proximity
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                    player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                        enemy.health -= 50
                    
        
        
        


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"img/explosion/exp{num}.png")
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)) )
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)  
        self.counter = 0
        
    def update(self):
        
        self.rect.x += screen_scroll
        
        EXPLOSION_SPEED = 4
        #update explosion animation
        self.counter+=1
        
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index +=1
            # if animation is complete then delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                
                self.image = self.images[self.frame_index]
                
class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0
        
    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1: #whole screen fade
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (0, 0 -  self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.direction == 2: #vertical screen fade down
            pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True
        
        return fade_complete
        
        
#create screen fades
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, BLACK, 6)
            
#create buttons
start_button = button.Button(20, 20, start_img, 0.5)
exit_button = button.Button(20, 80, exit_img, 0.5)
restart_button = button.Button(SCREEN_WIDTH // 2 -54, SCREEN_HEIGHT // 2 - 45, restart_img, 0.5)


#create sprite groups     
enemy_group =  pygame.sprite.Group()  
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()


world_data = []
for row in range(ROWS):
    r = [-1]* COLS
    world_data.append(r)

# load in level data
try:
    with open(f'Levels/level{level}_data.csv', newline ='') as csvfile:
                reader = csv.reader(csvfile, delimiter = ",")
                for x, row in enumerate(reader):
                    for y, tile1 in enumerate(row):
                        world_data[x][y] = int(tile1) 
                        
    
except FileNotFoundError:
    print("You need to create levels first")
                     
world = World()
player, health_bar = world.process_data(world_data)

enemy = Soldier("enemy", 400, 320, 1, 3, 30, 0)



                     
run = True
while run:
    clock.tick(FPS)

    
    # need to fill the screen every frame so we dont see the stuff from the previous frames. 
    if start_game == False:
        #main menu
        screen.fill(BLUE)
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False
    else:
            
        
        draw_bg()
        world.draw()
        
        if not main_music_started:
            main_music.play(-1, 0, 2000)
            main_music_started = True
        

        
        #show player health_bar 
        health_bar.draw(player.health)
        
        #show ammo
        draw_text('AMMO:', font, YELLOW, 10, 45)
        bullet_img_resized = pygame.transform.scale(bullet_img,(int(bullet_img.get_width() * 0.6), int(bullet_img.get_height() * 0.6)) )
        for i in range(player.ammo):
            screen.blit(bullet_img_resized, (50 + (i * 5), 50))
        #show grenade
        draw_text('GRENADES:', font, YELLOW, 10, 25)
        grenade_img_resized = pygame.transform.scale(grenade_img,(int(grenade_img.get_width() * 0.5), int(grenade_img.get_height() * 0.5)) )
        for i in range(player.grenades):
            screen.blit(grenade_img_resized, (75 + (i * 8), 28))
        
        player.update()
        player.draw()
        
        
        
        for enemy in enemy_group:
            enemy.update()
            enemy.draw()
            enemy.ai()
        
        # update and draw groups. The purpose of creating groups is to handle multiple instances of these bullets and groups
        bullet_group.update()
        bullet_group.draw(screen)
        
        grenade_group.update()
        grenade_group.draw(screen)
        
        explosion_group.update()
        explosion_group.draw(screen)
        
        item_box_group.update()
        item_box_group.draw(screen)
        
        decoration_group.update()
        water_group.update()
        exit_group.update()
        
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)
        
        #show intro
        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0
        
        # update player actions
        if player.alive:
            #shoot bullets
            if shoot:
                player.shoot()
            # throw grenades
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (player.rect.size[0] * 0.5 * player.direction), 
                                player.rect.top, 0.85, player.direction)
                grenade_group.add(grenade)
                grenade_thrown = True
                # reduce grenades
                player.grenades-=1
            if player.in_air:
                player.update_action(2) #2=jump
            elif moving_left or moving_right:
                player.update_action(1) # running=1
            else:
                player.update_action(0) # idle=0
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            #check if player had completed the level
            if level_complete:
                start_intro = True
                level+=1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    with open(f'Levels/level{level}_data.csv', newline ='') as csvfile:
                        reader = csv.reader(csvfile, delimiter = ",")
                        for x, row in enumerate(reader):
                            for y, tile1 in enumerate(row):
                                world_data[x][y] = int(tile1) 
                     
                world = World()
                player, health_bar = world.process_data(world_data)
        
                             
        else:
            screen_scroll = 0
            main_music.stop()
            if death_fade.fade():
                
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_Scroll = 0
                    world_data = reset_level()
                    with open(f'Levels/level{level}_data.csv', newline ='') as csvfile:
                        reader = csv.reader(csvfile, delimiter = ",")
                        for x, row in enumerate(reader):
                            for y, tile1 in enumerate(row):
                                world_data[x][y] = int(tile1) 
                        
                    world = World()
                    screen_scroll, level_complete = player.move(moving_left, moving_right)
                    player, health_bar = world.process_data(world_data)
                    main_music_started = False
        
        
        # keyboard input is an event
    
    for event in pygame.event.get():
        # quit
        if event.type == pygame.QUIT:
            run = False
        # key pressed down   
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_f:
                grenade = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
                
            if event.key == pygame.K_ESCAPE:
                run = False
        
        # key released   
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_f:
                grenade = False
                grenade_thrown = False
            
            
    pygame.display.update()
    # setting frame rate lock is important so that cpu doesnt just compute everything as fast as it can
            
pygame.quit()

