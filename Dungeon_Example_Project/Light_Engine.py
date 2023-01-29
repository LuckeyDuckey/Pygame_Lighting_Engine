import math as meth
import numpy as np
import random

import pygame
from pygame.locals import *

pygame.init()

pygame.display.set_caption("Light Render")
screen = pygame.display.set_mode((1200, 720), pygame.DOUBLEBUF)
display = pygame.Surface((400, 240))
clock, fps = pygame.time.Clock(), 1000

tileset = pygame.transform.scale(pygame.image.load("Dungeon_Tileset.png"), (160, 160)).convert_alpha()

def get_tile(x, y):
    surf = tileset.copy()
    surf.set_clip(pygame.Rect(x*16, y*16, 16, 16))
    img = surf.subsurface(surf.get_clip())
    return img.copy()

tiles_textures = []

for y in range(10):
    for x in range(10):
        tiles_textures.append(get_tile(x,y))
        
class LIGHT:
    def __init__(self, size, color, intensity, point, angle=0, angle_width=360):
        self.size = size
        self.radius = size * 0.5
        self.render_surface = pygame.Surface((size, size))
        self.intensity = intensity
        self.angle = angle
        self.angle_width = angle_width
        self.point = point
        self.pixel_shader_surf = self.pixel_shader(np.full((size, size, 3), color, dtype=np.uint16))
        self.render_surface.set_colorkey((0,0,0))
    
    def get_intersection(self, p1, p2):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]

        if dx == 0:
            return [p2[0], (0 if dy <= 0 else self.size)]

        if dy == 0:
            return [(0 if dx <= 0 else self.size), p2[1]]
            
        y_gradient = dy / dx
        y_intercept = p1[1] - (p1[0] * y_gradient)

        y_line = 0 if dx <= 0 else self.size
        y_intersection = [y_line, (y_gradient * y_line) + y_intercept]

        if y_intersection[1] >= 0 and y_intersection[1] <= self.size:
            return y_intersection

        x_gradient = dx / dy
        x_intercept = p1[0] - (p1[1] * x_gradient)

        x_line = 0 if dy <= 0 else self.size
        x_intersection = [(x_gradient * x_line) + x_intercept, x_line]

        if x_intersection[0] >= 0 and x_intersection[0] <= self.size:
            return x_intersection

    def fill_shadows(self, render_surface, points):
        render_points = [points[0],points[4],points[1],points[2],points[3]]
        
        if points[2][0] + points[3][0] not in [1000, 0] and points[2][1] + points[3][1] not in [1000, 0]:
            if abs(points[2][0] - points[3][0]) == self.size: #x opposite
                
                if self.radius < points[2][1]:
                    render_points = [points[0], points[4], points[1], points[2], [0, self.size], [self.size, self.size], points[3]]

                if self.radius > points[2][1]:
                    render_points = [points[0], points[4], points[1], points[2], [self.size, 0], [0, 0], points[3]]

            elif abs(points[2][1] - points[3][1]) == self.size: #y opposite
                
                if self.radius < points[2][0]:
                    render_points = [points[0], points[4], points[1], points[2], [self.size, self.size], [self.size, 0], points[3]]

                if self.radius > points[2][0]:
                    render_points = [points[0], points[4], points[1], points[2], [0, self.size], [0, 0], points[3]]

            else:
                if points[2][0] != self.size and points[2][0] != 0:
                    render_points = [points[0], points[4], points[1], points[2], [points[3][0], points[2][1]], points[3]]
                    
                else:
                    render_points = [points[0], points[4], points[1], points[2], [points[2][0], points[3][1]], points[3]]
        
        pygame.draw.polygon(render_surface, (0,0,0), render_points)

    def get_corners(self, points, mx, my):
        corners = [points[0], points[2], points[2]]

        if mx >= points[1][0] and mx <= points[0][0]:#top / bottom
            if my < points[1][1]: corners = [points[0], points[1], points[1]]
            if my > points[0][1]: corners = [points[2], points[3], points[3]]

        if my >= points[0][1] and my <= points[2][1]:#left / right
            if mx < points[1][0]: corners = [points[1], points[2], points[2]]
            if mx > points[0][0]: corners = [points[0], points[3], points[3]]

        if (mx < points[1][0] and my < points[1][1]):#top left / bottom right
            corners = [points[0], points[2], points[1]]
        elif (mx > points[0][0] and my > points[2][1]):#top left / bottom right
            corners = [points[0], points[2], points[3]]

        if (mx > points[0][0] and my < points[1][1]):#top right / bottom left
            corners = [points[1], points[3], points[0]]
        elif (mx < points[1][0] and my > points[2][1]):#top right / bottom left
            corners = [points[1], points[3], points[2]]

        return corners

    def get_tiles(self, tiles, mx, my):
        points = []

        for i in range(len(tiles)):
            for x in range(len(tiles[i])):
                if tiles[i][x]:
                    if (x * 16 - mx >= (-self.radius)-16 and x * 16 - mx <= self.radius) and (i * 16 - my >= (-self.radius)-16 and i * 16 - my <= self.radius):
                        points.append([[x*16+16, i*16], [x*16, i*16], [x*16, i*16+16], [x*16+16, i*16+16]])

        return points

    def pixel_shader(self, array):
        final_array = np.array(array)

        for x in range(len(final_array)):
            
            for y in range(len(final_array[x])):

                #radial -----
                distance = meth.sqrt((x - self.radius)**2 + (y - self.radius)**2)
        
                radial_falloff = (self.radius - distance) * (1 / self.radius)

                if radial_falloff <= 0:
                    radial_falloff = 0
                #-----

                #angular -----
                point_angle = (180 / meth.pi) * -meth.atan2((self.radius - x), (self.radius - y)) + 180
                diff_anlge = abs(((self.angle - point_angle) + 180) % 360 - 180)
                    
                angular_falloff = ((self.angle_width / 2) - diff_anlge) * (1 / self.angle_width)

                if angular_falloff <= 0:
                    angular_falloff = 0

                if not self.point:
                    angular_falloff = 1
                #-----
        
                final_intensity = radial_falloff * angular_falloff * self.intensity
                final_array[x][y] = final_array[x][y] * final_intensity

        return pygame.surfarray.make_surface(final_array)
    
    def check_cast(self, points, dx, dy):
        render = False
    
        if self.point:
            for point in points:
            
                try:
                    color = self.pixel_shader_surf.get_at((int(point[0]-dx), int(point[1]-dy)))
                except:
                    color = (0,0,0,255)
                
                if color != (0,0,0,255):
                    render = True

        else:
            render = True

        return render

    def main(self, tiles, display, mx, my):
        self.render_surface.fill((0,0,0))
        self.render_surface.blit(self.pixel_shader_surf, (0, 0))
        
        dx, dy = mx - self.radius, my - self.radius

        for point in self.get_tiles(tiles, mx, my):

            if self.check_cast(point, dx, dy):

                corners = self.get_corners(point, mx, my)
                corners = [[corners[0][0] - dx, corners[0][1] - dy], [corners[1][0] - dx, corners[1][1] - dy], [corners[2][0] - dx, corners[2][1] - dy]]
                self.fill_shadows(self.render_surface, [corners[0], corners[1], self.get_intersection([self.radius] * 2, corners[1]), self.get_intersection([self.radius] * 2, corners[0]), corners[2]])
                
        pygame.draw.circle(self.render_surface, (255,255,255), (self.radius, self.radius), 2)
        
        display.blit(self.render_surface, (mx - self.radius, my - self.radius), special_flags=BLEND_RGBA_ADD)

        return display

