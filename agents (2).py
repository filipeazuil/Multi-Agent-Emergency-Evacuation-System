import spade
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio


class OccupantAgent(spade.agent.Agent):
    def __init__(self, jid, password, environment, location, mobility):
        super().__init__(jid, password)
        self.location = location  # Expected to be a Room object
        self.mobility = mobility
        self.environment = environment
        self.avoid_rooms = set()  # Keep track of rooms to avoid due to fire or earthquake

    async def setup(self):
        print(f"Occupant Agent {str(self.jid)} is ready.")
        print(f"Location: {self.location.name}, Mobility: {self.mobility}")
        self.add_behaviour(self.ReceiveInstructionsBehaviour())

    class ReceiveInstructionsBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=0.1)
            if msg:
                print(f"Received message: {msg.body}")
                if msg.body.startswith("Avoid room"):
                    room_name = msg.body.split()[-1]  # Extract room name to avoid
                    self.agent.avoid_rooms.add(room_name)
                    print(f"{self.agent.jid} will avoid room {room_name}.")
                elif msg.body == "EVACUATE":
                    await self.agent.navigate_to_exit()

    def get_next_room_towards_exit(self, target_room):
    
        neighbors = self.location.get_neighbors()
        # Filter out rooms to avoid (due to fire or earthquake)
        neighbors = [room for room in neighbors if room.name not in self.avoid_rooms]
        if not neighbors:
            print(f"No available rooms to move towards! {self.jid} is stuck.")
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

        print(f"{self.jid} is navigating from {self.location.name} to nearest exit at {nearest_exit.name}")

        # Check if the current location and exit are on the same floor
        if self.location.floor != nearest_exit.floor:
            elevator=self.environment.get_floor(self.location.floor).elevator
            if self.mobility=="disabled":
                destination=elevator
                method="elevator"
            else:
                staircase=self.environment.get_floor(self.location.floor).staircase
                dist_elev=self.location.distance_to(elevator)
                dist_stairs=self.location.distance_to(staircase)
                if dist_elev<=dist_stairs:
                    destination = elevator  
                    method="elevator"
                else:
                    destination=staircase
                    method="staircase"

            print(f"{self.jid} is moving to {destination.name} to change floors using the {method}.")
            # Navigate to the elevator or staircase first
            while self.location != destination:
                next_room = self.get_next_room_towards_exit(destination)
                await asyncio.sleep(5)
                print(f"{self.jid} moved from {self.location.name} to {next_room.name}")
                self.location = next_room
            # After reaching elevator or staircase, move to the target floor
            dest_room = self.environment.get_room(nearest_exit.floor-1,destination.coordinates[1],self.location.coordinates[2])
            self.location = dest_room
            print(f"{self.jid} is now on floor {self.location.floor} after using the {method}. Continuing to the exit.")
        while self.location != nearest_exit:
            next_room = self.get_next_room_towards_exit(nearest_exit)
            await asyncio.sleep(1)
            # Move to the next room and update location
            print(f"{self.jid} moved from {self.location.name} to {next_room.name}")
            self.location = next_room
        if self.location == nearest_exit:
            print(f"{self.jid} has arrived at the exit at {nearest_exit.name}!")


'''
class OccupantAgent(spade.agent.Agent):
    def __init__(self, jid, password, environment, location, mobility):
        super().__init__(jid, password)
        self.location = location  # Expected to be a Room object
        self.mobility = mobility
        self.environment=environment

    async def setup(self):
        print(f"Occupant Agent {str(self.jid)} is ready.")
        print(f"Location: {self.location.name}, Mobility: {self.mobility}")
        self.add_behaviour(self.ReceiveInstructionsBehaviour())

    class ReceiveInstructionsBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=0.1)
            if msg:
                print(f"Received message: {msg.body}")
                if msg.body == "EVACUATE":
                    await self.agent.navigate_to_exit()


    def get_next_room_towards_exit(self, target_room):
        """
        Selects the next room to move to, based on proximity to the target room.
        """
        # Get neighboring rooms
        neighbors = self.location.get_neighbors()
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

        print(f"{self.jid} is navigating from {self.location.name} to nearest exit at {nearest_exit.name}")

        # Check if the current location and exit are on the same floor
        if self.location.floor != nearest_exit.floor:
            elevator=self.environment.get_floor(self.location.floor).elevator
            if self.mobility=="disabled":
                destination=elevator
                method="elevator"
            else:
                staircase=self.environment.get_floor(self.location.floor).staircase
                dist_elev=self.location.distance_to(elevator)
                dist_stairs=self.location.distance_to(staircase)
                if dist_elev<=dist_stairs:
                    destination = elevator  
                    method="elevator"
                else:
                    destination=staircase
                    method="staircase"

            print(f"{self.jid} is moving to {destination.name} to change floors using the {method}.")
            # Navigate to the elevator or staircase first
            while self.location != destination:
                next_room = self.get_next_room_towards_exit(destination)
                await asyncio.sleep(5)
                print(f"{self.jid} moved from {self.location.name} to {next_room.name}")
                self.location = next_room
            # After reaching elevator or staircase, move to the target floor
            dest_room = self.environment.get_room(nearest_exit.floor-1,destination.coordinates[1],self.location.coordinates[2])
            self.location = dest_room
            print(f"{self.jid} is now on floor {self.location.floor} after using the {method}. Continuing to the exit.")
        while self.location != nearest_exit:
            next_room = self.get_next_room_towards_exit(nearest_exit)
            await asyncio.sleep(1)
            # Move to the next room and update location
            print(f"{self.jid} moved from {self.location.name} to {next_room.name}")
            self.location = next_room
        if self.location == nearest_exit:
            print(f"{self.jid} has arrived at the exit at {nearest_exit.name}!")
'''


