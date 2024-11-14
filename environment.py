import random
import time

# Room class to represent each room in the building
class Room:
    def __init__(self, floor_number, i,j):
        self.name = f"Room {floor_number}{i}{j}"  # Room ID, e.g., "Room_1"
        self.connections = []  # Rooms connected to this one
        self.elevator_connections = []
        self.staircase_connections = []
        self.coordinates=[floor_number,i,j]
        self.light=True
        self.floor=floor_number
        self.is_on_fire = False
        self.is_damaged = False
        self.is_taken = False
        self.noted_fire=False
        self.noted_earthquake = False
        self.noted_attack = False

    # Method to add a connection to another room
    def add_connection(self, other_room):
        self.connections.append(other_room)
    
    def add_elevator_connection(self, other_room):
        self.elevator_connections.append(other_room)
    
    def add_staircase_connection(self, other_room):
        self.staircase_connections.append(other_room)
    
    def distance_to(self, other_room):
        return abs(self.coordinates[0] - other_room.coordinates[0]) + abs(self.coordinates[1] - other_room.coordinates[1]) + abs(self.coordinates[2] - other_room.coordinates[2])
    
    def get_neighbors(self):
        return self.connections

    def start_fire(self):
        self.is_on_fire = True
        self.spread_fire()
        
    def spread_fire(self):
        if random.random() < 0.2: # There is 20% probability the fire will spread to closer rooms
            next_room=random.choice(self.connections)
            next_room.start_fire()
            print(f"Fire is spreading to {next_room.name}")

    def damage_by_earthquake(self):
        if random.random()<0.5:
            self.light=False
        self.is_damaged = True
    
    def taken_by_attacker(self):
        self.is_taken = True


# Floor class to represent each floor with rooms and assembly points
class Floor:
    def __init__(self, floor_number, num_rows, num_cols):
        self.floor_number = floor_number
        self.rooms = [[Room(floor_number,i,j) for j in range(num_cols)] for i in range(num_rows)]

    # Get room by its coordinates on the floor
    def get_room(self, row, col):
        return self.rooms[row][col]

    # Method to create connections between adjacent rooms
    def create_room_connections(self):
        rows, cols = len(self.rooms), len(self.rooms[0])
        for i in range(rows):
            for j in range(cols):
                room = self.get_room(i,j)
                # Connect with room to the right
                if j < cols - 1:
                    right_room = self.rooms[i][j + 1]
                    room.add_connection(right_room)
                    right_room.add_connection(room)
                # Connect with room below
                if i < rows - 1:
                    below_room = self.rooms[i + 1][j]
                    room.add_connection(below_room)
                    below_room.add_connection(room)


# Building class to represent the entire building with floors, rooms, and an elevator
class Building:
    def __init__(self):
        self.floors = [Floor(1,5,4), Floor(2,5,4), Floor(3,5,4), Floor(4,5,4)]  # Four floors with 5x4 room layout
        self.elevator = "Elevator"  # Simplified elevator as a connection between floors
        self.create_floor_connections()
        self.agents = {}
        self.emergency_agents = {}
        self.management_agents = {}
        self.assembly_points=[self.floors[0].get_room(0,0),self.floors[0].get_room(4,0)]
        self.begin=time.time()
        self.num_fires=[0,0]
        self.num_earthquakes=[0,0]
        self.num_attacks=[0,0]
        self.responses=0

    # Create room connections within each floor
    def create_floor_connections(self):
        for floor in self.floors:
            floor.create_room_connections()
        
    def get_room(self, floor, row, col):
        return self.floors[floor].get_room(row, col)

    def get_floor(self, floor_number):
        return self.floors[floor_number-1]

    # Connect a room on one floor to a room on another floor via the elevator
    def connect_elevator(self, floor1_room, floor2_room):
        floor1_room.add_elevator_connection(floor2_room)
        floor2_room.add_elevator_connection(floor1_room)
        self.floors[floor2_room.coordinates[0]-1].elevator=floor2_room
        self.floors[floor1_room.coordinates[0]-1].elevator=floor1_room
    
    # Connect a room on one floor to a room on another floor via the elevator
    def connect_staircase(self, floor1_room, floor2_room):
        floor1_room.add_staircase_connection(floor2_room)
        floor2_room.add_staircase_connection(floor1_room)
        self.floors[floor2_room.coordinates[0]-1].staircase=floor2_room
        self.floors[floor1_room.coordinates[0]-1].staircase=floor1_room
        
    def add_agent(self, agent):
        self.agent=agent
        self.agents[self.agent.jid]=self.agent

    def add_emergency_agent(self, emergency_agent):
        self.emergency_agent=emergency_agent
        self.emergency_agents[self.emergency_agent.jid]=self.emergency_agent

    def add_management_agent(self, management_agent):
        self.management_agent=management_agent
        self.management_agents[self.management_agent.jid]=self.management_agent
    
    def trigger_random_event(self):
        # Randomly trigger a fire or earthquake
        if random.random() < 0.5:  # 50% chance for fire
            floor = random.choice(self.floors)
            room = random.choice(random.choice(floor.rooms))
            room.start_fire()

        elif random.random() < 0.3:  # 30% chance for earthquake
            floor = random.choice(self.floors)
            room = random.choice(random.choice(floor.rooms))
            room.damage_by_earthquake()	
        
        elif random.random() < 0.3:
            floor = random.choice(self.floors)
            room = random.choice(random.choice(floor.rooms))
            room.taken_by_attacker()
            

    def simulate_step(self):
        self.trigger_random_event()
        
    def is_building_evacuated(self):
        for i in self.agents.values():
            if i.is_evacuated==False:
                return False
        return True

    def get_random_room(self):
        floor = random.choice(self.floors)
        return random.choice(random.choice(floor.rooms))
       
        
    def connect_elevators(self):
        room_003 = self.get_room(0,0,3)
        room_103 = self.get_room(1,0,3)
        room_203 = self.get_room(2,0,3)
        room_303 = self.get_room(3,0,3)
        self.connect_elevator(room_003, room_103)
        self.connect_elevator(room_203, room_303)
    
    def connect_staircases(self):
        room_043 = self.get_room(0,4,3)
        room_143 = self.get_room(1,4,3)
        room_343 = self.get_room(3,4,3)
        room_243 = self.get_room(2,4,3)
        self.connect_staircase(room_243, room_343)
        self.connect_staircase(room_043, room_143)

    def perfomance_metrics(self):
        print(f"Number of Fires Extinguished / Total Fires: {self.num_fires[0]}/{self.num_fires[1]}")
        print(f"Number of Earthquakes: {self.num_earthquakes[0]}/{self.num_earthquakes[1]}")
        print(f"Number of Attacks Controlled / Total Attacks: {self.num_attacks[0]}/{self.num_attacks[1]}")
        print(f"Number of Occupant Agents Evacuated / Total Occupant Agents: {len(self.agents.keys())}/{len(self.agents.keys())}")
        time_spent_list=[]
        for i in self.agents.values():
            time_spent=i.finish_time - self.begin
            time_spent_list.append(time_spent)
            print(f"Agent {i.agent_name} took {time_spent} to evacuate")
        total_time=max(time_spent_list)
        print(f"Total Evacuation Time: {total_time}")
        #print(f"Number of problems solved by Emergency Responders: {self.responses}")
    	#print(f"Average Response Time of Emergency Responders: {avg}")
