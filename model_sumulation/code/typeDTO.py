from enum import Enum, unique
import numpy as np

@unique
class DirectAgentRoad(Enum):
    All = 0
    Up = 1
    Down = 2
    Left = 3
    Right = 4


@unique
class TypeAgents(Enum):
    BaseRoad = 0
    LineRoadNonMen = 1
    LineRoadMen = 2
    GenCars = 3
    GenHumans = 4
    Car = 5


class BAgent:
    def __init__(self, direct=DirectAgentRoad.Down,
                 from_dir=np.array([True, True, True, True]),
                 block_dir=np.array([]),
                 type_agent=TypeAgents.BaseRoad):
        #  положение агента
        self.dir = direct
        #  направления из down,left,up,right
        self.from_dir = from_dir
        #  блокировка направления к агенту
        self.block_dir = block_dir
        #  тип агента
        self.type_agent = type_agent

    def dir_rotate90(self):
        if self.dir == DirectAgentRoad.Down:
            self.dir = DirectAgentRoad.Left
        elif self.dir == DirectAgentRoad.Left:
            self.dir = DirectAgentRoad.Up
        elif self.dir == DirectAgentRoad.Up:
            self.dir = DirectAgentRoad.Right
        elif self.dir == DirectAgentRoad.Right:
            self.dir = DirectAgentRoad.Down
        self.from_dir = np.roll(self.from_dir,1)
        self.block_dir = np.roll(self.block_dir,1)


class BaseRoadAgent(BAgent):
    def __init__(self):
        super().__init__(direct=DirectAgentRoad.Down,
                         from_dir=np.array([True, True, True, True]),
                         block_dir=np.array([]),
                         type_agent=TypeAgents.BaseRoad)

    def _dir_rotate90(self):
        super(BaseRoadAgent, self)._dir_rotate90()


class LineRoadMenAgent(BAgent):
    def __init__(self):
        super().__init__(direct=DirectAgentRoad.Down,
                         from_dir=np.array([False, False, True, False]),
                         block_dir=np.array([]),
                         type_agent=TypeAgents.LineRoadMen)

    def _dir_rotate90(self):
        super(LineRoadMenAgent, self)._dir_rotate90()


class GenCarsAgent(BAgent):
    def __init__(self):
        super().__init__(direct=DirectAgentRoad.Down,
                         from_dir=np.array([True, True, True, True]),
                         block_dir=np.array([]),
                         type_agent=TypeAgents.GenCars)

    def _dir_rotate90(self):
        super(GenCarsAgent, self)._dir_rotate90()


class GenHumansAgent(BAgent):
    def __init__(self):
        super().__init__(direct=DirectAgentRoad.Down,
                         from_dir=np.array([True, True, True, True]),
                         block_dir=np.array([]),
                         type_agent=TypeAgents.GenHumans)

    def _dir_rotate90(self):
        super(GenHumansAgent, self)._dir_rotate90()