class EmergencyResponderAgent(spade.agent.Agent):
    def __init__(self, jid, password, environment):
        super().__init__(jid, password)
        self.environment = environment  # Environment to check for events

    async def setup(self):
        print(f"Emergency Responder Agent {str(self.jid)} is ready.")
        # Adding the behavior to monitor events and send evacuation instructions
        self.add_behaviour(self.MonitorEventsBehaviour())
        self.add_behaviour(self.SendEvacuationInstructionsBehaviour())
        
    class SendEvacuationInstructionsBehaviour(CyclicBehaviour):
        async def run(self):
            occupants = ["occupant1@localhost", "occupant2@localhost", "occupant3@localhost"]
            for i in occupants:
                # Send an evacuation message to each OccupantAgent
                msg = Message(to=i)  # Replace with real occupant agent JIDs
                msg.body = "EVACUATE"  # The action or instruction for the occupant agent
                await self.send(msg)
                print(f"Sent evacuation message to {msg.to}")

            # Stop the behavior after sending the message to all occupants
            await self.agent.stop()  

    class MonitorEventsBehaviour(CyclicBehaviour):
        async def run(self):
            # Monitor the environment for any fire or earthquake events
            await asyncio.sleep(0.5)  # Check every 2 seconds (can be adjusted)
            # Check for fire in rooms
            for floor in self.agent.environment.floors:
                for row in floor.rooms:
                    for room in row:
                        if room.is_on_fire:
                            print(f"Emergency Responder detected fire in {room.name}!")
                            # Send evacuation instruction to avoid fire
                            await self.send_evacuate_instruction(room)
                            print(f"Emergency Responder is heading to {room.name} to extinguish the fire.")
                            # Move to the room and extinguish fire
                            await self.navigate_to_room(room)
                            room.is_on_fire = False
                            print(f"Fire extinguished in {room.name}.")

            # Check for earthquake damage
            for floor in self.agent.environment.floors:
                for row in floor.rooms:
                    for room in row:
                        if room.is_damaged:
                            print(f"Emergency Responder detected earthquake damage in {room.name}!")
                            # Send evacuation instruction to avoid damaged rooms
                            await self.send_evacuate_instruction(room)

        async def send_evacuate_instruction(self, room):
            # Send evacuation instruction to all occupants to avoid this room
            occupants = ["occupant1@localhost", "occupant2@localhost", "occupant3@localhost"]  # Placeholder JIDs
            for jid in occupants:
                msg = Message(to=jid)
                msg.body = f"Avoid room {room.name} due to fire or earthquake damage."
                await self.send(msg)
                print(f"Sent evacuation message to {jid} for {room.name}")

        async def navigate_to_room(self, room):
            await asyncio.sleep(2)  # Simulate time taken to reach the room


'''
class EmergencyResponderAgent(spade.agent.Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)

    async def setup(self):
        print(f"Emergency Responder Agent {str(self.jid)} is ready.")
        # Adding the behavior to send evacuation instructions
        self.add_behaviour(self.SendEvacuationInstructionsBehaviour())

    class SendEvacuationInstructionsBehaviour(CyclicBehaviour):
        async def run(self):
            occupants = ["occupant1@localhost", "occupant2@localhost", "occupant3@localhost"]
            for i in occupants:
                # Send an evacuation message to each OccupantAgent
                msg = Message(to=i)  # Replace with real occupant agent JIDs
                msg.body = "EVACUATE"  # The action or instruction for the occupant agent
                await self.send(msg)
                print(f"Sent evacuation message to {msg.to}")

            # Stop the behavior after sending the message to all occupants
            await self.agent.stop()         
'''


