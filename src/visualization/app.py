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

party_colors = ["#092573", "#250973", "#500973", "#730950", "#8f0303"]

test_clusters = [
    {'data': {'id': 'one', 'label': 'Node 1', 'size':30, 'color':party_colors[0]}},
    {'data': {'id': 'two', 'label': 'Node 2', 'size':40, 'color':party_colors[1]}},
    {'data': {'id': 'three', 'label': 'Node 3', 'size':80, 'color':party_colors[2]}},
    {'data': {'id': 'four', 'label': 'Node 4', 'size':65, 'color':party_colors[3]}}
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
        style={'width': '100%', 'height': '90%'},
        layout={
            'name': 'cose'
        },
        stylesheet=[
            {
                'selector':'node',
                'style':{
                    'background-color' :'#DADADA',
                    'line-color':'#DADADA',
                    'color':'#0096E0'
                }
            }
        ],
        id="topic_graph"
    )
    topic_div = dash.html.Div([
        dash.html.H2("Topics", className="graph_title"),
        graph], id="topics", className="container")
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
                    'background-color' :'#DADADA',
                    'line-color':'#DADADA',
                    'color':'#000000'
                }
            }
        ]
    node_hover_style =  {
        "selector": 'node[id = "{}"]'.format(node['id']),
        "style": {
            'background-color':'#7c7c7c',
            'line-color':'#7c7c7c',
            'label': 'data(label)',
            'z-index': '999'
        }
    }
    if node:
        default_stylesheet.append(node_hover_style)
    return default_stylesheet

# --- Cluster Rendering ---

def get_party_color(party_polarity):
    # 0 corresponds to 100% republican
    # 1.0 corresponds to 100% democrat
    color = party_colors[round(party_polarity * len(party_colors))]
    return color

def render_community_graph():
    """
    Renders the subgraph of communities for the current topic in the knowledge graph
    """
    community_div = dash.html.Div([
        dash.html.H2("Topic Clusters", className="graph_title"),
        get_clusters("Families")], id="communities", className="container")
    return community_div

@app.callback(
    Output("communities", "children"),
    Input("topic_dropdown", "value"),
    prevent_initial_call=True
)
def get_clusters(topic):
    # To render the clusters, I just made some nodes of various sizes?
    cluster_graph = cyto.Cytoscape(elements=test_clusters, style={'width': '100%', 'height': '90%'},
                                    stylesheet=[
                                        {
                                            "selector":"node",
                                            "style":{
                                                "height":"data(size)",
                                                "width":"data(size)",
                                                "background-color":"data(color)"
                                            }
                                        }
                                    ])
    return cluster_graph

# --- Get and display cluster details ---

def render_community_details(cluster=None):
    """
    Renders community details (lobbyists, legislor relationships) for the currently selected community 
    in the knowledge graph
    """
    children = [dash.html.Div([dash.html.H2("Cluster Details", style={"padding-top":"0.3em"})], id="details_title"),
                get_cluster_people(cluster),
                get_cluster_stats(cluster)]
    
    details_div = dash.html.Div(children, id="details", className="container")
    return details_div

def get_cluster_people(cluster):
    people_elements = []
    # Congress members
    people_elements.append(dash.html.H3("Members"))
    congresspeople = ["Mitch McConnell", "John Thune"]
    congress_list = dash.html.Ul([dash.html.Li(p) for p in congresspeople])
    people_elements.append(congress_list)
    # Lobbyists
    people_elements.append(dash.html.H3("Lobbyists"))
    lobbyists = ["Joe Schmoe", "Sally Bally"]
    lobbyist_list = dash.html.Ul([dash.html.Li(l) for l in lobbyists])
    people_elements.append(lobbyist_list)
    people = dash.html.Div(people_elements, id="people")
    return people

def get_cluster_stats(cluster):
    return dash.html.Div(id="cluster_stats")

# Render the page structure

@app.callback(
    Output("parent_container", "children"),
    Input("topic_graph_data", "data")
)
def render_parent_container(graph_data=None):
    topic_graph = render_topic_graph(graph_data)
    communities = render_community_graph()
    details = render_community_details()
    return topic_graph, communities, details

def render_layout() -> None:
    return dash.html.Div([
        dash.dcc.Store(id="topic_graph_data", data=None),
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
