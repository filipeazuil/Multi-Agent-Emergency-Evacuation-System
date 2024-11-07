class Building:
    def __init__(self):
    
        self.floors = 2
        self.rows = 2
        self.columns = 3
        
        self.structure = [[[None for _ in range(self.columns)] for _ in range(self.rows)] for _ in range(self.floors)]
        
        self.rooms = [[[{"door": True, "windows": 1} for _ in range(self.columns)] 
                       for _ in range(self.rows)] for _ in range(self.floors)]
                       
        self.incidents = [[[False for _ in range(self.columns)] for _ in range(self.rows)] for _ in range(self.floors)]
        
        self.occupants = {}
        self.emergency = {} # 
        self.buildingmanagement = {}
        
        self.elevator = {"location": (0, 0, 0), "status": "idle"}  # Elevador localizado na entrada
        self.emergency_stairs = [{"floor": floor, "location": (2, 1)} for floor in range(self.floors)]  # Escada de emergência em cada andar
        self.exits = [(self.floors - 1, 1, 2)] 

	self.elevator_moving = False
        self.elevator_occupied = False
        self.elevator_operational = True # Passa a falso em caso de incêndio por exemplo
        
        # Gerenciamento de alarmes e emergência
        self.alarm_triggered_earthquake = False
        self.alarm_triggered_fire = False
        self.evacuated_rooms = []
        
        
    def trigger_alarm_earthquake(self):
        self.alarm_triggered_earthquake = True
        self.disable_elevator()
        print("Earthquake alarm triggered. Elevator disabled.")
        
        # Notificar ocupantes com instruções específicas para terremoto
        for occupant in self.get_all_occupants():
            occupant.receive_alert("Earthquake detected! Move carefully to safe areas. Avoid elevators.")
        print("All occupants notified of earthquake protocol.")
        
        
    def trigger_alarm_fire(self):
        self.alarm_triggered_fire = True
        self.disable_elevator()
        print("Fire alarm triggered. Elevator disabled.")
        
        # Notificar ocupantes com instruções específicas para incêndio
        for occupant in self.get_all_occupants():
            occupant.receive_alert("Fire detected! Evacuate to the nearest exit immediately.")
        print("All occupants notified of fire evacuation protocol.")
        
        
    def detect_fire(self, floor, row, column):
        incident = {
            "floor": floor,
            "row": row,
            "column": column,
            "type": "Fire"
        }
        self.incidents.append(incident)
        self.disable_elevator()
        self.trigger_alarm()
        print(f"Fire incident detected at floor {floor}, row {row}, column {column}. Evacuate building.")
    
    
    # Função para detectar um problema de saúde
    def detect_health_issue(self, floor, row, column):
        incident = {
            "floor": floor,
            "row": row,
            "column": column,
            "type": "Health Issue"
        }
        self.incidents.append(incident)
        self.dispatch_medical_team(floor, row, column)
        print(f"Health issue detected at floor {floor}, row {row}, column {column}. Medical team dispatched.")
        
        
    def detect_earthquake(self, floor, row, column):
    	incident = {
    		"floor" = floor, 
    		"row" = row,
    		"column" = column, 
    		"type" = "Earthquake"
    	}
    	self.incidents.append(incident)
    	self.trigger_alarm_earthquake()
    	print(f"Earthquake detected")
    
       
    def set_room(self, floor, row, column, value):
        if 0 <= floor < self.floors and 0 <= row < self.rows and 0 <= column < self.columns:
            self.structure[floor][row][column] = value
        else:
            raise IndexError("Invalid floor, row, or column index")

    def get_room(self, floor, row, column):
        if 0 <= floor < self.floors and 0 <= row < self.rows and 0 <= column < self.columns:
            return self.structure[floor][row][column]
        else:
            raise IndexError("Invalid floor, row, or column index")

    def display_building(self):
        for floor in range(self.floors):
            print(f"Floor {floor}:")
            for row in range(self.rows):
                print(self.structure[floor][row])
            print()
            
    def disable_elevator(self):
        self.elevator_operational = False
        self.elevator["status"] = "disabled"
        print("Elevator disabled due to emergency.")

    def enable_elevator(self):
        self.elevator_operational = True
        self.elevator["status"] = "idle"
        print("Elevator is now operational.")


    def register_agent(self, agent):
        self.agents.append(agent)
        print(f"Agent {agent.jid} registered in the building.")

    def update_agent_location(self, agent, new_location):
        agent.location = new_location
        print(f"Agent {agent.jid} moved to {new_location}.")
        
    def detect_incident(self, floor, row, column, type):
        incident = {
            "floor": floor,
            "row": row,
            "column": column,
            "type": type  # Incêndio, problema de saúde etc
        }
        self.incidents.append(incident)  
        print(f"Incident detected at floor {floor}, row {row}, column {column}")
       
    def reset_building(self):
        self.structure = [[[None for _ in range(self.columns)] for _ in range(self.rows)] for _ in range(self.floors)]
        self.agents.clear()
        print("Building reset to initial state.")
     
    def deploy_emergency_responders(self):
        for agent in self.agents:
            if isinstance(agent, EmergencyResponderAgent):
                agent.evacuate()
                print(f"Emergency responder {agent.jid} deployed.")

    def simulate_evacuation(self):
        print("Starting evacuation simulation...")
        for agent in self.agents:
            if isinstance(agent, OccupantAgent):
                agent.navigate_to_exit()
            elif isinstance(agent, EmergencyResponderAgent):
                agent.evacuate()
                agent.assist_occupants()
                agent.manage_flow()
                agent.respond_to_incidents()
                


