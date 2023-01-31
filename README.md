# Pygame 2D Lighting Engine
[![python 3.10.6](https://img.shields.io/badge/python-3.10.6-blue)](https://www.python.org/) [![pygame 2.1.2](https://img.shields.io/badge/pygame-2.1.2-green)](https://www.pygame.org/wiki/about)
## Infomation
This is a 2D lighting engine made in python to be used with the pygame library. it features dynamic lights that cast shadows and colors mix properly.
## Performance
## Feedback / Bugs
## How to install
To install the engine you simply download the ```Pygame_Lights.py``` file and place it in the same directory as the python file in which you are attempting to use it in. After you have done this make sure you have numpy and pygame installed as they are neccessary for the usage of this library, they can be installed using the 2 commands listed below simply run them in you terminal:
```
pip install numpy --user
pip install pygame --user
```
# Usage
## Overview
Using this engine is very simple. For starters you will need to import the engine do this pimply by adding ```import Pygame_Lights``` to the top of your code. after that you will want to initialize a light. this can be done using this line of code:
```python
Light = Pygame_Lights.LIGHT(size:int, color:Tuple[int,int,int], intensity:int(0-1), point:Boolean, angle:int(0-360), angle_width:int(0-360))
```
```size:int``` -> The size of the light can by any size however the bigger the worse for performance

```color:Tuple[int,int,int]t``` -> The color of the light in RGB format each value is 0-255

```intensity:int(0-1)``` -> The intesnsity of the light each value is 0-1

```point:Boolean``` -> A boolean value determining weather the light is a point light or not

```angle:int(0-360)``` -> The angle at which the light faces (only needed if the light is a point light)

```angle_width:int(0-360)``` -> The width of the point light (only needed if the light is a point light)

##

Next you will need to update the lights each frame this will require a few extra lines of code:
```python
lights_display = pygame.Surface((display.get_size()))

lights_display.blit(Pygame_Lights.global_light(display.get_size(), intensity:int(0-255)), (0,0))
Light.main(Rects:Tuple[pygame.Rect], lights_display, x:int, y:int)
    
display.blit(lights_display, (0,0), special_flags=BLEND_RGBA_MULT)
```
the only 2 lines you need to worry about are ```lights_display.blit(...)``` and ```Light.main(...)``` so ill walk you through what each does.
##
```
lights_display.blit(Pygame_Lights.global_light(display.get_size(), intensity:int(0-255)), (0,0))
``` 
```intensity:int(0-255)``` -> The intensity at which the whole screen will be lit up.

all this line does is simply provide a base light for the screen or else everything would be dark so you can control how dark the whole screen is without using many smaller lights.
##
```
Light.main(Rects:Tuple[pygame.Rect], lights_display, x:int, y:int)
``` 
```Rects:Tuple[pygame.Rect]``` -> This is a list of rectangles of which the light will cast shadows this can be as long as you want

```x:int, y:int``` -> The x, y co-ordinates of the light

This line must be run for each light individually as each light need updating each frame with its position and objects to cast shadows of.
## Example
