"""
Jack D'Iorio
jcdiorio@uvm.edu
CS 021

Simulates DLA using Pygame
"""

import random
import pygame
import math

from ast import literal_eval
from sys import exit

from configparser import ConfigParser

pygame.init()
pygame.font.init()

# Waits for enter key to be pressed
def wait():
    while True:
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            return

# Exit event handling code for pygame
def exit_handle():
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        pygame.quit()
        exit()
    return

# Draws a seed particle and places it in the center of the canvas
def start_seed(particle_size):
    center_x, center_y = (width / 2), (height / 2)
    seed = pygame.Rect((center_x, center_y), (particle_size, particle_size))
    pygame.draw.rect(screen, (0, 255, 0), seed)
    tree.append(seed)
    pygame.display.update(seed)

# Returns a tuple of (x, y) coordinates on edge of circle with radius r
def position_gen(r):
    center_x, center_y = (width / 2), (height / 2)
    rand_x, rand_y = -1, -1
    angle = 2 * math.pi * random.random()
    rand_x = r * math.cos(angle) + center_x
    rand_y = r * math.sin(angle) + center_y
    return (rand_x, rand_y) 

# Returns a tuple of (x, y) coordinates after random walk with constraints
def next_move(particle, r, step):
    new_x = random.choice([(step * -1), 0, step])
    new_y = random.choice([(step * -1), 0, step])
    particle.move_ip(new_x, new_y)
    
    # Keep particle in circle
    center_x, center_y = (width / 2), (height / 2)
    pos = (particle.left - center_x) ** 2 + (particle.top - center_y) ** 2
    if pos > r ** 2:
        particle.move_ip(new_x * -1, new_y * -1)
    
    return (new_x, new_y)

# Checks if particle is dettatched from tree and sticks due to k_stick
def check_collision(particle, tree, k_stick):
    if particle.collidelist(tree) != -1 and random.random() < k_stick:
        tree.append(particle)
        return False
    else:
        return True

# Returns distance from seed to farthest particle + 2 particle diameters
def gen_radius(tree, particle_size):
    cntr_x, cntr_y = tree[0].left, tree[0].top
    greatest_dist = 0
    for rect in tree:
        dist = math.sqrt((rect.left - cntr_x) ** 2 + (rect.top - cntr_y) ** 2)
        if dist > greatest_dist:
            greatest_dist = dist
    return greatest_dist + (2 * particle_size)

# Checks if particle is near tree and if not, sets step size to particle_width
def check_neighbors(particle, tree, particle_size):
    growth = particle_size * 2
    particle.inflate_ip(growth, growth)
    if particle.collidelist(tree) != -1:
        particle.inflate_ip((growth * -1), (growth * -1))
        return 1
    else:
        particle.inflate_ip((growth * -1), (growth * -1))
        return particle_size

#                   _____Main loop and simulation______
while True:

    # Reads config file for settings
    config = ConfigParser()
    config.read("config.cfg")
    settings = dict(config.items("SIM_SETTINGS"))

    width = int(settings["width"])
    height = int(settings["height"])
    particle_number = int(settings["particle-number"])
    particle_width = int(settings["particle-width"])
    stick_chance = float(settings["stick-chance"])
    color_lst = literal_eval(settings["color-list"])
    
    # Sets or generates random seed
    try:
        random.seed(float(settings["set-random-seed"]))
    except ValueError:
        random.seed()

    # Sets up pygame window
    screen = pygame.display.set_mode((width, height))
    screen.fill((0, 0, 0))
    pygame.display.set_caption("DLA Simulation")
    cur_font = pygame.font.SysFont("Cascadia Code", 20)
    pygame.display.flip()

    # Resets tree, creates seed
    tree = []
    start_seed(particle_width)

    for i in range(particle_number):

        # Set radius so that the circle tightly encloses the tree
        radius = gen_radius(tree, particle_width)

        # Generates particle on edge of bounding circle
        gen_coords = position_gen(radius)
        particle = pygame.Rect(gen_coords, (particle_width, particle_width))

        # Simulates particle until it attatches to tree
        dettatched = True
        while dettatched:

            # Ensures user can quit during simulation
            exit_handle()

            # Sets step_size after checking for adjacent particles
            step_size = check_neighbors(particle, tree, particle_width)

            # Random walk
            new_x, new_y = next_move(particle, radius, step_size)

            # Check for particle collision with tree
            dettatched = check_collision(particle, tree, stick_chance)
                
        # Re-adjusts particle to be adjacent to collision
        particle.move_ip(new_x * -1, new_y * -1)
        
        # Change color based on list, divide colors evenly
        color_margin = particle_number / len(color_lst)
        particle_color = color_lst[int(i / color_margin)]

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