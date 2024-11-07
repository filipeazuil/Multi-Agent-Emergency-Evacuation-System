import spade
from spade.behaviour import CyclicBehaviour
from spade.message import Message


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

    async def navigate_to_exit(self):
        exit_a=self.environment.assembly_points[0]
        exit_b=self.environment.assembly_points[1]

        # Choose the nearest exit based on a distance calculation
        exit_a_dist = self.location.distance_to(exit_a)
        exit_b_dist = self.location.distance_to(exit_b)
        nearest_exit = exit_a if exit_a_dist <= exit_b_dist else exit_b

        print(f"{self.jid} is navigating from {self.location.name} to nearest exit at {nearest_exit.name}")

        # Move towards the exit step by step
        while self.location != nearest_exit:
            # Find the next best room to move towards the exit
            next_room = self.get_next_room_towards_exit(nearest_exit)
            if next_room:
                # Move to the next room and update location
                print(f"{self.jid} moved from {self.location.name} to {next_room.name}")
                self.location = next_room
            else:
                print(f"{self.jid} is unable to find a path to the exit!")
                break

        if self.location == nearest_exit:
            print(f"{self.jid} has arrived at the exit at {nearest_exit.name}!")
        self.location = "Exit"  # Mark as exited

    def get_next_room_towards_exit(self, target_room):
        """
        Selects the next room to move to, based on proximity to the target room.
        """
        # Get neighboring rooms
        neighbors = self.location.get_neighbors()
        # Sort neighbors by distance to the target room and pick the closest
        neighbors = sorted(neighbors, key=lambda room: room.distance_to(target_room))
        return neighbors[0] if neighbors else None



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
