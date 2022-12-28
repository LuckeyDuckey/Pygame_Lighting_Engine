import math as meth
import numpy as np

import pygame
from pygame.locals import *

pygame.init()

pygame.display.set_caption("Light Render")
display = pygame.display.set_mode((1250, 750), pygame.DOUBLEBUF)
clock, fps = pygame.time.Clock(), 1000

bg = pygame.transform.scale(pygame.image.load("baldcat.png"), (1250, 750)).convert()

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
        render_points = points
        
        if points[2][0] + points[3][0] not in [1000, 0] and points[2][1] + points[3][1] not in [1000, 0]:
            if abs(points[2][0] - points[3][0]) == self.size: #x opposite
                
                if self.radius < points[2][1]:
                    render_points = [points[0], points[1], points[2], [0, self.size], [self.size, self.size], points[3]]

                if self.radius > points[2][1]:
                    render_points = [points[0], points[1], points[2], [self.size, 0], [0, 0], points[3]]

            elif abs(points[2][1] - points[3][1]) == self.size: #y opposite
                
                if self.radius < points[2][0]:
                    render_points = [points[0], points[1], points[2], [self.size, self.size], [self.size, 0], points[3]]

                if self.radius > points[2][0]:
                    render_points = [points[0], points[1], points[2], [0, self.size], [0, 0], points[3]]

            else:
                if points[2][0] != self.size and points[2][0] != 0:
                    render_points = [points[0], points[1], points[2], [points[3][0], points[2][1]], points[3]]
                    
                else:
                    render_points = [points[0], points[1], points[2], [points[2][0], points[3][1]], points[3]]
        
        pygame.draw.polygon(render_surface, (0,0,0), render_points)

    def get_corners(self, points, mx, my):
        corners = [points[0], points[2]]

        if mx >= points[1][0] and mx <= points[0][0]:#top / bottom
            if my < points[1][1]: corners = [points[0], points[1]]
            if my > points[0][1]: corners = [points[2], points[3]]

        if my >= points[0][1] and my <= points[2][1]:#left / right
            if mx < points[1][0]: corners = [points[1], points[2]]
            if mx > points[0][0]: corners = [points[0], points[3]]

        if (mx < points[1][0] and my < points[1][1]) or (mx > points[0][0] and my > points[2][1]):#top left / bottom right
            corners = [points[0], points[2]]

        if (mx > points[0][0] and my < points[1][1]) or (mx < points[1][0] and my > points[2][1]):#top right / bottom left
            corners = [points[1], points[3]]

        return corners

    def get_tiles(self, tiles, mx, my):
        points = []

        for i in range(len(tiles)):
            for x in range(len(tiles[i])):
                if (x * 50 - mx >= (-self.radius)-50 and x * 50 - mx <= self.radius) and (i * 50 - my >= (-self.radius)-50 and i * 50 - my <= self.radius) and tiles[i][x]:
                    points.append([[x*50+50, i*50], [x*50, i*50], [x*50, i*50+50], [x*50+50, i*50+50]])

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

    def main(self, tiles, display, mx, my):
        self.render_surface.fill((0,0,0))
        self.render_surface.blit(self.pixel_shader_surf, (0, 0), special_flags=BLEND_RGBA_ADD)

        for point in self.get_tiles(tiles, mx, my):

            corners = self.get_corners(point, mx, my)
            dx, dy = mx - self.radius, my - self.radius
            corners = [[corners[0][0] - dx, corners[0][1] - dy], [corners[1][0] - dx, corners[1][1] - dy]]

            self.fill_shadows(self.render_surface, [corners[0], corners[1], self.get_intersection([self.radius] * 2, corners[1]), self.get_intersection([self.radius] * 2, corners[0])])
            
        self.render_surface.blit(display, (0 - mx + self.radius, 0 - my + self.radius), special_flags=BLEND_RGBA_MULT)
        display.fill((0,0,0))
        
        pygame.draw.circle(self.render_surface, (255,255,255), (self.radius, self.radius), 5)
        
        display.blit(self.render_surface, (mx - self.radius, my - self.radius))

        return display

class MAP:
    def __init__(self):
        self.tiles = [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                      [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                      [1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                      [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                      [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                      [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                      [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                      [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                      [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                      [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                      [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                      [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                      [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                      [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                      [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]

    def render(self, win):
        for i in range(len(self.tiles)):
            for x in range(len(self.tiles[i])):
                if self.tiles[i][x]:
                    tile_pos = [x*50, i*50]
                    pygame.draw.rect(win, (0,0,0), pygame.Rect(tile_pos[0], tile_pos[1], 50, 50))
                    self.render_sides(i, x, tile_pos, win)

    def render_sides(self, i, x, tile_pos, display):
        if i > 0:
            if not self.tiles[i-1][x]:
                pygame.draw.line(display, (255,255,255), [tile_pos[0], tile_pos[1]], [tile_pos[0]+50, tile_pos[1]])
                
        if i < 14:
            if not self.tiles[i+1][x]:
                pygame.draw.line(display, (255,255,255), [tile_pos[0], tile_pos[1]+50], [tile_pos[0]+50, tile_pos[1]+50])

        if x > 0:
            if not self.tiles[i][x-1]:
                pygame.draw.line(display, (255,255,255), [tile_pos[0], tile_pos[1]], [tile_pos[0], tile_pos[1]+50])
                
        if x < 24:
            if not self.tiles[i][x+1]:
                pygame.draw.line(display, (255,255,255), [tile_pos[0]+50, tile_pos[1]], [tile_pos[0]+50, tile_pos[1]+50])

    def clicking(self, mx, my, button):
        if button: self.tiles[my // 50][mx // 50] = 1
        else: self.tiles[my // 50][mx // 50] = 0

def global_light(bg, intensity):
    dark = pygame.Surface(bg.get_size()).convert_alpha()
    dark.fill((0, 0, 0, 255 - intensity))
    bg.blit(dark, (0, 0))
    return bg

world = MAP()

#size, color, intensity, point, angle=0, angle_width=360

#light_test = LIGHT(500, (255,255,255), 1, False)
light_test = LIGHT(1000, (255,255,255), 1, True, 0, 90)

light_test1 = LIGHT(1000, (255,0,0), 1, True, 0, 90)
light_test2 = LIGHT(1000, (0,255,0), 1, True, 0, 90)
light_test3 = LIGHT(1000, (0,0,255), 1, True, 0, 90)

surfaces = []

while True:
    clock.tick(fps)
    #display.fill((0,0,0))
    display.blit(bg, (0, 0))

    mx, my = pygame.mouse.get_pos()

    surfaces = [global_light(display.copy(), 25)]
    #surfaces.append(light_test.main(world.tiles, display.copy(), mx, my))

    surfaces.append(light_test1.main(world.tiles, display.copy(), 300, 150))
    surfaces.append(light_test2.main(world.tiles, display.copy(), 950, 150))
    surfaces.append(light_test3.main(world.tiles, display.copy(), 625, 150))
    
    display.fill((0,0,0))

    for surface in surfaces:
        display.blit(surface, (0,0), special_flags=BLEND_RGBA_ADD)

    world.render(display)
    if pygame.mouse.get_pressed()[0]: world.clicking(mx, my, 1)
    if pygame.mouse.get_pressed()[2]: world.clicking(mx, my, 0)

    for event in pygame.event.get():
        if event.type == QUIT: pygame.quit()

    pygame.display.set_caption(str(clock.get_fps()))
    pygame.display.update()
