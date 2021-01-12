# owen moogk
# ai flappy bird
# jan 1 2020

# imports
import pygame, random, os, time, sys, pickle
from random import randint
import neat

# pygame settings
windowWidth = 600
windowHeight = 800
birdHeight = 30
birdWidth = 40

# game settings
gameSpeed = 30
gravity = 0.8
jumpPower = 12
pipeHeight = 650
pipeWidth = 75 
pipeGap = 200
birdX = 100
pipeSpeed = 5

# clock
clock = pygame.time.Clock()

# assets
pipeImg = pygame.transform.scale(pygame.image.load(os.path.join("assets","pipe.png")), (pipeWidth, pipeHeight))
pipeImgFlipped = pygame.transform.flip(pipeImg, False, True)
backgroundImg = pygame.transform.scale(pygame.image.load(os.path.join("assets","background.png")), (windowWidth, windowHeight))
birdImg = pygame.transform.scale(pygame.image.load(os.path.join("assets","bird.png")), (birdWidth, birdHeight))
baseImg = pygame.image.load(os.path.join("assets","base.png"))
pygame.font.init()
font = pygame.font.SysFont("comicsans", 50)

# display
screen = pygame.display.set_mode((windowWidth, windowHeight))
pygame.display.set_caption('Flappy Bird')

# bird class
class bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ySpeed = 0
    def jump(self):
        self.ySpeed = 0-jumpPower
        self.tick_count = 0
        self.height = self.y
    def gravity(self):
        self.ySpeed += gravity
        self.y += ySpeed
    def topBottomCollision(self):
        playing = True
        if self.y < 0:
            playing = False
        if self.y > windowHeight - birdHeight:
            playing = False
        return(playing)

# pipe class
class pipe:
    def __init__(self, yBottom,x):
        self.yBottom = yBottom
        self.yTop = yBottom - pipeGap - pipeHeight
        self.x = x
        self.pointScored = False

def renderScore(score):
    score_label = font.render("Score: " + str(score),1,(255,255,255))
    screen.blit(score_label, (10, 10))

def eval_genomes(genomes,config):
    
    # configuring all the birds and their data
    ge = []
    birds = []
    nets = []
    for g in genomes:
        net = neat.nn.FeedForwardNetwork(g,config)
        nets.append(net)
        birds.append(bird(230, 350))
        g.fitness = 0
        ge.append(g)



    pipes = []
    pipes.append(pipe(randint(pipeGap + 50,windowHeight-200),windowWidth))

    playing = True
    score = 0

    # when the player is in the game (ie not lost or on the starting screen)
    while playing:
        # looping thru events
        events = pygame.event.get()
        for event in events:
            # if x button pressed stop just break out of these loops
            if event.type == pygame.QUIT:
                running = False
                playing = False

        # background
        screen.blit(backgroundImg,(0,0))

        for bird in birds:
            bird.gravity()
            playing = bird.topBottomCollision()

        # when the pipe is far enough along then append a new one
        if pipes[len(pipes)-1].x < windowWidth - 200:
            pipes.append(pipe(randint(pipeGap + 50,windowHeight-200),windowWidth))

        # loop thru pipes
        for pipe in pipes:
            for bird in birds:
                # collision detection
                if pipe.x < bird.x + birdWidth and pipe.x + pipeWidth > bird.x and (pipe.yBottom < bird.y + birdHeight or pipe.yBottom - pipeGap > bird.y): # checking if the pipe x overlaps with the bird x
                    playing = False
            # move pipes
            i.x -= pipeSpeed
            
            # blit images
            screen.blit(pipeImg,(i.x,i.yBottom))
            screen.blit(pipeImgFlipped, (i.x,i.yTop))

            # when off screen delete
            if i.x < 0 - pipeWidth:
                pipes.remove(pipes[0])

        # bird onto screen
        screen.blit(birdImg,(b1.x,b1.y))
        score += 1
        renderScore(score)

        # display
        clock.tick(gameSpeed)
        pygame.display.update()

def run(config_path):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(eval_genomes, 50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "neat-config.txt")
    run(config_path)