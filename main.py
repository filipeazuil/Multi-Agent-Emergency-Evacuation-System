import spade
import asyncio
from environment import Building
from agents import OccupantAgent, EmergencyResponderAgent, BuildingManagementAgent

async def main():
    building = Building()
    building.connect_elevators()
    building.connect_staircases()
    
    occupant_agent_1 = OccupantAgent("occupant1@localhost", "password", "Agent 1" ,building, "able-bodied")
    occupant_agent_2 = OccupantAgent("occupant2@localhost", "password", "Agent 2", building, "disabled")
    occupant_agent_3 = OccupantAgent("occupant3@localhost", "password", "Agent 3" , building, "able-bodied")
    occupant_agent_4 = OccupantAgent("occupant4@localhost", "password", "Agent 4", building, "disabled")
    emergency_responder_agent_1 = EmergencyResponderAgent("responder1@localhost", "password", "Fire-fighter", building, "firefighter")
    emergency_responder_agent_2 = EmergencyResponderAgent("responder2@localhost", "password", "Rescue Worker", building, "Rescue Worker")
    emergency_responder_agent_3 = EmergencyResponderAgent("responder3@localhost", "password", "Paramedic", building, "Paramedic")
    emergency_responder_agent_4 = EmergencyResponderAgent("responder4@localhost", "password", "Security Officer", building, "Security Officer")
    building_management_agent = BuildingManagementAgent("management@localhost", "password", building, "Central")
   

    building.add_agent(occupant_agent_1)
    building.add_agent(occupant_agent_2)
    building.add_agent(occupant_agent_3)
    building.add_agent(occupant_agent_4)
    building.add_emergency_agent(emergency_responder_agent_1)
    building.add_emergency_agent(emergency_responder_agent_2)
    building.add_emergency_agent(emergency_responder_agent_3)
    building.add_emergency_agent(emergency_responder_agent_4)
    building.add_management_agent(building_management_agent)
        
    await occupant_agent_1.start(auto_register=True)
    await occupant_agent_2.start(auto_register=True)
    await occupant_agent_3.start(auto_register=True)
    await occupant_agent_4.start(auto_register=True)
    await emergency_responder_agent_1.start(auto_register=True)
    await emergency_responder_agent_2.start(auto_register=True)
    await emergency_responder_agent_3.start(auto_register=True)
    await emergency_responder_agent_4.start(auto_register=True)
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
    await emergency_responder_agent_3.stop()
    await emergency_responder_agent_4.stop()
    await building_management_agent.stop()
    

if __name__ == "__main__":
    asyncio.run(main())

