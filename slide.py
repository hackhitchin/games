#!/usr/bin/env python3

import sys, pygame, numpy, random, time
from joystick import Joystick

pygame.init()

size = (width, height) = (240,64)
black = (0,0,0)

BOARDX=20
BOARDY=10

BASEX=96    # Horizontal start position of board

screen = pygame.display.set_mode(size, pygame.SCALED)

# Repeat keydown events every 200ms - for block movement
pygame.key.set_repeat(200)

# Custom event for running the game
ANIMATE=pygame.event.custom_type()

# Fonts
# "Score" and "Lines"
scoreword_f = pygame.font.Font(None, 16)
# The score and lines counts
scoretext_f = pygame.font.Font("digital-7.monoitalic.ttf",28)
# "High score"
highword_f = pygame.font.Font(None, 14)
# High score
hightext_f = pygame.font.Font("digital-7.monoitalic.ttf",20)

# "Game over!"
gameover_f = pygame.font.Font(None, 32)   # Default pygame font

# "Press any key"
presskey_f = pygame.font.Font(None, 14)


score = 0
lines = 0
highscore = 0
newhs = False

board = numpy.zeros((BOARDX,BOARDY), int)

# Startup screen
slide = numpy.array([
    [ 0,1,1,0,0,2,0,3,0,0,0,0,5,0,0,0,0,0,0],
    [ 1,0,0,1,0,2,0,0,0,0,0,0,5,0,0,0,0,0,0],
    [ 1,0,0,0,0,2,0,4,0,0,5,5,5,0,0,6,6,0,0],
    [ 0,1,1,0,0,2,0,4,0,5,0,0,5,0,6,0,0,6,0],
    [ 0,0,0,1,0,2,0,4,0,5,0,0,5,0,6,6,6,6,0],
    [ 1,0,0,1,0,2,0,4,0,5,0,0,5,0,6,0,0,0,0],
    [ 0,1,1,0,0,2,0,4,0,0,5,5,5,0,0,6,6,6,0]
])

# Which shape is selected
shape=None
shape_n = 0

# Position of shape
shapex = 0
shapey = 0

# Next shape, if picked
nextshape=None
ns_n = 0

# All the blocks, in every possible orientation
tetr = [ [numpy.array([
        [0,1,0,0],
        [1,1,1,0],
        [0,0,0,0],
        [0,0,0,0]]),
    numpy.array([
        [0,1,0,0],
        [0,1,1,0],
        [0,1,0,0],
        [0,0,0,0]]),
    numpy.array([
        [0,0,0,0],
        [1,1,1,0],
        [0,1,0,0],
        [0,0,0,0]]),
    numpy.array([
        [0,1,0,0],
        [1,1,0,0],
        [0,1,0,0],
        [0,0,0,0]])
    ],
    [numpy.array([
        [0,2,0,0],
        [0,2,0,0],
        [0,2,0,0],
        [0,2,0,0]]),
    numpy.array([
        [0,0,0,0],
        [2,2,2,2],
        [0,0,0,0],
        [0,0,0,0]])
    ],
    [numpy.array([
        [3,3,0,0],
        [3,3,0,0],
        [0,0,0,0],
        [0,0,0,0]])
    ],
    [numpy.array([
        [4,0,0,0],
        [4,4,0,0],
        [0,4,0,0],
        [0,0,0,0]]),
    numpy.array([
        [0,4,4,0],
        [4,4,0,0],
        [0,0,0,0],
        [0,0,0,0]])
    ],
    [numpy.array([
        [0,5,0,0],
        [5,5,0,0],
        [5,0,0,0],
        [0,0,0,0]]),
    numpy.array([
        [5,5,0,0],
        [0,5,5,0],
        [0,0,0,0],
        [0,0,0,0]])
    ],
    [numpy.array([
        [6,0,0,0],
        [6,0,0,0],
        [6,6,0,0],
        [0,0,0,0]]),
    numpy.array([
        [6,6,6,0],
        [6,0,0,0],
        [0,0,0,0],
        [0,0,0,0]]),
    numpy.array([
        [6,6,0,0],
        [0,6,0,0],
        [0,6,0,0],
        [0,0,0,0]]),
    numpy.array([
        [0,0,6,0],
        [6,6,6,0],
        [0,0,0,0],
        [0,0,0,0]])
    ],
    [numpy.array([
        [0,7,0,0],
        [0,7,0,0],
        [7,7,0,0],
        [0,0,0,0]]),
    numpy.array([
        [7,0,0,0],
        [7,7,7,0],
        [0,0,0,0],
        [0,0,0,0]]),
    numpy.array([
        [7,7,0,0],
        [7,0,0,0],
        [7,0,0,0],
        [0,0,0,0]]),
    numpy.array([
        [7,7,7,0],
        [0,0,7,0],
        [0,0,0,0],
        [0,0,0,0]])
    ]
]

