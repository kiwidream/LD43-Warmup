import pyglet
from pyglet.window import key
from drawable import Drawable
import sys
import math

class Character(Drawable):

  def __init__(self, game, w, h):
    super().__init__(game, w, h)
    character_group = pyglet.graphics.OrderedGroup(-((w-1)//1+(h-1)//1)*256)
    self.east_i = self.init_sprite('character_e.png', character_group, 0, 0, False)
    self.north_i = self.init_sprite('character_n.png', character_group, 0, 0, False)
    self.sprites[self.north_i].visible = False
    self.origX = self.sprites[self.east_i].width // 2
    self.origY = self.sprites[self.east_i].height // 2
    self.current_path = None
    self.move_to = None
    self.vw = 0
    self.vh = 0

  def update(self, dt):
    if self.current_path and len(self.current_path) > 0:
      mw, mh = self.current_path[0].head
      self.move_to = (mw + 1.3, mh + 0.5)
      if (round(self.w, 2), round(self.h, 2)) == self.move_to:
        self.current_path = self.current_path[1:]
        self.move_to = None

    if self.move_to:
      mw, mh = self.move_to
      dw, dh = mw - self.w, mh - self.h
      theta = math.atan2(dh, dw)
      dist = math.sqrt(dw**2 + dh**2)
      speed = min(2.5*dt, dist*0.8)
      self.vw = speed * math.cos(theta)
      self.vh = speed * math.sin(theta)
    else:
      self.vw = 0
      self.vh = 0

    self.w += self.vw
    self.h += self.vh

    if self.vw > 0.01:
      self.sprites_rel[self.north_i] = (0, 0)
      self.sprites[self.north_i].scale_x = 1
      self.sprites[self.north_i].visible = True
      self.sprites[self.east_i].visible = False
      self.need_pos_update = True
    elif self.vw < -0.01:
      self.sprites[self.east_i].scale_x = -1
      self.sprites_rel[self.east_i] = (self.sprites[self.north_i].width, 0)
      self.sprites[self.north_i].visible = True
      self.sprites[self.east_i].visible = True
      self.sprites[self.north_i].visible = False
      self.need_pos_update = True
    elif self.vh > 0.01:
      self.sprites_rel[self.north_i] = (self.sprites[self.north_i].width, 0)
      self.sprites[self.north_i].scale_x = -1
      self.sprites[self.north_i].visible = True
      self.sprites[self.east_i].visible = False
      self.need_pos_update = True
    elif self.vh < -0.01:
      self.sprites_rel[self.east_i] = (0, 0)
      self.sprites[self.east_i].scale_x = 1
      self.sprites[self.east_i].visible = True
      self.sprites[self.north_i].visible = False
      self.need_pos_update = True



    cell_i = int(math.floor(self.h)*self.game.world.WIDTH + math.floor(self.w-0.8))
    h = 0
    colour = (255,255,255)
    if cell_i >= 0 and cell_i < len(self.game.world.cells):
      h = self.game.world.cells[cell_i].height
      colour = self.game.world.cells[cell_i].col

    self.z = max(h, 0) * self.game.CELL_Z + 1

    self.update_position()

    for sprite in self.sprites:
      sprite.color = colour
      sprite.group = pyglet.graphics.OrderedGroup(int(-(math.floor(self.w-0.8)+math.floor(self.h))*256+1))