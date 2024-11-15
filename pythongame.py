import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt
import pygame
import sys
import random
import threading
import io
import time

# Initialize Pygame
pygame.init()

# Set up the display
screen_width, screen_height = 1920,1080
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("vamsi selected game")

# Define colors 
WHITE = (255, 255, 255)
BLUE = (135, 206, 235)
RED  = (255, 0, 0)

# Load the cloud image
cloud_image = pygame.image.load('Resources/cloud.png')  # Ensure this file is in the same directory (c:users/spand)
cloud_image = pygame.transform.scale(cloud_image, (150, 80))  # Scale to desired size

# load player image
player_image = pygame.image.load('Resources/player.png')
player_image = pygame.transform.scale(player_image,(120,120))

# Load the Meteor image
meteor_image = pygame.image.load('Resources/meteor.png')  # Ensure this file is in the same directory (c:users/spand)
meteor_image = pygame.transform.scale(meteor_image, (150, 150))  # Scale to desired size

player_pos = [200,700]
player_speed = 5     
player_direction = "right" 


class Cloud():
    def __init__(self,x,y):
        self.x = x   # here x,y gives the center position of circle
        self.y = y

    def shape(self,surface):
        surface.blit(cloud_image,(self.x,self.y))

    def moveLeft(self,speed=1):
        self.x -= speed

clouds = [] 
x = 1800
y = 500
for _ in range(5):
    x -= 300
    new_cloud = Cloud(x,y)
    clouds.append(new_cloud)


class Meteor():
    def __init__(self,s,v):
        self.s = s   # here s,v gives the center position of circle
        self.v = v
        self.has_passed = False  # Track if the meteor has passed the player

    def shape(self,surface):
        surface.blit(meteor_image,(self.s,self.v))

    def moveLeft(self,speed):
        self.s -= speed

meteors = []
s = 1900
v = 200
for _ in range(6):
    s -= 300
    new_meteor = Meteor(s,v)
    meteors.append(new_meteor)

# Function to check collision between player and a meteor
def is_collision(player_rect,meteor_rect):
    return player_rect.colliderect(meteor_rect)


# Initial data for the graph
score = 0
data = [0,5,10,15,20]
font = pygame.font.Font(None,36)    # None for default family font, and 36 is font size


# Function to generate the graph
def generate_graph(data):
    x_values = range(1, 6)   # Set the x-axis to a fixed range 1 to 5
    # Update Y-axis based on the current range in data
    max_y = max(data)
    min_y = max(0,max_y - 20)
    y_ticks = [min_y + (i * 5) for i in range(5)]   # Generate y-tick values with 5 values, starting from min_score up to max_score or higher
    # Create figure and axis with dynamic Y limits
    plt.figure(figsize = (3, 3), dpi = 100)
    plt.plot(x_values,data,color = 'blue',marker = 'o')
    plt.title("Score Graph")
    plt.xlabel("Events")
    plt.ylabel("Score")
    plt.xticks(x_values)  # This forces matplotlib explicitly to show each tick from 1 to 5
    plt.yticks(y_ticks)
    plt.ylim(min_y,max_y)  # Adjust Y-axis to the range of data
    plt.grid(True)
    plt.tight_layout()  # to make sure layout fits within figure size

    # Save to an in-memory buffer instead of a file
    buffer = io.BytesIO()
    plt.savefig(buffer, format = 'png', transparent = True)
    buffer.seek(0)
    plt.close()
    return buffer

# Generate the initial graph and load it into Pygame
graph_buffer = generate_graph(data)
graph_image = pygame.image.load(graph_buffer, 'Resources/graph.png')

# Lock for thread-safe image updates
graph_lock = threading.Lock()

# Event flag for graph updates
graph_updated_event = threading.Event()

# Background thread to update the graph with load image from buffer
def background_graph_update():
    global graph_image
    while True:
        time.sleep(1)
        new_buffer = generate_graph(data)
        with graph_lock:  # Ensure that only one thread updates the graph image at a time
            graph_image = pygame.image.load(new_buffer, "Resources/graph.png")
        graph_updated_event.clear()  # Reset the flag after update

# Start the background graph update thread
graph_thread = threading.Thread(target=background_graph_update, daemon=True)
graph_thread.start()




# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    dt = clock.get_time() / 1000  # Adjust object movement using delta time (dt) for consistent speed# to get the time since the last frame, which helps to make the game movement time-dependent instead of frame-dependent

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player_pos[1] -= player_speed

    if keys[pygame.K_DOWN]:
        player_pos[1] += player_speed

    if keys[pygame.K_LEFT]:
        player_pos[0] -= player_speed 
        player_direction = "left"

    if keys[pygame.K_RIGHT]:
        player_pos[0] += player_speed 
        player_direction = "right"

    if keys[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit()  
        
    # Limit the player x and y-axis position to stay within the screen boundaries
    player_pos[0] = max(180,min(player_pos[0],1600))
    player_pos[1] = max(120,min(player_pos[1],850))  # y-coordinate #screen.get_height()-player1_image.get_height() = 850, for aasumption we take it as 850

    player_rect = pygame.Rect(player_pos[0],player_pos[1],player_image.get_width(),player_image.get_height())
     
    # Boundary check and direction change in x-axis
    if player_direction == "right":
        current_image = player_image
    elif player_direction == 'left':
        current_image = pygame.transform.flip(player_image, True, False)  # Flip horizontally for left
    
    
    # Screen background  
    screen.fill(BLUE)
    screen.blit(current_image,(player_pos[0],player_pos[1]))
    
    # Draw and Continuously move the 6 clouds to the left
    for cloud in clouds:
        cloud.shape(screen)
        cloud.moveLeft(speed = 3)

        # Reset cloud position if it moves out of the screen
        if cloud.x < 0:
            cloud.x = 1900  # Move cloud back to the right side of the screen
            cloud.y = random.randrange(150, 800)

    # Draw and Continuously move the 6 meteorss to the left
    for meteor in meteors:
        meteor.shape(screen)
        meteor.moveLeft(speed = 3)

        # Reset meteor position if it moves out of the screen
        if meteor.s < 0:
            meteor.s = 1900     # Move meteor back to the right side of the screen
            meteor.v = random.randrange(100, 800)
            meteor.has_passed = False     # Reset has_passed flag for new meteor position

        meteor_rect = pygame.Rect(meteor.s,meteor.v,130,130)

        # Check for collision with the player
        if is_collision(player_rect,meteor_rect):
            running = False  # Stop the game loop to quit


        if meteor.s < player_pos[0] and not meteor.has_passed:
            score += 5  # Award points for each meteor avoided
            meteor.has_passed = True  # Mark meteor as passed to prevent repeated scoring
            data = data[1:] + [score]  # Update data to keep the rolling 5 most recent score increments
            graph_updated_event.set()  # Trigger graph update
            

    # Display the score and graph on the screen  
    score_text = font.render(f'score:{score}',True,RED)     # font.render(...) creates a text image showing the current score
    screen.blit(score_text,(1500,150))                      # screen.blit(...) draws this text on the screen at specific position (x,y)
    screen.blit(graph_image, (1400, 200))
    

    # Update the display
    pygame.display.flip()
    clock.tick(60)


# Quit Pygame
pygame.quit()
sys.exit()