import spade
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
import time


class OccupantAgent(spade.agent.Agent):
    def __init__(self, jid, password, agent_name, environment, location, mobility):
        super().__init__(jid, password)
        self.agent_name = agent_name
        self.location = location  # Expected to be a Room object
        self.mobility = mobility
        self.environment = environment
        self.avoid_rooms = set()  # Keep track of rooms to avoid due to fire or earthquake
        self.is_evacuated = False

    async def setup(self):
        print(f"Occupant Agent {self.agent_name} is ready. Location: {self.location.name}, Mobility: {self.mobility}")
        if self.mobility=="able-bodied": self.pace=2
        else: self.pace=3
        self.add_behaviour(self.ReceiveInstructionsBehaviour())

    class ReceiveInstructionsBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=0.1)
            if msg:
                if msg.body.startswith("Due to fire or earthquake damage, avoid room"):
                    room_name = msg.body.split()[-1]  # Extract room name to avoid
                    self.agent.avoid_rooms.add(room_name)

                elif msg.body.startswith("Assembly Point"):
                    print(f"{self.agent.agent_name} will redirect his route due to assembly point blocked")
                    await self.agent.redirect_route_to_exit()

                elif msg.body == "EVACUATE":
                    await self.agent.navigate_to_exit()

    def get_next_room_towards_exit(self, target_room):

        neighbors = self.location.get_neighbors()
        # Filter out rooms to avoid (due to fire or earthquake)
        neighbors = [room for room in neighbors if room.name not in self.avoid_rooms]
        if not neighbors:
            print(f"No available rooms to move towards! {self.agent_name} is stuck.")
            return None
        # Sort neighbors by distance to the target room and pick the closest
        neighbors = sorted(neighbors, key=lambda room: room.distance_to(target_room))
        return neighbors[0] if neighbors else None

    async def navigate_to_exit(self):
        exit_a = self.environment.assembly_points[0]
        exit_b = self.environment.assembly_points[1]

        # Choose the nearest exit based on a distance calculation
        exit_a_dist = self.location.distance_to(exit_a)
        exit_b_dist = self.location.distance_to(exit_b)
        nearest_exit = exit_a if exit_a_dist <= exit_b_dist else exit_b

        print(f"{self.agent_name} is navigating from {self.location.name} to nearest exit at {nearest_exit.name}")

        # Check if the current location and exit are on the same floor
        if self.location.floor != nearest_exit.floor:
            elevator = self.environment.get_floor(self.location.floor).elevator
            if self.mobility == "disabled":
                destination = elevator
                method = "elevator"
            else:
                staircase = self.environment.get_floor(self.location.floor).staircase
                dist_elev = self.location.distance_to(elevator)
                dist_stairs = self.location.distance_to(staircase)
                if dist_elev <= dist_stairs:
                    destination = elevator
                    method = "elevator"
                else:
                    destination = staircase
                    method = "staircase"

            print(f"{self.agent_name} is moving to {destination.name} to change floors using the {method}.")
            # Navigate to the elevator or staircase first
            while self.location != destination:
                next_room = self.get_next_room_towards_exit(destination)
                await asyncio.sleep(self.pace)
                print(f"{self.agent_name} moved from {self.location.name} to {next_room.name}")
                self.location = next_room
            # After reaching elevator or staircase, move to the target floor
            dest_room = self.environment.get_room(nearest_exit.floor - 1, destination.coordinates[1],
                                                  self.location.coordinates[2])
            self.location = dest_room
            await asyncio.sleep(4)
            print(f"{self.agent_name} is now on floor {self.location.floor} after using the {method}. Continuing to the exit.")
        while self.location != nearest_exit:
            next_room = self.get_next_room_towards_exit(nearest_exit)
            await asyncio.sleep(self.pace)
            # Move to the next room and update location
            print(f"{self.agent_name} moved from {self.location.name} to {next_room.name}")
            self.location = next_room
        if self.location == nearest_exit:
            print(f"{self.agent_name} has arrived at the exit at {nearest_exit.name}!")
            self.finish_time=time.time()
            self.is_evacuated=True

    async def redirect_route_to_exit(self):
        await self.navigate_to_exit()
       
    def get_is_evacuated(self):
        return self.is_evacuated

'''
_____________________________________________________________________________________________________________________

'''

