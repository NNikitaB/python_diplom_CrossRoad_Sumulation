from pydantic import BaseModel
from enum import unique, IntEnum
from mesa import Agent, Model
from uuid import UUID

@unique
class TypeAgents(IntEnum):
    BaseRoad = 0
    LineRoadNonMen = 1
    LineRoadMen = 2
    GenCars = 3
    GenHumans = 4
    Car = 5


@unique
class DirectAgentRoad(IntEnum):
    All = 0
    Up = 1
    Down = 2
    Left = 3
    Right = 4


class TypeDirect(BaseModel):
    down: bool
    left: bool
    up: bool
    right: bool

    def get_arr(self):
        return [self.down, self.left, self.up, self.right]

    def roll90(self):
        """

        Rotate to right

        """
        self.down, self.left, self.up, self.right = self.right, self.down, self.left, self.up


class BAgent(Agent):
    #  положение агента
    dir: DirectAgentRoad = DirectAgentRoad.Down
    #  направления из down,left,up,right
    from_dir: TypeDirect = TypeDirect(down=True, left=True, up=True, right=True)
    #  блокировка направления к агенту
    block_dir: TypeDirect = TypeDirect(down=False, left=False, up=False, right=False)
    #  тип агента
    type_agent: TypeAgents = TypeAgents.BaseRoad


    def dir_rotate90(self):
        if self.dir == DirectAgentRoad.Down:
            self.dir = DirectAgentRoad.Left
        elif self.dir == DirectAgentRoad.Left:
            self.dir = DirectAgentRoad.Up
        elif self.dir == DirectAgentRoad.Up:
            self.dir = DirectAgentRoad.Right
        elif self.dir == DirectAgentRoad.Right:
            self.dir = DirectAgentRoad.Down
        self.from_dir.roll90()
        self.block_dir.roll90()