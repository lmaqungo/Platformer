import pygame
import button
import csv
import pickle

pygame.init()



SCREEN_WIDTH = 495
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
LOWER_MARGIN = 90
SIDE_MARGIN = 150

ROWS = 20
MAX_COLS = 100
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
current_tile = 0
level = 1

clock = pygame.time.Clock()
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('Level Editor')

#define game variables
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1

# load buttons
save_button_img = pygame.image.load('img/save_btn.png')
load_button_img = pygame.image.load('img/load_btn.png')


# store tiles in list

img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f"img/tile/{x}.png")
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)


#define colors
green = pygame.color.Color('green')
white = pygame.color.Color('white')
red = pygame.color.Color('red')
grey = pygame.color.Color('grey')
black = pygame.color.Color('black')
blue = (66, 164, 245)

# define font
font = pygame.font.SysFont('Arial', 16)

# create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1]* MAX_COLS
    world_data.append(r)

# create ground
for tile in range(0, MAX_COLS):
    world_data[ROWS-1][tile] = 0
    
# function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))
     
        


def draw_bg():
    screen.fill(white)
        
def draw_grid():
    #vertical lines
    for c in range(MAX_COLS + 1):
        pygame.draw.line(screen, black, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, SCREEN_HEIGHT))
        
        
    for c in range(ROWS + 1):
        pygame.draw.line(screen, black, (0, c * TILE_SIZE), (SCREEN_WIDTH, c * TILE_SIZE))
        

def draw_world():
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile >= 0:
                screen.blit(img_list[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE))
                
save_button = button.Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT + LOWER_MARGIN - 65, save_button_img, 0.4)
load_button = button.Button(SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT + LOWER_MARGIN - 65, load_button_img, 0.4)

button_list = []
button_col = 0
button_row = 0
for i in range(len(img_list)):
    tile_button = button.Button(SCREEN_WIDTH + (50 * button_col) + 15, 50 * button_row + 30, img_list[i], 1)
    button_list.append(tile_button)
    button_col+=1
    if button_col == 3:
        button_row += 1
        button_col = 0
        
run = True
while run:
    screen.fill(red)
    
    draw_bg()
    draw_grid()
    draw_world()
        
    pygame.draw.rect(screen, blue, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))
    pygame.draw.rect(screen, blue, (0, SCREEN_HEIGHT, SCREEN_WIDTH + SIDE_MARGIN , LOWER_MARGIN))
    
   
    if save_button.draw(screen):
        
        
        with open(f'Levels/level{level}_data.csv', 'w', newline ='') as csvfile:
            writer = csv.writer(csvfile, delimiter = ",")
            for row in world_data:
                writer.writerow(row)
                
        print(f"Level {level} saved")
                
    if load_button.draw(screen):
        
        scroll = 0 
        
        try:
            with open(f'Levels/level{level}_data.csv', newline ='') as csvfile:
                reader = csv.reader(csvfile, delimiter = ",")
                for x, row in enumerate(reader):
                    for y, tile in enumerate(row):
                        world_data[x][y] = int(tile)
        except FileNotFoundError:
            print("Level does not exist")
                 
        
    
    draw_text(f"Level: {level}", font, white, 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
    draw_text("Press UP or DOWN to change level", font, white, 10, SCREEN_HEIGHT + LOWER_MARGIN - 75)
    
    
    button_count = 0
    for button_count,i in enumerate(button_list):
        if i.draw(screen):
            current_tile = button_count
    
    
    pygame.draw.rect(screen, red, button_list[current_tile].rect, 3)
    
    if scroll_left == True and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right == True and scroll < (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH:
        scroll += 5 * scroll_speed
        
    
    pos = pygame.mouse.get_pos()
    x = (pos[0] + scroll) // TILE_SIZE
    y = pos[1]  // TILE_SIZE
    
    
    if pos[0]  < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
        
        if pygame.mouse.get_pressed()[0] == 1:
            if world_data[y][x] != current_tile:
                world_data[y][x] = current_tile
        if pygame.mouse.get_pressed()[2] == 1:
            world_data[y][x] = -1
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                scroll_left = True
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 5
            if event.key == pygame.K_UP:
                level +=1
            if event.key == pygame.K_DOWN and level > 1:
                level -=1
                
                
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 1
            
    pygame.display.update()
    clock.tick(FPS)
pygame.quit()

