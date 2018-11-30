import pyglet
from drawable import Drawable
import sys

class Tile(Drawable):

  def __init__(self, game, w, h, z, group, tile_type='grass'):
    super().__init__(game, w, h, z)
    self.init_sprite('tile_'+tile_type+'.png', group)