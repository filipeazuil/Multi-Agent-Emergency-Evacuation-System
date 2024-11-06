import random

# Room class to represent each room in the building
class Room:
    def __init__(self, name):
        self.name = name  # Room ID, e.g., "Room_1"
        self.connections = []  # Rooms connected to this one

    # Method to add a connection to another room
    def add_connection(self, other_room):
        self.connections.append(other_room)
        print(f"Connection created between {self.name} and {other_room.name}")


# Floor class to represent each floor with rooms and assembly points
class Floor:
    def __init__(self, floor_number, num_rows, num_cols):
        self.floor_number = floor_number
        self.rooms = [[Room(f"Room_{floor_number}_{i * num_cols + j + 1}") for j in range(num_cols)] for i in range(num_rows)]
        
        # Designate opposite corners as assembly points on the first floor
        if floor_number == 1:
            self.assembly_points = [self.rooms[0][0], self.rooms[-1][-1]]  # Top-left and bottom-right rooms as assembly points
        else:
            self.assembly_points = []

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

    # Create room connections within each floor
    def create_floor_connections(self):
        for floor in self.floors:
            floor.create_room_connections()
        print("All room connections within floors created.")

    # Connect a room on one floor to a room on another floor via the elevator
    def connect_elevator(self, floor1_room, floor2_room):
        floor1_room.add_connection(floor2_room)
        floor2_room.add_connection(floor1_room)
        print(f"{floor1_room.name} on Floor 1 connected to {floor2_room.name} on Floor 2 via elevator.")


# Initialize the building environment
building_env = Building()

# Example: Set up the elevator to connect Room 1 on Floor 1 to Room 1 on Floor 2
floor1_room1 = building_env.floors[0].get_room(0, 0)  # Room_1_1 on Floor 1
floor2_room1 = building_env.floors[1].get_room(0, 0)  # Room_2_1 on Floor 2
building_env.connect_elevator(floor1_room1, floor2_room1)

# Print building configuration and assembly points
for floor in building_env.floors:
    print(f"\nFloor {floor.floor_number}:")
    for row in floor.rooms:
        for room in row:
            print(f"{room.name} connected to {[r.name for r in room.connections]}")
    if floor.assembly_points:
        print("Assembly Points:", [ap.name for ap in floor.assembly_points])
