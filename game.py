import pyglet
pyglet.options['debug_gl'] = False
from pyglet.gl import *
from pyglet.graphics import Batch
from pyglet.image.atlas import TextureBin
from pyglet.window import mouse
from camera import Camera
from world import World
import sys
import cProfile
import math
from pyglet.window import key
from reloadr import autoreload

glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glEnable(GL_ALPHA_TEST)
glAlphaFunc(GL_GREATER, .1)
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

class Game:
  bin = TextureBin()
  bin_loaded = {}

  batch = Batch()

  CELL_HEIGHT = 32
  CELL_WIDTH = 64
  CELL_Z = 13

  def __init__(self):
    self.window = pyglet.window.Window()
    self.cull_sprites = []
    self.camera = Camera(self)
    self.world = World(self)
    self.keys_pressed = []


  def register_cull(self, sprite):
    self.cull_sprites.append(sprite)

  def to_screen(self, w, h, z=0):
    x = (w - h) * self.CELL_WIDTH // 2
    y = (w + h) * self.CELL_HEIGHT // 2 + z
    return x, y

  def to_coords(self, x, y, height=0):
    x -= self.CELL_WIDTH // 2
    y -= self.CELL_Z * (height + 1)
    w = y / self.CELL_HEIGHT + x / self.CELL_WIDTH
    h = y / self.CELL_HEIGHT - x / self.CELL_WIDTH
    return math.floor(w), math.floor(h)



game = Game()
fps_display = pyglet.clock.ClockDisplay()

def main():
  pyglet.app.run()


def update(dt):
  game.camera.update(dt)
  game.world.update(dt)

pyglet.clock.schedule_interval(update, 1.0/60.0)
pyglet.clock.set_fps_limit(60)

@game.window.event
def on_key_press(symbol, modifiers):
  game.keys_pressed.append(symbol)
  if symbol == key.E:
    pyglet.app.exit()

@game.window.event
def on_key_release(symbol, modifiers):
  game.keys_pressed.remove(symbol)

@game.window.event
def on_mouse_press(x, y, button, modifiers):
  x -= game.window.width // 2
  y -= game.window.height // 2
  x /= game.camera.zoom
  y /= game.camera.zoom
  if button == mouse.LEFT:
    game.world.on_click(x, y)


@game.window.event
def on_draw():
  game.window.clear()
  dt = pyglet.clock.tick()


  game.camera.apply()
  game.world.draw()
  game.batch.draw()
  game.camera.reset()
  fps_display.draw()



if __name__ == '__main__':
  cProfile.run('main()')