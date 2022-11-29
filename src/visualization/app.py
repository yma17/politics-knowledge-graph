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
    # TODO: add a popup on load that shows how to use the app
    # so people don't get lost in the multiple layouts
    # See this example from Dash:
    # https://github.com/plotly/dash-sample-apps/blob/main/apps/dash-manufacture-spc-dashboard/app.py
    return

# --- Topic Graph Rendering ---

topic_graph_fp = "./data/topics/"

SUBJECTS = ["Government operations and politics", "Finance and financial sector", "Economics and public finance", "Armed forces and national security", "Health"]

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
    current_topic - the topic we want a subgraph for, input as a string. Value is the
    current selected topic in the "topic_dropdown" element.

    Returns:
    graph - a list of dictionaries containing data for a Dash Cytoscape graph

    See examples of this format here:
    https://dash.plotly.com/cytoscape
    """
    if current_topic is None:
        raise PreventUpdate
    edge_df = pd.read_csv(topic_graph_fp + "filtered_sub_top.csv")
    topic_df = edge_df[edge_df["top_name"] == current_topic]
    topic_nid = topic_df["top_nid"].iloc[0]
    nodes = [{'data': {'id': str(topic_nid), 'label': current_topic}}]
    edges = []
    node_limit = 10
    for i, row in enumerate(topic_df.itertuples()):
        # This is limited to avoid the screen being overwhelmed
        if i > node_limit:
            break
        # Creates nodes in the following format:
        # {'data': {'id': 'one', 'label': 'Node 1'}}
        node = {"data": {"id": str(row[2]), "label": row[4]}}
        nodes.append(node)
        # Creates edges in the following format:
        # {'data': {'source': 'one', 'target': 'two'}}
        edge = {'data': {'source': str(row[2]), 'target': str(row[3])}}
        edges.append(edge)
    graph = nodes + edges
    return graph

@app.callback(
    Output("topics", "children"),
    Input("topic_graph_data", "data")
)
def render_topic_graph(graph_data) -> list:
    """
    Renders the subgraph containing topics from the knowledge graph

    Parameters
    ---
    graph_data - The graph elements generated in the get_topic_graph_elements function and
    stored in the "topic_graph" dash.dcc.Store() element. This is updated whenever the topic
    chosen in the "topic_dropdown" element is changed.

    Returns
    ---
    topic_div - A list of dash elements that will be children of the "topics" div element
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
    topic_div = [
        dash.html.H2("Topics", className="graph_title"),
        graph]
    return topic_div