# Random bag - attempts to avoid long runs where a particular piece
# is not seen by making it more likely that pieces not selected
# recently will be picked
class bag:
    def __init__(self,size):
        self.size = size
        self.bag = []
        self.count = 0

        # initialise bag
        for c in range(size*2):
            self.__replace__()

    def __replace__(self):
        self.bag.append(self.count)
        self.count += 1
        if self.count >= self.size:
            self.count = 0

    def get(self):
        n = self.bag.pop(random.randrange(len(self.bag)))
        self.__replace__()
        return n

# Turn a number between 1 and 7 into an RGB colour 
def col(n,bright=255):
    r = bright if n & 1 else 0
    g = bright if n & 2 else 0
    b = bright if n & 4 else 0

    return (r,g,b)

# Return True if no collision, False otherwise
def clear_collision(shape, sx, sy):
    for x,y in ( (x,y) for x in range(4) for y in range(4) ):
        if shape[x,y]:
            if x+sx<0:
                # Hit the left-hand edge
                return False
            if y+sy <0 or y+sy >= BOARDY:
                # Hit the top or bottom edge
                return False
            if x+sx<BOARDX and board[x+sx,y+sy]:
                # Hit a block
                return False
    return True

# Check for any filled lines. Need only check from startx to startx+3, as
# that's the maximum number of lines one shape could create.
# Return number of lines removed
def linecheck(startx):
    lines = 0
    removedlines = []
    for x in range(min(startx+3,BOARDX-1),startx-1,-1):
        for y in range(BOARDY):
            if not board[x,y]:
                break
        else:
            # All blocks on this line filled
            lines+=1

            # Remove this line
            for xx in range(x,BOARDX-1):
                board[xx] = board[xx+1]
            # Add new blank line at right of board
            board[BOARDX-1] = numpy.zeros(BOARDY)

            pygame.draw.rect(screen, (192,192,192), pygame.Rect(BASEX+x*6,2,6,6*BOARDY))
            removedlines.append(x)

    if lines:
        # Draw screen and pause for a moment to animate
        pygame.display.flip()
        pygame.time.wait(100)
        for x in removedlines:
            pygame.draw.rect(screen, (64,64,64), pygame.Rect(BASEX+x*6,2,6,6*BOARDY))
        pygame.time.wait(100)
        pygame.display.flip()

        # Clear out queued ANIMATE events
        pygame.event.get(ANIMATE)

    return lines

# Text positions on screen
scorex = None
linesy = None
hsx = None

