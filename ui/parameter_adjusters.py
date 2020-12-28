from .adjuster_types import ChoicePicker
from math import sqrt
from parameters import Parameters
from simulation import BLUE, RED
import tkinter as tk


class AdjusterContainer:
    """Contains an adjuster and a label for that adjuster"""
    def __init__(self, parent, adjuster_type, name, *args, **kwargs):
        self.name = name
        frame = tk.Frame(parent)
        tk.Label(frame, text=name + ':').pack(side='left')
        self.adjuster = adjuster_type(frame, *args, **kwargs)
        self.adjuster.pack(side='left')
        frame.pack(side='top')


class ParameterAdjusters(tk.Frame):
    """A box that contains adjuster_types that are used to adjust simulation parameters"""
    def __init__(self, root):
        self.root = root
        self.parameters = root.parameters
        super().__init__(width=200, height=root.parameters.canvas_height - 100, bd=1, relief='solid')

        self.adjuster_containers = [
            AdjusterContainer(self, ChoicePicker, 'district_size', 16,
                              get_choices=self.get_district_size_choices, after_select=self.check_grid_width_valid),
            AdjusterContainer(self, ChoicePicker, 'grid_width', 24,
                              get_choices=self.get_grid_width_choices),
            AdjusterContainer(self, ChoicePicker, 'help_party', 'blue', choices=['blue', 'red'],
                              after_select=self.confirm_help_party, result_formatter=self.help_party_result_formatter)
        ]
        self.adjusters = {ac.name: ac.adjuster for ac in self.adjuster_containers}

    def get_parameters(self):
        kwargs = {name: self.get_parameter(name) for name in self.adjusters.keys()}
        if any(parameter is None for parameter in kwargs.values()):
            return None
        return Parameters(**kwargs)

    def get_parameter(self, name):
        """Returns the parameter by name as set in this frame"""
        return self.adjusters[name].get()

    @staticmethod
    def get_district_size_choices():
        return [i*i for i in range(2, 10)]

    def check_grid_width_valid(self):
        if self.get_parameter('grid_width') not in self.get_grid_width_choices():
            self.adjusters['grid_width'].var.set('invalid')

    def get_grid_width_choices(self):
        district_width = int(sqrt(int(self.get_parameter('district_size'))))
        return [districts_per_row * district_width for districts_per_row in range(2, 15)]

    def confirm_help_party(self):
        party = self.get_parameter('help_party')
        help_party = party
        hinder_party = {'red': BLUE, 'blue': RED}[party.name]
        if self.root.parameters.help_party != help_party:  # if a change happened
            self.root.parameters.help_party = self.root.canvas.parameters.help_party = help_party
            self.root.parameters.hinder_party = self.root.canvas.parameters.hinder_party = hinder_party
            for district in self.root.canvas.districts:
                district.net_advantage *= -1

    @staticmethod
    def help_party_result_formatter(result):
        return {'blue': BLUE, 'red': RED}[result]
