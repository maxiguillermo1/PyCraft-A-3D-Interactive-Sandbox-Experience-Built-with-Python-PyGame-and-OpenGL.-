import pygame as pg
import numpy as np
import random as rand
from pygame.locals import *
from OpenGL.GL import *
from PIL import Image
from math import *
from OpenGL.GLU import *


class Mesh:
    def __init__(self, x, y, z, image):
        self.x = x
        self.y = y
        self.z = z
        self.img = image
        self.vertices = []
        self.tex_coords = []
        self.edges = []
        self.img_data = self.img.convert("RGB").tobytes()

    def move_verts(self, x, y, z):
        for i in range(len(self.vertices)):
            self.vertices[i][0] += float(x)
            self.vertices[i][1] += float(y)
            self.vertices[i][2] += float(z)

    def combine_with_mesh(self, other):
        self.vertices.extend(other.vertices)
        self.tex_coords.extend(other.tex_coords)
        self.normals.extend(other.normals)

    def render(self):
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.img.width, self.img.height, 0, GL_RGB, GL_UNSIGNED_BYTE,
                     self.img_data)
        glEnable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        o = 0
        for i in range(0, len(self.vertices)):
            glNormal3fv(self.normals[i])
            glTexCoord2fv(self.tex_coords[o])
            glVertex3fv(self.vertices[i])
            o += 1
            if o >= 4:
                o = 0
        glEnd()
        glDisable(GL_TEXTURE_2D)


class OBJMesh(Mesh):
    def __init__(self, x, y, z, obj_file_path):
        image = Image.open("grass.jpeg")
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        super().__init__(x, y, z, image)
        self.vertices = []
        self.normals = []
        self.tex_coords = []

        self.load_obj(obj_file_path)

    def load_obj(self, obj_file_path):
        # Implement the logic to parse the OBJ file and extract vertices, texture coordinates, and normals
        # You can refer to existing OBJ parsing libraries or tutorials for guidance on how to accomplish this.
        pass


