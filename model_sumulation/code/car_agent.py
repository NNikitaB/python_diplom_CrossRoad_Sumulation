from mesa import Agent
from human_agent import Human


class Car(Agent):
    def __init__(self, name, model,id_gen =id:ID_Gen, vector=-1):
        super().__init__(name, model)
        self.name = name
        self.vec = vector  # choice([-1,1])

    def step(self):
        print("{0}={1} activated Car".format(self.name, self.pos))
        x, y = self.pos
        new_position = x, y+self.vec
        for it in self.model.grid.iter_neighbors((x, y), moore=True, include_center=False, radius=1):
            if isinstance(it, Human) and it.pos == new_position:
                return
            elif isinstance(it, Car):
                if it.pos == new_position:
                    return

        self.model.grid.move_agent(self, new_position)

