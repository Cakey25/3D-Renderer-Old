
# Imports
import pygame as pg
import numpy
import math
import time
from config import *
# Name changes
vec2 = pg.math.Vector2
vec3 = pg.math.Vector3

class Camera:
    def __init__(self, skew) -> None:
        # Attributes
        self.pos = vec3(0, 0, -5)
        self.vel = vec3(0, 0, 0)
        self.rot = vec3(0, 0, 0)
        self.sensor = vec2(SCREEN_SIZE / 10_000)
        self.focal = 0.1
        self.skew = skew

    def update(self, keys, mouse_vel):
        # Horizonal plane movement
        if keys[pg.K_w] and not keys[pg.K_s]:
            self.pos.z += MOVE_SPEED * math.cos(self.rot.y)
            self.pos.x -= MOVE_SPEED * math.sin(self.rot.y)
        if keys[pg.K_s] and not keys[pg.K_w]:
            self.pos.z -= MOVE_SPEED * math.cos(self.rot.y)
            self.pos.x += MOVE_SPEED * math.sin(self.rot.y)
        if keys[pg.K_d] and not keys[pg.K_a]:
            self.pos.z -= MOVE_SPEED * math.sin(self.rot.y)
            self.pos.x -= MOVE_SPEED * math.cos(self.rot.y)
        if keys[pg.K_a] and not keys[pg.K_d]:
            self.pos.z += MOVE_SPEED * math.sin(self.rot.y)
            self.pos.x += MOVE_SPEED * math.cos(self.rot.y)
        # Apply gravity
        if self.pos.y < 0: 
            self.vel.y += GRAVITY
        if self.pos.y > 0:
            self.pos.y = 0
            self.vel.y = 0
        self.pos += self.vel
        # Jump
        if keys[pg.K_SPACE] and self.pos.y == 0:
            self.vel.y = JUMP_HEIGHT
        # Change rotation based on mouse vel
        self.rot.x += mouse_vel.y * LOOK_SPEED
        self.rot.y += mouse_vel.x * LOOK_SPEED

    def render(self, renderer, points):
        # List to store positions of points
        rendered_points = []
        for point in points:
            # Multiply matrices
            point = numpy.dot((renderer.cam), point)
            point = numpy.dot((renderer.rotZ), point)
            point = numpy.dot((renderer.rotY), point)
            point = numpy.dot((renderer.rotX), point)
            point = numpy.dot(renderer.projection, point)


            # Perspective matrix (in camera)
            self.perspective = [[(1 / point[2]), 0, 0, 0],
                                [0, (1 / point[2]), 0, 0],
                                [0, 0, 1, 0],
                                [0, 0, 0, 1]]
            # Finish multiplying
            point = numpy.dot(self.perspective, point) 
            point = numpy.dot(renderer.off, point)
            # Add to lsit
            rendered_points.append(vec2(point[0], point[1]))
        return rendered_points

class Renderer:
    def __init__(self, res, skew) -> None:
        self.resolution = vec2(res)
        self.offset = vec2(res / 2)
        # Create camera
        self.camera = Camera(skew=skew)

    def render_vertices(self, scene, vertices):
        # Create matrices
        self.create_matrices()
        self.coordinates = self.camera.render(self, vertices)#
        
        # Draw points on screen
        for point in self.coordinates:
            pg.draw.circle(scene.screen, point_col, point, POINT_RADIUS)

    def render_lines(self, scene, lines):
        for line in lines:
            pos1 = vec2(self.coordinates[line[0]])
            pos2 = vec2(self.coordinates[line[1]])
            pg.draw.aaline(scene.screen, point_col, pos1, pos2)

    def create_matrices(self):
        # Camera position
        self.cam = [[1, 0, 0, self.camera.pos.x],
                    [0, 1, 0, self.camera.pos.y],
                    [0, 0, 1, self.camera.pos.z],
                    [0, 0, 0, 1]]
        # Camera X
        self.rotX = [[1, 0, 0, 0],
                     [0, math.cos(self.camera.rot.x), -math.sin(self.camera.rot.x), 0],
                     [0, math.sin(self.camera.rot.x), math.cos(self.camera.rot.x), 0],
                     [0, 0, 0, 1]]
        # Camera Y
        self.rotY = [[math.cos(self.camera.rot.y), 0, math.sin(self.camera.rot.y), 0],
                     [0, 1, 0, 0],
                     [-math.sin(self.camera.rot.y), 0, math.cos(self.camera.rot.y), 0],
                     [0, 0, 0, 1]]
        # Camera Z
        self.rotZ = [[math.cos(self.camera.rot.z), -math.sin(self.camera.rot.z), 0, 0],
                     [math.sin(self.camera.rot.z), math.cos(self.camera.rot.z), 0, 0],
                     [0, 0, 1, 0],
                     [0, 0, 0, 1]]
        # Projection matrix
        self.projection = [[(self.camera.focal * self.resolution.x) / (2 * self.camera.sensor.x), self.camera.skew, 0, 0],
                           [0, (self.camera.focal * self.resolution.y) / (2 * self.camera.sensor.y), 0, 0],
                           [0, 0, -1, 0],
                           [0, 0, 0, 1]]
        # Offset matrix
        self.off = [[1, 0, 0, self.offset.x],
                    [0, -1, 0, self.offset.y],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]]

class Scene:
    def __init__(self) -> None:
        # Initialise things
        pg.init()
        pg.mouse.set_visible(False)
        
        # Screen
        self.screen = pg.display.set_mode(SCREEN_SIZE)
        self.clock = pg.Clock()

    def new_scene(self):
        self.running = True
        # Vertices list
        self.vertices = [[-1, -1, -1, 1],
                         [ 1, -1, -1, 1],
                         [-1,  1, -1, 1],
                         [ 1,  1, -1, 1],
                         [-1, -1,  1, 1],
                         [ 1, -1,  1, 1],
                         [-1,  1,  1, 1],
                         [ 1,  1,  1, 1]]
        # Initialise renderer
        self.lines = [[0, 1],
                      [2, 3],
                      [4, 5],
                      [6, 7],
                      [0, 2],
                      [0, 4],
                      [1, 3],
                      [1, 5],
                      [2, 6],
                      [3, 7],
                      [4, 6],
                      [5, 7]]

        self.renderer = Renderer(res=SCREEN_SIZE, skew=0)

    def events(self):
        # Grab all mouse input
        pg.event.set_grab(True)
        # Get keyboard input
        self.keys = pg.key.get_pressed()
        # Events loop
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.running = False
        # Get mouse velocity
        self.mouse_vel = vec2(pg.mouse.get_rel())

    def update(self):
        # Update camera
        self.renderer.camera.update(self.keys, self.mouse_vel)

    def render(self):
        self.screen.fill(background_col)
        # Render cube
        self.renderer.render_vertices(self, self.vertices)
        self.renderer.render_lines(self, self.lines)

if __name__ == '__main__':
    scene = Scene()
    scene.new_scene()
    while scene.running:
        scene.events()
        scene.update()
        start = time.time()
        scene.render()
        end = time.time()
        print(f'Time for render is :{end - start}')
        pg.display.flip()
        scene.clock.tick(FPS)

    pg.quit()
