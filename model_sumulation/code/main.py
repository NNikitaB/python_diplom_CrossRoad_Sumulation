import json
import random
from enum import Enum, unique, IntEnum
from random import choice
import jsonpickle
import numpy as np
from mesa import Agent, Model
from mesa.time import RandomActivation, BaseScheduler
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
import os
import glob
from pydantic import BaseModel
from typing import List, Tuple

from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import floyd_warshall


@unique
class DirectAgentRoad(IntEnum):
    All = 0
    Up = 1
    Down = 2
    Left = 3
    Right = 4


@unique
class TypeAgents(IntEnum):
    BaseRoad = 0
    LineRoadNonMen = 1
    LineRoadMen = 2
    GenCars = 3
    GenHumans = 4
    Car = 5


class TypeDirect(BaseModel):
    down: bool
    left: bool
    up: bool
    right: bool

    def get_arr(self):
        return [self.down, self.left, self.up, self.right]

    def roll90(self):
        '''поворот по часовой'''
        self.down, self.left, self.up, self.right = self.right, self.down, self.left, self.up


class BAgent(BaseModel):
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


class BaseRoadAgent(BAgent):
    def __init__(self):
        super().__init__(dir=DirectAgentRoad.Down,
                         from_dir=TypeDirect(down=True, left=True, up=True, right=True),
                         block_dir=TypeDirect(down=False, left=False, up=False, right=False),
                         type_agent=TypeAgents.BaseRoad)


class LineRoadMenAgent(BAgent):
    def __init__(self):
        super().__init__(dir=DirectAgentRoad.Down,
                         from_dir=TypeDirect(down=True, left=False, up=False, right=False),
                         block_dir=TypeDirect(down=False, left=False, up=False, right=False),
                         type_agent=TypeAgents.LineRoadMen)


class GenCarsAgent(BAgent):
    def __init__(self):
        super().__init__(dir=DirectAgentRoad.Down,
                         from_dir=TypeDirect(down=True, left=True, up=True, right=True),
                         block_dir=TypeDirect(down=False, left=False, up=False, right=False),
                         type_agent=TypeAgents.GenCars)


class GenHumansAgent(BAgent):
    def __init__(self):
        super().__init__(dir=DirectAgentRoad.Down,
                         from_dir=TypeDirect(down=True, left=True, up=True, right=True),
                         block_dir=TypeDirect(down=False, left=False, up=False, right=False),
                         type_agent=TypeAgents.GenHumans)


class TypeSaveModel(BaseModel):
    name_model: str
    matrix: List[List[List[BAgent]]]
    matrix_size: tuple


# path_images = 'model_sumulation/images/png/'
#path_images = 'model_sumulation/'
tornado_path = r"/local/custom/(.*)"
path_images = 'model_sumulation/images/png/'
path_models = 'model_sumulation/models/'


class Human(Agent):
    def __init__(self, name, model,vector=-1):
        super().__init__(name, model)
        self.name = name
        self.vec = vector  # choice([-1,1])

    def step(self):
        print("{0}={1} activated Human".format(self.name, self.pos))
        x, y = self.pos
        new_position = x+self.vec, y
        for it in self.model.grid.iter_neighbors((x,y),moore=True,include_center=False,radius=1):
            if isinstance(it, Car) and it.pos == new_position:
                return
        self.model.grid.move_agent(self, new_position)


class Car(Agent):
    def __init__(self, name, model,vector=-1):
        super().__init__(name, model)
        self.name = name
        self.vec = vector  # choice([-1,1])

    def step(self):
        print("{0}={1} activated Car".format(self.name,self.pos))
        x, y = self.pos
        new_position = x, y+self.vec
        for it in self.model.grid.iter_neighbors((x,y),moore=True,include_center=False,radius=1):
            if isinstance(it, Human) and it.pos == new_position:
                return
            elif isinstance(it, Car):
                if it.pos == new_position:
                    return

        self.model.grid.move_agent(self, new_position)


