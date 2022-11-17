import dash
import dash_cytoscape as cyto
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate

import pandas as pd

app = dash.Dash(__name__)
app.title = "REP-G"
server = app.server

test_graph = [
    {'data': {'id': 'one', 'label': 'Node 1'}},
    {'data': {'id': 'two', 'label': 'Node 2'}},
    {'data': {'source': 'one', 'target': 'two'}}
]

topic_graph_fp = "./data/topics/"
house_or_senate = "house"

def show_instructions():
    # We should definitely have a popup on load that shows how to use the app
    # so people don't get lost in the multiple layouts
    return

@app.callback(
    Output("topic_graph_data", "data"),
    Input("house_dropdown", "n_clicks") # I'm going to change this later, this is just a placeholder for now
)
def get_topic_graph_elements(n_clicks, current_topic = "Health"):
    """
    Get the elements for the subgraph that relate to the current topic in a format
    usable by Cytoscape.js

    Inputs
    -----
    n_clicks - a fake input to test this callback function
    
    current_topic - the topic we want a subgraph for, input as a string

    Returns:
    """
    if n_clicks is None:
        raise PreventUpdate
    node_df = pd.read_csv(topic_graph_fp + "subject_topic_nodes.tsv", sep="\t")
    edge_df = pd.read_csv(topic_graph_fp + "subject_topic_full_edges.tsv", sep="\t")
    topic_df = edge_df[edge_df["top_name"] == current_topic]
    topic_nid = topic_df["top_nid"].iloc[0]
    nodes = [{'data': {'id': str(topic_nid), 'label': current_topic}}]
    edges = []
    i = 0
    for row in topic_df.itertuples():
        # For now, this is limited to avoid the screen being overwhelmed
        if i > 10:
            break
        # Creates nodes in the following format:
        # {'data': {'id': 'one', 'label': 'Node 1'}}
        node = {"data": {"id": str(row[1]), "label": row[3]}}
        nodes.append(node)
        # Creates edges in the following format:
        # {'data': {'source': 'one', 'target': 'two'}}
        edge = {'data': {'source': str(row[1]), 'target': str(row[2])}}
        edges.append(edge)
        i += 1
    graph = nodes + edges
    return graph

def render_topic_graph(graph_data):
    """
    Renders the subgraph containing topics from the knowledge graph
    """
    graph = cyto.Cytoscape(
        elements=graph_data,
        style={'width': '100%', 'height': '100%'},
        layout={
            'name': 'cose'
        }
    )
    topic_div = dash.html.Div([graph],id="topics", className="container")
    return topic_div

def render_community_graph():
    """
    Renders the subgraph of communities for the current topic in the knowledge graph
    """
    community_div = dash.html.Div(id="communities", className="container")
    return community_div

def render_community_details():
    """
    Renders community details (lobbyists, legislor relationships) for the currently selected community 
    in the knowledge graph
    """
    display = "none"
    details_div = dash.html.Div(id="details", className="container", 
                                style={"display": display})
    return details_div

@app.callback(
    Output("parent_container", "children"),
    Input("topic_graph_data", "data")
)
def render_parent_container(graph_data=test_graph):
    topic_graph = render_topic_graph(graph_data)
    communities = render_community_graph()
    details = render_community_details()
    return topic_graph, communities, details

def render_layout() -> None:
    return dash.html.Div([
        dash.dcc.Store(id="topic_graph_data", data=test_graph),
        # Banner for top of the page
        dash.html.Div([
            dash.html.H1("REP-G", id="title"), 
            dash.html.A("Help"), 
            dash.html.A("About"),
            dash.html.Button("Click me!", id="house_dropdown", n_clicks=0)], 
            id="banner"),
        # Main container that holds each of the main application views
        dash.html.Div([], id="parent_container"),
        dash.html.Div(id="footer")
    ], 
    id="main-container")

app.layout = render_layout()

if __name__ == '__main__':
    app.run_server(debug=True)