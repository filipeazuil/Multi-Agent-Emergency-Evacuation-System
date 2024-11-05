class Building:
    def __init__(self):
        self.floors = 3
        self.rows = 3
        self.columns = 3
        self.structure = [[[None for _ in range(3)] for _ in range(3)] for _ in range(3)]
        self.agents = []

    def set_room(self, floor, row, column, value):
        if 0 <= floor < self.floors and 0 <= row < self.rows and 0 <= column < self.columns:
            self.structure[floor][row][column] = value
        else:
            raise IndexError("Invalid floor, row, or column index")

    def get_room(self, floor, row, column):
        if 0 <= floor < self.floors and 0 <= row < self.rows and 0 <= column < self.columns:
            return self.structure[floor][row][column]
        else:
            raise IndexError("Invalid floor, row, or column index")

    def display_building(self):
        for floor in range(self.floors):
            print(f"Floor {floor}:")
            for row in range(self.rows):
                print(self.structure[floor][row])
            print()

    def register_agent(self, agent):
        self.agents.append(agent)
        print(f"Agent {agent.jid} registered in the building.")

    def update_agent_location(self, agent, new_location):
        agent.location = new_location
        print(f"Agent {agent.jid} moved to {new_location}.")

    def simulate_evacuation(self):
        print("Starting evacuation simulation...")
        for agent in self.agents:
            if isinstance(agent, OccupantAgent):
                agent.navigate_to_exit()
            elif isinstance(agent, EmergencyResponderAgent):
                agent.evacuate()
                agent.assist_occupants()
                agent.manage_flow()
                agent.respond_to_incidents()


