import random

# Room class to represent each room in the building
class Room:
    def __init__(self, floor_number, i,j):
        self.name = f"Room {floor_number}{i}{j}"  # Room ID, e.g., "Room_1"
        self.connections = []  # Rooms connected to this one
        self.elevator_connections = []
        self.staircase_connections = []
        self.coordinates=[floor_number,i,j]
        self.floor=floor_number
        self.is_on_fire = False  # State of fire
        self.is_damaged = False  # State of earthquake damage
        self.noted_fire=False
        self.noted_earthquake = False

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
        self.spread_fire
        
    def spread_fire(self):
    	if random.random() < 0.2: # There is 50% probability the fire will spread to closer rooms
    	    next_room=random.choice(self.connections)
    	    next_room.start_fire()
    	    print(f"Fire from room {self.name} is spreading to {next_room.name}")

    def damage_by_earthquake(self):
        self.is_damaged = True


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
        self.floors = [Floor(1, 3, 2), Floor(2, 3, 2), Floor(3,3,2), Floor(4,3,2)]  # Two floors with 3x2 room layout
        self.elevator = "Elevator"  # Simplified elevator as a connection between floors
        self.create_floor_connections()
        self.agents = {}
        self.emergency_agents = {}
        self.management_agents = {}
        self.assembly_points=[self.floors[0].get_room(0,0),self.floors[0].get_room(2,0)]

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
        if random.random() < 0.3:  # 10% chance for fire
            floor = random.choice(self.floors)
            room = random.choice(random.choice(floor.rooms))
            while room.is_on_fire==True:
            	room = random.choice(random.choice(floor.rooms))
            print(f"Fire started in {room.name}!")
            room.start_fire()

        if random.random() < 0.15:  # 5% chance for earthquake
            floor = random.choice(self.floors)
            room = random.choice(random.choice(floor.rooms))
            while room.is_damaged==True:
            	room = random.choice(random.choice(floor.rooms))
            room.damage_by_earthquake()	

    def simulate_step(self):
        # This could be a loop where agents check if events have been triggered
        self.trigger_random_event()


