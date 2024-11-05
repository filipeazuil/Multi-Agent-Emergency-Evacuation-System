import spade
import asyncio
from environment import Building
from agents import OccupantAgent, EmergencyResponderAgent

async def main():
    building = Building()
    
    occupant_agent_1 = OccupantAgent("occupant@localhost", "password", "Room 101", "able-bodied", "Assembly Point A")
    occupant_agent_2 = OccupantAgent("occupant@localhost", "password", "Room 101", "able-bodied", "Assembly Point B")
    occupant_agent_3 = OccupantAgent("occupant@localhost", "password", "Room 101", "disabled", "Assembly Point A")
    
    emergency_responder_agent_1 = EmergencyResponderAgent("responder@localhost", "password")

    building.register_agent(occupant_agent_1)
    building.register_agent(emergency_responder_agent_1)

    await occupant_agent_1.start(auto_register=True)
    await emergency_responder_agent_1.start(auto_register=True)
    
    try:
    	await asyncio.sleep(60)
    except asyncio.CancelledError:
    	pass
    		
    await occupant_agent_1.stop()
    await emergency_responder_agent_1.stop()

    building.simulate_evacuation()
	
if __name__ == "__main__":
	spade.run(main())	

