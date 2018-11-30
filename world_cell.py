import pyglet
from drawable import Drawable
from tile import Tile
import sys
import random

class WorldCell(Drawable):

  def __init__(self, game, w, h, group, height):
    self.tiles = []
    super().__init__(game, w, h)

    self.height = height
    self.col = (255, 255, 255)

    if height == -1:
      self.tiles.append(Tile(game, w, h, 0, group, 'water'))
    else:
      for z in range(height):
        self.tiles.append(Tile(game, w, h, z * game.CELL_Z, group, 'dirt'))

      tile = 'dirt' if random.randint(0,3) > height else 'grass'
      self.tiles.append(Tile(game, w, h, height * game.CELL_Z, group, tile))

  def update_col(self, col):
    for tile in self.tiles:
      for sprite in tile.sprites:
        sprite.color = (col, col, col)

  def init_shadow(self, cells):
    o_range = 3
    obscuring = [(-i, -j) for i in range(o_range) for j in range(o_range)]
    obscure_factor = 0
    for d_w, d_h in obscuring:
      i = (self.h+d_w)*64+ self.w+d_w
      if i >= 0 and i < len(cells):
        cell = cells[i]
        dheight = cell.height - self.height
        obscure_factor += 2 * int((dheight == -d_w or dheight == -d_h) and dheight > 0)
    self.col = tuple([255-obscure_factor*10 for i in range(3)])

    for tile in self.tiles:
      for sprite in tile.sprites:
        sprite.color = self.col

  def draw(self):
    for tile in self.tiles:
      tile.draw()

  def update(self, dt):
    for tile in self.tiles:
      tile.update(dt)