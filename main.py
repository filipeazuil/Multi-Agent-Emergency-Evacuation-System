import spade
import asyncio
from environment import Building
from agents import OccupantAgent, EmergencyResponderAgent

async def main():
    building = Building()
    #setting up the elevator
    room_000 = building.get_room(0,0,0)
    room_100 = building.get_room(1,0,0)
    room_021 = building.get_room(0,2,1)
    room_121 = building.get_room(1,2,1)
    room_321 = building.get_room(3,2,1)
    room_200 = building.get_room(2,0,0)
    room_300 = building.get_room(3,0,0)
    room_221 = building.get_room(2,2,1)
    building.connect_elevator(room_000, room_100)
    building.connect_staircase(room_021, room_121)
    building.connect_elevator(room_200, room_300)
    building.connect_staircase(room_221, room_321)
    
    occupant_agent_1 = OccupantAgent("occupant1@localhost", "password", building, room_121, "able-bodied")
    occupant_agent_2 = OccupantAgent("occupant2@localhost", "password", building, room_000, "disabled")
    occupant_agent_3 = OccupantAgent("occupant3@localhost", "password", building, room_321, "able-bodied")
    occupant_agent_4 = OccupantAgent("occupant4@localhost", "password", building, room_100, "disabled")
    emergency_responder_agent_1 = EmergencyResponderAgent("responder1@localhost", "password", building, room_000, "firefighter", True)
    emergency_responder_agent_2 = EmergencyResponderAgent("responder2@localhost", "password", building, room_121, "earthquake specialist", False)
   

    building.add_agent(occupant_agent_1)
    building.add_agent(occupant_agent_2)
    building.add_agent(occupant_agent_3)
    building.add_agent(occupant_agent_4)
    building.add_emergency_agent(emergency_responder_agent_1)
    building.add_emergency_agent(emergency_responder_agent_2)
        
    await occupant_agent_1.start(auto_register=True)
    await occupant_agent_2.start(auto_register=True)
    await occupant_agent_3.start(auto_register=True)
    await occupant_agent_4.start(auto_register=True)
    await emergency_responder_agent_1.start(auto_register=True)
    await emergency_responder_agent_2.start(auto_register=True)
    
    
    while not (occupant_agent_1.is_evacuated and occupant_agent_2.is_evacuated and occupant_agent_3.is_evacuated and occupant_agent_4.is_evacuated):
        building.simulate_step()
        await asyncio.sleep(1)
    print("Every Occupant evacuated! Success!")
    await occupant_agent_1.stop()
    await occupant_agent_2.stop()
    await occupant_agent_3.stop()
    await occupant_agent_4.stop()
    await emergency_responder_agent_1.stop()
    await emergency_responder_agent_2.stop()
	
if __name__ == "__main__":
	asyncio.run(main())	

