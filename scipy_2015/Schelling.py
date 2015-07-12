'''
Schelling Segregation Model
=========================================

A simple implementation of a Schelling segregation model.

This version demonstrates the ASCII renderer.
To use, run this code from the command line, e.g.
    $ ipython -i Schelling.py

viz is the visualization wrapper around
To print the current state of the model:
    viz.render()

To advance the model by one step and print the new state:
    viz.step()

To advance the model by e.g. 10 steps and print the new state:
    viz.step_forward(10)

'''

from __future__ import division  # For Python 2.x compatibility

import random

from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector

from mesa.visualization.TextVisualization import (TextData, TextGrid,
    TextVisualization)

X = 0
Y = 1


class SchellingModel(Model):
    '''
    Model class for the Schelling segregation model.
    '''

    def __init__(self, height, width, density, minority_pc, homophily):
        '''
        '''

        self.height = height
        self.width = width
        self.density = density
        self.minority_pc = minority_pc
        self.homophily = homophily

        self.schedule = RandomActivation(self)
        self.grid = SingleGrid(height, width, torus=True)

        self.happy = 0
        self.total_agents = 0
        self.datacollector = DataCollector(
            {"unhappy": lambda m: m.total_agents - m.happy},
            # For testing purposes, agent's individual x and y
            {"x": lambda a: a.pos[X], "y": lambda a: a.pos[Y]})

        self.running = True

        # Set up agents
        # We use a grid iterator that returns
        # the coordinates of a cell as well as
        # its contents. (coord_iter)
        for cell, x, y in self.grid.coord_iter():
            if random.random() < self.density:
                if random.random() < self.minority_pc:
                    agent_type = 1
                else:
                    agent_type = 0

                agent = SchellingAgent(self.total_agents, agent_type)
                self.grid.position_agent(agent, x, y)
                self.schedule.add(agent)
                self.total_agents += 1

    def step(self):
        '''
        Run one step of the model. If All agents are happy, halt the model.
        '''
        self.happy = 0  # Reset counter of happy agents
        self.schedule.step()
        self.datacollector.collect(self)

        if self.happy == self.total_agents:
            self.running = False


class SchellingAgent(Agent):
    '''
    Schelling segregation agent
    '''
    def __init__(self, coords, agent_type):
        '''
         Create a new Schelling agent.

         Args:
            unique_id: Unique identifier for the agent.
            x, y: Agent initial location.
            agent_type: Indicator for the agent's type (minority=1, majority=0)
        '''
        self.unique_id = coords
        self.pos = coords
        self.type = agent_type

    def step(self, model):
        similar = 0
        for neighbor in model.grid.neighbor_iter(self.pos):
            if neighbor.type == self.type:
                similar += 1

        # If unhappy, move:
        if similar < model.homophily:
            model.grid.move_to_empty(self)
        else:
            model.happy += 1


class SchellingTextVisualization(TextVisualization):
    '''
    ASCII visualization for schelling model
    '''

    def __init__(self, model):
        '''
        Create new Schelling ASCII visualization.
        '''
        self.model = model

        grid_viz = TextGrid(self.model.grid, self.ascii_agent)
        happy_viz = TextData(self.model, 'happy')
        self.elements = [grid_viz, happy_viz]

    @staticmethod
    def ascii_agent(a):
        '''
        Minority agents are X, Majority are O.
        '''
        if a.type == 0:
            return 'O'
        if a.type == 1:
            return '#'

if __name__ == "__main__":
    model = SchellingModel(10, 10, 0.85, 0.2, 3)
    viz = SchellingTextVisualization(model)

