import pygame
import random 
import math

pygame.init()

#frames per second
FPS = 60

#height and width of the window
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 4, 4

#height and width of each tile
RECT_HEIGHT = HEIGHT//ROWS
RECT_WIDTH = WIDTH//COLS

OUTLINE_COLOR = (187, 173, 160)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOR = (205, 192, 180)
FONT_COLOR = (119, 110, 101)

FONT = pygame.font.SysFont("comicsans", 60, bold=True)
MOVE_VEL = 20

#initialisation of the window
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")

#A tile in the game
class Tile:
    #each tile has different color based on value
    #2, 4, 8 etc have different colors
    COLORS = [
        (237, 229, 218),
        (238, 225, 201),
        (243, 178, 122),
        (246, 150, 101),
        (247, 124, 95),
        (247, 95, 59),
        (237, 208, 115),
        (237, 204, 99),
        (236, 202, 80),
    ]

    #constructor takes the value, row and col of the tile
    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        #x and y coordinate for the tile
        self.x = col * RECT_WIDTH
        self.y = row * RECT_HEIGHT

    #function to set the color based on the value of the tile
    def get_color(self):
        #get the color based on the index in the COLORS list
        #log2(2)=1 but its at index 0 so we subtract 1
        #similarily, log2(4)-1 = 2-1 = 1, and at index 1 of COLORS we have color for 4
        color_index = int(math.log2(self.value)) - 1
        color = self.COLORS[color_index]
        return color
    
    #function to draw the tile onto the board at its position
    def draw(self, window):
        color = self.get_color()
        pygame.draw.rect(window, color, (self.x, self.y, RECT_WIDTH, RECT_HEIGHT))

        #this creates a surface that contains our text
        text = FONT.render(str(self.value), 1, FONT_COLOR)

        #blit will put the text surface onto the window
        window.blit(
            text, 
            #this defines position of the text, we want the text in the middle of the tile
            (
                self.x + (RECT_WIDTH/2 - text.get_width()/2),
                self.y + (RECT_HEIGHT/2 - text.get_height()/2),
            ),
        )
    
    #sets the row and col of a tile based on its x and y
    def set_pos(self, ceil=False):
        #when moving to the left
        if ceil:
            self.row = math.ceil(self.y/RECT_HEIGHT)
            self.col = math.ceil(self.x/RECT_WIDTH)
        
        #when moving to the right
        else:
            self.row = math.floor(self.y/RECT_HEIGHT)
            self.col = math.floor(self.x/RECT_WIDTH)

    #function to move the tile
    def move(self, delta):
        self.x += delta[0]
        self.y += delta[1]

#function to draw the grid
def draw_grid(window):
    for row in range (1, ROWS):
        y = RECT_HEIGHT * row
        pygame.draw.line(window, OUTLINE_COLOR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)
    
    for col in range(1, COLS):
        x = RECT_WIDTH * col
        pygame.draw.line(window, OUTLINE_COLOR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS)
    
    pygame.draw.rect(window, OUTLINE_COLOR, (0, 0, WIDTH, HEIGHT), OUTLINE_THICKNESS)

#to set the look of the pygame window and to draw tiles
def draw(window, tiles):
    window.fill(BACKGROUND_COLOR)

    #to draw our tiles, we will use a dictionary tiles
    for tile in tiles.values():
        tile.draw(window)

    #call function to draw the grid
    draw_grid(window)
    pygame.display.update()


#function to generate random positions for the tiles
def get_random_pos(tiles):
    row = None
    col = None
    while True:
        #this will generate random rows, cols within the grid
        row = random.randrange(0, ROWS)
        col = random.randrange(0, COLS)

        #this will check if the cell is empty or not
        #by checking if the key exists in tiles dictionary or not
        if f"{row}{col}" not in tiles:
            break
    
    return row, col

