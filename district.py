from collections import defaultdict
from parties import TIE


class District:
    def __init__(self, canvas, p1, p2):
        self.canvas = canvas

        (self.x1, self.y1), (self.x2, self.y2) = p1, p2  # in grid coordinates
        self.net_advantage = 0  # ADVANTAGE score - DISADVANTAGE score
        self.people = []
        self.get_people()
        # self.color = '#' + ''.join(choice(list('0123456789abcdef')) for _ in range(6))  # random color
        self.draw()

    def __repr__(self):
        return f'District that contains a person at {self.people[0].x, self.people[0].y} ' \
               f'won by {self.get_winner()} with +{abs(self.net_advantage)} people margin'

    def get_winner(self):
        """Get whichever party has a majority of people, or a tie"""
        if self.net_advantage == 0:
            return TIE
        return self.canvas.parameters.advantage if self.net_advantage > 0 else self.canvas.parameters.advantage.opponent

    def get_people(self):
        """Used only on initialization, for filling self.people list, setting up people, and setting score"""
        for grid_y in range(int(self.y1), int(self.y2)):
            for grid_x in range(int(self.x1), int(self.x2)):
                person = self.canvas.people_grid[grid_y][grid_x]

                self.people.append(person)
                person.district = self
                self.net_advantage += 1 if person.party == self.canvas.parameters.advantage else -1

    def draw(self):
        """Draw the outline and shading of the district"""
        # outline
        line_ids = set()
        line_id_occurrence_map = defaultdict(int)
        for person in self.people:
            for line_id in person.edge_ids:
                line_ids.add(line_id)
                line_id_occurrence_map[line_id] += 1
        for line_id in line_ids:
            # hide if not on edge of district (repeated)
            state = 'hidden' if line_id_occurrence_map[line_id] > 1 else 'normal'
            if self.canvas.line_id_state_map[line_id] != state:
                self.canvas.itemconfig(line_id, state=state)
                self.canvas.line_id_state_map[line_id] = state

        # fill
        color = self.get_winner().color
        for person in self.people:
            if person.outer_color != color:
                self.canvas.itemconfig(person.outer_id, fill=color)
                person.outer_color = color
