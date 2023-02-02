# Pygame 2D Lighting Engine
[![python 3.10.6](https://img.shields.io/badge/python-3.10.6-blue)](https://www.python.org/) [![pygame 2.1.2](https://img.shields.io/badge/pygame-2.1.2-green)](https://www.pygame.org/wiki/about)
![alt text](https://github.com/LuckeyDuckey/Pygame_Lighting_Engine/blob/main/imgs/Dungeon.PNG)
## Infomation
This is a 2D lighting engine made in python to be used with the pygame library. It features dynamic lights that cast shadows and colors mix properly. It is still fairly simple and lacks many of the features of modern game engine lighting systems however as far as I can tell this is the first available generalizable 2D lighting system in pygame so I thought I would document it for anyone looking to use it. This is still in development so in the future it will hopefully have many more features unless I get bored of this project and move on which I hope I don't but we shall see.
## Performance
.
## Feedback / Bugs
If you encounter any bugs with the package please let me know and I will attempt to fix them as soon as possible this is still in development so is bound to have a few bugs here and there. Also if you think of any ideas that you think are worth adding reach out to me depending on what they are and if I like them I might add them to the package. Also please note that when lights go inside rectangles the shadows will look messed up this is not a bug lights should simply not be inside shadow-casting rectangles.
## How to install
To install the engine you simply download the ```Pygame_Lights.py``` file and place it in the same directory as the python file in which you are attempting to use it in. After you have done this make sure you have numpy and pygame installed as they are necessary for the usage of this library, they can be installed using the 2 commands listed below simply run them in your terminal:
```
pip install numpy --user
pip install pygame --user
```
# Usage
## Overview
Using this engine is very simple. For starters, you will need to import the engine do this simply by adding ```import Pygame_Lights``` to the top of your code. After that, you will want to initialize a light. This can be done using this line of code:
```python
Light = Pygame_Lights.LIGHT(size:int, pixel_shader:pygame.Surface)
```
```size:int``` -> The size of the light can be any size however the bigger the worse for performance

```pixel_shader:pygame.Surface``` -> This is a pygame surface that is used as the lights texture it can be loaded from an image or created using the pixel_shader function that is built into this package
##
If you want to generate a light texture using this package you must use the pixel_shader function which takes in some parameters about the light and will return a pygame surface based on those parameters, I will go over how to use it here:
```python
Pygame_Lights.pixel_shader(size:int, color:Tuple[int,int,int], intensity:int(0-1), point:Boolean, angle:int(0-360), angle_width:int(0-360))
```
```size:int``` -> The size of the light can be any size however the bigger the worse for performance

```color:Tuple[int,int,int]``` -> The color of the light in RGB format each value is 0-255

```intensity:int(0-1)``` -> The intensity of the light each value is 0-1

```point:Boolean``` -> A boolean value determining whether the light is a point light or not

```angle:int(0-360)``` -> The angle at which the light faces (only needed if the light is a point light)

```angle_width:int(0-360)``` -> The width of the point light (only needed if the light is a point light)

##

Next, you will need to update the lights in each frame this will require a few extra lines of code:
```python
lights_display = pygame.Surface((display.get_size()))

lights_display.blit(Pygame_Lights.global_light(display.get_size(), intensity:int(0-255)), (0,0))
Light.main(Rects:Tuple[pygame.Rect], lights_display, x:int, y:int)
    
display.blit(lights_display, (0,0), special_flags=BLEND_RGBA_MULT)
```
The only 2 lines you need to worry about are ```lights_display.blit(...)``` and ```Light.main(...)``` so ill walk you through what each does.
##
```python
lights_display.blit(Pygame_Lights.global_light(display.get_size(), intensity:int(0-255)), (0,0))
``` 
```intensity:int(0-255)``` -> The intensity at which the whole screen will be lit up.

All this line does is simply provide a base light for the screen or else everything would be dark so you can control how dark the whole screen is without using many smaller lights.
##
```python
Light.main(Rects:Tuple[pygame.Rect], lights_display, x:int, y:int)
``` 
```Rects:Tuple[pygame.Rect]``` -> This is a list of rectangles of which the light will cast shadows this can be as long as you want

```x:int, y:int``` -> The x, y co-ordinates of the light

This line must be run for each light individually as each light needs to update each frame with its position and objects to cast shadows off.
##
Another function that the lights class features, that is non-essential to running the code, is the baked_lighting function this function allows for shadows to be baked into the light texture, which can greatly boost performance in certain situations, it should only be used on lights that are stationary that cast shadows of stationary objects.
```python
Light.baked_lighting(tiles:Tuple[pygame.Rect], x:int, y:int, reset_surface:Boolean):
``` 
```tiles:Tuple[pygame.Rect]``` -> This is a list of rectangles of which the light will cast shadows this can be as long as you want

```x:int, y:int``` -> The x, y co-ordinates of the light

```reset_surface:Boolean``` -> This will determine weather to reset the surface if this function has already been called before
##
Some extra things to keep in mind are that first of all a light can only illuminate something to its base RGB value this means that a white light cannot brighten a black object so if you fill the screen black and cannot see your light that is why. Also, lights of red color can only illuminate the red channel of the RGB colors of something so a red light on a green background will appear invisible as the red light does not interact with green. Another thing to keep in mind is that any rendering that is performed after the ```display.blit(lights_display, (0,0), special_flags=BLEND_RGBA_MULT)``` line will not be affected by the lighting effects and will have their base RGB values. When creating a light the texture for the light must be generated this is a very time-consuming process and can take longer depending on the size of the light so when running a program if it is taking a long time to start that is because it is generating the textures for the lights so do not close the program just wait for it to finish what it is doing then it will run like normal.
## Example
I have created a quick example code to show you how to get started using the package it is nothing complicated but can be expanded upon.
```python
import pygame
from pygame.locals import *
import Pygame_Lights

pygame.init()

pygame.display.set_caption("Light Render")
display = pygame.display.set_mode((500, 500), pygame.DOUBLEBUF)
clock, fps = pygame.time.Clock(), 240

light = Pygame_Lights.LIGHT(500, Pygame_Lights.pixel_shader(500, (255,255,255), 1, False))
shadow_objects = [pygame.Rect(200,200,100,100)]

while True:
    clock.tick(fps)
    display.fill((255,255,255))

    mx, my = pygame.mouse.get_pos()

    #Lighting ------
    lights_display = pygame.Surface((display.get_size()))
    
    lights_display.blit(Pygame_Lights.global_light(display.get_size(), 25), (0,0))
    light.main(shadow_objects, lights_display, mx, my)
    
    display.blit(lights_display, (0,0), special_flags=BLEND_RGBA_MULT)
    #---------------

    pygame.draw.rect(display, (255,255,255), shadow_objects[0])

    for event in pygame.event.get():
        if event.type == QUIT: pygame.quit()

    pygame.display.set_caption(str(clock.get_fps()))
    pygame.display.update()

```
More examples can be found in the files of this repository there is an example for point lights that can be found in the ```Basic_Example``` folder and another demo can be found that uses a dungeon tileset which can be found in the ```Dungeon_Example_Project``` folder. Side note please do not judge the code in the dungeon demo it is not my best code as I just wanted something functional so some of the code is garbage.
