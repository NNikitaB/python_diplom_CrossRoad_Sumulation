import random
from enum import Enum, unique
from random import choice
import jsonpickle
from mesa import Agent, Model
from mesa.time import RandomActivation, BaseScheduler
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

path_images = ''



class Car(Agent):
    def __init__(self, name, model,vector=-1):
        super().__init__(name, model)
        self.name = name
        self.vec = vector  # choice([-1,1])
    def step(self):
        print("{0}={1} activated GenCar".format(self.name,self.pos))
        x, y = self.pos
        y += self.vec
        new_position = x, y
        self.model.grid.move_agent(self, new_position)


class GenCar(Agent):
    def __init__(self, name, model):
        super().__init__(name, model)
        self.name = name
        self.vec = -1
        self.b = 0
        self.e = 5
        self.d = 0
    def step(self):
        print("{} activated GenCar".format(self.name))
        if self.b<self.e:
            self.b+=1
        else:
            self.b = self.d
            a = Car(random.randint(30,100000), self.model)
            self.model.grid.place_agent(a, self.pos)
            self.model.schedule.add(a)
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


@unique
class TypeAgents(Enum):
    BaseRoad = 0
    LineRoadNonMen = 1
    LineRoadMen = 2



class MMdl(Model):
    def __init__(self, n_agents,size):
        super().__init__()
        self.schedule = BaseScheduler(self)
        self.grid = MultiGrid(size, size, torus=True)
        n = int(size / 2)
        coords = [ (n,i)for i in range(0, size, 1)]
        for i in range(size):
            a = Road(i, self)
            self.schedule.add(a)
            self.grid.place_agent(a, coords[i])
        a = GenCar(19, self)
        self.schedule.add(a)
        self.grid.place_agent(a, (n, size-1))


        self.dc = DataCollector(model_reporters={"agent_count":
                                                     lambda m: m.schedule.get_agent_count()},
                                agent_reporters={"name": lambda a: a.name})
    def step(self):
        self.schedule.step()
        self.dc.collect(self)




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
    portrayal = {"Shape": "circle",
                    "Filled": "true",
                    "Layer": 0,
                    "Color": "black",
                    "r": 0.5}
    if agent.unique_id < 19:
        portrayal["Shape"] = path_images+"base_road.png"
        portrayal["Color"] = "black"
        portrayal["Layer"] = 0
        portrayal["r"] = 1
    elif agent.unique_id == 19:
        portrayal["Shape"] = path_images+"gen_cur.png"
        portrayal["Color"] = "blue"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.5
    else:
        portrayal["Shape"] = path_images+"car.png"
        portrayal["Color"] = "red"
        portrayal["Layer"] = 2
        portrayal["r"] = 0.2

    return portrayal


#grid = CanvasGrid(agent_portrayal, 25, 25, 500, 500)
#server = ModularServer(MyModel,[grid],"My Model",{'n_agents': 10})
#server.launch()

grid = CanvasGrid(agent_portrayal, 16, 16, 500, 500)
server = ModularServer(MMdl,[grid],"MMdl",{'n_agents': 100,'size':16})
server.launch()

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