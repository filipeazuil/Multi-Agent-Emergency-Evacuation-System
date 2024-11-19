import dash
from dash import dcc, html, Input, Output, dcc
import plotly.express as px
from environment import Building

building = Building()
building.connect_elevators()
building.connect_staircases()

# Global variable to store simulation data
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

# Define the app layout
app.layout = html.Div([
    html.H1("Building Evacuation Dashboard"),
    dcc.Graph(id='metrics-graph'),
    html.Div(id='event-log')
])

# Callback to update the graph
@app.callback(
    Output('metrics-graph', 'figure'),
    [Input('interval', 'n_intervals')]
)
def update_graph(n):
    # Get the latest simulation data
    data = building.get_simulation_state()

    # Create a bar chart to visualize the metrics
    fig = px.bar(x=['Fires', 'Earthquakes', 'Attacks', 'Saved Agents'],
                 y=[data['fires'], data['earthquakes'], data['attacks'], data['saved_agents']])
    return fig

# Callback to update the event log
@app.callback(
    Output('event-log', 'children'),
    [Input('interval', 'n_intervals')]
)
def update_event_log(n):
    return html.Ul([html.Li(event) for event in simulation_data['events']])

# Function to run the simulation and update the dashboard
def run_simulation_and_dashboard(building):
    global simulation_data
    simulation_data['total_agents'] = len(building.agents)

    while not building.is_building_evacuated():
        building.simulate_step()

        # Update simulation data
        simulation_data['fires'] += building.num_fires
        simulation_data['earthquakes'] += building.num_earthquakes
        simulation_data['attacks'] += building.num_attacks
        simulation_data['saved_agents'] = sum(1 for agent in building.agents.values() if agent.is_evacuated)

        # Update event log (adjust based on your simulation's event handling)
        for event in building.get_recent_events():
            simulation_data['events'].append(event)

        # Trigger dashboard updates
        app.run_server(debug=True, use_reloader=False)

# Main execution
if __name__ == '__main__':
    building = Building()  # Initialize your building object
    run_simulation_and_dashboard(building)