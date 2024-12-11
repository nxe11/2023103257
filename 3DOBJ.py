import os
import sys
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random
import time

# 벡터 연산 함수
def vector_add(v1, v2):
    return [v1[i] + v2[i] for i in range(len(v1))]

def vector_scale(v, scalar):
    return [v[i] * scalar for i in range(len(v))]

def magnitude(v):
    return math.sqrt(sum(x ** 2 for x in v))

def normalize(v):
    mag = magnitude(v)
    return [x / mag for x in v] if mag > 0 else [0.0, 0.0, 0.0]

# PyInstaller 리소스 파일 경로 처리 함수
def get_resource_path(relative_path):
    """
    PyInstaller 환경에서의 리소스 경로 반환.
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# AABB 충돌 검사 함수
def check_collision(obj1, obj2):
    min1 = [min([v[i] for v in obj1.vertices]) + obj1.position[i] for i in range(3)]
    max1 = [max([v[i] for v in obj1.vertices]) + obj1.position[i] for i in range(3)]
    min2 = [min([v[i] for v in obj2.vertices]) + obj2.position[i] for i in range(3)]
    max2 = [max([v[i] for v in obj2.vertices]) + obj2.position[i] for i in range(3)]

    return all(min1[i] <= max2[i] and max1[i] >= min2[i] for i in range(3))

# .obj 파일 로더
def load_obj(file_path):
    vertices = []
    faces = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith('v '):
                parts = line.split()
                vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif line.startswith('f '):
                parts = line.split()
                faces.append([int(p.split('/')[0]) - 1 for p in parts[1:]])
    return vertices, faces

# OpenGL 물체 클래스
class Object3D:
    def __init__(self, vertices, faces, position):
        self.vertices = vertices
        self.faces = faces
        self.position = position
        self.velocity = [0.0, 0.0, 0.0]
        self.angular_velocity = [0.0, 0.0, 0.0]
        self.face_colors = [(1.0, 1.0, 1.0) for _ in faces]
        self.last_collision_time = 0
        self.collision_duration = 0.5

    def update(self):
        self.velocity[1] -= 0.01
        self.position = vector_add(self.position, self.velocity)

        for i in range(3):
            if self.position[i] < -5.0:
                self.position[i] = -5.0
                self.velocity[i] = -self.velocity[i] * 0.8
            elif self.position[i] > 5.0:
                self.position[i] = 5.0
                self.velocity[i] = -self.velocity[i] * 0.8

    def render(self, wireframe):
        glPushMatrix()
        glTranslatef(*self.position)

        mode = GL_LINE if wireframe else GL_FILL
        glPolygonMode(GL_FRONT_AND_BACK, mode)

        for i, face in enumerate(self.faces):
            glColor3f(*self.face_colors[i])
            glBegin(GL_TRIANGLES)
            for vertex_index in face:
                glVertex3fv(self.vertices[vertex_index])
            glEnd()

        glPopMatrix()

    def set_face_color(self, face_index, color):
        if 0 <= face_index < len(self.face_colors):
            self.face_colors[face_index] = color

    def apply_random_bounce(self):
        direction = [random.uniform(-1, 1) for _ in range(3)]
        magnitude = random.uniform(0.2, 0.5)
        self.velocity = vector_scale(direction, magnitude)

    def check_collision(self, other):
        current_time = time.time()
        for i, face_self in enumerate(self.faces):
            self_face_vertices = [vector_add(self.vertices[v], self.position) for v in face_self]
            for j, face_other in enumerate(other.faces):
                other_face_vertices = [vector_add(other.vertices[v], other.position) for v in face_other]

                if self.polygon_aabb_collision(self_face_vertices, other_face_vertices):
                    self.face_colors[i] = (1.0, 0.0, 0.0)
                    other.face_colors[j] = (1.0, 0.0, 0.0)
                    self.last_collision_time = current_time
                    other.last_collision_time = current_time

        if current_time - self.last_collision_time > self.collision_duration:
            self.face_colors = [(1.0, 1.0, 1.0) for _ in self.face_colors]
        if current_time - other.last_collision_time > other.collision_duration:
            other.face_colors = [(1.0, 1.0, 1.0) for _ in other.face_colors]

    def polygon_aabb_collision(self, vertices1, vertices2):
        min1 = [min([v[i] for v in vertices1]) for i in range(3)]
        max1 = [max([v[i] for v in vertices1]) for i in range(3)]
        min2 = [min([v[i] for v in vertices2]) for i in range(3)]
        max2 = [max([v[i] for v in vertices2]) for i in range(3)]

        return all(min1[i] <= max2[i] and max1[i] >= min2[i] for i in range(3))

# 바닥 렌더링
def render_ground():
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_QUADS)
    glVertex3f(-5.0, -5.0, -5.0)
    glVertex3f(5.0, -5.0, -5.0)
    glVertex3f(5.0, -5.0, 5.0)
    glVertex3f(-5.0, -5.0, 5.0)
    glEnd()

# 초기화
pygame.init()
screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
pygame.display.set_caption("3D OBJ Collision Engine")
gluPerspective(45, (800 / 600), 0.1, 50.0)
glTranslatef(0.0, 0.0, -15)

# 물체 초기화
obj_files = [
    get_resource_path("resources/pyramid.obj"),
    get_resource_path("resources/sphere.obj"),
    get_resource_path("resources/cube.obj"),
    get_resource_path("resources/cube24.obj"),
]
initial_positions = [[-3, 3, 0], [-1.5, 4, 0], [0, 5, 0], [1.5, 6, 0], [3, 7, 0]]
objects = [Object3D(*load_obj(f), p) for f, p in zip(obj_files, initial_positions)]

# 와이어프레임 모드로만 렌더링
wireframe_mode = True

# 메인 루프
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for obj in objects:
                obj.apply_random_bounce()
                obj.set_face_color(0, (1.0, 0.0, 0.0))

    for obj in objects:
        for other_obj in objects:
            if obj != other_obj:
                obj.check_collision(other_obj)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    render_ground()
    for obj in objects:
        obj.update()
        obj.render(wireframe_mode)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
