import spade
import asyncio
from environment import Building
from agents import OccupantAgent, EmergencyResponderAgent, BuildingManagementAgent
import dash
from dash import dcc, html
from threading import Thread
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Initialize Dash app
app = dash.Dash(__name__)

# Initialize global variables
performance_metrics = [0] * 6
agent_locations = [0, 0, 0, 0]
measures = [None, None, None]
active_situations = ""  # To store active situations of rooms
recent_updates=""
# Define the Dash layout
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1("Building Evacuation Simulation", style={"text-align": "center", "color": "#2E86C1"}),
            ],
            style={
                "backgroundColor": "#D5DBDB", 
                "padding": "30px", 
                "borderRadius": "10px",
                "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.2)",
                "marginBottom": "30px"
            },
        ),

        # Main container for left and right side sections
        html.Div(
            children=[
                # Left container for Building Structure, Performance Metrics, and Agent Locations
                html.Div(
                    children=[
                        # Building Structure Section
                        html.Div(
                            children=[
                                html.H3("Building Structure", style={"color": "#2874A6", "font-size": "24px"}),
                                html.Div(
                                    children=[
                                        html.P(id="measures", style={"font-size": "18px", "color": "#1F618D"}),
                                    ],
                                    style={"padding": "20px", "borderRadius": "10px", "backgroundColor": "#E8F8F5", "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)"},
                                ),
                            ],
                            style={"marginBottom": "30px", "padding": "20px", "borderRadius": "15px", "backgroundColor": "#D5DBDB"},
                        ),

                        # Performance Metrics Section
                        html.Div(
                            children=[
                                html.H3("Performance Metrics", style={"color": "#2874A6", "font-size": "24px"}),
                                html.Div(
                                    children=[
                                        html.P(id="fires-metrics", style={"font-size": "18px", "color": "#1F618D"}),
                                        html.P(id="earthquake-metrics", style={"font-size": "18px", "color": "#1F618D"}),
                                        html.P(id="attack-metrics", style={"font-size": "18px", "color": "#1F618D"}),
                                    ],
                                    style={"padding": "20px", "borderRadius": "10px", "backgroundColor": "#E8F8F5", "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)"},
                                ),
                            ],
                            style={"marginBottom": "30px", "padding": "20px", "borderRadius": "15px", "backgroundColor": "#D5DBDB"},
                        ),

                        # Agent Locations Section
                        html.Div(
                            children=[
                                html.H3("Agent Locations", style={"color": "#2874A6", "font-size": "24px"}),
                                html.Div(
                                    children=[
                                        html.P(id="agent-location-1", style={"font-size": "18px", "color": "#1F618D"}),
                                        html.P(id="agent-location-2", style={"font-size": "18px", "color": "#1F618D"}),
                                        html.P(id="agent-location-3", style={"font-size": "18px", "color": "#1F618D"}),
                                        html.P(id="agent-location-4", style={"font-size": "18px", "color": "#1F618D"}),
                                    ],
                                    style={"padding": "20px", "borderRadius": "10px", "backgroundColor": "#E8F8F5", "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)"},
                                ),
                            ],
                            style={"marginBottom": "30px", "padding": "20px", "borderRadius": "15px", "backgroundColor": "#D5DBDB"},
                        ),
                    ],
                    style={"flex": "1", "display": "flex", "flexDirection": "column"},  # Flex container for the left side
                ),

                # Right container for Active Situations and Recent Updates (aligned with agent locations)
                html.Div(
                    children=[
                        html.H3("Active Situations in Rooms", style={"color": "#2874A6", "font-size": "24px"}),
                        html.Div(
                            children=[
                                html.Pre(id="activesituations", style={"font-size": "18px", "color": "#1F618D"}),
                            ],
                            style={"padding": "20px", "borderRadius": "10px", "backgroundColor": "#E8F8F5", "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)"},
                        ),
                        html.H3("Recent Updates", style={"color": "#2874A6", "font-size": "24px"}),
                        html.Div(
                            children=[
                                html.Pre(id="recentupdates", style={"font-size": "20px", "color": "#1F618D"}),
                            ],
                            style={"padding": "20px", "borderRadius": "10px", "backgroundColor": "#E8F8F5", "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)"},
                        ),
                    ],
                    style={
                        "flex": "1", 
                        "height": "100%", 
                        "overflow": "auto", 
                        "padding": "20px", 
                        "borderRadius": "15px", 
                        "backgroundColor": "#D5DBDB",
                        "display": "flex", 
                        "flexDirection": "column",
                    },  # Ensure both Active Situations and Recent Updates are stacked vertically
                ),
            ],
            style={"display": "flex", "gap": "20px", "height": "100vh"},  # Flex container to align left and right side sections
        ),

        # Interval Component to Update Every 0.5s
        dcc.Interval(
            id="interval-component",
            interval=500,  # Update every 0.5 seconds
            n_intervals=0
        )
    ],
    style={"fontFamily": "Arial, sans-serif", "backgroundColor": "#F4F6F6", "padding": "20px"}
)

