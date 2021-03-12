# 功能
该项目分别使用 Pierre Dellacheric 算法和 Q-learning 算法实现俄罗斯方块游戏智能算法。在 Pierre Dellacheric 算法中通过经验公式，遍历当前方块所有放置情况的分数并选择其最大者；在 Q-learning 算法中先通过剪枝将状态空间简化至表格型强化学习能够接受的范围，再使用 Q-learning 算法进行训练。

该项目实现的俄罗斯方块游戏采用通用标准，具体为如下三项
+ 俄罗斯方块游戏区域大小为 10×20

+ 俄罗斯方块有7种不同形状的方块，如下图所示

![tetris](https://github.com/FlowerForAlgernon/ai_tetris/blob/main/pic/tetris.png)

+ 选择下一个方块的策略为 7-bag 策略而非完全的随机选择。所谓的 7-bag 策略是指将7个形状不同的方块放到一个 bag 中，打乱 bag 中方块的顺序后再每次从中选择一个方块。当一个 bag 中所有方块都被选择时再建立另一个 bag。这样使得两个相同形状的方块最多只会相隔12个方块

# 使用
+ 运行游戏：
```shell
python game.py
```

+ 使用 Pierre Dellacheric 算法运行游戏：
```shell
python PierreDellacherie.py
```

+ 使用 Q-learning 算法运行游戏：
```shell
python QLearning.py
```
