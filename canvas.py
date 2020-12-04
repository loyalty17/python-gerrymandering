from district import District
from math import ceil, sqrt
from parties import BLUE, RED
from person import Person
from random import random
from swap_manager import SwapManager
import tkinter as tk


class Canvas(tk.Canvas):
    """Manages people, districts, and swapping, subclass of tkinter Canvas"""

    def __init__(self, root, parameters):
        self.root = root
        self.parameters = parameters
        super().__init__(width=parameters.width, height=parameters.height)
        self.pack()

        self.running = False
        self.swap_manager = SwapManager(self)

        self.line_id_state_map = {}
        self.people_grid = []
        self.generate_people()

        self.districts = []
        self.generate_districts()

        self.run()

        self.bind('<Button-1>', self.left_click)
        self.bind('<Button-2>', self.middle_click)
        self.bind('<Button-3>', self.right_click)

    def run(self):
        self.running = True
        self.swap_dispatch()

    def pause(self):
        self.running = False

    def rerun_simulation(self):
        if self.parameters.score_list is not None:  # add score to list for tests
            score = self.get_score()[self.parameters.advantage.name]
            self.parameters.score_list.append(score)

        if self.root.simulation_number == self.parameters.num_simulations:
            self.root.quit()
        self.running = False
        self.pack_forget()
        self.root.simulation_number += 1
        self.root.canvas = Canvas(self.root, self.parameters)

    def left_click(self, _):
        self.run()

    def middle_click(self, _):
        if not self.districts:  # if no districts
            self.generate_districts()

    def right_click(self, _):
        self.pause()

    def swap_dispatch(self):
        """Called every MS_BETWEEN_DRAWS (while running), calls do_swap multiple times if needed, draws once"""
        if not self.running:
            return

        if self.parameters.num_swaps_per_draw == 1:
            self.swap_manager.do_swap()  # draws in do_swap if 1 swap per draw
        else:  # if multiple swaps per draw
            to_draw = set()
            for _ in range(self.parameters.num_swaps_per_draw):
                self.swap_manager.do_swap()
                to_draw.add(self.swap_manager.district1)
                to_draw.add(self.swap_manager.district2)
            for district in to_draw:
                district.draw()

        self.root.after(self.parameters.ms_between_draws, self.swap_dispatch)

    def get_score(self):
        """Return a dict of format {party: num_districts_won, ...}"""
        score = {'blue': 0, 'red': 0, 'tie': 0}
        for district in self.districts:
            score[district.get_winner().name] += 1
        return score

    def generate_people(self):
        """Create grid of people with randomized parties"""
        # make sure people's parties are random but same number of people for each
        parties = [RED, BLUE] * ceil(self.parameters.grid_width ** 2 / 2)
        parties = sorted(parties, key=lambda _: random())  # more efficient than random.shuffle

        square_width = self.parameters.width / self.parameters.grid_width
        for y in range(0, self.parameters.grid_width):
            row = []
            for x in range(0, self.parameters.grid_width):
                person1 = (x * square_width, y * square_width)
                person2 = ((x + 1) * square_width, (y + 1) * square_width)
                party = parties[x + y * self.parameters.grid_width]
                row.append(Person(self, person1, person2, x, y, party=party))
            self.people_grid.append(row)
        for row in self.people_grid:
            for person in row:
                person.secondary_init()

    def generate_districts(self):
        """Generate square districts, of size DISTRICT_SIZE.

        We know this can fit because of assertions in constants.py"""
        district_width = sqrt(self.parameters.district_size)
        for grid_x in range(int(sqrt(self.parameters.num_districts))):
            for grid_y in range(int(sqrt(self.parameters.num_districts))):
                grid_person1 = grid_x * district_width, grid_y * district_width
                grid_person2 = (grid_x + 1) * district_width, (grid_y + 1) * district_width
                self.districts.append(District(self, grid_person1, grid_person2))