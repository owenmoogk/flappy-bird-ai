# init
import pygame, random, os, time, neat
pygame.font.init()  # init font
windowWidth = 600
windowHeight = 900
myFont = pygame.font.SysFont("comicsans", 50)
screen = pygame.display.set_mode((windowWidth, windowHeight))
pygame.display.set_caption("Flappy Bird")

# generation stuff
gen = 0

# settings
gameSpeed = 30
gravity = 1
jumpPower = 10
pipeHeight = 650
pipeWidth = 75 
birdHeight = 30
birdWidth = 40
pipeGap = 200
birdX = 100
pipeSpeed = 7
drawLines = True

# images
pipeImg = pygame.transform.scale(pygame.image.load(os.path.join('assets','pipe.png')).convert_alpha(),(pipeWidth, pipeHeight))
backgroundImg = pygame.transform.scale(pygame.image.load(os.path.join("assets","background.png")).convert_alpha(), (windowWidth, windowHeight))
birdImg = pygame.transform.scale(pygame.image.load(os.path.join("assets","bird.png")), (birdWidth, birdHeight))

class Bird:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tick_count = 0
        self.vel = 0
        
    def jump(self):
        self.vel = -1 * jumpPower

    def move(self):

        self.vel += gravity
        self.y += self.vel

    def topBottomCollision(self):
        collided = False
        if self.y < 0:
            collided = True
        if self.y > windowHeight - birdHeight:
            collided = True
        return(collided)

    def draw(self):
        screen.blit(birdImg,(self.x,self.y))

class Pipe:

    def __init__(self, x):
        
        self.x = x
        self.height = 0

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pipeImg, False, True)
        self.PIPE_BOTTOM = pipeImg

        self.passed = False

        self.set_height()

    def set_height(self):

        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + pipeGap

    def move(self):
        self.x -= pipeSpeed

    def draw(self):
        screen.blit(self.PIPE_TOP, (self.x, self.top))
        screen.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        if self.x < bird.x + birdWidth and self.x + pipeWidth > bird.x and (self.bottom < bird.y + birdHeight or self.bottom - pipeGap > bird.y):
            return True
        return False

def draw_window(birds, pipes, score, gen, pipe_ind):
    screen.blit(backgroundImg, (0,0))

    for pipe in pipes:
        pipe.draw()

    for bird in birds:
        if drawLines:
            try:
                pygame.draw.line(screen, (255,0,0), (bird.x + birdWidth/2, bird.y + birdHeight/2), (pipes[pipe_ind].x + pipeWidth/2, pipes[pipe_ind].bottom - pipeGap), 5)
                pygame.draw.line(screen, (255,0,0), (bird.x + birdWidth/2, bird.y + birdHeight/2), (pipes[pipe_ind].x + pipeWidth/2, pipes[pipe_ind].bottom), 5)
            except:
                pass
        bird.draw()

    # score label
    score_label = myFont.render("Score: " + str(score),1,(255,255,255))
    screen.blit(score_label, (windowWidth - score_label.get_width() - 15, 10))

    # generations label
    score_label = myFont.render("Gens: " + str(gen),1,(255,255,255))
    screen.blit(score_label, (10, 10))

    # alive label
    score_label = myFont.render("Alive: " + str(len(birds)),1,(255,255,255))
    screen.blit(score_label, (10, 50))

    pygame.display.update()

# this is the main function that is called
# the while loop runs the game while there are birds
def eval_genomes(genomes, config):

    global gen
    gen += 1

    # this is the ai part
    nets = []
    birds = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        # making a bird for every gene / neural network
        birds.append(Bird(230,350))
        ge.append(genome)

    # starting the pipes and score
    pipes = [Pipe(700)]
    score = 0

    clock = pygame.time.Clock()

    # main while loop
    while len(birds) > 0:
        clock.tick(gameSpeed)

        # quit function
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                break


        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1

        # give each bird a fitness of 0.1 for each frame it stays alive
        for x, bird in enumerate(birds):
            ge[x].fitness += 0.1
            bird.move()

            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                bird.jump()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            # check for collision
            for bird in birds:
                if pipe.collide(bird):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            # can add this line to give more reward for passing through a pipe (not required)
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(windowWidth))

        for r in rem:
            pipes.remove(r)

        for bird in birds:
            if bird.topBottomCollision():
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        draw_window(birds, pipes, score, gen, pipe_ind)

def run(config_file):

    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat-config.txt')
    run(config_path)