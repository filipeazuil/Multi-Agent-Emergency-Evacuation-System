# Room class to represent each room in the building
class Room:
    def __init__(self, floor_number, i,j):
        self.name = f"Room {floor_number}{i}{j}"  # Room ID, e.g., "Room_1"
        self.connections = []  # Rooms connected to this one
        self.coordinates=[floor_number,i,j]

    # Method to add a connection to another room
    def add_connection(self, other_room):
        self.connections.append(other_room)
    
    def distance_to(self, other_room):
    	return abs(self.coordinates[0] - other_room.coordinates[0]) + abs(self.coordinates[1] - other_room.coordinates[1]) + abs(self.coordinates[2] - other_room.coordinates[2])
    
    def get_neighbors(self):
    	return self.connections


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
                room = self.rooms[i][j]
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
        self.floors = [Floor(1, 3, 2), Floor(2, 3, 2)]  # Two floors with 3x2 room layout
        self.elevator = "Elevator"  # Simplified elevator as a connection between floors
        self.create_floor_connections()
        self.agents = {}
        self.emergency_agents = {}
        self.management_agents = {}
        self.assembly_points=[self.floors[0].get_room(0,0),self.floors[0].get_room(2,1)]

    # Create room connections within each floor
    def create_floor_connections(self):
        for floor in self.floors:
            floor.create_room_connections()
        
    def get_room(self, floor, row, col):
    	return self.floors[floor-1].get_room(row, col)

    # Connect a room on one floor to a room on another floor via the elevator
    def connect_elevator(self, floor1_room, floor2_room):
        floor1_room.add_connection(floor2_room)
        floor2_room.add_connection(floor1_room)
        
    def add_agent(self, agent):
    	self.agent=agent
    	self.agents[self.agent.jid]=self.agent
    	
    def add_emergency_agent(self, emergency_agent):
    	self.emergency_agent=emergency_agent
    	self.emergency_agents[self.emergency_agent.jid]=self.emergency_agent
    	
    def add_management_agent(self, management_agent):
    	self.management_agent=management_agent
    	self.management_agents[self.management_agent.jid]=self.management_agent

