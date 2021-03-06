"""
这份代码实现了 Pierre Dellacherie 算法，详情可参考 https://blog.csdn.net/qq_41882147/article/details/80005763
"""

import os
import random
import pygame
from game import *
from gameconst import *



class PierreDellacherie():
    """
    计算特定方块放置情况下 Pierre Dellacherie 算法的经验公式值
    """
    def __init__(self, field_width, field_height, A):
        self.field_map = None
        self.field_width = field_width
        self.field_height = field_height
        self.landing_height = 0
        self.eroded_piece_cells_metric = 0
        self.board_row_transitions = 0
        self.board_col_transitions = 0
        self.board_buried_holes = 0
        self.board_wells = 0
        self.a1, self.a2, self.a3, self.a4, self.a5, self.a6 = A

    def copyMap(self, field_map):
        """
        复制当前游戏区域，在新的游戏区域上尝试方块不同放置情况
        """
        self.field_map = [[0] * self.field_width for _ in range(self.field_height)]
        for y in range(self.field_height):
            for x in range(self.field_width):
                if type(field_map[y][x]) is Brick:
                    self.field_map[y][x] = 1
                elif field_map[y][x] == 1:
                    self.field_map[y][x] = 2

    def checkLine(self, line):
        for brick in self.field_map[line]:
            if brick == 0:
                return False
        return True

    def eliminateLines(self):
        lines = 0
        for y0 in list(range(self.field_height))[::-1]:
            while self.checkLine(y0):
                lines += 1
                for y in list(range(y0 + 1))[::-1]:
                    for x in range(self.field_width):
                        if y == y0:
                            self.field_map[y][x] = 0
                        elif self.field_map[y][x] == 1:
                            self.field_map[y + 1][x] = 1
                            self.field_map[y][x] = 0
                        elif self.field_map[y][x] == 2:
                            self.field_map[y + 1][x] = 2
                            self.field_map[y][x] = 0
        return lines

    def getLandingHeight(self, position, layout):
        """
        计算当前方块放置之后，方块重心距离游戏区域底部的距离
        """
        self.landing_height = 0
        for (x, y) in layout:
            self.landing_height += self.field_height - (position[1] + y)
        self.landing_height /= 4

    def getErodedPieceCellsMetric(self, lines):
        """
        计算方块放置后消除的行数与当前摆放的方块中被消除的小方块的格数的乘积
        """
        self.eroded_piece_cells_metric = 0
        bricks = 0
        for y in range(self.field_height):
            for x in range(self.field_width):
                bricks = bricks + 1 if self.field_map[y][x] == 2 else bricks
        self.eroded_piece_cells_metric = lines * (4 - bricks)

    def getBoardRowTransitions(self):
        """
        对于游戏区域每一行，从左往右看，从无小方格到有小方格是一种“变换”，从有小方格到无小方格也是一种“变换”。
        计算方块放置后各行中“变换”之和
        """
        self.board_row_transitions = 0
        for y in range(self.field_height):
            for x in range(self.field_width - 1):
                if x == 0 and self.field_map[y][x] == 0:
                    self.board_row_transitions += 1
                if self.field_map[y][x] == 0 and self.field_map[y][x + 1] != 0:
                    self.board_row_transitions += 1
                if self.field_map[y][x] != 0 and self.field_map[y][x + 1] == 0:
                    self.board_row_transitions += 1
            if self.field_map[y][self.field_width - 1] == 0:
                self.board_row_transitions += 1

    def getBoardColTransitions(self):
        """
        计算方块放置后各列中“变换”之和
        """
        self.board_col_transitions = 0
        for x in range(self.field_width):
            for y in range(self.field_height - 1):
                if self.field_map[y][x] == 0 and self.field_map[y + 1][x] != 0:
                    self.board_col_transitions += 1
                if self.field_map[y][x] != 0 and self.field_map[y + 1][x] == 0:
                    self.board_col_transitions += 1
            if self.field_map[self.field_height - 1][x] == 0:
                self.board_col_transitions += 1

    def getBoardBuriedHoles(self):
        """
        计算各列中的“空洞”小方格数之和
        """
        self.board_buried_holes = 0
        for x in range(self.field_width):
            for y in range(self.field_height - 1):
                if self.field_map[y][x] != 0 and self.field_map[y + 1][x] == 0:
                    self.board_buried_holes += 1

    def getBoardWells(self):
        """
        计算各列中“井”的深度的连加和
        """
        self.board_wells = 0
        for x in range(self.field_width):
            is_hole = False
            hole_deep = 0
            for y in range(self.field_height):
                if not is_hole and self.field_map[y][x] == 0 and ((x == 0 and self.field_map[y][x + 1] != 0) or \
                                                                  (x == self.field_width - 1 and self.field_map[y][x - 1] != 0) or \
                                                                  (0 < x < self.field_width - 1 and self.field_map[y][x - 1] != 0 and self.field_map[y][x + 1] != 0)):
                    is_hole = True
                    hole_deep += 1
                    self.board_wells += hole_deep
                elif is_hole and self.field_map[y][x] == 0:
                    hole_deep += 1
                    self.board_wells += hole_deep
                else:
                    is_hole = False
                    hole_deep = 0

    def initialize(self, position, layout, field_map):
        self.copyMap(field_map)
        self.getLandingHeight(position, layout)
        self.getErodedPieceCellsMetric(self.eliminateLines())
        self.getBoardRowTransitions()
        self.getBoardColTransitions()
        self.getBoardBuriedHoles()
        self.getBoardWells()

    def evaluate(self, position, layout, field_map):
        self.initialize(position, layout, field_map)
        score = self.a1 * self.landing_height \
              + self.a2 * self.eroded_piece_cells_metric \
              + self.a3 * self.board_row_transitions \
              + self.a4 * self.board_col_transitions \
              + self.a5 * self.board_buried_holes \
              + self.a6 * self.board_wells
        return score


