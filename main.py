import spade
import asyncio
from environment import Building
from agents import OccupantAgent, EmergencyResponderAgent, BuildingManagementAgent

async def main():
    building = Building()
    #setting up the elevator
    room_003 = building.get_room(0,0,3)
    room_103 = building.get_room(1,0,3)
    room_043 = building.get_room(0,4,3)
    room_143 = building.get_room(1,4,3)
    room_343 = building.get_room(3,4,3)
    room_203 = building.get_room(2,0,3)
    room_303 = building.get_room(3,0,3)
    room_243 = building.get_room(2,4,3)
    building.connect_elevator(room_003, room_103)
    building.connect_staircase(room_043, room_143)
    building.connect_elevator(room_203, room_303)
    building.connect_staircase(room_243, room_343)
    
    occupant_agent_1 = OccupantAgent("occupant1@localhost", "password", "Agent 1" ,building, room_103, "able-bodied")
    occupant_agent_2 = OccupantAgent("occupant2@localhost", "password", "Agent 2", building, room_243, "disabled")
    occupant_agent_3 = OccupantAgent("occupant3@localhost", "password", "Agent 3" , building, room_343, "able-bodied")
    occupant_agent_4 = OccupantAgent("occupant4@localhost", "password", "Agent 4", building, room_343, "disabled")
    emergency_responder_agent_1 = EmergencyResponderAgent("responder1@localhost", "password", "Fire-fighter", building, room_203, "firefighter")
    emergency_responder_agent_2 = EmergencyResponderAgent("responder2@localhost", "password", "Earthquake Specialist", building, room_143, "earthquake specialist")
    building_management_agent = BuildingManagementAgent("management@localhost", "password", building)
   

    building.add_agent(occupant_agent_1)
    building.add_agent(occupant_agent_2)
    building.add_agent(occupant_agent_3)
    building.add_agent(occupant_agent_4)
    building.add_emergency_agent(emergency_responder_agent_1)
    building.add_emergency_agent(emergency_responder_agent_2)
    building.add_management_agent(building_management_agent)
        
    await occupant_agent_1.start(auto_register=True)
    await occupant_agent_2.start(auto_register=True)
    await occupant_agent_3.start(auto_register=True)
    await occupant_agent_4.start(auto_register=True)
    await emergency_responder_agent_1.start(auto_register=True)
    await emergency_responder_agent_2.start(auto_register=True)
    await building_management_agent.start(auto_register=True)
    
    
    while not (building.is_building_evacuated()):
        building.simulate_step()
        await asyncio.sleep(10)
        
     
    print("Every Occupant evacuated! Success!")
    building.perfomance_metrics()
    await occupant_agent_1.stop()
    await occupant_agent_2.stop()
    await occupant_agent_3.stop()
    await occupant_agent_4.stop()
    await emergency_responder_agent_1.stop()
    await emergency_responder_agent_2.stop()
    await building_management_agent.stop()
    

if __name__ == "__main__":
    asyncio.run(main())