#function that allows us to move the tiles
def move_tiles(window, tiles, clock, direction):
    updated = True

    #blocks tells us the tiles which have already merged
    #so that we dont merge them again
    #e.g. 2 2 2 2
    #according to the rules of the gam this should give 4 4
    #but if we dont use blocks we might get something like 8
    blocks = set()

    #we want to move the tiles left to right
    #the furthest on the left will be moved first
    
    if direction == "left":
        #we will sort the tiles into a list
        #so that we can merge them correctly
        #right now we have them in a dictionary

        #sort_func will sort the tiles by their columns
        sort_func = lambda x : x.col

        #order in which we sort the column
        reverse = False 

        #specifies how much we want to move each tile in each frame
        #-MOVE_VEL: negative is for the movement towards left basically x coordinate
        # and 0 is the y coordinate, so only column will change and row remains same
        delta = (-MOVE_VEL, 0)

        #checks if we are already at the boundary or not
        boundary_check = lambda tile: tile.col == 0

        #to get the next tile or the tile on the left of the current tile
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col-1}")

        #check to see if the tiles are in the position to be merged or not
        #tiles will be merged if the tile being moved is completely on top of another tile
        merge_check = lambda tile, next_tile: tile.x > next_tile.x + MOVE_VEL

        #to stop moving when we reach the tile of different value
        move_check = (
            lambda tile, next_tile: tile.x > next_tile.x + RECT_WIDTH + MOVE_VEL
        )

        #to determine whether to round up or down after a move
        ceil = True
    
    elif direction == "right":
        sort_func = lambda x: x.col
        reverse = True
        delta = (MOVE_VEL, 0)
        boundary_check = lambda tile: tile.col == COLS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col + 1}")
        merge_check = lambda tile, next_tile: tile.x < next_tile.x - MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.x + RECT_WIDTH + MOVE_VEL < next_tile.x
        )
        ceil = False

    elif direction == "up":
        sort_func = lambda x: x.row
        reverse = False
        delta = (0, -MOVE_VEL)
        boundary_check = lambda tile: tile.row == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row - 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y > next_tile.y + MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.y > next_tile.y + RECT_HEIGHT + MOVE_VEL
        )
        ceil = True

    elif direction == "down":
        sort_func = lambda x: x.row
        reverse = True
        delta = (0, MOVE_VEL)
        boundary_check = lambda tile: tile.row == ROWS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row + 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y < next_tile.y - MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.y + RECT_HEIGHT + MOVE_VEL < next_tile.y
        )
        ceil = False

    #the loop runs if the screen is updated
    #if the screen is not updated the loop will break
    while updated:
        clock.tick(FPS)

        #we initially keep updated as False, 
        #if any update occurs we change it to True
        updated = False

        #we will sort the tiles in the correct order 
        sorted_tiles = sorted(tiles.values(), key=sort_func, reverse=reverse)

        #iterate over each tile in the sorted tiles list
        for i, tile in enumerate(sorted_tiles):
            
            #check if the tile is at the boundary 
            if boundary_check(tile):
                continue

            #get the next tile
            next_tile = get_next_tile(tile)

            #if next tile does not exist, we simply move our tile
            if not next_tile:
                tile.move(delta) 
            
            #check if the tile is there and is of the same value
            #we also check if the tile and the next_tile has been merged before or not
            #we do this by checking if they exist in blocks set or not
            elif (tile.value == next_tile.value and tile not in blocks and next_tile not in blocks):
                #if the tile hasnt completely covered the next tile
                #then we keep moving the tile
                if merge_check(tile, next_tile):
                    tile.move(delta)
                
                #if the tiles are in the position to be merged, then merge them
                else:
                    
                    #take the value of the next tile and multiply it by 2
                    next_tile.value *= 2
                    
                    #we now remove the tile that merged with the next tile
                    #the index of the tile is i
                    sorted_tiles.pop(i)

                    #then we add the next_tile into the blocks set
                    #as it has already been merged
                    blocks.add(next_tile)
            
            #if we have a tile and its value is not same as the current tile
            #then we move the current tile till the border of the next tile
            elif move_check(tile, next_tile):
                tile.move(delta)
            
            #none of the above conditions is true
            #this means no update occured, so updated remains False
            else:
                continue
            
            tile.set_pos(ceil)
            updated = True

        #call the function to update the tiles dictionary after the movement
        update_tiles(window, tiles, sorted_tiles)
    
    #call the function to check if the game is over or not
    return end_move(tiles)


#function to check if game is over or not
def end_move(tiles):

    #if all the tiles are filled
    if len(tiles) == 16:
        return "Lost! GAME OVER"
    
    #to set the tiles for a new game
    row, col = get_random_pos(tiles)
    tiles[f"{row}{col}"] = Tile(random.choice([2,4]), row, col)
    return "Continue"


#function to update the tiles dictionary after the movement
def update_tiles(window, tiles, sorted_tiles):
    
    #remove everything from the dictionary
    tiles.clear()

    #then, simply just copy all the tiles that remain in sorted_list
    #onto the tiles dictionary
    for tile in sorted_tiles:
        tiles[f"{tile.row}{tile.col}"] = tile
    
    draw(window, tiles)

#function to generate two tiles of value 2 at random positions
#this is at the start of the game
def generate_tiles():
    tiles = {}
    for _ in range(2):
        #get_random_pos will generate the random positions
        row, col = get_random_pos(tiles)
        tiles[f"{row}{col}"] = Tile(2, row, col)
    return tiles


#main function
def main(window):
    #clock object will regulate the speed of the while loop
    clock = pygame.time.Clock()
    run = True

    #tiles is basically a dictionary for the objects of the class Tile
    # 00 is the coordinate (0, 0), 20 is the coordinate (2, 0)
    tiles = generate_tiles()

    #GAME LOOP
    while run:
        #the while loop will run at most 1 time in 60 seconds because FPS=60
        clock.tick(FPS)

        #runs the loop for event in event.get()
        for event in pygame.event.get():
            #checks if the user wants to quit the game or not 
            if event.type == pygame.QUIT:
                run = False
                break

            #checks if a key was pressed or not
            if event.type == pygame.KEYDOWN:
                #check if key pressed is left
                if event.key == pygame.K_LEFT:
                    move_tiles(window, tiles, clock, "left")
                #check if key pressed is right 
                elif event.key == pygame.K_RIGHT:
                    move_tiles(window, tiles, clock, "right")
                #check if key pressed is up
                if event.key == pygame.K_UP:
                    move_tiles(window, tiles, clock, "up")
                #check if key pressed is down
                if event.key == pygame.K_DOWN:
                    move_tiles(window, tiles, clock, "down")

        
        #call the function which changes the look of the window
        draw(window, tiles)
    
    #this will quit the pygame window
    pygame.quit()

if __name__ == "__main__":
    main(WINDOW)
