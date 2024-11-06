import spade
from spade.behaviour import CyclicBehaviour
from spade.message import Message


class OccupantAgent(spade.agent.Agent):
    def __init__(self, jid, password, location, mobility):
        super().__init__(jid, password)
        self.location = location
        self.mobility = mobility

    async def setup(self):
        print(f"Occupant Agent {str(self.jid)} is ready.")
        print(f"Location: {self.location}, Mobility: {self.mobility}")
        # Adding the behavior to listen for incoming messages from the EmergencyResponderAgent
        self.add_behaviour(self.ReceiveInstructionsBehaviour())

    class ReceiveInstructionsBehaviour(CyclicBehaviour):
        async def run(self):
            # Wait for the message from the EmergencyResponderAgent
            msg = await self.receive(timeout=0.1)  # Wait for a message, with a timeout of 10 seconds
            if msg:
                print(f"Received message: {msg.body}")
                if msg.body == "EVACUATE":
                    # If the message instructs to evacuate, execute the navigation method
                    await self.agent.navigate_to_exit()

    async def navigate_to_exit(self):
        print(f"Navigating to the nearest exit from location {self.location}...")
        # Implement navigation logic here (this is a simple print for now)
        self.location = "Exit"  # Assume they reach the exit
        print(f"Occupant {self.jid} has arrived at the exit.")


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
