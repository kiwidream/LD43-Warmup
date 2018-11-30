import pyglet
from world_cell import WorldCell
from drawable import Drawable
from character import Character
import noise
import sys
import random
import math
import heapq
from search import Graph, Frontier, Arc, generic_search

class World(Drawable):

  WIDTH = 64
  HEIGHT = 64

  def __init__(self, game, x=0, y=0):
    self.groups = [pyglet.graphics.OrderedGroup(-i*256) for i in range(self.WIDTH+self.HEIGHT)]
    self.cells = [None for w in range(self.WIDTH) for h in range(self.HEIGHT)]
    self.last_w = 0
    self.last_h = 0
    self.character = Character(game, self.WIDTH // 2 + 0.3, self.HEIGHT // 2 + 0.5)
    game.camera.target = self.character

    shape = (self.WIDTH, self.HEIGHT)
    scale = 20.0
    octaves = 6
    persistence = 0.5
    lacunarity = 2.0

    heightmap = [[0 for h in range(self.HEIGHT)] for w in range(self.WIDTH)]
    rand_z = random.randint(0, 2**12)
    for i in range(shape[0]):
        for j in range(shape[1]):
            heightmap[i][j] = noise.pnoise3(i/scale,
                                        j/scale,
                                        rand_z,
                                        octaves=octaves,
                                        persistence=persistence,
                                        lacunarity=lacunarity,
                                        repeatx=self.WIDTH,
                                        repeaty=self.HEIGHT,
                                        base=0)

    for w in range(self.WIDTH):
      for h in range(self.HEIGHT):
        height = -1
        if heightmap[w][h] > -0.15:
          height = int((heightmap[w][h] + 0.15) // 0.05)
        self.cells[h*self.WIDTH + w] = WorldCell(game, w, h, self.groups[w+h], height)

    for w in range(self.WIDTH):
      for h in range(self.HEIGHT):
        self.cells[h*self.WIDTH + w].init_shadow(self.cells)

    super().__init__(game, x, y)
    self.game.camera.x, self.game.camera.y = self.game.to_screen(self.WIDTH // 2, self.HEIGHT // 2)

  def on_click(self, x, y):
    c_x, c_y = x + self.game.camera.x, y + self.game.camera.y
    max_w, max_h = self.game.to_coords(c_x, c_y)

    for test_height in range(1, 10):
      w, h = self.game.to_coords(c_x, c_y, test_height)
      if w >= 0 and w < self.WIDTH and h >= 0 and h < self.HEIGHT:
        if self.cells[h*self.WIDTH+w].height >= test_height:
          max_w, max_h = w, h


    goal_cell = self.cells[max_h*self.WIDTH+max_w]
    if goal_cell.height >= 0:
      self.cells[self.last_h*self.WIDTH+self.last_w].update_col(255)
      self.last_w, self.last_h = max_w, max_h
      goal_cell.update_col(100)
      frontier = AStarFrontier(self.cells,
                              (math.floor(self.character.w-1.29), math.floor(self.character.h-0.49)),
                              (max_w, max_h))
      self.character.current_path = next(generic_search(frontier.routing_graph, frontier), None)[1:]
      self.character.move_to = None

  def draw(self):
    for cell in self.cells:
      cell.draw()
    self.character.draw()

  def update(self, dt):
    for cell in self.cells:
      cell.update(dt)
    self.character.update(dt)

class RoutingGraph(Graph):
  DIRECTIONS = [('N' ,    1,  0),
                ('E' ,    0, -1),
                ('S' ,   -1,  0),
                ('W' ,    0,  1),
                ('NW' ,   1,  1),
                ('NE' ,   1, -1),
                ('SW' ,  -1, -1),
                ('SE' ,  -1,  1)]
  WIDTH = 64
  HEIGHT = 64

  def __init__(self, cells, start, goal):
    self.cells = cells
    self.starting_list = [start]
    self.goal = goal

  def starting_nodes(self):
    """Returns (via a generator) a sequence of starting nodes."""
    for starting_node in self.starting_list:
      yield starting_node

  def is_goal(self, node):
    """Returns true if the given node is a goal node."""
    return node == self.goal

  def estimated_cost_to_goal(self, node):
    w, h = node
    goal_w, goal_h = self.goal
    dw = abs(goal_w - w)
    dh = abs(goal_h - h)
    return max(dw, dh)

  def outgoing_arcs(self, node):
    """Returns a sequence of Arc objects corresponding to all the
    edges in which the given node is the tail node. The label is
    automatically generated."""

    w, h = node
    for direction in self.DIRECTIONS:
      label, dw, dh = direction
      move = w + dw, h + dh
      if w + dw < self.WIDTH and h + dh < self.HEIGHT and w + dw >= 0 and h + dh >= 0:
        next_cell = self.cells[(h+dh)*self.WIDTH+(w+dw)]
        current_cell = self.cells[h*self.WIDTH+w]
        if next_cell.height >= 0 and abs(next_cell.height - current_cell.height) <= 1:
          yield Arc(node, move, label, 1)

class StablePQ:
  def __init__(self):
    self.q = []
    self.i = 0

  def push(self, cost, path):
    heapq.heappush(self.q, (cost, self.i, path))
    self.i += 1

  def pop(self):
    cost, i, path = heapq.heappop(self.q)
    return cost, path

  def __len__(self):
    return len(self.q)

class AStarFrontier(Frontier):
  """Implements a frontier container appropriate for depth-first
  search."""

  def __init__(self, cells, start, goal):
    """The constructor takes no argument. It initialises the
    container to an empty list."""
    self.q = StablePQ()
    self.routing_graph = RoutingGraph(cells, start, goal)
    self.seen_nodes = []
    self.expanded_nodes = []

  def add(self, path):
    if path[-1].head in self.seen_nodes:
      return

    h = self.routing_graph.estimated_cost_to_goal(path[-1].head)
    cost = sum([arc.cost for arc in path]) + h

    self.q.push(cost, path)

  def __iter__(self):
    while len(self.q) > 0:
      cost, path = self.q.pop()
      if path[-1].head not in self.seen_nodes:
        self.expanded_nodes.append((path[-1].head[1], path[-1].head[0]))
        self.seen_nodes.append(path[-1].head)
        yield path