@app.callback(
    Output("topic_graph", "stylesheet"),
    Input("topic_graph", "mouseoverNodeData"),
    prevent_initial_call=True
)
def generate_topic_graph_stylesheet(node) -> list:
    """
    Returns a dictionary containing stylesheet elements for the Dash Cytoscape topic graph.
    The "node_hover_style" updates the style of the currently selected node, passed in by the
    "topic_graph"s "mouseoverNodeData" element.

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
    
    Returns
    ---
    default_stylesheet - a list of stylesheet elements in dictionary format
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
def render_community_graph():
    """
    Renders the subgraph of communities (clusters) for the current topic in the knowledge graph

    This is a Cytoscape element with nodes representing each cluster and no edges.

    Parameters
    ---
    None

    Returns
    ---
    community_div - a dash.html.Div() element containing the heading and Cytoscape element for
    the currently selected subgraph of topics
    """
    community_div = dash.html.Div(get_clusters(), id="communities", className="container")
    return community_div

@app.callback(
    # TODO: make this function actually use the topic to filter and retrieve data
    Output("communities", "children"),
    Input("topic_dropdown", "value"),
    Input("topic_graph", "tapNodeData"),
    prevent_initial_call = True # Prevents us from getting an error message while the topic graph loads
)
def get_clusters(subject=SUBJECTS[0], topic={"label":"Government employee pay"}):
    """
    Retrieves the cluster data from the backend for the selected topic, then formats it and returns a Cytoscape graph with the appropriate styling
    to represent the clusters.

    Parameters
    ---
    subject - The current subject selected from the topic_dropdown as a string
        Ex. "Health"

    topic - The most recently clicked topic in the topic graph in a dictionary format representing that node's data
        Ex. {"id":0, "name":"Medicare"}
    """
    if subject == None or topic == None:
        raise PreventUpdate
    current_topic = topic["label"]
    cluster_elem = [dash.html.H2("Topic Clusters", className="graph_title")]
    cluster_df = pd.read_csv("./data/clusters/viz_clusters.csv")
    all_clusters = cluster_df.columns
    # Determine which column to use for the clusters' sizes and colors
    size, color = None, None
    for c in all_clusters:
        if current_topic in c:
            if subject in c:
                if "size" in c:
                    size = c
                if "color" in c:
                    color = c
    # Use this until we have an updated topic graph that does not include topics we didn't analyze
    if size == None:
        raise PreventUpdate
    ctyo_elements = [{"data":{"id":str(i), "size":cluster_df[size].iloc[i], "color": cluster_df[color].iloc[i]}} for i in range(cluster_df.shape[0])]
    cluster_graph = cyto.Cytoscape(elements=ctyo_elements, style={'width': '100%', 'height': '90%'},
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
    cluster_elem.append(cluster_graph)
    return cluster_elem
# --- Get and display cluster details ---

def render_community_details(cluster=None):
    """
    Renders community details (lobbyists, legislor relationships) for the currently selected community 
    in the knowledge graph

    TODO: Implement functions to retrieve appropriate data/statistics (get_cluster_people() and get_cluster_stats())
    Currently these just have placeholder/dummy data.
    """
    cluster_stats = dash.html.Div(get_cluster_stats(cluster), id="cluster_stats")
    children = [dash.html.Div([dash.html.H2("Cluster Details", style={"padding-top":"0.3em"})], id="details_title"),
                get_cluster_people(cluster), cluster_stats]
                #dash.html.Div(id="cluster_stats")] TODO: Replace the above with this after impelementing the appropriate
                # callback for get_cluster_stats()
    
    details_div = dash.html.Div(children, id="details", className="container")
    return details_div

def get_cluster_people(cluster=None):
    """
    Retrieve the people from the knowledge graph connected to the currently selected cluster,
    then render the associated HTML elements based on the retrieved data.

    TODO: Implement this function - may want to separate this into separate functions to retrieve
    both congresspeople and lobbyists for a given cluster as well as to render the HTML elements.

    Currently uses dummy data in the form of lists of strings (congresspeople and lobbyists).
    """
    people_elements = [dash.html.H2("Cluster Members")]
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

def get_member_parties(cluster=None):
    """
    Retrieve statistics about the parties of members in the currently selected cluster,
    then render the associated HTML elements based on the retrieved data.

    TODO: Implement this function
    """
    number_cluster_members = 10
    percent_dem = 0
    percent_rep = 0
    percent_ind = 0
    party_elements =[
        dash.html.P(f"Number of members: {number_cluster_members}", id="num_members"),
        dash.html.H4("Party composition:"),
        dash.html.P(f"{percent_dem}% Democrat"),
        dash.html.P(f"{percent_rep}% Republican"),
        dash.html.P(f"{percent_ind}% Independent")
    ]
    return party_elements

def get_common_topics(cluster=None):
    """
    Retrieve statistics about the parties of members in the currently selected cluster,
    then render the associated HTML elements based on the retrieved data.

    TODO: Implement this function
    """
    example_topics = {"Health":0.45, "Families":0.231, "Taxation":0.895}
    topic_elements = [
        dash.html.H4("Common Legislation Topics")
    ]
    for t in example_topics.keys():
        topic_elements.append(dash.html.P(t))
        topic_elements.append(dash.html.P(f"Probability of similar voting: {example_topics[t]}"))
    return topic_elements

def get_common_committees():
    """
    Retrieve statistics about the committees with members in the currently selected cluster,
    then render the associated HTML elements based on the retrieved data.

    TODO: Implement this function
    """
    example_committees = {"Appropriations": 10, "Ethics": 5, "Homeland Security": 3}
    committee_elements = [
        dash.html.H4("Common Subcommittees")
    ]
    for c in example_committees.keys():
        committee_elements.append(dash.html.P(c))
        committee_elements.append(dash.html.P(f"{example_committees[c]} committee members"))
    return committee_elements

#@app.callback(
#   TODO: Implement this callback function- should take in the currently selected (clicked) cluster and render
#   the appropriate details in each of its child elements (the three Divs: member_parties, common_topics,
#   and common_committees)
#   
#   Output("cluster_stats", "children"),
#   Input()
#)
def get_cluster_stats(cluster=None):
    """
    Retrieves the HTML elements containing data on a clusters' members, the common legislation topics in the cluster
    and the most common subcomittees in the cluster

    Parameters
    ---
    cluster - to be implemented

    Returns
    ---
    div_list - a list of 3 dash.html.Div elements containing the data listed above, updated dynamically
    based on user input.
    """
    member_parties = dash.html.Div(get_member_parties(), id="member_parties")
    common_topics = dash.html.Div(get_common_topics(), id="common_topics")
    common_committees = dash.html.Div(get_common_committees(), id="common_committees")
    return [member_parties, common_topics, common_committees]

# Render the page structure

def render_parent_container():
    """
    Renders the HTML elements of the parent_container Div element on load

    Parameters
    ---
    None

    Returns
    ---
    topic_graph - a dash.html.Div element containing the topic graph related HTML elements on the page

    communities - a dash.html.Div element containing the 
    """
    topic_graph = dash.html.Div(id="topics", className="container")
    communities = render_community_graph()
    details = render_community_details()
    return topic_graph, communities, details

def render_layout():
    """
    Renders the HTML elements of the page on load

    Parameters
    ---
    None

    Returns
    ---
    main_container - a dash.html.Div element containing a list of child
    elements with all other elements in the app.
    """
    return dash.html.Div([
        dash.dcc.Store(id="topic_graph_data", data=None),
        # Banner for top of the page
        dash.html.Div([
            dash.html.H1("REP-G", id="title", className="header_element"), 
            dash.html.P("Select a topic to learn more!", className="header_element"),
            dash.dcc.Dropdown(SUBJECTS, SUBJECTS[0], id="topic_dropdown"),
            dash.html.P("Help", className="header_element", id="help"),
            dash.html.P("About", className="header_element", id="about")],
            id="banner"),
        # Main container that holds each of the main application views
        dash.html.Div(render_parent_container(), id="parent_container"),
        dash.html.Div(id="footer")
    ], 
    id="main-container")

app.layout = render_layout()

if __name__ == '__main__':
    app.run_server(debug=True)