class MAP:
    def __init__(self):
        self.tiles = [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                      [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                      [1,0,0,0,0,1,1,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,1],
                      [1,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,1],
                      [1,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1],
                      [1,1,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,1],
                      [1,1,0,1,1,1,1,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,1],
                      [1,0,0,0,0,1,1,0,0,0,0,1,1,1,1,1,0,1,1,0,0,0,0,0,1],
                      [1,0,0,0,0,1,1,1,0,0,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1],
                      [1,0,0,0,0,1,1,1,0,0,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1],
                      [1,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,1],
                      [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,1],
                      [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                      [1,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,1],
                      [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]

        self.shadow_tiles = [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                             [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                             [1,0,0,0,0,1,1,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,1],
                             [1,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,1],
                             [1,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1],
                             [1,1,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,1],
                             [1,1,0,1,1,1,1,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,1],
                             [1,0,0,0,0,1,1,0,0,0,0,1,1,1,1,1,0,1,1,0,0,0,0,0,1],
                             [1,0,0,0,0,1,1,1,0,0,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1],
                             [1,0,0,0,0,1,1,1,0,0,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1],
                             [1,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,1],
                             [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,1],
                             [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                             [1,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,1],
                             [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]
        
        self.texture_map = [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                            [1,0,0,0,0,1,1,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,1],
                            [1,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,1],
                            [1,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1],
                            [1,1,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,1],
                            [1,1,0,1,1,1,1,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,1],
                            [1,0,0,0,0,1,1,0,0,0,0,1,1,1,1,1,0,1,1,0,0,0,0,0,1],
                            [1,0,0,0,0,1,1,1,0,0,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1],
                            [1,0,0,0,0,1,1,1,0,0,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1],
                            [1,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,1],
                            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,1],
                            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                            [1,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,1],
                            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]
        
        self.generate_tiles()

    def render(self, win):
        for i in range(len(self.tiles)):
            for x in range(len(self.tiles[i])):
                tile_pos = [x*16, i*16]
                win.blit(tiles_textures[self.texture_map[i][x]], tile_pos)

    def generate_tiles(self):
        for i in range(len(self.tiles)):
            for x in range(len(self.tiles[0])):
                self.texture_map[i][x] = self.render_tile(i, x)
                if self.tiles[i][x]:
                    if i == 14:
                        self.shadow_tiles[i][x] = 1
                    else:
                        if not self.tiles[i+1][x]: self.shadow_tiles[i][x] = 0
                        else: self.shadow_tiles[i][x] = 1
                else:
                    self.shadow_tiles[i][x] = 0

    def render_tile(self, i, x):
        tile_states = []

        if i == 0:
            if x == 0:
                tile_states = [1,1,1,1,self.tiles[i][x],self.tiles[i][x+1],1,self.tiles[i+1][x],self.tiles[i+1][x+1]]
            elif x == 24:
                tile_states = [1,1,1,self.tiles[i][x-1],self.tiles[i][x],1,self.tiles[i-1][x-1],self.tiles[i-1][x],1]
            else:
                tile_states = [1,1,1,self.tiles[i][x-1],self.tiles[i][x],self.tiles[i][x+1],self.tiles[i+1][x-1],self.tiles[i+1][x],self.tiles[i+1][x+1]]
            
        elif i == 14:
            if x == 0:
                tile_states = [1,self.tiles[i-1][x],self.tiles[i-1][x+1],1,self.tiles[i][x],self.tiles[i][x+1],1,1,1]
            elif x == 24:
                tile_states = [self.tiles[i-1][x-1],self.tiles[i-1][x],1,self.tiles[i][x-1],self.tiles[i][x],1,1,1,1]
            else:
                tile_states = [self.tiles[i-1][x-1],self.tiles[i-1][x],self.tiles[i-1][x+1],self.tiles[i][x-1],self.tiles[i][x],self.tiles[i][x+1],1,1,1]

        else:
            if x == 0:
                tile_states = [1,self.tiles[i-1][x],self.tiles[i-1][x+1],1,self.tiles[i][x],self.tiles[i][x+1],1,self.tiles[i+1][x],self.tiles[i+1][x+1]]
            elif x == 24:
                tile_states = [self.tiles[i-1][x-1],self.tiles[i-1][x],1,self.tiles[i][x-1],self.tiles[i][x],1,self.tiles[i+1][x-1],self.tiles[i+1][x],1]
            else:
                tile_states = [self.tiles[i-1][x-1],self.tiles[i-1][x],self.tiles[i-1][x+1],self.tiles[i][x-1],self.tiles[i][x],self.tiles[i][x+1],self.tiles[i+1][x-1],self.tiles[i+1][x],self.tiles[i+1][x+1]]

        #--------------------------------------

        if tile_states[4]:
            if (not tile_states[8] or not tile_states[5]) and tile_states[3] and tile_states[1] and tile_states[7]:
                return random.choice([0,10,20,30])

            elif (not tile_states[6] or not tile_states[3]) and tile_states[5] and tile_states[1] and tile_states[7]:
                return random.choice([5,15,25,35])

            elif not tile_states[7] and tile_states[1]:
                return random.choice([1,2,3,4])

            elif not tile_states[1] and tile_states[3] and tile_states[5] and tile_states[7]:
                return random.choice([41,42,43,44])

            elif not tile_states[2] and tile_states[1] and tile_states[5]:
                return 40

            elif not tile_states[0] and tile_states[1] and tile_states[3]:
                return 45

            elif not tile_states[3] and not tile_states[0] and not tile_states[1]:
                return random.choice([50,54])

            elif not tile_states[1] and not tile_states[2] and not tile_states[5]:
                return random.choice([53,55])

            else:
                return 78

        else:
            return random.choice([6,7,8,9,16,17,18,19,26,27,28,29])

    def clicking(self, mx, my, button):
        if button: self.tiles[my // 16][mx // 16] = 1
        else: self.tiles[my // 16][mx // 16] = 0
        self.generate_tiles()

def global_light(size, intensity):
    dark = pygame.Surface(size).convert_alpha()
    dark.fill((255, 255, 255, intensity))
    return dark

world = MAP()

#size, color, intensity, point, angle=0, angle_width=360
light_test = LIGHT(150, (255, 185, 9), 1, False)

lights = []

surfaces = []

while True:
    clock.tick(fps)
    display.fill((0,0,0))

    mx, my = pygame.mouse.get_pos()
    mx = round(mx // 3)
    my = round(my // 3)

    world.render(display)
    if pygame.mouse.get_pressed()[0]: world.clicking(mx, my, 1)
    if pygame.mouse.get_pressed()[2]: world.clicking(mx, my, 0)

    if pygame.mouse.get_pressed()[1]: lights.append([LIGHT(150, (255, 185, 9), 1, False), [mx,my]])

    lights_display = pygame.Surface((display.get_size()))

    lights_display.blit(global_light(display.get_size(), 50), (0,0))
    light_test.main(world.shadow_tiles, lights_display, mx, my)
    
    for light in lights:
        light[0].main(world.shadow_tiles, lights_display, light[1][0], light[1][1])
        display.blit(tiles_textures[90], (light[1][0]-8,light[1][1]-8))
    
    display.blit(lights_display, (0,0), special_flags=BLEND_RGBA_MULT)

    for event in pygame.event.get():
        if event.type == QUIT: pygame.quit()

    surf = pygame.transform.scale(display, (1200, 720))
    screen.blit(surf,(0,0))

    pygame.display.set_caption(str(clock.get_fps()))
    pygame.display.update()