class BuildingManagementAgent(spade.agent.Agent):
    def __init__(self, jid, password, environment):
        super().__init__(jid, password)
        self.environment = environment  # Reference to building environment with exits, elevators, rooms, etc.
        self.alarm_triggered = False
        self.fire_detected = False
        self.earthquake_detected = False
        self.elevator_locked = True  # Elevator is locked by default during emergencies
        self.door_status = {}  # Track door status (locked/unlocked) for each area
        self.room_status = {}  # Track each room's status (e.g., fire, damage, occupancy)

    async def setup(self):
        print(f"Building Management Agent {str(self.jid)} is ready.")
        self.add_behaviour(self.ManageBuildingBehaviour())
        self.add_behaviour(self.BroadcastRoomStatusBehaviour())
        self.add_behaviour(self.ElevatorRequestHandler())
        self.add_behaviour(self.RouteOccupantsBehaviour())  # New behavior for routing occupants

    class ManageBuildingBehaviour(CyclicBehaviour):
        async def run(self):
            self.check_and_update_conditions()
            await self.control_infrastructure()
            await self.agent.pause(1)

        def check_and_update_conditions(self):
            """
            Monitor and update emergency conditions in the building.
            Detect fires, earthquakes, and other hazards; trigger alarms as necessary, and manage elevator usage.
            """
            for room in self.agent.environment.rooms:
                room.update_status()  # Check and update room status
                
                # Detect fires and initiate evacuation protocols
                if room.is_on_fire and not self.agent.alarm_triggered:
                    self.trigger_alarm("fire")
                    self.lock_elevator()
                
                # Track status of each room (on fire, damaged, or empty)
                self.agent.room_status[room.name] = (
                    "on fire" if room.is_on_fire else 
                    "damaged" if room.is_damaged else 
                    "empty" if room.is_empty else 
                    "occupied"
                )

            # Check for earthquake damage
            for room in self.agent.environment.rooms:
                if room.is_damaged and not self.agent.earthquake_detected:
                    self.trigger_alarm("earthquake")

        def trigger_alarm(self, hazard_type):
            """
            Trigger the alarm and initiate emergency protocols.
            """
            self.agent.alarm_triggered = True
            if hazard_type == "fire":
                print("ALARM TRIGGERED: Fire detected! Initiating evacuation protocols.")
                self.unlock_all_exits()  # Open all exits
                self.lock_elevator()
            elif hazard_type == "earthquake":
                self.agent.earthquake_detected = True
                print("ALARM TRIGGERED: Earthquake detected! Assessing structural integrity.")
                self.evaluate_structural_safety()
                self.lock_elevator()

        def unlock_all_exits(self):
            """
            Unlock all exits for a safe evacuation.
            """
            for door in self.agent.environment.doors:
                door.unlock()
                self.agent.door_status[door.name] = "unlocked"
                print(f"Door {door.name} unlocked for evacuation.")

        def lock_elevator(self):
            """
            Lock the elevator to prevent general occupant use during emergencies.
            """
            self.agent.elevator_locked = True
            print("Elevator locked for general use due to hazard, but it can be unlocked for disabled occupants if needed.")

        def unlock_elevator_for_disabled(self):
            """
            Temporarily unlock the elevator for disabled occupants during an evacuation.
            """
            self.agent.elevator_locked = False
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
                await self.agent.pause(5)  # Allow time for the occupant to enter
                self.agent.lock_elevator()

    class BroadcastRoomStatusBehaviour(CyclicBehaviour):
        async def run(self):
            """
            Periodically broadcast room status updates (fire, damage, occupancy) to all occupants and responders.
            """
            status_message = self.compose_room_status_message()
            
            # Broadcast to all occupants
            for occupant_jid in self.agent.environment.occupant_jids:
                msg = Message(to=occupant_jid)
                msg.body = status_message
                await self.send(msg)

            # Broadcast to all responders
            for responder_jid in self.agent.environment.responder_jids:
                msg = Message(to=responder_jid)
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

    class RouteOccupantsBehaviour(CyclicBehaviour):
        async def run(self):
            """
            Periodically send specific routing instructions to each occupant based on current room hazards.
            """
            for occupant in self.agent.environment.occupants:
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
            safe_rooms = [room for room in self.agent.environment.rooms if room.name not in self.agent.room_status or self.agent.room_status[room.name] == "empty"]
            
            # Find the nearest safe room to the occupant's location
            safe_room = min(safe_rooms, key=lambda room: occupant.location.distance_to(room))
            return safe_room.name if safe_room else "no safe rooms available"
