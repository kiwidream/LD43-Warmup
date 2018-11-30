import pyglet
import sys
import random

class Drawable:

  def __init__(self, game, w=0, h=0, z=0):
    self.game = game
    self.w = w
    self.h = h
    self.z = z
    self.x, self.y = self.screen_coords()
    self.origX, self.origY = 0, 0
    self.group = None
    self.sprites = []
    self.sprites_rel = []
    self.last_cull = None
    self.need_pos_update = True
    self.allow_cull = True

  def screen_coords(self):
    x = (self.w - self.h) * self.game.CELL_WIDTH / 2
    y = (self.w + self.h) * self.game.CELL_HEIGHT / 2 + self.z
    return x, y

  def init_sprite(self, filename, group, rel_x=0, rel_y=0, cull=True):
    if filename not in self.game.bin_loaded.keys():
      image = pyglet.image.load('sprites/'+filename)
      texture = self.game.bin.add(image)
      self.game.bin_loaded[filename] = texture
    else:
      texture = self.game.bin_loaded[filename]

    i = len(self.sprites)
    self.sprites_rel.append((rel_x, rel_y))
    s_x, s_y = self.sprite_coords(i)
    self.sprites.append(pyglet.sprite.Sprite(texture, s_x, s_y, batch=self.game.batch, group=group))
    if cull:
      self.game.register_cull(self.sprites[i])
    col = 255
    self.sprites[i].color = (col,col,col)

    return i

  def update_position(self):
    self.need_pos_update = True

  def sprite_coords(self, i=None):
    if i is None or i >= len(self.sprites_rel):
      return (0, 0)

    return self.x + self.sprites_rel[i][0], self.y + self.sprites_rel[i][1]

  def update(self, dt):
    pass

  def draw(self):

    if self.need_pos_update:
      self.x, self.y = self.game.to_screen(self.w, self.h, self.z)

      for i in range(len(self.sprites)):
        self.sprites[i].position = self.sprite_coords(i)

      self.need_pos_update = False