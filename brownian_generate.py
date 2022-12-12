"""
Jack D'Iorio
jcdiorio@uvm.edu
CS 021

Simulates DLA using Pygame

"""

import random
from random import choice
import pygame
import math
from ast import literal_eval
from re import findall
from sys import exit

pygame.init()
pygame.font.init()

# Waits for enter key to be pressed (4 indents ugh!)
def wait():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

# Draws a 5x5 seed and places it in the center of the screen 
def start_seed():
    seed = pygame.Rect((((width - 5) / 2), ((height - 5) / 2)), (5, 5))
    pygame.draw.rect(screen, (0, 255, 0), seed)
    tree.append(seed)
    pygame.display.update(seed)

# Returns a tuple of (x, y) coordinates on edge of circle with radius r
def position_gen(r):
    center_x, center_y = (width / 2), (height / 2)
    rand_x, rand_y = -1, -1
    while (rand_x - center_x) ** 2 + (rand_y - center_y) ** 2 != r ** 2:
        angle = 2 * math.pi * random.random()
        rand_x = r * math.cos(angle) + center_x
        rand_y = r * math.sin(angle) + center_y
    return (rand_x, rand_y)

# Returns a tuple of (x, y) coordinates after random walk with constraints
def next_move(particle, r):
    new_x = random.randint(-1, 1)
    new_y = random.randint(-1, 1)
    particle.move_ip(new_x, new_y)

    # Keep particle on screen
    if particle.left < 0 or particle.left > width:
        particle.move_ip(new_x * -1, 0)
    if particle.top < 0 or particle.top > height:
        particle.move_ip(0, new_y * -1)
    
    # Keep particle in circle
    center_x, center_y = (width / 2), (height / 2)
    pos = (particle.left - center_x) ** 2 + (particle.top - center_y) ** 2
    if pos > r ** 2:
        particle.move_ip(new_x * -1, new_y * -1)
    
    return (new_x, new_y)


# Checks if particle collides with tree
def check_collision(particle, tree):
    if particle.collidelist(tree) != -1:
        tree.append(particle)
        return False
    else:
        return True

# Returns distance from seed to farthest particle
def gen_radius(tree):
    cntr_x, cntr_y = tree[0].left, tree[0].top
    greatest_dist = 0
    for rect in tree:
        dist = math.sqrt((rect.left - cntr_x) ** 2 + (rect.top - cntr_y) ** 2)
        if dist > greatest_dist:
            greatest_dist = dist
    return greatest_dist + 10 # Adds 2 particle diameters for more accurate sim

#                   _____Main loop and simulation______
while True:

    # Grabs and sets settings from config.txt using regex to grab numbers
    with open("FinalProject/config.txt") as f:
        settings = [line.rstrip() for line in f]
        gen_settings = findall(r"[-+]?(?:\d*\.*\d+)", "".join(settings[:5]))
    
    width = int(gen_settings[0])
    height = int(gen_settings[1])
    particle_number = int(gen_settings[2])

    # Check if random seed is entered or is generated
    randgen_seed = float(gen_settings[3])
    if randgen_seed != 0:
        random.seed(randgen_seed)
    else:
        random.seed()
    
    # Sets color tuple list from config.txt dynamically beginning at line 8
    color_lst = []
    for i in range(7, len(settings)):
        color_lst.append(literal_eval(settings[i])) # literal_eval is safe!
    color_margin = particle_number / len(color_lst)

    # Sets up pygame window
    screen = pygame.display.set_mode((width, height))
    screen.fill((0, 0, 0))
    pygame.display.set_caption("DLA Simulation")
    cur_font = pygame.font.SysFont("Cascadia Code", 20)
    pygame.display.flip()

    # Resets tree, creates seed
    tree = []
    start_seed()

    for i in range(particle_number):

        # Set radius so that the circle tightly encloses the tree
        radius = gen_radius(tree)

        # Generates particle on edge of bounding circle
        particle = pygame.Rect(position_gen(radius), (5, 5))

        # Simulates particle until it attatches to tree
        dettatched = True
        while dettatched:

            # Clear event queue to prevent crashing while not handling events
            pygame.event.clear()

            # Random walk
            new_x, new_y = next_move(particle, radius)

            # Check for particle collision with tree
            dettatched = check_collision(particle, tree)
                
        # Re-adjusts particle to be adjacent to collision
        if new_x != 0:
            particle.move_ip(new_x * -1, 0)
        if new_y != 0:
            particle.move_ip(0, new_y * -1)
        
        # Change color based on time added
        try:
            particle_color = color_lst[int(i / color_margin)]
        except IndexError:
            particle_color = color_lst[-1]

        # Draw when done walking
        pygame.draw.rect(screen, particle_color, particle)
        pygame.display.update(particle)

    # Display text to help user
    message = "'Enter' for new fractal."
    text_surface = cur_font.render(f'{message}', True, (255, 255, 255))
    screen.blit(text_surface, (0, 0))
    pygame.display.flip()
    
    # Waits to generate a new tree until enter is pressed or exits
    wait()