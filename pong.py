import pandas as pd
import pygame
from sklearn.neighbors import KNeighborsRegressor

# Variables
WIDTH = 1200
HEIGHT = 600
BORDER = 20
VELOCITY = 1
FRAMERATE = 300


# class definitions
class Ball:
    RADIUS = 20

    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def show(self, colour):
        global screen
        pygame.draw.circle(screen, colour, (self.x, self.y), self.RADIUS)

    def update(self):
        """
        Updates ball position and handles collision
        """
        global background_Colour, foreground_Colour

        new_x = self.x + self.vx
        new_y = self.y + self.vy

        if new_x < BORDER + self.RADIUS:
            self.vx = -self.vx
        elif new_y < BORDER + self.RADIUS or new_y > HEIGHT - BORDER - self.RADIUS:
            self.vy = - self.vy
        elif new_x + Ball.RADIUS > WIDTH - Paddle.WIDTH and abs(new_y - paddle.y) < Paddle.HEIGHT // 2:
            self.vx = - self.vx
        else:
            self.show(background_Colour)
            self.x = self.x + self.vx
            self.y = self.y + self.vy
            self.show(foreground_Colour)


class Paddle:
    WIDTH = 20
    HEIGHT = 100

    def __init__(self, y):
        self.y = y

    def show(self, colour):
        global screen
        pygame.draw.rect(screen, colour,
                         pygame.Rect(WIDTH - self.WIDTH,
                                     self.y - self.HEIGHT // 2,
                                     self.WIDTH, self.HEIGHT))

    def update(self, new_y):
        # new_y = pygame.mouse.get_pos()[1]
        if new_y - self.HEIGHT // 2 > BORDER \
                and new_y + self.HEIGHT // 2 < HEIGHT - BORDER:
            self.show(background_Colour)
            self.y = new_y
            self.show(foreground_Colour)


# Create objects
ball = Ball(WIDTH - Ball.RADIUS - 20, HEIGHT // 2 - 20, - VELOCITY, - VELOCITY)

# Draw the scenario
pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
foreground_Colour = pygame.Color("white")
background_Colour = pygame.Color("black")

screen.fill(background_Colour)  # adds colour to the background

# adds borders to the screen
pygame.draw.rect(screen, foreground_Colour, pygame.Rect((0, 0), (WIDTH, BORDER)))
pygame.draw.rect(screen, foreground_Colour, pygame.Rect(0, 0, BORDER, HEIGHT))
pygame.draw.rect(screen, foreground_Colour, pygame.Rect(0, HEIGHT - BORDER, WIDTH, BORDER))

ball.show(foreground_Colour)  # adds the ball to the screen

paddle = Paddle(HEIGHT // 2)
paddle.show(foreground_Colour)

clock = pygame.time.Clock()  # controls the framerate of the game


# machine learning data collection
# sample = open("game.csv", "w")  # opens a file for writing
# print("x,y,vx,vy,Paddle.y", file=sample)  # initial print to file
pong = pd.read_csv('game.csv')
pong = pong.drop_duplicates()

X = pong.drop(columns="Paddle.y")
y = pong['Paddle.y']

clf = KNeighborsRegressor(n_neighbors=3)
clf.fit(X, y)

df = pd.DataFrame(columns=['x', 'y', 'vx', 'vy'])

# superloop unless player clicks exit on OS gui
while True:
    event = pygame.event.poll()
    if event.type == pygame.QUIT:  # if user clicks quit then loop breaks to exit program
        break

    clock.tick(FRAMERATE)

    pygame.display.flip()  # updates the screen

    # machine learning
    # toPredict = df.append({'x': ball.x, 'y': ball.y, 'vx': ball.vx, 'vy': ball.vy}, ignore_index=True)
    toPredict = pd.concat([df, pd.DataFrame([{'x': ball.x, 'y': ball.y, 'vx': ball.vx, 'vy': ball.vy}])], ignore_index=True)
    shouldMove = clf.predict(toPredict)

    paddle.update(shouldMove[0])
    ball.update()

    # print("{}, {}, {}, {}, {}".format(ball.x, ball.y, ball.vx, ball.vy, paddle.y), file=sample) # prints data to file


pygame.quit()  # won't work on macOS possibly
