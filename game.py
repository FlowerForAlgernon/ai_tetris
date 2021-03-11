import random
import pygame
from gameconst import *



class Brick():
    def __init__(self, screen, brick_position, brick_color):
        self.screen = screen
        self.position = brick_position
        self.color = brick_color
        self.image = pygame.Surface([Brick_size, Brick_size])
        self.image.fill(self.color)

    def setColor(self, new_color):
        self.color = new_color
        self.image.fill(self.color)

    def draw(self):
        self.screen.blit(self.image, (self.position[0] * Brick_size, self.position[1] * Brick_size))


class Block():
    def __init__(self, screen, field_width, field_height, block_layouts, block_direction, block_color, block_position):
        self.screen = screen
        self.field_width = field_width
        self.field_height = field_height
        self.layouts = block_layouts
        self.direction = block_direction
        self.layout = self.layouts[self.direction]
        self.position = block_position
        self.color = block_color
        self.option = None
        self.is_stop = False
        self.is_failed = False
        self.bricks = [Brick(self.screen, (self.position[0] + x, self.position[1] + y), self.color) for (x, y) in self.layout]

    def left(self, field_map):
        new_position = (self.position[0] - 1, self.position[1])
        if not self.is_stop and self.isLegal(self.layout, new_position, field_map) is State.Success:
            self.position = new_position
            self.refreshBircks()

    def right(self, field_map):
        new_position = (self.position[0] + 1, self.position[1])
        if not self.is_stop and self.isLegal(self.layout, new_position, field_map) is State.Success:
            self.position = new_position
            self.refreshBircks()

    def down(self, field_map):
        new_position = (self.position[0], self.position[1] + 1)
        if not self.is_stop and self.isLegal(self.layout, new_position, field_map) is State.Success:
            self.position = new_position
            self.refreshBircks()
        if not self.is_stop and self.isLegal(self.layout, new_position, field_map) is State.Bottom:
            for (brick, (x, y)) in zip(self.bricks, self.layout):
                if self.position[1] + y < 0:
                    self.is_failed = True
                else:
                    field_map[self.position[1] + y][self.position[0] + x] = brick
            self.is_stop = True

    def rotate(self, field_map):
        new_direction = (self.direction + 1) % len(self.layouts)
        new_layout = self.layouts[new_direction]
        if not self.is_stop and self.isLegal(new_layout, self.position, field_map) is State.Success:
            self.direction = new_direction
            self.layout = new_layout
            self.refreshBircks()

    def isLegal(self, new_layout, new_position, field_map):
        (x0, y0) = new_position
        for (x, y) in new_layout:
            if x + x0 < 0 or x + x0 >= self.field_width:
                return State.Middle
            if y + y0 >= self.field_height or (y + y0 > 0 and type(field_map[y + y0][x + x0]) is Brick):
                return State.Bottom
        return State.Success

    def refreshBircks(self):
        for (brick, (x, y)) in zip(self.bricks, self.layout):
            brick.position = (self.position[0] + x, self.position[1] + y)

    def update(self, field_map):
        if self.option is Option.Rotate:
            self.rotate(field_map)
        elif self.option is Option.Down:
            self.down(field_map)
        elif self.option is Option.Left:
            self.left(field_map)
        elif self.option is Option.Right:
            self.right(field_map)

    def draw(self):
        for brick in self.bricks:
            brick.draw()