class GenCar(Agent):
    def __init__(self, name, model):
        super().__init__(name, model)
        self.name = name
        self.vec = -1
        self.b = 0
        self.e = 5
        self.d = 0
        self.all = 5

    def step(self):
        print("{} activated GenCar".format(self.name))
        if self.all < 0:
            return
        if self.b<self.e:
            self.b+=1
        else:
            self.b = self.d
            a = Car(random.randint(30,10000000), self.model)
            self.model.grid.place_agent(a, self.pos)
            self.model.schedule.add(a)
            self.all -= 1
        return


class GenHumans(Agent):
    def __init__(self, name, model,):
        super().__init__(name, model)
        self.name = name
        self.vec = -1
        self.b = 0
        self.e = 10
        self.d = 0
        self.all = 5

    def step(self):
        print("{} activated GenHumans".format(self.name))
        if self.all < 0:
            return
        if self.b<self.e:
            self.b+=1
        else:
            self.b = self.d
            a = Human(random.randint(30,10000000), self.model)
            self.model.grid.place_agent(a, self.pos)
            self.model.schedule.add(a)
            self.all -= 1
        return


class Road(Agent):
    def __init__(self, name, model):
        super().__init__(name, model)
        self.name = name
        #self.len = [i for i in range(1,11)]

# дорога с пешеходным и машмнами
# изображения для фигур
# добавить карты для пешеходов и машин
# проверить
# добавить дорогу с направлением и агл дейкстры для агентов
# проверить
# добавить графический редактор и xml





class GraphMap:
    def __init__(self, sz):
        self.size = sz
        self.matr = np.zeros((sz, sz), int)

    def set_graph(self, matr):
        for i in range(self.size):
            for j in range(self.size):
                self.matr[i][j] = matr[i][j]
        graph = matr
        dist_matrix, predecessors = floyd_warshall(csgraph=graph, directed=False, return_predecessors=True)

    def get_path(self, v1, v2):
        pass


class MMdl(Model):
    def __init__(self, n_agents,size):
        super().__init__()
        # 'model_sumulation/models/road_default.json'
        #self.schedule, self.grid, self.dc = \
        #self.file_read('model_sumulation/models/road_default.json')
        with open(path_models +'road_default.json', "r") as f:
            json_raw = f.read()
            tsm = TypeSaveModel.parse_raw(json_raw)
            s, sz = tsm.matrix_size
            m = tsm.matrix
            self.schedule = BaseScheduler(self)
            self.grid = MultiGrid(sz, sz, torus=True)
            for i in range(sz):
                for j in range(sz):
                    mt = m[i][j]
                    if mt:
                       #print(mt)
                        for it in mt:
                            if it.type_agent == TypeAgents.LineRoadMen:
                                print(it.type_agent)
                                a = Road(self.next_id(), self)
                                self.schedule.add(a)
                                self.grid.place_agent(a, (i, j))
                            elif it.type_agent == TypeAgents.GenCars:
                                print('ddddddddddddddddddddd',it.type_agent)
                                a = GenCar(self.next_id(), self)
                                self.schedule.add(a)
                                self.grid.place_agent(a, (i, j))
                            elif it.type_agent == TypeAgents.GenHumans:
                                print('GenHumans',it.type_agent)
                                a = GenHumans(self.next_id(), self)
                                self.schedule.add(a)
                                self.grid.place_agent(a, (i, j))
                            elif it.type_agent == TypeAgents.Car:
                                raise NotImplementedError

            self.dc = DataCollector(model_reporters={"agent_count":
                                                         lambda m: m.schedule.get_agent_count()},
                                    agent_reporters={"name": lambda a: a.name})



    def step(self):
        self.schedule.step()
        self.dc.collect(self)

    def file_read(self,path):
        #print(os.path.dirname(__file__))
        with open(path,"r") as f:
            json_raw = f.read()
            tsm = TypeSaveModel.parse_raw(json_raw)
            s, sz = tsm.matrix_size
            m = tsm.matrix
            return self.file_init(sz, m)

    def file_init(self,size,matr):
        self.schedule = BaseScheduler(self)
        self.grid = MultiGrid(size, size, torus=True)
        for i in range(size):
            for j in range(size):
                mt = matr[i][j]
                if mt != []:
                    print(mt)
                    for it in mt:
                        if it.type_agent == TypeAgents.LineRoadMen:
                            a = Road(self.next_id(), self)
                            self.schedule.add(a)
                            self.grid.place_agent(a, (i, j))
                        elif it.type_agent == TypeAgents.GenCars:
                            a = GenCar(self.next_id(), self)
                            self.schedule.add(a)
                            self.grid.place_agent(a, (i, j))
        self.dc = DataCollector(model_reporters={"agent_count":
                                                     lambda m: m.schedule.get_agent_count()},
                                agent_reporters={"name": lambda a: a.name})
        #return schedule, grid, dc

    def file_read_error(self):
        size=20
        self.file_read()
        self.schedule = BaseScheduler(self)
        self.grid = MultiGrid(size, size, torus=True)
        n = int(size / 2)
        coords = [(n, i) for i in range(0, size, 1)]
        for i in range(size):
            a = Road(i, self)
            self.schedule.add(a)
            self.grid.place_agent(a, coords[i])
        a = GenCar(19, self)
        self.schedule.add(a)
        self.grid.place_agent(a, (n, size - 1))

        self.dc = DataCollector(model_reporters={"agent_count":
                                                     lambda m: m.schedule.get_agent_count()},
                                agent_reporters={"name": lambda a: a.name})


