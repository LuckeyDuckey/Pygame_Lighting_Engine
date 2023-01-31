import math as meth
import numpy as np

import pygame
from pygame.locals import *

pygame.init()

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
            if abs(points[2][0] - points[3][0]) == self.size:
                
                if self.radius < points[2][1]:
                    render_points = [points[0], points[4], points[1], points[2], [0, self.size], [self.size, self.size], points[3]]

                if self.radius > points[2][1]:
                    render_points = [points[0], points[4], points[1], points[2], [self.size, 0], [0, 0], points[3]]

            elif abs(points[2][1] - points[3][1]) == self.size:
                
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

        if mx >= points[1][0] and mx <= points[0][0]:
            if my < points[1][1]: corners = [points[0], points[1], points[1]]
            if my > points[0][1]: corners = [points[2], points[3], points[3]]

        if my >= points[0][1] and my <= points[2][1]:
            if mx < points[1][0]: corners = [points[1], points[2], points[2]]
            if mx > points[0][0]: corners = [points[0], points[3], points[3]]

        if (mx < points[1][0] and my < points[1][1]):
            corners = [points[0], points[2], points[1]]
        elif (mx > points[0][0] and my > points[2][1]):
            corners = [points[0], points[2], points[3]]

        if (mx > points[0][0] and my < points[1][1]):
            corners = [points[1], points[3], points[0]]
        elif (mx < points[1][0] and my > points[2][1]):
            corners = [points[1], points[3], points[2]]

        return corners

    def get_tiles(self, tiles, mx, my):
        points = []

        for rect in tiles:
            if (rect.x - mx >= (-self.radius) - rect.width and rect.x - mx <= self.radius) and (rect.y - my >= (-self.radius)-rect.height and rect.y - my <= self.radius):
                points.append([[rect.x+rect.width, rect.y], [rect.x, rect.y], [rect.x, rect.y+rect.height], [rect.x+rect.width, rect.y+rect.height]])

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
        
        pygame.draw.circle(self.render_surface, (255,255,255), (self.radius, self.radius), 5)
        
        display.blit(self.render_surface, (mx - self.radius, my - self.radius), special_flags=BLEND_RGBA_ADD)

        return display

def global_light(size, intensity):
    dark = pygame.Surface(size).convert_alpha()
    dark.fill((255, 255, 255, intensity))
    return dark