class Cube(Mesh):
    def __init__(self, x, y, z):
        image = Image.open("grass.jpeg")
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        super().__init__(x, y, z, image)

        self.vertices = []
        self.normals = []
        self.tex_coords = [
            [0.0, 0.0], [1.0, 0.0], [1.0, 0.0], [0.0, 1.0]
        ]

        self.front, self.top, self.west, self.east, self.back, self.bottom = True, True, True, True, True, True

    def make_mesh(self):
        if self.front:
            self.vertices.extend([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
            self.normals.extend([[0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1]])

        if self.top:
            self.vertices.extend([[0, 0, 1], [1, 0, 1], [1, 0, 0], [0, 0, 0]])
            self.normals.extend([[0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0]])

        if self.west:
            self.vertices.extend([[0, 0, 1], [0, 1, 1], [0, 1, 0], [0, 0, 0]])
            self.normals.extend([[1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0]])

        if self.east:
            self.vertices.extend([[1, 0, 1], [1, 1, 1], [1, 1, 0], [1, 0, 0]])
            self.normals.extend([[-1, 0, 0], [-1, 0, 0], [-1, 0, 0], [-1, 0, 0]])

        if self.bottom:
            self.vertices.extend([[0, 1, 1], [1, 1, 1], [1, 1, 0], [0, 1, 0]])
            self.normals.extend([[0, -1, 0], [0, -1, 0], [0, -1, 0], [0, -1, 0]])


class Chunk:
    def __init__(self):
        self.base = Cube(0, 0, 0)
        self.base.make_mesh()

        self.blocks = []

        for z in range(0, 8):
            y_dimension = []
            for y in range(0, 8):
                x_dimension = []
                for x in range(0, 8):
                    r = rand.randint(0, 1)
                    x_dimension.append(r)
                y_dimension.append(x_dimension)
            self.blocks.append(y_dimension)

        for x in range(0, 8):
            for y in range(0, 8):
                for z in range(0, 8):
                    if self.blocks[x][y][z] == 1:
                        b = Cube(0, 0, 0)

                        if x >= 1 and self.blocks[x - 1][y][z] == 1:
                            b.west = False
                        if x < 7 and self.blocks[x + 1][y][z] == 1:
                            b.east = False
                        if y >= 1 and self.blocks[x][y - 1][z] == 1:
                            b.top = False
                        if y < 7 and self.blocks[x][y + 1][z] == 1:
                            b.bottom = False
                        if z >= 1 and self.blocks[x][y][z - 1] == 1:
                            b.front = False
                        if z < 7 and self.blocks[x][y][z + 1] == 1:
                            b.back = False

                        b.make_mesh()
                        b.move_verts(x, y, z)
                        self.base.combine_with_mesh(b)

    def render(self):
        self.base.render()


class Camera:
    x, y, z, rot_y, dir_z, dir_x = 0, 0, 5, 0, -1, 0

    @staticmethod
    def move_forward(speed):
        Camera.x += Camera.dir_x * speed
        Camera.z += Camera.dir_z * speed

    @staticmethod
    def move_backward(speed):
        Camera.x -= Camera.dir_x * speed
        Camera.z -= Camera.dir_z * speed

    @staticmethod
    def move_left(speed):
        # Calculate the right vector
        right_x = Camera.dir_z
        right_z = -Camera.dir_x

        # Subtract the right vector times speed from the current position
        Camera.x -= right_x * speed
        Camera.z -= right_z * speed

    @staticmethod
    def move_right(speed):
        # Calculate the right vector
        right_x = Camera.dir_z
        right_z = -Camera.dir_x

        # Add the right vector times speed to the current position
        Camera.x += right_x * speed
        Camera.z += right_z * speed

    @staticmethod
    def move_up(speed):
        # Add speed to the current y-coordinate
        Camera.y += speed

    @staticmethod
    def move_down(speed):
        # Subtract speed from the current y-coordinate
        Camera.y -= speed


class Main:
    test = Chunk()

    last_mouse_x, last_mouse_y = 0, 0

    @staticmethod
    def start():
        pg.init()
        pg.display.set_mode((1280, 720), DOUBLEBUF | OPENGL)
        pg.display.set_caption("COMPUTER GRAPHICS")

        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)  # Changed from GL_REPEAT
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)  # Changed from GL_REPEAT

        gluPerspective(70, 1280 / 720, 0.1, 100.0)

        glEnable(GL_DEPTH_TEST)

        pg.mouse.set_visible(False)

        Main.loop()

    @staticmethod
    def loop():
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            keys = pg.key.get_pressed()

            mouse_x, mouse_y = pg.mouse.get_pos()

            if Main.last_mouse_x != mouse_x:
                Camera.rot_y += (mouse_x - Main.last_mouse_x) / 100
                Camera.dir_x = sin(Camera.rot_y)
                Camera.dir_z = -cos(Camera.rot_y)
                mouse_x, mouse_y = 1280 / 2, 720 / 2
                Main.last_mouse_x, Main.last_mouse_y = mouse_x, mouse_y
                pg.mouse.set_pos(1280 / 2, 720 / 2)

            # Handle WASDQE input for camera control
            if keys[pg.K_w]:
                Camera.move_forward(0.3)
            if keys[pg.K_s]:
                Camera.move_backward(0.3)
            if keys[pg.K_a]:
                Camera.move_left(0.3)
            if keys[pg.K_d]:
                Camera.move_right(0.3)
            if keys[pg.K_q]:
                Camera.move_down(0.3)
            if keys[pg.K_e]:
                Camera.move_up(0.3)

            if keys[pg.K_ESCAPE]:
                pg.quit()
                quit()

            glPushMatrix()

            glClearColor(0.0, 0.0, 0.0, 0.0)
            pos = [1.0, 3.0, 1.0, 0.0]
            ambient = [0.8, 0.9, 1.0, 1.0]

            glShadeModel(GL_SMOOTH)
            glLightfv(GL_LIGHT0, GL_POSITION, pos)
            glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glClearColor(0.8, 0.9, 1.0, 1.0)

            gluLookAt(Camera.x, Camera.y + 1.0, Camera.z, Camera.x + Camera.dir_x, Camera.y + 1.0,
                      Camera.z + Camera.dir_z, 0.0, 1.0, 0.0)

            Main.test.render()
            glPopMatrix()
            pg.display.flip()


Main.start()
