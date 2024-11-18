from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import time
import random

# Global variables to track simulation state
simulation_data = {
    "fires": 0,
    "earthquakes": 0,
    "attacks": 0,
    "saved_agents": 0,
    "total_agents": 0,
    "events": []
}

# Create the Dash app
app = Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1("Building Evacuation Dashboard"),
    html.Div([
        html.H3("Simulation Metrics"),
        html.Div([
            html.P("Number of Fires: "),
            html.P(id="num-fires"),
        ]),
        html.Div([
            html.P("Number of Earthquakes: "),
            html.P(id="num-earthquakes"),
        ]),
        html.Div([
            html.P("Number of Attacks: "),
            html.P(id="num-attacks"),
        ]),
        html.Div([
            html.P("Saved Agents: "),
            html.P(id="saved-agents"),
        ]),
        html.Div([
            html.P("Total Agents: "),
            html.P(id="total-agents"),
        ]),
    ]),
    html.Div([
        html.H3("Event Log"),
        html.Ul(id="event-log"),
    ]),
    dcc.Interval(id="interval", interval=1000, n_intervals=0)  # Update every second
])


# Callbacks to update the metrics and event log
@app.callback(
    [Output("num-fires", "children"),
     Output("num-earthquakes", "children"),
     Output("num-attacks", "children"),
     Output("saved-agents", "children"),
     Output("total-agents", "children"),
     Output("event-log", "children")],
    [Input("interval", "n_intervals")]
)
def update_dashboard(n_intervals):
    global simulation_data
    return (
        str(simulation_data["fires"]),
        str(simulation_data["earthquakes"]),
        str(simulation_data["attacks"]),
        str(simulation_data["saved_agents"]),
        str(simulation_data["total_agents"]),
        [html.Li(event) for event in simulation_data["events"][-10:]]
    )


# Function to simulate the environment and update data
def simulate_environment(building):
    global simulation_data
    simulation_data["total_agents"] = len(building.agents)

    while not building.is_building_evacuated():
        building.simulate_step()
        
        # Update events based on random events triggered
        for floor in building.floors:
            for row in floor.rooms:
                for room in row:
                    if room.is_on_fire:
                        simulation_data["fires"] += 1
                        simulation_data["events"].append(f"Fire in {room.name}")
                    if room.is_damaged:
                        simulation_data["earthquakes"] += 1
                        simulation_data["events"].append(f"Earthquake damaged {room.name}")
                    if room.is_taken:
                        simulation_data["attacks"] += 1
                        simulation_data["events"].append(f"Attack in {room.name}")
        
        # Track agents evacuated
        simulation_data["saved_agents"] = sum(
            1 for agent in building.agents.values() if agent.is_evacuated
        )

        time.sleep(10)  # Wait for the next simulation step


# Function to run the dashboard and simulation
def run_dashboard_and_simulation(building):
    import threading
    dashboard_thread = threading.Thread(target=lambda: app.run_server(debug=True, use_reloader=False))
    dashboard_thread.start()

    simulate_environment(building)

# To integrate this with the existing simulation
if __name__ == "__main__":
    from environment import Building
    building = Building()
    building.connect_elevators()
    building.connect_staircases()
    run_dashboard_and_simulation(building)

