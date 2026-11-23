from sys import argv
from random import choice, randint

class MazeGenerator:
    def __init__(self, width, height, filename) :
        self.__width = width
        self.__height = height
        self.__grid = []
        self.__entry = [0,0]
        self.__end = [height - 1, width - 1]
        self.__filename = filename

    def grid_gen(self, motif) :

        m_w = len(motif[0])
        m_h = len(motif)

        d_x = (self.__width - m_w) // 2
        d_y = (self.__height - m_h) // 2

        for dy in range(0, self.__height):
            ligne = ""
            for dx in range(0, self.__width):
                ligne += '0'
            self.__grid.append(ligne)

        for dy in range(0, m_h):
            for dx in range(0, m_w):
                if (motif[dy][dx] == '#'):
                    self.__grid[d_y + dy] = self.__grid[d_y + dy][:d_x + dx] + 'F' + self.__grid[d_y + dy][d_x + dx + 1:]


    def entry_and_exit(self):

        stop = False

        while not stop :
            self.__entry = [randint(0,self.__height - 1), randint(0,self.__width - 1)]
            if self.__grid[self.__entry[0]][self.__entry[1]] == 'F' :
                continue
            else :
                stop = True

        stop = False

        while not stop :
            self.__end = [randint(0,self.__height - 1), randint(0,self.__width - 1)]
            if self.__grid[self.__end[0]][self.__end[1]] == 'F' or self.__end == self.__entry:
                continue
            else :
                stop = True


    def write_in_file(self):
        with open(self.__filename, "w", encoding="utf-8") as f:
            for i in range(len(self.__grid)):
                f.write(self.__grid[i])
                f.write('\n')


    def path_gen(self):
        stack = [list(self.__entry)]
        head = stack[-1]
        self.__grid[head[0]] = self.__grid[head[0]][:head[1]] + 'X' + self.__grid[head[0]][head[1] + 1:]

        while head != self.__end and stack:
            head = stack[-1]
            neighbors = []
            for row, column in ((head[0] - 1, head[1]), (head[0] + 1, head[1]),
                                (head[0], head[1] - 1), (head[0], head[1] + 1)):
                if 0 <= row < self.__height and 0 <= column < self.__width \
                        and self.__grid[row][column] not in {'F', 'X'}:
                    neighbors.append([row, column])

            if neighbors:
                head = choice(neighbors)
                self.__grid[head[0]] = self.__grid[head[0]][:head[1]] + 'X' + self.__grid[head[0]][head[1] + 1:]
                stack.append(head)
            else:
                stack.pop()



WIDTH = 30
HEIGHT = 30

motif =["#.#.###",
        "#.#...#",
        "###.###",
        "..#.#..",
        "..#.###"]


maze = MazeGenerator(WIDTH, HEIGHT, argv[1])
maze.grid_gen(motif)
maze.entry_and_exit()
maze.path_gen()
maze.write_in_file()

