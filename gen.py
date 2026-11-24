from sys import argv
from random import choice, randint
from display import display_map


class MazeGenerator:
    def __init__(self, width, height, filename):
        self.__width = width
        self.__height = height
        self.__grid = []
        self.__path = []
        self.__entry = [0, 0]
        self.__end = [height - 1, width - 1]
        self.__filename = filename

    def grid_gen(self, motif):

        m_w = len(motif[0])
        m_h = len(motif)

        d_x = (self.__width - m_w) // 2
        d_y = (self.__height - m_h) // 2

        self.__grid = [[15 for dx in range(self.__width)]
                       for dy in range(self.__height)]

        for dy in range(0, m_h):
            for dx in range(0, m_w):
                if (motif[dy][dx] == '#'):
                    self.__grid[d_y + dy][d_x + dx] = -1

    def entry_and_exit(self):

        stop = False

        while not stop:
            self.__entry = [randint(0, self.__height - 1),
                            randint(0, self.__width - 1)]
            if self.__grid[self.__entry[0]][self.__entry[1]] == -1:
                continue
            else:
                stop = True

        stop = False

        while not stop:
            self.__end = [randint(0, self.__height - 1),
                          randint(0, self.__width - 1)]
            if self.__grid[self.__end[0]][self.__end[1]] == -1 \
                    or self.__end == self.__entry:
                continue
            else:
                stop = True

    def write_in_file(self):
        with open(self.__filename, "w", encoding="utf-8") as f:
            for i in range(len(self.__grid)):
                f.write(''.join(format(valeur, 'X').lower()
                                for valeur in self.__grid[i]))
                f.write('\n')

    def path_gen(self):
        stack = [list(self.__entry)]

        directions = ((-1, 0, 1, 4), (0, 1, 2, 8),
                      (1, 0, 4, 1), (0, -1, 8, 2))

        while stack:
            head = stack[-1]

            if head == self.__end:
                self.__path = [list(position) for position in stack]

            neighbors = []

            for dl, dc, bit, bit_opp in directions:
                row = head[0] + dl
                column = head[1] + dc
                if 0 <= row < self.__height and 0 <= column < self.__width \
                        and self.__grid[row][column] == 15:
                    neighbors.append([row, column, bit, bit_opp])

            if neighbors:
                row, column, bit, bit_opp = choice(neighbors)
                self.__grid[head[0]][head[1]] &= ~bit
                self.__grid[row][column] &= ~bit_opp
                stack.append([row, column])
            else:
                stack.pop()

        for row in range(self.__height):
            for column in range(self.__width):
                if self.__grid[row][column] == -1:
                    self.__grid[row][column] = 15


WIDTH = 10
HEIGHT = 10
START_POS = (0, 0)
END_POS = (WIDTH - 1, HEIGHT - 1)

motif = ["#.#.###",
         "#.#...#",
         "###.###",
         "..#.#..",
         "..#.###"
         ]

maze = MazeGenerator(WIDTH, HEIGHT, argv[1])
maze.grid_gen(motif)
maze.entry_and_exit()
maze.path_gen()
maze.write_in_file()

display_map(argv[1], START_POS, END_POS)