class MyAgent(Agent):
    def __init__(self, name, model):
        super().__init__(name, model)
        self.name = name
    def step(self):
        print("{} activated".format(self.name))

class MyModel(Model):
    def __init__(self, n_agents):
        super().__init__()
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(25, 25, torus=False)
        for i in range(n_agents):
            a = MyAgent(i, self)
            self.schedule.add(a)
            coords = (self.random.randrange(0, 25), self.random.randrange(0, 25))
            self.grid.place_agent(a, coords)
        self.dc = DataCollector(model_reporters={"agent_count":
                                                     lambda m: m.schedule.get_agent_count()},
                                agent_reporters={"name": lambda a: a.name})
    def step(self):
        self.schedule.step()
        self.dc.collect(self)

def agent_portrayal(agent):
    #rt_p = os.path.dirname(__file__)
    #for filename in glob.iglob(rt_p + '**/**', recursive=True):
    #print(rt_p)
    portrayal = {"Shape": "circle",
                    "Filled": "true",
                    "Layer": 0,
                    "Color": "black",
                    "r": 0.5}
    if isinstance(agent,Road):
        portrayal["Shape"] = path_images+"base_road.png"
        portrayal["Color"] = "black"
        portrayal["Layer"] = 0
        portrayal["r"] = 1
    elif isinstance(agent,GenCar) :
        portrayal["Shape"] = path_images+"gen_cur.png"
        portrayal["Color"] = "blue"
        portrayal["Layer"] = 0
        portrayal["r"] = 0.5
    elif isinstance(agent,GenHumans) :
        portrayal["Shape"] = path_images+"gen_human.png"
        portrayal["Color"] = "pink"
        portrayal["Layer"] = 0
        portrayal["r"] = 0.5
    elif isinstance(agent,Human) :
        portrayal["Shape"] = path_images+"human.png"
        portrayal["Color"] = "red"
        portrayal["Layer"] = 2
        portrayal["r"] = 0.2
    else:
        portrayal["Shape"] = path_images+"car.png"
        portrayal["Color"] = "red"
        portrayal["Layer"] = 2
        portrayal["r"] = 0.2

    return portrayal


#grid = CanvasGrid(agent_portrayal, 25, 25, 500, 500)
#server = ModularServer(MyModel,[grid],"My Model",{'n_agents': 10})
#server.launch()

grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500)
server = ModularServer(MMdl,[grid],"MMdl",{'n_agents': 100,'size':20})
#server.launch()

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

#Аксиомы
#Все по чем есдит авто - дорога
class Doroga():
    pass
class Bridge(Doroga):
    pass
class CrossRoad(Doroga):
    pass

# Граф строить
# И алгоритм поиска пути в графе для каждого водителя (дейкстра ли?)
# агент схема/карта/графовый путь - к которому обращаются машины
# создали обекты дороги, потом создали обект схема и сказали построить схемму с помощью дороги
#
#



# на будующее кэширование путей

#сделать нужно к концу диплома
#1 редактор
#2 запуск модели,отображение и показ


#3 подбор параметров для модели
#4 взаимодейстие нескольких перекрестков