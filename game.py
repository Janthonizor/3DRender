import pygame as pg
from OpenGL.GL import *
import numpy as np
import ctypes
from OpenGL.GL.shaders import compileProgram, compileShader


#philosophy
# bus -- link between cpu and graphics card
# shift data to graphics card 
# graphics card returns the data from where it is stored
# 

class App:
    def __init__(self):
        pg.init()
        # allow openGL to calculate the next frame before swapping it to desplay
        pg.display.set_mode((800,690), pg.OPENGL|pg.DOUBLEBUF)
        #control frame rate
        self.clock = pg.time.Clock()
        glClearColor(1.0,0.4,0.0,1)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        self.shader = self.createShader("shaders/vertex.txt", "shaders/fragment.txt")
        glUseProgram(self.shader)
        glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)
        self.triangle = Triangle()
        self.spiral_texture = Material("gfx/phi_spiral_icon.png")
        self.mainLoop()
    
    def createShader(self, vertexFilepath, fragmentFilepath):

        with open(vertexFilepath, 'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath, 'r') as f:
            fragment_src = f.readlines()

        shader = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER)
        )

        return shader
        
    def mainLoop(self):
        running = True
        while(running):
            for event in pg.event.get():
                if(event.type == pg.QUIT):
                    running = False
            #refresh frame, flip to new frame, and wait 
            glClear(GL_COLOR_BUFFER_BIT)

            glUseProgram(self.shader)
            self.spiral_texture.use()
            glBindVertexArray(self.triangle.vao)
            glDrawArrays(GL_TRIANGLES,0, self.triangle.vertex_count)

            pg.display.flip()
            self.clock.tick(60)
        self.quit()

    def quit(self):
        self.triangle.destroy()
        glDeleteProgram(self.shader)
        self.spiral_texture.destroy()
        pg.quit()

class Triangle:

    def __init__(self):

        # x,y,z,r,g,b,s,t
        self.vertices = (
            -0.5, -0.5, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0,
            0.5, -0.5, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0,
            0.0, 0.5, 0.0, 0.0, 0.0, 1.0, 0.5, 0.0
        )

        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.vertex_count = 3

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0,3,GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1,3,GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2,2,GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(24))
    
    def destroy(self):
        glDeleteVertexArrays(1,(self.vao,))
        glDeleteBuffers(1, (self.vbo,))


class Material:
    def __init__(self, filepath):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        #image = pg.image.load(filepath).convert_alpha()
        image = pg.image.load(filepath).convert()
        image_width, image_height = image.get_rect().size
        image_data = pg.image.tostring(image,"RGBA")
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width, image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        glGenerateMipmap(GL_TEXTURE_2D)
    
    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
    
    def destroy(self):
        glDeleteTextures(1, (self.texture,))


if __name__ == "__main__":
    myApp = App()