# Draw either the full screen (default) or just the high score (used for when
# a new high score is reached). Optionally alter the colour or brightness of
# the score/highscore
def draw(full=True, scorecol=64, hscol=64):
    global scorex, linesy, hsx

    if full:
        screen.fill(black)

    scoreword = scoreword_f.render("Score", True, (192,255,255), black)
    screen.blit(scoreword, (2,2))

    scoretext = scoretext_f.render(f"{score:04d}", True, (255,scorecol,scorecol), black)
    
    hstext = hightext_f.render(f"{highscore:04d}", True, (64,64,255), black)
    
    if scorex is None:
        # Just calculate positions once, in case minor variances in
        # anti-aliasing make things jump about
        scorex = 92-scoretext.get_width()
        linesy = scoretext.get_height()
        hsx = 92-hstext.get_width()

    hstext = hightext_f.render(f"{highscore:04d}", True, (hscol,hscol,255), black)
    screen.blit(hstext, (hsx, linesy*2))

    if not full:
        return

    screen.blit(scoretext, (scorex, 0))

    linesword = scoreword_f.render("Lines", True, (255,192,255), black)
    screen.blit(linesword, (2,2+linesy))

    linestext = scoretext_f.render(f"{lines:04d}", True, (64,255,64), black)
    screen.blit(linestext, (scorex, linesy))

    hsword = highword_f.render("High score", True, (255,255,192), black)
    screen.blit(hsword, (2,2+linesy*2))

    # Draw the board, and possibly a shape to the right of it
    for x in range(BOARDX+5):
        r = 32 if x==BOARDX-1 else 0

        for y in range(BOARDY):
            if x < BOARDX:
                v = board[x,y]
            else:
                v = 0

            if shape is not None and x>=shapex and y>=shapey:
                if (x< shapex+4 and y<shapey+4):
                    v = shape[shape_n][x-shapex,y-shapey] or v
            
            if nextshape is not None and BOARDX <= x < BOARDX+4 and 4 <= y <= 7:
                v = v or nextshape[ns_n][x-BOARDX-1,y-4]

            if v:
                pygame.draw.rect(screen, col(v), pygame.Rect(BASEX+x*6,2+y*6,6,6))
                pygame.draw.rect(screen, col(v,192), pygame.Rect(BASEX+x*6,2+y*6,6,6), width=1)
            elif x<BOARDX:
                c = 16+16*(y%2)
                pygame.draw.rect(screen, (c+r,c,c), pygame.Rect(BASEX+x*6,2+y*6,6,6))

    pygame.display.flip()

# Reset everything (except the high score) and play a game
def play():
    global board, shape,shape_n, nextshape, ns_n, shapex, shapey, score, lines, highscore, newhs
    
    endgame=0
    
    score = 0
    lines = 0
    newhs = False
    scoreflash = 0

    t_score = 0
    t_lines = 0

    board = numpy.zeros((BOARDX,BOARDY), int)

    tbag = bag(len(tetr))

    shape=tetr[tbag.get()]
    shape_n = 0

    shapex = BOARDX-4
    shapey = int((BOARDY-4)/2)

    nextshape=tetr[tbag.get()]
    ns_n = 0

    frames = 20
    animcount = frames
    drop = False 

    while not endgame:
        event = pygame.event.wait()

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.JOYAXISMOTION or event.type == pygame.JOYHATMOTION:
            js.event(event)

        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE or 
            event.type == pygame.JOYBUTTONDOWN and event.button <4):
            new_n = shape_n-1
            if new_n<0:
                new_n=len(shape)-1
            if clear_collision(shape[new_n], shapex, shapey):
                shape_n = new_n
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP or (event.type == Joystick.BUTTONDOWN and event.button == Joystick.UP):
            if clear_collision(shape[shape_n], shapex, shapey-1):
                shapey -= 1
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN or (event.type == Joystick.BUTTONDOWN and event.button == Joystick.DOWN):
            if clear_collision(shape[shape_n], shapex, shapey+1):
                shapey += 1

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT or (event.type == Joystick.BUTTONDOWN and event.button == Joystick.LEFT):
            drop = True
        elif event.type == pygame.KEYUP and event.key == pygame.K_LEFT or (event.type == Joystick.BUTTONUP and event.button == Joystick.LEFT):
            drop = False
            animcount = frames

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            endgame = True

        elif event.type == ANIMATE and (animcount==0 or drop):
            if clear_collision(shape[shape_n], shapex-1, shapey):
                shapex -= 1
                if nextshape is None:
                    # Is the current shape completely on the board?
                    for (x,y) in ((x,y) for x in range(4) for y in range(4)):
                        if shape[shape_n][x,y] and shapex+x>=BOARDX:
                            break
                    else:
                        # If so, pick the next shape ready for display
                        nextshape = tetr[tbag.get()]
            else:
                # Can't fall any further - are we all on the board?
                for (x,y) in ((x,y) for x in range(4) for y in range(4)):
                    if shape[shape_n][x,y]:
                        if x+shapex>= BOARDX:
                            endgame = 1
                            nextshape = None
                            break
                        else:
                            board[x+shapex,y+shapey] = shape[shape_n][x,y]
                else:
                    # Check for lines
                    lc = linecheck(shapex)
                    t_lines += lc
                    if lc:
                        t_score += 2*lc - 1   # 1, 3, 5, 7 points
                        if lc == 4:
                            t_score += 1          # 8 points for 4 lines
                        # Recalculate game speed - gets faster every 20 points
                        # Starts at 20*50ms = 1 second between moves
                        # Ends at 4*50ms = 200ms between moves
                        newframes = max(4,20-int(t_score/20))
                        if newframes != frames:
                            frames = newframes
                            scoreflash = 64

                    # All on the board, get the next shape
                    shapex = BOARDX
                    shapey = 4
                    shape = nextshape
                    shape_n = ns_n
                    nextshape = None

        animcount -= 1
        if animcount < 0:
            animcount = frames

        draw(scorecol=64+4*(32-abs(32-scoreflash)))
        if scoreflash>0:
            scoreflash -= 4

        # Scores tick up on the counter rather than being instantly applied
        if t_score>score and (animcount % 3 == 0):
            score+=1
            if score>highscore:
                highscore = score
                newhs = True
        if t_lines>lines and (animcount % 3 == 0):
            lines+=1

        if endgame:
            if t_score>score or t_lines>lines:
                score=t_score
                lines=t_lines
                if score>highscore:
                    highscore = score
                    newhs = True

            # Make sure the score wasn't in the process of flashing
            draw()

            textg = gameover_f.render("Game", True, (255,255,255))
            texto = gameover_f.render("Over", True, (255,255,255))
            b_textg = gameover_f.render("Game", True, (0,0,0))
            b_texto = gameover_f.render("Over", True, (0,0,0))
            textx = BASEX+6*BOARDX/2 - int(textg.get_width()/2)
            texty = 4
            # Draw it 4 times round the main text to separate from the background
            for (x,y) in [(-1,-1), (1,-1), (-1,1), (1,1)]:
                screen.blit(b_textg, (textx+x,texty+y))
            screen.blit(textg, (textx,texty))
            textx = BASEX+6*BOARDX/2 - int(texto.get_width()/2)
            texty = 2+textg.get_height()
            # Draw it 4 times round the main text to separate from the background
            for (x,y) in [(-1,-1), (1,-1), (-1,1), (1,1)]:
                screen.blit(b_texto, (textx+x,texty+y))
            screen.blit(texto, (textx,texty))
        pygame.display.flip()

