import pygame
from pygame.locals import *
import Pygame_Lights

pygame.init()

pygame.display.set_caption("Light Render")
display = pygame.display.set_mode((1250, 750), pygame.DOUBLEBUF)
clock, fps = pygame.time.Clock(), 1000

bg = pygame.transform.scale(pygame.image.load("baldcat.png"), (1250, 750)).convert()

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

        self.rects = self.get_rects()

    def get_rects(self):
        rects = []
        
        for i in range(len(self.tiles)):
            for x in range(len(self.tiles[i])):
                if self.tiles[i][x]:
                    rects.append(pygame.Rect(x*50, i*50, 50, 50))
                    
        return rects

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
        self.rects = self.get_rects()

world = MAP()

light_red = Pygame_Lights.LIGHT(1000, (255,0,0), 1, True, 0, 90)
light_green = Pygame_Lights.LIGHT(1000, (0,255,0), 1, True, 0, 90)
light_blue = Pygame_Lights.LIGHT(1000, (0,0,255), 1, True, 0, 90)

while True:
    clock.tick(fps)
    display.fill((0,0,0))
    display.blit(bg, (0, 0))

    mx, my = pygame.mouse.get_pos()

    #Lighting ------
    lights_display = pygame.Surface((display.get_size()))
    
    lights_display.blit(Pygame_Lights.global_light(display.get_size(), 25), (0,0))
    
    light_red.main(world.rects, lights_display, 300, 150)
    light_green.main(world.rects, lights_display, 950, 150)
    light_blue.main(world.rects, lights_display, 625, 150)
    
    display.blit(lights_display, (0,0), special_flags=BLEND_RGBA_MULT)
    #---------------

    world.render(display)
    if pygame.mouse.get_pressed()[0]: world.clicking(mx, my, 1)
    if pygame.mouse.get_pressed()[2]: world.clicking(mx, my, 0)

    for event in pygame.event.get():
        if event.type == QUIT: pygame.quit()

    pygame.display.set_caption(str(clock.get_fps()))
    pygame.display.update()