class AI():
    """
    找出经验公式值最大的放置方法并放置方块
    """
    def __init__(self, field_width, field_height, A):
        self.evaluation = PierreDellacherie(field_width, field_height, A)
        self.field_width = field_width
        self.field_height = field_height

    def getAllPossibleLocation(self, block, layout, field_map):
        """
        找出方块在特定方向下所有可行的放置位置
        """
        all_possible_position = []
        for x in range(self.field_width):
            if block.isLegal(layout, (x, -4), field_map) is not State.Middle:
                all_possible_position.append(x)
        return all_possible_position

    def findBottomPosition(self, block, x, layout, field_map):
        """
        找出方块最终下落到底部方块的堆顶的位置
        """
        y = -4
        while block.isLegal(layout, (x, y), field_map) is not State.Bottom:
            y += 1
        return y - 1

    def dropBlock(self, x0, y0, layout, field_map):
        """
        模拟将方块放置到目标底部位置上的情况
        """
        for (x, y) in layout:
            if 0 <= y0 + y < self.field_height:
                field_map[y0 + y][x0 + x] = 1
            if y0 + y < 0:
                return False
        return True

    def resetMap(self, field_map):
        """
        将游戏区域恢复到方块放置前，删除方块模拟放置信息
        """
        count = 0
        for y in range(self.field_height):
            for x in range(self.field_width):
                if field_map[y][x] == 1:
                    field_map[y][x] = 0
                    count += 1
                if count == 4:
                    return

    def getNewMap(self, block, position, direction, field_map):
        """
        通过游戏提供的接口将方块移动到目标位置
        """
        while block.direction is not direction:
            block.rotate(field_map)
        while block.position[0] > position[0]:
            block.left(field_map)
        while block.position[0] < position[0]:
            block.right(field_map)
        while not block.is_stop:
            block.down(field_map)

    def ai(self, block, field_map):
        best_position = (float('-inf'), (-1, -1), 0)
        for direction in range(len(block.layouts)):
            for x in self.getAllPossibleLocation(block, block.layouts[direction], field_map):
                y = self.findBottomPosition(block, x, block.layouts[direction], field_map)
                if self.dropBlock(x, y, block.layouts[direction], field_map):
                    score = self.evaluation.evaluate((x, y), block.layouts[direction], field_map)
                    if score > best_position[0]:
                        best_position = (score, (x, y), direction)
                self.resetMap(field_map)
        if best_position[0] > float('-inf'):
            self.getNewMap(block, best_position[1], best_position[2], field_map)
            return True
        else:
            return False


class AIGame(Game):
    def __init__(self):
        super(AIGame, self).__init__(10, 20)

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)

    def start(self, A):
        self.initialize()
        self.initializePygame()
        self.ai = AI(self.field_width, self.field_height, A)
        while not self.block_factory.is_failed and self.ai.ai(self.block_factory.cur_block, self.field_map):
            self.checkEvents()
            self.update()
            self.draw()
        return self.lines_num

    def startWithoutGUI(self, A):
        self.initialize()
        self.ai = AI(self.field_width, self.field_height, A)
        while not self.block_factory.is_failed and self.ai.ai(self.block_factory.cur_block, self.field_map):
            self.update()
            print("\r" + "Lines: " + str(self.lines_num), end="", flush=True)
        return self.lines_num


if __name__ == '__main__':
    A = [-4.500158825082766, 3.4181268101392694, -3.2178882868487753, -9.348695305445199, -7.899265427351652, -3.3855972247263626]
    game = AIGame()
    lines_num = game.start(A)
    #lines_num = game.startWithoutGUI(A)