draw()

# Intro animation
for slidein in range(BOARDX,-1,-1):
    for x in range(BOARDX-1):
        for y in range(BOARDY):
            try:
                board[x+1+slidein,y] = slide[y,x]
            except IndexError:
                pass
    draw()
    pygame.time.wait(100)

today = time.localtime()
if today.tm_mon == 12 and 10 < today.tm_mday < 31:
    hat = pygame.image.load("smallhat.png")
    screen.blit(hat, (142,1))

pygame.display.flip()

pygame.time.set_timer(ANIMATE,50)

js = Joystick()
js.set_repeat(200)
js.start()

b_textpk = presskey_f.render("Press any key to start", True, black)
pk_x = BASEX+6*BOARDX/2 - int(b_textpk.get_width()/2)
pk_y = 48

while True:
    clearkeys = False
    counter = 0
    while True:
        event = pygame.event.wait()

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.JOYAXISMOTION or event.type == pygame.JOYHATMOTION:
            js.event(event)

        elif event.type == pygame.KEYDOWN and clearkeys:
            break

        elif event.type == pygame.JOYBUTTONDOWN and clearkeys:
            break

        if event.type == ANIMATE:
            counter+=1
            # Wait until no keys are being pressed before telling the player
            # they can press a key to start
            if clearkeys:
                textpk = presskey_f.render("Press any key to start", True, col(7,63+12*abs(16-counter%31)))
                # Draw it 4 times round the main text to separate from the background
                for (x,y) in [(-1,-1), (1,-1), (-1,1), (1,1)]:
                    screen.blit(b_textpk, (pk_x+x,pk_y+y))

                screen.blit(textpk, (pk_x,pk_y))
                # Redraw the highscore
                if newhs:
                    draw(False, hscol=63+12*abs(8-counter%15))
                pygame.display.flip()
            elif counter>20:
                # Check to see no keys are being pressed
                clearkeys = not (any(pygame.key.get_pressed()) or any(js.get_pressed()))

    play()
