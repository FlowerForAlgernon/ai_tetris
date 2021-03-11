from enum import Enum
import pygame



class State(Enum):
    Success = 0
    Top = 1
    Middle = 2
    Bottom = 3

class Option(Enum):
    Rotate = 0
    Down = 1
    Left = 2
    Right = 3

Brick_size = 30
Blocks_layout = [
        [((0, 0), (0, 1), (0, 2), (0, 3)),  # 长条
         ((0, 1), (1, 1), (2, 1), (3, 1))],
		[((1, 0), (2, 0), (1, 1), (2, 1))], # 方块
		[((0, 1), (1, 0), (1, 1), (1, 2)),  # T型
         ((1, 0), (0, 1), (1, 1), (2, 1)),
         ((1, 0), (1, 1), (1, 2), (2, 1)),
         ((0, 1), (1, 1), (2, 1), (1, 2))],
		[((0, 0), (0, 1), (1, 1), (1, 2)),  # Z型
         ((0, 1), (1, 1), (1, 0), (2, 0))],
		[((1, 0), (1, 1), (0, 1), (0, 2)),  # S型
         ((0, 0), (1, 0), (1, 1), (2, 1))],
		[((0, 0), (1, 0), (1, 1), (1, 2)),  # J型
         ((2, 0), (2, 1), (1, 1), (0, 1)),
         ((1, 0), (1, 1), (1, 2), (2, 2)),
         ((0, 2), (0, 1), (1, 1), (2, 1))],
		[((0, 2), (1, 2), (1, 1), (1, 0)),  # L型
         ((0, 0), (0, 1), (1, 1), (2, 1)),
         ((2, 0), (1, 0), (1, 1), (1, 2)),
         ((2, 2), (2, 1), (1, 1), (0, 1))]]
Blocks_color = (
        pygame.Color(255, 0, 0),     # 长条为红色
        pygame.Color(0, 0, 255),     # 方块为蓝色
        pygame.Color(255, 255, 0),   # T型为黄色
        pygame.Color(0, 255, 255),   # Z型为青色
        pygame.Color(0, 255, 0),     # S型为绿色
        pygame.Color(255, 165, 0),   # J型为橙色
        pygame.Color(255, 181, 197)) # L型为粉色
Buttom_Blocks_color = (
        pygame.Color(255, 255, 255), # LV0为白色
        pygame.Color(255, 0, 0),     # LV1为红色
        pygame.Color(255, 255, 0),   # LV2为黄色
        pygame.Color(0, 0, 255),     # LV3为蓝色
        pygame.Color(255, 165, 0),   # LV4为橙色
        pygame.Color(255, 181, 197), # LV5为粉色
        pygame.Color(0, 255, 0),     # LV6为绿色
        pygame.Color(0, 255, 255),   # LV7为青色
        pygame.Color(160, 32, 240),  # LV8为紫色
        pygame.Color(144, 238, 144)) # LV9为浅绿
Blocks_speed = [30, 27, 21, 16, 12, 9, 8, 7, 6, 5, 4, 3, 2, 1]

Game_name = "Tetris"
Framerate = 20
Font_size = 25
