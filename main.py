import spade
import asyncio
from environment import Building
from agents import OccupantAgent, EmergencyResponderAgent

async def main():
    building = Building()
    #setting up the elevator
    room_000 = building.get_room(0,0,0)
    room_100 = building.get_room(1,0,0)
    building.connect_elevator(room_000, room_100)
    
    occupant_agent_1 = OccupantAgent("occupant1@localhost", "password", building, room_100, "able-bodied")
    occupant_agent_2 = OccupantAgent("occupant2@localhost", "password", building, room_000, "able-bodied")
    occupant_agent_3 = OccupantAgent("occupant3@localhost", "password", building, room_100, "disabled")
    
    emergency_responder_agent_1 = EmergencyResponderAgent("responder@localhost", "password")

    building.add_agent(occupant_agent_1)
    building.add_agent(occupant_agent_2)
    building.add_agent(occupant_agent_3)
    building.add_emergency_agent(emergency_responder_agent_1)

    await occupant_agent_1.start(auto_register=True)
    await occupant_agent_2.start(auto_register=True)
    await occupant_agent_3.start(auto_register=True)
    await emergency_responder_agent_1.start(auto_register=True)
    
    try:
    	await asyncio.sleep(10)
    except asyncio.CancelledError:
    	pass
    		
    await occupant_agent_1.stop()
    await occupant_agent_2.stop()
    await occupant_agent_3.stop()
    await emergency_responder_agent_1.stop()
	
if __name__ == "__main__":
	spade.run(main())	