class EmergencyResponderAgent(spade.agent.Agent):
    def __init__(self, jid, password, responder_name, environment, location, job):
        super().__init__(jid, password)
        self.responder_name=responder_name
        self.environment = environment  # Environment to check for events
        self.location = location
        self.job = job

    async def setup(self):
        print(f"Emergency Responder Agent {self.responder_name} is ready.")
        self.add_behaviour(self.MonitorEventsBehaviour())

    class MonitorEventsBehaviour(CyclicBehaviour):
        async def run(self):
            # Monitor the environment for any fire or earthquake events
            await asyncio.sleep(0.5)  # Check every 0.5 seconds (can be adjusted)
            # Check for fire in rooms
            if self.agent.job == "firefighter":
                for floor in self.agent.environment.floors:
                    for row in floor.rooms:
                        for room in row:
                            if room.is_on_fire and room.noted_fire==False:
                                self.agent.environment.num_fires+=1
                                print(f"{self.agent.responder_name} detected fire in {room.name}! Heading to {room.name} to extinguish the fire.")
                                room.noted_fire=True
                                # Send evacuation instruction to avoid fire
                                await self.send_evacuate_instruction(room,"fire")
                                # Move to the room and extinguish fire
                                await asyncio.sleep(3)
                                await self.agent.navigate_to_room(room)
                                room.is_on_fire = False
                                room_noted_fire=False
            elif self.agent.job == "earthquake specialist":
                # Check for earthquake damage
                for floor in self.agent.environment.floors:
                    for row in floor.rooms:
                        for room in row:
                            if room.is_damaged and room.noted_earthquake==False:
                                self.agent.environment.num_earthquakes+=1
                                room.noted_earthquake=True
                                if room in self.agent.environment.assembly_points:
                                    self.agent.environment.assembly_points.remove(room)
                                    self.agent.environment.num_fires+=1
                                    print(f"Assembly Point {room.name} blocked due to earthquake damage")
                                    await self.send_assembly_point_blocked(room)
                                else:
                                    print(f"{self.agent.responder_name} detected earthquake damage in {room.name}!")
                                    # Send evacuation instruction to avoid damaged rooms
                                    await self.send_evacuate_instruction(room,"earthquake")

        async def send_evacuate_instruction(self, room, why):
            # Send evacuation instruction to all occupants to avoid this room
            print(f"Agents will avoid room {room.name} due to {why}")
            occupants = self.agent.environment.agents.keys()
            for occupant in occupants:
                msg = Message(to=str(occupant))
                msg.body = f"Due to {why}, avoid room {room.name}"
                await self.send(msg)

        async def send_assembly_point_blocked(self, room):
            occupants = self.agent.environment.agents.keys()
            for occupant in occupants:
                msg = Message(to=str(occupant))
                msg.body = f"Assembly room {room.name} blocked due to earthquake damage."
                await self.send(msg)

    def get_next_room_towards_destination(self, target_room):

        neighbors = self.location.get_neighbors()
        # Filter out rooms to avoid (due to fire or earthquake)
        neighbors = [room for room in neighbors]
        if not neighbors:
            print(f"No available rooms to move towards! {self.responder_name} is stuck.")
            return None
        # Sort neighbors by distance to the target room and pick the closest
        neighbors = sorted(neighbors, key=lambda room: room.distance_to(target_room))
        return neighbors[0] if neighbors else None

    async def navigate_to_room(self, room):

        # Check if the current location and exit are on the same floor
        if self.location.floor != room.floor:
            elevator = self.environment.get_floor(self.location.floor).elevator
            staircase = self.environment.get_floor(self.location.floor).staircase
            dist_elev = self.location.distance_to(elevator)
            dist_stairs = self.location.distance_to(staircase)
            if dist_elev <= dist_stairs:
                destination = elevator
                method = "elevator"
            else:
                destination = staircase
                method = "staircase"
            print(f"{self.responder_name} is moving to {destination.name} to change floors using the {method}.")
            # Navigate to the elevator or staircase first
            while self.location != destination:
                next_room = self.get_next_room_towards_destination(destination)
                await asyncio.sleep(1)
                print(f"{self.responder_name} moved from {self.location.name} to {next_room.name}")
                self.location = next_room
            # After reaching elevator or staircase, move to the target floor
            dest_room = self.environment.get_room(room.floor - 1, destination.coordinates[1],
                                                  self.location.coordinates[2])
            self.location = dest_room
            await asyncio.sleep(4)
            print(
                f"{self.responder_name} is now on floor {self.location.floor} after using the {method}.")
        while self.location != room:
            next_room = self.get_next_room_towards_destination(room)
            await asyncio.sleep(1)
            # Move to the next room and update location
            print(f"{self.responder_name} moved from {self.location.name} to {next_room.name}")
            self.location = next_room
        if self.location == room:
            print(f"{self.responder_name} has arrived at {room.name}. Fire extinguished.")
            
'''
_________________________________________________________________________________________________________________
'''

class BuildingManagementAgent(spade.agent.Agent):
    def __init__(self, jid, password, environment):
        super().__init__(jid, password)
        self.environment = environment

    async def setup(self):
        print(f"Building Management Agent {str(self.jid)} is ready.")
        self.add_behaviour(self.SendEvacuationInstructionsBehaviour())
    
    class SendEvacuationInstructionsBehaviour(CyclicBehaviour):
        async def run(self):
            occupants = self.agent.environment.agents.keys()
            tasks = []
            for i in occupants:
                # Send an evacuation message to each OccupantAgent
                msg = Message(to=str(i))  # Replace with real occupant agent JIDs
                msg.body = "EVACUATE"  # The action or instruction for the occupant agent
                tasks.append(self.send(msg))
                print(f"Sent evacuation message to {msg.to}")
            await asyncio.gather(*tasks)

            # Stop the behavior after sending the message to all occupants
            await self.agent.stop()
        