class BlockFactory():
    def __init__(self, screen, field_width, field_height):
        self.screen = screen
        self.field_width = field_width
        self.field_height = field_height
        self.bag = list(range(7))
        random.shuffle(self.bag)
        self.block_index = 0
        self.cur_block = self.choose()
        self.next_block = self.choose()
        self.is_failed = False

    def setBag(self):
        last_block = self.bag[-1]
        flag = True
        while flag:
            random.shuffle(self.bag)
            flag = True if self.bag[0] == last_block else False

    def choose(self):
        block_type = self.bag[self.block_index]
        self.block_index += 1
        if self.block_index == len(self.bag):
            self.setBag()
            self.block_index = 0
        block_layouts = Blocks_layout[block_type]
        block_direction = random.randint(0, len(block_layouts) - 1)
        return Block(self.screen, self.field_width, self.field_height, block_layouts, block_direction, Blocks_color[block_type], (self.field_width // 2 - 2, -4))

    def update(self, level, time, field_map):
        if self.cur_block.is_failed:
            self.is_failed = True
        elif self.cur_block.is_stop:
            self.cur_block = self.next_block
            self.next_block = self.choose()
        else:
            self.cur_block.update(field_map)
            interval = Blocks_speed[level] if level < 14 else 1
            if time % interval == 0:
                self.cur_block.down(field_map)

    def draw(self, level, field_map):
        self.cur_block.draw()
        for lows in field_map:
            for brick in lows:
                if type(brick) is Brick:
                    brick.setColor(Buttom_Blocks_color[level % 10])
                    brick.draw()


class Game():
    def __init__(self, field_width, field_height):
        self.field_width = field_width
        self.field_height = field_height

    def initializePygame(self):
        pygame.init()
        pygame.display.set_caption(Game_name)
        self.screen = pygame.display.set_mode(((self.field_width + 8) * Brick_size, self.field_height * Brick_size))
        self.level_font = pygame.font.Font(None, Font_size)
        self.score_font = pygame.font.Font(None, Font_size)
        self.lines_font = pygame.font.Font(None, Font_size)
        self.framerate = pygame.time.Clock()
        self.frame = [Brick(self.screen, (x, y), pygame.Color(169, 169, 169)) for y in range(self.field_height) for x in range(self.field_width, self.field_width+8) if y == 0 or y == self.field_height-1 or y == 7 or x == self.field_width or x == self.field_width+7]
        self.block_factory = BlockFactory(self.screen, self.field_width, self.field_height)

    def initialize(self):
        self.time = 0
        self.level = 0
        self.lines_num = 0
        self.score = 0
        self.block_factory = BlockFactory(None, self.field_width, self.field_height)
        self.field_map = [[0] * self.field_width for _ in range(self.field_height)]

    def checkEvents(self, block, field_map):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    block.rotate(field_map)
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    block.option = Option.Down
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    block.option = Option.Left
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    block.option = Option.Right
            if event.type == pygame.KEYUP:
                block.option = None

    def checkLine(self, line):
        for brick in self.field_map[line]:
            if brick == 0:
                return False
        return True

    def eliminateLines(self):
        combo = 0
        for y0 in list(range(self.field_height))[::-1]:
            while self.checkLine(y0):
                self.lines_num += 1
                combo += 1
                for y in list(range(y0+1))[::-1]:
                    for x in range(self.field_width):
                        if y == y0:
                            self.field_map[y][x] = 0
                        elif type(self.field_map[y][x]) is Brick:
                            self.field_map[y][x].position = (self.field_map[y][x].position[0], self.field_map[y][x].position[1] + 1)
                            self.field_map[y + 1][x] = self.field_map[y][x]
                            self.field_map[y][x] = 0
        if combo == 1:
            self.score += 100
        elif combo == 2:
            self.score += 400
        elif combo == 3:
            self.score += 900
        elif combo == 4:
            self.score += 2500

    def checkUpgrade(self):
        if self.lines_num <= 150:
            self.level = self.lines_num // 30
        else:
            self.level = (self.lines_num - 150) // 50 + 5

    def drawNextBlock(self):
        next_block = Block(self.screen, self.field_width, self.field_height, self.block_factory.next_block.layouts, self.block_factory.next_block.direction, self.block_factory.next_block.color, (12, 3))
        next_block.refreshBircks()
        next_block.draw()

    def drawLevelScoreLine(self):
        level_string = "Level: " + str(self.level)
        score_string = "Score: " + str(self.score)
        lines_string = "Lines: " + str(self.lines_num)
        level_image = self.level_font.render(level_string, True, pygame.Color(255, 255, 255))
        score_image = self.score_font.render(score_string, True, pygame.Color(255, 255, 255))
        lines_image = self.lines_font.render(lines_string, True, pygame.Color(255, 255, 255))
        self.screen.blit(level_image, (370, 240))
        self.screen.blit(score_image, (370, 260))
        self.screen.blit(lines_image, (370, 280))

    def drawFrame(self):
        for brick in self.frame:
            brick.draw()
        self.drawLevelScoreLine()
        self.drawNextBlock()

    def update(self):
        self.block_factory.update(self.level, self.time, self.field_map)
        self.eliminateLines()
        self.checkUpgrade()

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.block_factory.draw(self.level, self.field_map)
        self.drawFrame()
        pygame.display.flip()

    def start(self):
        self.initialize()
        self.initializePygame()
        while not self.block_factory.is_failed:
            self.framerate.tick(Framerate)
            self.time += 1
            self.checkEvents(self.block_factory.cur_block, self.field_map)
            self.update()
            self.draw()


if __name__ == '__main__':
    game = Game(10, 20)
    game.start()
