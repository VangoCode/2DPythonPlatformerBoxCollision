## RON VARSHAVSKY - https://github.com/vangocode
## started: 2020-08-30
## finished:2020-08-31
## 2d box platformer template for Ms. G's Computer Science Course


import pygame, time

BLACK   = (  0,  0,  0)
WHITE   = (255,255,255)
RED     = (255,  0,  0)
GREEN   = (  0,255,  0)
BLUE    = (  0,  0,255)
OUTLINE = 0

#-----------------------
# CLASSES
#-----------------------
class Player(object):
    """ A basic player controller
    data:                                behaviour:
        x  - x-axis position                  horizontal movement
        y  - y-axis position                  vertical movement
        w  - player width
        h  - player height
        dx - x-velocity (dx^-> in physics)    horizontal velocity
        dy - y-velocity (dy^-> in physics)    vertical velocity
        b  - bottom of player
        r  - right of player
        state - state player is in (idle or jumping)
    """
    def __init__(self, x, y, w, h):
        self.x  = x
        self.y  = y
        self.w  = w
        self.h  = h
        self.dx = 0
        self.dy = 0
        self.r  = x + w
        self.b  = y + h
        self.state = 'jumping'

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.w, self.h), OUTLINE)
        self.state = 'jumping'

    def update(self, dt):
        self.x += self.dx
        self.y += self.dy
        self.r  = self.x + self.w
        self.b  = self.y + self.h

        # update your gravity if you're falling
        if self.state == 'jumping':
            self.dy += GRAVITY * dt

    def _check_hits(self,other):
        # basically checking all the side(s) you are in contact with
        if self.x+self.dx<other.x:
            self.leftHit = True
        if self.r+self.dx>other.r:
            self.rightHit = True
        if self.b+self.dy>other.b:
            self.bottomHit = True
        if self.y+self.dy < other.y:
            self.topHit = True

    def _check_corners(self,other):
        # corners are pretty tricky. here we are finding how far into the object you are
        #   based on your x, and y positions. if you're farther into the x, you're coming
        #       from the side, vice-versa and you're coming from the top or bottom. it's
        #           actually very mathematically pleasing. further reading:
        # https://gamedev.stackexchange.com/questions/17502/how-to-deal-with-corner-collisions-in-2d
        if self.leftHit and self.topHit: #top left of object               
            if abs(self.r-other.x) > abs(self.b-other.y):
                self.leftHit = False
            else:
                self.topHit = False
        if self.rightHit and self.topHit: # top right of object
            if abs(self.x-other.r) > abs(self.b-other.y):
                self.rightHit = False
            else:
                self.topHit = False
        if self.leftHit and self.bottomHit: # bottom left of object
            if abs(self.r-other.x) > abs(self.y-other.b):
                self.leftHit = False
            else:
                self.bottomHit = False
        if self.rightHit and self.bottomHit: # bottom right of object
            if abs(self.x-other.r) > abs(self.y-other.b):
                self.rightHit = False
            else:
                self.bottomHit = False
                
    def _remove_collision(self,other):
        if self.leftHit: 
            self.dx = 0
            self.x = other.x-self.w
        if self.topHit:
            self.dy = 0
            self.state = 'idle' # if you're hitting the top, stop making you fall through
            self.y = other.y-self.h
        if self.rightHit:
            self.dx = 0
            self.x = other.r
        if self.bottomHit:
            self.dy = 0
            self.y = other.b

    def check_collision(self, other):
        self.leftHit, self.rightHit, self.topHit, self.bottomHit = False, False, False, False
        if self.r + self.dx > other.x and self.x + self.dx < other.r and self.b + self.dy > other.y and self.y + self.dy < other.b:
                self._check_hits(other)
                self._check_corners(other)
                self._remove_collision(other)
                
    def move_right(self, speed, dt):
        self.dx = speed * dt
    def move_left(self, speed, dt):
        self.dx = -speed * dt
    def reset_dx(self):
        self.dx = 0
    def jump(self, power):
        self.dy = -power
        self.state = 'jumping'


class Block(object):
    """ A basic block object
    data:                
        x  - x-axis position
        y  - y-axis position
        w  - block width
        h  - block height
        b  - bottom of block
        r  - right of block
    """
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.r = x+w
        self.b = y+h

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.w, self.h), OUTLINE)

#--------------------------
# MAIN PROGRAM
#--------------------------
pygame.init()
WIDTH  = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

state = 'idle'

# DELTA TIME - to standardize speed across a varity of FPS. 
# if you are interested in understanding how it works, you can read
# https://gafferongames.com/post/fix_your_timestep/
frameTime = time.clock()

# player object
player = Player(WIDTH / 2, HEIGHT / 2 - 200, 20, 30)
RUN_SPEED = 450 # n pixels per second runspeed
GRAVITY   = 8  # gravity - higher is stronger
JUMP_POWER = 2 # self explanatory; your jump power

blocks = []

counter = 1
for i in range(WIDTH // 50 - 5):
    for j in range(counter):
        blocks.append(Block(i * 50, HEIGHT - j * 50, 50, 50))
    counter+=1
for i in range(WIDTH // 50):
    blocks.append(Block(i * 50, HEIGHT - 50, 50, 50))
blocks.append(Block(WIDTH / 2 - 400, HEIGHT / 2 - 150, 200, 100))

def redrawGameWindow():
    screen.fill(BLACK)
    # player is defined as an object
    player.draw(screen)
    # blocks is defined as an array of objects
    for i in range(len(blocks)):
        blocks[i].draw(screen)

def check_keys():
    keys = pygame.key.get_pressed()

    # the state if is so you can't jump while already in the air.
    if keys[pygame.K_SPACE] and player.state == 'idle':
        player.jump(JUMP_POWER)

    if keys[pygame.K_RIGHT] and not player.leftHit:
        player.move_right(RUN_SPEED, dt)
    elif keys[pygame.K_LEFT] and not player.rightHit:
        player.move_left(RUN_SPEED, dt)
    else:
        player.reset_dx()

inPlay = True
while inPlay:
    for event in pygame.event.get():        #Check for any events
        if event.type == pygame.QUIT:       #If user clicked close
            inPlay=False
    redrawGameWindow()
    dt = time.clock() - frameTime
    frameTime = time.clock()

    for i in range(len(blocks)):
        player.check_collision(blocks[i])

    player.update(dt)
    
    check_keys()
    
    
    pygame.display.update()

# always exit pygame in the end =)
pygame.quit()
