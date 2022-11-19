import dash
import dash_cytoscape as cyto
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate

import pandas as pd

app = dash.Dash(__name__)
app.config.suppress_callback_exceptions=True
app.title = "REP-G: REpresenting Politics with Graphs"
server = app.server

def show_instructions():
    # We should definitely have a popup on load that shows how to use the app
    # so people don't get lost in the multiple layouts
    return

# --- Topic Graph Rendering ---

test_graph = [
    {'data': {'id': 'one', 'label': 'Node 1'}},
    {'data': {'id': 'two', 'label': 'Node 2'}},
    {'data': {'source': 'one', 'target': 'two'}}
]

topic_graph_fp = "./data/topics/"
topics = ["Families", "Health", "Taxation", "Energy", "Economics and public finance"]

@app.callback(
    Output("topic_graph_data", "data"),
    Input("topic_dropdown", "value")
)
def get_topic_graph_elements(current_topic = "Families"):
    """
    Get the elements for the subgraph that relate to the current topic in a format
    usable by Cytoscape.js

    Inputs
    -----
    n_clicks - a fake input to test this callback function
    
    current_topic - the topic we want a subgraph for, input as a string

    Returns:
    """
    if current_topic is None:
        raise PreventUpdate
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
        },
        stylesheet=[
            {
                'selector':'node',
                'style':{
                    'background-color' :'#6A6A6A',
                    'line-color':'#BABABA',
                    'color':'#0096E0'
                }
            }
        ],
        id="topic_graph"
    )
    topic_div = dash.html.Div([graph],id="topics", className="container")
    return topic_div

@app.callback(
    Output("topic_graph", "stylesheet"),
    Input("topic_graph", "mouseoverNodeData"),
    prevent_initial_call=True
)
def generate_topic_graph_stylesheet(node):
    """
    Returns a dictionary containing stylesheet elements for the Cytoscape graph.

    Parameters
    ---
    node - data from a hovered over node in the topic_graph, provided in the dictionary format:
    {'data':{'id':0, 'label':'name'}}

    See Plotly Cytoscape documentation on how to use callbacks:
    https://dash.plotly.com/cytoscape/events

    And on how to change a graph's style:
    https://dash.plotly.com/cytoscape/styling

    Finally, a helpful example:
    https://github.com/plotly/dash-cytoscape/blob/master/usage-stylesheet.py
    """
    default_stylesheet = [
            {
                'selector':'node',
                'style':{
                    'background-color' :'#6A6A6A',
                    'line-color':'#BABABA',
                    'color':'#0096E0'
                }
            }
        ]
    node_hover_style =  {
        "selector": 'node[id = "{}"]'.format(node['id']),
        "style": {
            'background-color':'#CACACA',
            'line-color':'#CACACA',
            'label': 'data(label)',
            'z-index': '999'
        }
    }
    if node:
        default_stylesheet.append(node_hover_style)
    return default_stylesheet

# --- Cluster Rendering ---

party_colors = ["#b8232d", "#a923b8" "#7523b8", "#4123b8", "#234bb8"] 
# Interpolate between 5 colors - chosen based on party parameter... goes from red to blue
# Number of members will impact the size
#test_clusters = [
#    {'data': {'id': 0, 'members': 10, 'topic':'Families', 'party': 0.5}},
#    {'data': {'id': 1, 'members': 15, 'topic':'Families', 'party': 0.2}},
#    {'data': {'id': 2, 'members': 6, 'topic':'Families', 'party': 0.1}},
#    {'data': {'id': 3, 'members': 24, 'topic':'Families', 'party': 0.8}}
#]

def get_party_color(party_polarity):
    # 0 corresponds to 100% republican
    # 1.0 corresponds to 100% democrat
    color = party_colors[round(party_polarity)]
    return color

def render_community_graph():
    """
    Renders the subgraph of communities for the current topic in the knowledge graph
    """
    community_div = dash.html.Div(id="communities", className="container")
    return community_div

@app.callback(
    Output("communities", "children"),
    Input("topic_dropdown", "value"),
    prevent_initial_call=True
)
def get_clusters(topic):
    # To render the clusters, I just made some nodes of various sizes?
    cluster_graph = cyto.Cytoscape(elements=[], style={'width': '100%', 'height': '100%'},)
    return cluster_graph

def render_community_details():
    """
    Renders community details (lobbyists, legislor relationships) for the currently selected community 
    in the knowledge graph
    """
    children = [dash.html.H2("Cluster Details")]
    
    details_div = dash.html.Div(children, id="details", className="container")
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
            dash.html.H1("REP-G", id="title", className="header_element"), 
            dash.html.P("Select a topic to learn more!", className="header_element"),
            dash.dcc.Dropdown(topics, topics[0], id="topic_dropdown"),
            dash.html.P("Help", className="header_element", id="help"),
            dash.html.P("About", className="header_element", id="about")],
            id="banner"),
        # Main container that holds each of the main application views
        dash.html.Div([], id="parent_container"),
        dash.html.Div(id="footer")
    ], 
    id="main-container")

app.layout = render_layout()

if __name__ == '__main__':
    app.run_server(debug=True)