# Update performance metrics and active room situations every interval (i.e., 0.5 seconds)
@app.callback(
    [
        Output("fires-metrics", "children"),
        Output("earthquake-metrics", "children"),
        Output("attack-metrics", "children"),
        Output("agent-location-1", "children"),
        Output("agent-location-2", "children"),
        Output("agent-location-3", "children"),
        Output("agent-location-4", "children"),
        Output("measures", "children"),
        Output("activesituations", "children"),  # Add active situations output
        Output("recentupdates", "children"),
    ],
    [Input("interval-component", "n_intervals")]
)
def update_metrics(n):
    # Access global performance metrics
    fires_extinguished = performance_metrics[0]
    total_fires = performance_metrics[1]
    earthquakes = performance_metrics[2]
    total_earthquakes = performance_metrics[3]
    attacks_controlled = performance_metrics[4]
    total_attacks = performance_metrics[5]

    agent1_location = agent_locations[0]
    agent2_location = agent_locations[1]
    agent3_location = agent_locations[2]
    agent4_location = agent_locations[3]
    activesituations = active_situations
    recentupdates = recent_updates

    # Return the active situations that were set in the main function
    return (
        f"Fires Extinguished / Total Fires: {fires_extinguished}/{total_fires} ({fires_extinguished/total_fires*100 if total_fires != 0 else 0:.1f}%)",
        f"Earthquakes Cleaned / Total Earthquakes: {earthquakes}/{total_earthquakes} ({earthquakes/total_earthquakes*100 if total_earthquakes!=0 else 0:.1f}%)",
        f"Attacks Controlled / Total Attacks: {attacks_controlled}/{total_attacks} ({attacks_controlled/total_attacks*100 if total_attacks!=0 else 0:.1f}%)",
        f"Agent 1 Location: {agent1_location}",
        f"Agent 2 Location: {agent2_location}",
        f"Agent 3 Location: {agent3_location}",
        f"Agent 4 Location: {agent4_location}",
        f"This building has {measures[0]} floors and {measures[1]}x{measures[2]} structure!",
        activesituations,  # Show the active situations for rooms
        recentupdates,
    )


def run_dash(app):
    app.run_server(debug=True, use_reloader=False)

async def main():
    dash_thread = Thread(target=run_dash, args=(app,))
    dash_thread.start()
    building = Building()
    global measures
    measures = [building.num_floors, building.rows, building.cols]
    building.connect_elevators()
    building.connect_staircases()
    
    occupant_agent_1 = OccupantAgent("occupant1@localhost", "password", "Agent 1", building, "able-bodied")
    occupant_agent_2 = OccupantAgent("occupant2@localhost", "password", "Agent 2", building, "disabled")
    occupant_agent_3 = OccupantAgent("occupant3@localhost", "password", "Agent 3", building, "able-bodied")
    occupant_agent_4 = OccupantAgent("occupant4@localhost", "password", "Agent 4", building, "disabled")
    emergency_responder_agent_1 = EmergencyResponderAgent("responder1@localhost", "password", "Fire-fighter", building, "firefighter")
    emergency_responder_agent_2 = EmergencyResponderAgent("responder2@localhost", "password", "Rescue Worker", building, "Rescue Worker")
    emergency_responder_agent_3 = EmergencyResponderAgent("responder3@localhost", "password", "Paramedic", building, "Paramedic")
    emergency_responder_agent_4 = EmergencyResponderAgent("responder4@localhost", "password", "Security Officer", building, "Security Officer")
    building_management_agent = BuildingManagementAgent("management@localhost", "password", building, "Building Management")
   
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
    
    # Start simulation
    while not building.is_building_evacuated():
        building.simulate_step()
        await asyncio.sleep(1)

        # Update global performance metrics
        global performance_metrics
        performance_metrics = [building.num_fires[0], building.num_fires[1], building.num_earthquakes[0], building.num_earthquakes[1], building.num_attacks[0], building.num_attacks[1]]

        # Update agent locations dynamically
        global agent_locations
        agent_locations = [
            (agent.location.name if hasattr(agent.location, 'name') else agent.location)
            for agent in building.agents.values()
        ]
        
        # Update active situations
        global active_situations
        active_situations = ""
        for floor in building.floors:
            for i in range(floor.num_cols):
                for j in range(floor.num_rows):
                    room=floor.get_room(j,i)
                    if room.is_on_fire:
                        active_situations += f"Fire in room {room.name}.\n"
                    if room.is_damaged:
                        active_situations += f"Earthquake damage in room {room.name}.\n"
                    if room.is_taken:
                        active_situations += f"Attack in room {room.name}.\n"
                        
        global recent_updates
        recent_updates=building.updates
        
    print("Every Occupant evacuated! Success!")
    values = building.performance_metrics()
    
    # Stop all agents
    await occupant_agent_1.stop()
    await occupant_agent_2.stop()
    await occupant_agent_3.stop()
    await occupant_agent_4.stop()
    await emergency_responder_agent_1.stop()
    await emergency_responder_agent_2.stop()
    await emergency_responder_agent_3.stop()
    await emergency_responder_agent_4.stop()
    await building_management_agent.stop()
    return values
    dash_thread.stop()

if __name__ == "__main__":
    asyncio.run(main())

