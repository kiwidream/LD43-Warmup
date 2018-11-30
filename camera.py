import pyglet
from drawable import Drawable
from pyglet.window import key
from pyglet.gl import *
import sys

class Camera(Drawable):

  zoom = 2
  speed = 6

  def __init__(self, game):
    self.game = game
    self.x = 0
    self.y = 0
    self.vx = 0
    self.vy = 0
    self.rx = 0
    self.ry = 0
    self.width = self.game.window.width
    self.height = self.game.window.height
    self.radio = self.width / self.height
    self.last_cull = None
    self.target = None

  def reset(self):
    glLoadIdentity()
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

  def apply(self):
    self.reset()
    glTranslatef(-int(self.x*self.zoom)+self.width//2, -int(self.y*self.zoom)+self.height//2, 0)
    glScaled(self.zoom, self.zoom, 1)
    glRotatef(self.rx, 1, 0, 0)
    glRotatef(self.ry, 0, 1, 0)

  def update(self, dt):
    self.x += self.vx
    self.y += self.vy
    self.vx *= 0.92
    self.vy *= 0.92

    if self.target is None:
      if key.W in self.game.keys_pressed:
        self.vy = self.vy + (self.speed / self.zoom - self.vy) * 0.6
      elif key.S in self.game.keys_pressed:
        self.vy = self.vy + (-self.speed / self.zoom - self.vy) * 0.6

      if key.D in self.game.keys_pressed:
        self.vx = self.vx + (self.speed / self.zoom - self.vx) * 0.6
      elif key.A in self.game.keys_pressed:
        self.vx = self.vx + (-self.speed / self.zoom - self.vx) * 0.6
    else:
      self.x += (self.target.x + self.target.origX - self.x) * 0.1
      self.y += (self.target.y + self.target.origY - self.y) * 0.1

    if key.UP in self.game.keys_pressed:
      self.zoom *= 1.1
      self.last_cull = None
    elif key.DOWN in self.game.keys_pressed:
      self.zoom *= 0.9
      self.last_cull = None

    if self.last_cull is None or abs(self.last_cull[0] - self.x) > 128 or abs(self.last_cull[1] - self.y) > 128:

      for sprite in self.game.cull_sprites:
        will_be_culled = abs(self.x - sprite.x) * self.zoom > self.width // 2 + 512 or abs(self.y - sprite.y) * self.zoom > self.height // 2  + 512

        if sprite.visible is will_be_culled:
          sprite.visible = not will_be_culled

      self.last_cull = (self.x, self.y)