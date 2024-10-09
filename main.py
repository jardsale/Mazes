from collections import defaultdict, deque
import pygame as pg
import random
import sys
import glob
from PIL import Image


# RGB values for select colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)


class Square:
    def __init__(self, x, y, color):
        x_scaled = 20 * x + 20
        y_scaled = 20 * y + 20
        self.color = color

        # List of edges in the order: top, bottom, left, right
        self.edges = [pg.Rect(x_scaled, y_scaled, 20, 2),
                      pg.Rect(x_scaled, y_scaled+19, 20, 2),
                      pg.Rect(x_scaled, y_scaled, 2, 20),
                      pg.Rect(x_scaled+19, y_scaled, 2, 20)]

        self.box = pg.Rect(x_scaled, y_scaled, 20, 20)

    def paint(self, surface):
        pg.draw.rect(surface, self.color, self.box)

        for edge in self.edges:
            if edge:
                pg.draw.rect(surface, BLACK, edge)


class DFSMaze:
    def __init__(self, width, height, start_pos):
        self.width = width
        self.height = height
        self.start_pos = start_pos

        self.graph = self.full_graph()
        self.maze = self.empty_graph()

        # Initializing pygame objects
        self.pg_screen = pg.display.set_mode((width * 20 + 40, height * 20 + 40))
        self.pg_squares = [[[None] for i in range(width)] for j in range(height)]
        self.pg_grid = self.pg_grid()

    def empty_graph(self):
        g = dict()
        for node in self.graph:
            g[node] = []

        return g

    def full_graph(self):
        g = defaultdict(list)
        for x in range(self.width):
            for y in range(self.height):
                if x > 0:
                    g[(x, y)].append((x-1, y))
                if x < self.width - 1:
                    g[(x, y)].append((x+1, y))
                if y > 0:
                    g[(x, y)].append((x, y-1))
                if y < self.height - 1:
                    g[(x, y)].append((x, y+1))

        return dict(g)

    def pg_grid(self):
        for node in self.maze:
            square = Square(node[0], node[1], WHITE)
            self.pg_squares[node[0]][node[1]] = square

        self.pg_squares[0][0].edges[0] = None
        self.pg_squares[self.start_pos[0]-1][self.start_pos[1]-1].edges[1] = None

    def update_edges(self, tup):
        x = tup[0]
        y = tup[1]
        if (x, y-1) in self.maze[(x, y)]:
            self.pg_squares[x][y].edges[0] = None
            self.pg_squares[x][y-1].edges[1] = None
        if (x, y+1) in self.maze[(x, y)]:
            self.pg_squares[x][y].edges[1] = None
            self.pg_squares[x][y+1].edges[0] = None
        if (x-1, y) in self.maze[(x, y)]:
            self.pg_squares[x][y].edges[2] = None
            self.pg_squares[x-1][y].edges[3] = None
        if (x+1, y) in self.maze[(x, y)]:
            self.pg_squares[x][y].edges[3] = None
            self.pg_squares[x+1][y].edges[2] = None

    def paint_grid(self):
        self.pg_screen.fill(WHITE)

        for row in self.pg_squares:
            for square in row:
                square.paint(self.pg_screen)

    def dfs(self):
        stack = deque([(self.start_pos, self.start_pos)])
        v = self.start_pos
        explored = {self.start_pos}
        order = []

        while stack:

            edges = self.graph[v]
            random.shuffle(edges)

            for adj in edges:
                if adj not in explored:
                    stack.append((v, adj))

            i = random.random()
            if i > 0.99:
                edge = stack.pop()
            else:
                edge = stack.popleft()

            if edge[1] not in explored:
                self.maze[edge[0]].append(edge[1])
                self.maze[edge[1]].append(edge[0])
                explored.add(edge[1])
                order.append(edge)

                v = edge[1]

        return order

    def animate(self, order):
        pg.init()
        g = self.empty_graph()
        clock = pg.time.Clock()
        order = iter(order)
        remaining = True
        i = 0
        while 1:
            if remaining:
                try:
                    connection = next(order)
                except StopIteration:
                    remaining = False
                    pg.image.save(self.pg_screen, "DFS_maze.jpg")

            if remaining:
                g[connection[0]].append(connection[1])
                g[connection[1]].append(connection[0])
                self.update_edges(connection[1])
                self.paint_grid()
                #pg.image.save(self.pg_screen, f"frames/{i}.jpg")
                i += 1
                pg.display.flip()
                clock.tick(60)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    self.make_gif()
                    sys.exit()

    def make_gif(self):
        frames = [Image.open(image) for image in glob.glob(f"frames/*")]
        frames.sort(key=lambda frame: int(frame.filename.replace(".jpg", "").replace("frames/", "")))
        frame_one = frames[0]
        frame_one.save("maze.gif", format="GIF", append_images=frames,
                        save_all=True, duration=100, loop=0)


def main():
    maze = DFSMaze(40, 40, (0, 0))
    order = maze.dfs()
    maze.animate(order)


if __name__ == '__main__':
    main()