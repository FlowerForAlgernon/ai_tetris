"""
这份代码使用 Q learning 算法训练并运行俄罗斯方块游戏 ai。其中简化状态空间的方法可参考论文 Adapting Reinforcement Learning to Tetris
"""

import numpy as np
from game import *



sub_well = 4
base = 7


def getStateIndex(field_width, field_height, field_map):
    """
    因为每一列有 7 种不同的情况，所以采用七进制数来作为状态索引
    """
    temp = [0 for _ in range(field_width)]
    convert = {}
    for i in range(-(base - 1)//2, (base - 1)//2 + 1):
        convert[i] = i + (base - 1)//2
    for x in range(field_width):
        while temp[x] < field_height and field_map[temp[x]][x] == 0:
            temp[x] += 1
    index = 0
    for i in range(field_width-1):
        if temp[i+1] - temp[i] > (base - 1)//2:
            index += base**i * convert[(base - 1)//2]
        elif temp[i+1] - temp[i] < -(base - 1)//2:
            index += base**i * convert[-(base - 1)//2]
        else:
            index += base**i * convert[temp[i+1] - temp[i]]
    return index


def getAllPossibleLocation(field_width, field_map, block, layout):
    all_possible_position = []
    for x in range(field_width):
        if block.isLegal(layout, (x, -4), field_map) is not State.Middle:
            all_possible_position.append(x)
    return all_possible_position


def findBottomPosition(field_map, block, x, layout):
    y = -4
    while block.isLegal(layout, (x, y), field_map) is not State.Bottom:
        y += 1
    return y - 1


def dropBlock(field_height, field_map, x0, y0, layout):
    for (x, y) in layout:
        if 0 <= y0 + y < field_height:
            field_map[y0 + y][x0 + x] = 1
        if y0 + y < 0:
            return False
    return True


def resetMap(field_width, field_height, field_map):
    count = 0
    for y in range(field_height):
        for x in range(field_width):
            if field_map[y][x] == 1:
                field_map[y][x] = 0
                count += 1
            if count == 4:
                return


def getNewMap(block, position, direction, field_map):
    while block.direction is not direction:
        block.rotate(field_map)
    while block.position[0] > position[0]:
        block.left(field_map)
    while block.position[0] < position[0]:
        block.right(field_map)
    while not block.is_stop:
        block.down(field_map)


class QLearning(Game):
    def __init__(self):
        super(QLearning, self).__init__(sub_well, 1000)
        self.repeat_num = 200
        self.alpha = 0.2
        self.gamma = 0.8
        self.lambda_ = 0.3
        self.epsilon = 0.01
        self.key = [((s, b), (p, d)) for s in range(base**(self.field_width-1)) for b in range(7) for p in range(self.field_width) for d in range(4)]
        self.V = [0 for _ in range(len(self.key))]
        self.Q = dict(zip(self.key, self.V))
        #self.Q = np.load('QL.npy').item()

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)

    def getBlock(self, block):
        for x in range(len(Blocks_color)):
            if block.color == Blocks_color[x]:
                return x

    def getReward(self):
        temp = [0 for _ in range(self.field_width)]
        for x in range(self.field_width):
            while temp[x] < self.field_height and self.field_map[temp[x]][x] == 0:
                temp[x] += 1
        buried_holes = 0
        block = self.block_factory.cur_block
        for (x, y) in block.layout:
            i = 1
            while block.position[1]+y+i < self.field_height and self.field_map[block.position[1]+y+i][x] == 0:
                buried_holes += 1
                i += 1
        return np.var(temp)*(-2) + buried_holes*(-1)

    def getAllActions(self, block):
        actions = []
        for direction in range(len(block.layouts)):
            for x in getAllPossibleLocation(self.field_width, self.field_map, block, block.layouts[direction]):
                y = findBottomPosition(self.field_map, block, x, block.layouts[direction])
                if dropBlock(self.field_height, self.field_map, x, y, block.layouts[direction]):
                    actions.append((x, direction))
                    resetMap(self.field_width, self.field_height, self.field_map)
        return actions

    def getBestActionWithGreedy(self, block):
        block_type = self.getBlock(block)
        state = getStateIndex(self.field_width, self.field_height, self.field_map)
        actions = self.getAllActions(block)
        actions_value = {}
        for action in actions:
            actions_value[action] = self.Q[((state, block_type), action)]
        if actions_value == {}:
            return None
        elif random.random() > self.epsilon:
            return max(actions_value, key=actions_value.get)
        else:
            return list(actions_value.keys())[random.randint(0, len(actions_value)-1)]

    def getBestAction(self, block):
        block_type = self.getBlock(block)
        state = getStateIndex(self.field_width, self.field_height, self.field_map)
        actions = self.getAllActions(block)
        actions_value = {}
        for action in actions:
            actions_value[action] = self.Q[((state, block_type), action)]
        if actions_value == {}:
            return None
        return max(actions_value, key=actions_value.get)

    def train(self):
        record = []
        for i in range(1, self.repeat_num+1):
            self.initialize()
            while not self.block_factory.is_failed:
                cur_state = getStateIndex(self.field_width, self.field_height, self.field_map)
                cur_block = self.getBlock(self.block_factory.cur_block)
                cur_action = self.getBestActionWithGreedy(self.block_factory.cur_block)
                cur_index = ((cur_state, cur_block), cur_action)
                if cur_action == None: break
                getNewMap(self.block_factory.cur_block, cur_action, cur_action[1], self.field_map)
                next_state = getStateIndex(self.field_width, self.field_height, self.field_map)
                next_block = self.getBlock(self.block_factory.next_block)
                next_action = self.getBestAction(self.block_factory.next_block)
                next_index = ((next_state, next_block), next_action)
                if next_action == None: break
                self.Q[cur_index] += self.alpha*(self.getReward()+self.gamma*self.Q[next_index] - self.Q[cur_index])
                self.update()
            print("Epoch:"+str(i)+"/"+str(self.repeat_num)+"   Lines:"+ str(self.lines_num)+"   Alpha:"+str(self.alpha))
            record.append(self.lines_num)
            if i % 100 == 0:
                self.alpha *= 0.5
                np.save('QL.npy', {"V": self.V})
                np.save('record_QL.npy', {"record": record})
        np.save('QL.npy', self.Q)
        np.save('record_QL.npy', {"record": record})


class QLGame(Game):
    def __init__(self):
        super(QLGame, self).__init__(10, 20)
        self.Q = np.load('QL.npy', allow_pickle=True).item()
        self.col = 0

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)

    def getBlock(self, block):
        for x in range(len(Blocks_color)):
            if block.color == Blocks_color[x]:
                return x

    def cutFieldMap(self, position):
        new_field_map = [[0]*sub_well for _ in range(self.field_height)]
        for y in range(self.field_height):
            for x in range(sub_well):
                new_field_map[y][x] = self.field_map[y][position+x]
        return new_field_map

    def getAllActions(self, field_width, field_height, block, field_map, init_pos):
        actions = {}
        for direction in range(len(block.layouts)):
            for x in getAllPossibleLocation(field_width, field_map, block, block.layouts[direction]):
                y = findBottomPosition(field_map, block, x, block.layouts[direction])
                if dropBlock(field_height, field_map, x, y, block.layouts[direction]):
                    block_type = self.getBlock(block)
                    state = getStateIndex(field_width, field_height, field_map)
                    actions[(x + init_pos, direction)] = self.Q[((state, block_type), (x, direction))]
                    resetMap(field_width, field_height, field_map)
        return actions

    def getBestAction(self):
        actions = {}
        cur_block = Block(self.block_factory.cur_block.screen, sub_well, self.field_height, self.block_factory.cur_block.layouts, self.block_factory.cur_block.direction, self.block_factory.cur_block.color, (0, -4))
        for x in range(self.field_width - sub_well + 1):
            loc_actions = self.getAllActions(sub_well, self.field_height, cur_block, self.cutFieldMap(x), x)
            for k, v in loc_actions.items():
                if k in actions:
                    actions[k].append(v)
                else:
                    actions[k] = [v]
        for k, v in actions.items():
            actions[k] = max(v)
        return max(actions, key=actions.get) if actions != {} else None

    def start(self):
        self.initialize()
        self.initializePygame()
        while not self.block_factory.is_failed:
            self.checkEvents()
            action = self.getBestAction()
            if action == None:
                break
            getNewMap(self.block_factory.cur_block, action, action[1], self.field_map)
            self.update()
            self.draw()
        return self.lines_num



if __name__ == '__main__':
    train = QLearning()
    train.train()
    
    game = QLGame()
    game.start()
