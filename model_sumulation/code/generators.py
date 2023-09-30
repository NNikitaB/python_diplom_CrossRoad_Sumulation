from pydantic import BaseModel
from mesa import Agent, Model
from car_agent import Car
from uuid import uuid4,UUID


class IDGen(BaseModel):
    id: int
    uuid_: UUID


stack_obj = []


class GenCar(Agent):
    def __init__(self, agent_id, model, number_car):
        super().__init__(agent_id, model)
        self.agent_id = agent_id
        self.stack_car = [model.next_id() for i in range(number_car)]
        self.uuid = uuid4()
        self.vec = -1
        self.b = 0
        self.e = 5
        self.d = 0
        self.all = 5

    def step(self):
        print("{} activated GenCar".format(self.agent_id))
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