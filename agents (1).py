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
        self.environment = environment  # Reference to building environment with exits, elevators, rooms, etc.
        self.alarm_triggered = False
        self.elevator_locked = False  # Elevator is locked by default during emergencies
        self.room_status = {}  # Track each room's status (e.g., fire, damage, occupancy)

    async def setup(self):
        print(f"Building Management Agent {str(self.jid)} is ready.")
        self.add_behaviour(self.ManageBuildingBehaviour())
        self.add_behaviour(self.BroadcastRoomStatusBehaviour())
        self.add_behaviour(self.ElevatorRequestHandler())
        self.add_behaviour(self.RouteOccupantsBehaviour())  

    class ManageBuildingBehaviour(CyclicBehaviour):
        async def run(self):
            # Periodically check building conditions
            self.check_and_update_conditions()
            await self.agent.pause(1)

        def check_and_update_conditions(self):
            """
            Monitor and update emergency conditions in the building.
            Detect fires, earthquakes, and other hazards; trigger alarms as necessary, and manage elevator usage.
            Update each room's status as "on fire", "damaged", or "clear".
            """
            
            for floor in self.environment.floors:
                for row in floor.rooms:
                    for room in row:
                        # Update room status based on its current state
                        if room.is_on_fire:
                            self.room_status[room.name] = "on fire"
                            # Trigger alarm for fire if not already done
                            if not self.alarm_triggered:
                                self.trigger_alarm("fire")
                        
                        elif room.is_damaged:
                            self.room_status[room.name] = "damaged"
                            # Trigger alarm for earthquake if not already done
                            if not self.alarm_triggered:
                                self.trigger_alarm("earthquake")
                        
                        else:
                            # Mark the room as clear if there are no hazards
                            self.room_status[room.name] = "clear"

        def trigger_alarm(self, hazard_type):
            """
            Trigger the alarm and initiate emergency protocols.
            """
            self.alarm_triggered = True
            if hazard_type == "fire":
                print("ALARM TRIGGERED: Fire detected! Initiating evacuation protocols.")
                
            elif hazard_type == "earthquake":
                print("ALARM TRIGGERED: Earthquake detected! Locking elevator and assessing structure.")
            
            self.unlock_safe_exits()
            self.lock_elevator()
            # lock das nao safe exits (preciso verificar se tem alguem la dentro)

        def unlock_safe_exits(self):
            """
            Unlock only safe exits for a safe evacuation and lock unsafe exits if they are empty.
            """
            for assembly_point in self.environment.assembly_points:
                if not assembly_point.is_damaged and not assembly_point.is_on_fire:
                    # Unlock the exit if it’s safe
                    assembly_point.unlock()
                    print(f"Assembly Point {assembly_point.name} unlocked for evacuation.")
                else:
                    # Check if the unsafe assembly point is empty before locking it
                    is_occupied = any(
                        agent.location == assembly_point
                        for agent in self.environment.agents.values()
                    )

                    if not is_occupied:
                        assembly_point.lock()
                        print(f"Unsafe Assembly Point {assembly_point.name} is empty and locked.")
                    else:
                        print(f"Unsafe Assembly Point {assembly_point.name} remains unlocked due to occupancy.")


        def lock_elevator(self):
            """
            Lock the elevator to prevent general occupant use during emergencies.
            """
            self.elevator_locked = True
            print("Elevator locked for general use due to hazard, but it can be unlocked for disabled occupants if needed.")

        def unlock_elevator_for_disabled(self):
            """
            Temporarily unlock the elevator for disabled occupants during an evacuation.
            """
            self.elevator_locked = False
            print("Elevator temporarily unlocked for disabled occupant evacuation.")

    class ElevatorRequestHandler(CyclicBehaviour):
        async def run(self):
            """
            Listen for elevator requests from disabled occupants and unlock the elevator if a request is received.
            """
            msg = await self.receive(timeout=1)
            if msg and msg.body == "REQUEST_ELEVATOR_ACCESS":
                # Temporarily unlock the elevator for the disabled occupant
                self.agent.unlock_elevator_for_disabled()
                
                # Send a confirmation message to the requesting occupant
                confirmation_msg = Message(to=str(msg.sender))
                confirmation_msg.body = "ELEVATOR_ACCESS_GRANTED"
                await self.send(confirmation_msg)
                print(f"Elevator access granted for {msg.sender}.")
                
                # Re-lock the elevator after a short delay
                await asyncio.sleep(5)
                self.agent.lock_elevator()

    class BroadcastRoomStatusBehaviour(CyclicBehaviour):
        async def run(self):
            """
            Periodically broadcast room status updates (fire, damage, occupancy) to all occupants and responders.
            """
            status_message = self.compose_room_status_message()
            
            # Broadcast to all occupants
            for occupant_jid in self.agent.environment.agents.keys():
                msg = Message(to=str(occupant_jid))
                msg.body = status_message
                await self.send(msg)

            # Broadcast to all responders
            for responder_jid in self.agent.environment.emergency_agents.keys():
                msg = Message(to=str(responder_jid))
                msg.body = status_message
                await self.send(msg)

            await self.agent.pause(10)  # Send updates every 10 seconds

        def compose_room_status_message(self):
            """
            Create a message summarizing the current status of each room.
            """
            status_message = "Room Status Update:\n"
            for room_name, status in self.agent.room_status.items():
                status_message += f"{room_name}: {status}\n"
            return status_message.strip()

    class RouteOccupantsBehaviour(CyclicBehaviour): #nao sei se e suposto fazer isto
        async def run(self):
            """
            Periodically send specific routing instructions to each occupant based on current room hazards.
            """
            for occupant in self.agent.environment.agents.values():
                # Determine the safest exit or room based on the current conditions
                safe_room = self.find_safest_route(occupant)
                
                # Send the occupant the specific room to proceed to
                msg = Message(to=occupant.jid)
                msg.body = f"Proceed to {safe_room} for safe evacuation."
                await self.send(msg)
                print(f"Sent routing instruction to {occupant.jid}: Proceed to {safe_room}")

            await self.agent.pause(10)  # Re-evaluate routes every 10 seconds

        def find_safest_route(self, occupant):
            """
            Calculate the safest route or exit for an occupant based on the current room conditions.
            """
            # Example logic: Filter out rooms that are on fire or damaged
            safe_rooms = [room for floor in self.agent.environment.floors 
                          for row in floor.rooms 
                          for room in row 
                          if room.name not in self.agent.room_status or self.agent.room_status[room.name] == "clear"]
            
            # Find the nearest safe room to the occupant's location
            safe_room = min(safe_rooms, key=lambda room: occupant.location.distance_to(room), default=None)
            return safe_room.name if safe_room else "no safe rooms available"


        
