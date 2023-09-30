from mesa import Agent
from car_agent import Car


class Human(Agent):
    def __init__(self, name, model, vector=-1):
        super().__init__(name, model)
        self.name = name
        self.vec = vector  # choice([-1,1])

    def step(self):
        print("{0}={1} activated Human".format(self.name, self.pos))
        x, y = self.pos
        new_position = x+self.vec, y
        for it in self.model.grid.iter_neighbors((x, y), moore=True, include_center=False, radius=1):
            if isinstance(it, Car) and it.pos == new_position:
                return
        self.model.grid.move_agent(self, new_position)
