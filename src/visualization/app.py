import dash
import dash_cytoscape as cyto
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate

import pandas as pd

# -- Timing Function -- #
import time
import functools


def timefunc(func):
    """Call a function and time its execution."""

    @functools.wraps(func)
    def time_closure(*args, **kwargs):
        """
        The function that will be called by timefunc.
        
        Time elapsed is given in seconds.
        """
        start = time.perf_counter()
        result = func(*args, **kwargs)
        time_elapsed = time.perf_counter() - start
        print(f"Function: {func.__name__}, Time: {time_elapsed}")
        return result

    return time_closure

# -- App --

app = dash.Dash(__name__)
app.config.suppress_callback_exceptions=True
app.title = "REP-G: REpresenting Politics with Graphs"
server = app.server

@app.callback(
    Output("instruction_box", "style"),
    [Input("help", "n_clicks"), Input("markdown_close", "n_clicks")],
    prevent_initial_call=True
)
def show_instructions(help_click, close_click):
    ctx = dash.callback_context.triggered_id
    if ctx == "help":
        return {"display": "block"}
    else:
        return {"display": "none"}

def render_instructions():
    """
    Renders a modal with instructions on how to use the app
    """
    return dash.html.Div([
        dash.html.Div([
            dash.html.Div(
                        className="close-container",
                        children=dash.html.Button(
                            "Close",
                            id="markdown_close",
                            n_clicks=0,
                            className="closeButton",
                        )),
            dash.html.Div(
                        className="markdown-text",
                        children=dash.dcc.Markdown(
                            children=(
                                """
                        # Welcome to REP-G!
                        This is a dashboard to learn about political behavior in the US House of Representatives. You can click
                        on various areas of the dashboard to explore politican's voting patterns on different types of legislation,
                        how they are influenced by lobbyists, and more!

                        ## How to Use this Tool
                        Choose a general area (topic) to explore using the dropdown on the main menu bar. The "topic graph" shows what more specific areas
                        of legislation correspond with this topic. Clicking a node in this graph will allow you to explore groups of representatives with similar
                        behavior (voting patterns) in this area. These groups or "clusters" are shown in the "Topic Cluster" pie chart.
                        
                        You can then click each of these clusters (areas in the pie chart) to get more details about the Representatives with those voting patterns, which lobbyists
                        support them, who tends to sponsor the most bills, and their party makeup.
                        
                        ## The Team
                        REP-G was created by Christian Clark, Shreyas Verma, Yingchen Ma, Manoj Parmar, and Sanchita Porwal in Fall 2022 for the Georgia Tech
                        Data and Visual Analytics course (CSE6242). We hope you enjoy using our tool!

                        ## Source Code
                        You can find the source code of this app on our [Github repository](https://github.com/yma17/politics-knowledge-graph).
                    """
                            )))
        ], id="instructions")
        ], className="modal", id="instruction_box")

# --- Topic Graph Rendering ---

SUBJECTS = ["Government operations and politics", "Finance and financial sector", "Economics and public finance", "Armed forces and national security", "Health"]

@app.callback(
    Output("topic_graph_data", "data"),
    Input("current_topic", "data")
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
    edge_df = pd.read_csv("./data/topics/filtered_sub_top.csv")
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
#@timefunc
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
        style={'width': '100%', 'height': '85%'},
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
        dash.html.P("Hover over the nodes associated with the central topic node and then select a sub-topic for more details.", style={"font-size":"small"}),
        graph]
    return topic_div

@app.callback(
    Output("current_topic", "data"),
    Input("topic_dropdown", "value")
)
def store_current_topic(value):
    """
    Store the currently selected topic from the topic list in the dcc.Store element
    with the id indicated above for future use.
    """
    return value

@app.callback(
    Output("current_subtopic", "data"),
    Input("topic_graph", "tapNodeData")
)
def store_current_subtopic(click):
    """
    Store the currently clicked topic node data in the dcc.Store element
    with the id indicated above for future use.
    """
    return click

@app.callback(
    Output("current_cluster", "data"),
    Input("cluster_pie", "clickData")
)
def store_current_cluster(click):
    """
    Store the currently clicked cluster data in the dcc.Store element
    with the id indicated above for future use.
    """
    return click

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
    Output("communities", "children"),
    Input("current_topic", "data"),
    Input("current_subtopic", "data"),
    prevent_initial_call = True # Prevents us from getting an error message while the topic graph loads
)
#@timefunc
def get_clusters(topic=SUBJECTS[0], subtopic={"label":"Government employee pay"}):
    """
    Retrieves the cluster data from the backend for the selected topic, then formats it and returns a plotly Pie graph with the appropriate styling
    to represent the clusters.

    Parameters
    ---
    subject - The current subject selected from the topic_dropdown as a string
        Ex. "Health"

    topic - The most recently clicked topic in the topic graph in a dictionary format representing that node's data
        Ex. {"id":0, "name":"Medicare"}
    """
    if topic == None or subtopic == None:
        raise PreventUpdate
    subtopic = subtopic["label"]
    cluster_elem = [dash.html.H2("Subtopic Clusters", className="graph_title"),
                    dash.html.P("These clusters are determined by politicians' voting patterns for the chosen sub-topic.", 
                    style={"font-size":"small", "padding-left":"2rem"}),
                    dash.html.B("You can click a cluster (section of the pie chart) for further exploration.",
                    style={"font-size":"small", "padding-left":"2rem"})]
    # Retrieve and filter the data
    cluster_df = pd.read_csv("./data/clusters/viz_clusters.csv")
    top_df = cluster_df[cluster_df["topic"] == topic]
    sub_df = top_df[top_df["subtopic"] == subtopic].iloc[0:3]
    cluster_nums = [i for i in range(3)]
    cluster_pie = go.Figure(data=go.Pie(labels=cluster_nums, values=sub_df["total_members"], text=cluster_nums, hovertemplate="Cluster %{text}" + "<br>Number of Members: %{value}</br>",
                                    marker_colors=sub_df["color"]), layout=go.Layout(paper_bgcolor='#e3ebf0', margin=dict(
        l=10,
        r=15,
        b=10,
        t=10,
        pad=4)))
    pie_comp = dash.dcc.Graph(figure=cluster_pie, style={"height":"65%","width":"100%"}, id="cluster_pie")
    cluster_elem.append(pie_comp)
    return cluster_elem

#@app.callback(
#    Output("footer", "children"),
#    Input("topic_dropdown", "value"),
#    Input("current_subtopic", "data"),
#    Input("cluster_pie", "clickData")
#)
#@timefunc
def get_current_cluster(topic, subtopic, cluster):
    """
    Takes in raw data from Dash callbacks for the topic dropdown, topic/subtopic graph, 
    and cluster pie chart, then formats them into a tuple ihe following format:

    (topic: str, subtopic: str, cluster: int)
    """
    if topic == None:
        return ("Government operations and politics", "Government employee pay", 0)
    if subtopic != None:
        subtopic = subtopic["label"]
    if cluster != None:
        cluster = int(cluster["points"][0]["label"])
    return (topic, subtopic, cluster)

# --- Get and display cluster details ---

@app.callback(
    Output("details", "children"),
    Input("current_topic", "data"),
    Input("current_subtopic", "data"),
    Input("current_cluster", "data")
)
def render_community_details(topic, subtopic, cluster=None):
    """
    Renders community details (lobbyists, legislor relationships) for the currently selected community 
    in the knowledge graph
    """
    topic, subtopic, cluster = get_current_cluster(topic, subtopic, cluster)
    cluster_stats = dash.html.Div(get_cluster_stats(topic, subtopic, cluster), id="cluster_stats")
    children = [dash.html.Div([dash.html.H2(f"Cluster {cluster} Details", style={"padding-top":"0.3em"})], id="details_title"),
                get_cluster_people(topic, subtopic, cluster), cluster_stats]
                #dash.html.Div(id="cluster_stats")] TODO: Replace the above with this after impelementing the appropriate
                # callback for get_cluster_stats()
    return children

def get_cluster_people(topic = "Government operations and politics", subtopic = "Government employee pay", cluster = 0):
    """
    Retrieve the congress people from the knowledge graph connected to the currently selected cluster,
    then render the associated HTML elements based on the retrieved data.


    """
    people_elements = [dash.html.H2("Most Influential Cluster Members", id="member_title")]
    # Congress members
    if topic == None or cluster == None:
        return people_elements

    people_df = pd.read_csv("./data/results/q9_most_influential_members.csv")
   
    top_df = people_df[people_df["topic"] == topic]
    sub_df = top_df[top_df["subtopic"] == subtopic]

    li = []

    for i in range(1,6):
        name = sub_df.iloc[cluster]["name_rank_" + str(i)]
        count = sub_df.iloc[cluster]["count_rank_" + str(i)]
        li.append(dash.html.Li(name, className="congress_member"))
        li.append(dash.html.Li(f"{count} bills sponsored", className="bills_sponsored"))

    congress_list = dash.html.Ul(li, id="congress_list")
    people_elements.append(congress_list)

    people = dash.html.Div(people_elements, id="people")
    return people

def get_member_parties(topic=None, subtopic=None, cluster=None):
    """
    Retrieve statistics about the parties of members in the currently selected cluster,
    then render the associated HTML elements based on the retrieved data.

    TODO: Implement this function
    """
    # Retrieve and filter our data
    member_parties_df = pd.read_csv("./data/results/q1_party_distribution.csv")
    if subtopic == None or cluster == None:
        raise PreventUpdate
    top_df = member_parties_df[member_parties_df["topic"] == topic]
    sub_df = top_df[top_df["subtopic"] == subtopic]

    # Organize it into a format we can visualize
    num_dem = sub_df.iloc[cluster]["D"]
    num_rep = sub_df.iloc[cluster]["R"]
    num_other = sub_df.iloc[cluster]["I"] + sub_df.iloc[cluster]["ID"]
    counts = [num_dem, num_rep, num_other]
    colors = ["#092573","#8F0303","#500973"]
    parties = ["Democratic","Republican","Independent"]

    party_pie = go.Figure(data=go.Pie(labels=parties, values=counts,
                                    marker_colors=colors), layout=go.Layout(paper_bgcolor='#fff1f1', margin=dict(
        l=10,
        r=15,
        b=10,
        t=10,
        pad=4
    )))
    party_elements =[
        dash.html.H4("Party composition:"),
        dash.dcc.Graph(figure=party_pie, style={"height":"80%", "width":"80%", "padding-top":"1em"})
    ]
    return party_elements

def get_common_lobbyists(topic=None, subtopic=None, cluster=None):
    """
    Retrieve statistics about the parties of members in the currently selected cluster,
    then render the associated HTML elements based on the retrieved data.
    """
    if subtopic == None or cluster == None:
        raise PreventUpdate
    topic_elements = [
        dash.html.H4("Common Lobbyists")
    ]

    lobbyist_df = pd.read_csv("./data/results/q3_most_important_lobbyists.csv")
    cluster_df = pd.read_csv("./data/clusters/viz_clusters.csv")

    # We have to retrieve and calculate the cluster size
    ct_df = cluster_df[cluster_df["topic"] == topic]
    clusters_df = ct_df[ct_df["subtopic"] == subtopic]
    total_members = clusters_df[clusters_df["cluster_id"] == cluster]["total_members"]
    total_members = total_members.iloc[0]
    
    top_df = lobbyist_df[lobbyist_df["topic"] == topic]
    sub_df = top_df[top_df["subtopic"] == subtopic]

    count = []
    name = []

    for i in range(1,6):
        count.append(sub_df.iloc[cluster]["count_rank_" + str(i)]/total_members)
        name.append(sub_df.iloc[cluster]["name_rank_" + str(i)])

    layout = go.Layout(
        xaxis=dict(
            showticklabels=False
        ),
        margin=dict(
        l=10,
        r=15,
        b=10,
        t=10,
        pad=4),
        paper_bgcolor='#fff1f1',
        yaxis=dict(
            title_text="Fraction of Group"
        )
    )
    topic_bar= go.Figure(data=go.Bar(x=name, y=count, marker_color="#756bb1"), layout=layout)
    topic_bar.update_layout(autosize=False, width=300, height=300)
    topic_comp = dash.dcc.Graph(figure=topic_bar)
    topic_elements.append(topic_comp)

    return topic_elements

def get_common_committees(topic=None, subtopic=None, cluster=None):
    """
    Retrieve statistics about the committees with members in the currently selected cluster,
    then render the associated HTML elements based on the retrieved data.

    TODO: Implement this function
    """
    if subtopic == None or cluster == None:
        raise PreventUpdate

    committees_df = pd.read_csv("./data/results/q4.1_most_important_committees.csv")
    cluster_df = pd.read_csv("./data/clusters/viz_clusters.csv")

    # We have to retrieve and calculate the cluster size
    ct_df = cluster_df[cluster_df["topic"] == topic]
    clusters_df = ct_df[ct_df["subtopic"] == subtopic]
    total_members = clusters_df[clusters_df["cluster_id"] == cluster]["total_members"]
    total_members = total_members.iloc[0]

    top_df = committees_df[committees_df["topic"] == topic]
    sub_df = top_df[top_df["subtopic"] == subtopic]
    committee = []
    count = []

    for i in range(1,4):
        count.append(sub_df.iloc[cluster]["count_rank_" + str(i)]/total_members)
        committee.append(sub_df.iloc[cluster]["name_rank_" + str(i)])
    
    # We have to check for a string type - if it is NaN then it will be a float
    # so we can use empty string as a name
    names = [c[13:] if type(c) == str else "" for c in committee]
    layout = go.Layout(
        xaxis=dict(
            tickfont=dict(size=9),
            title_text="Committee Name"
        ),
        margin=dict(
        l=10,
        r=15,
        b=10,
        t=10,
        pad=4),
        paper_bgcolor='#fff1f1',
        yaxis=dict(
            title_text="Fraction of Group"
        )
    )
    committee_bar= go.Figure(data=go.Bar(x=names, y=count, marker_color="#756bb1"), layout=layout)
    committee_bar.update_layout(autosize=False, width=300, height=350)
    committee_elements = [
        dash.html.H4("Common Committees"),
        dash.dcc.Graph(figure=committee_bar, style={"height":"100%", "width":"50%"})
    ]
    return committee_elements

@timefunc
def get_cluster_stats(topic=None, subtopic=None, cluster=None):
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
    member_parties = dash.html.Div(get_member_parties(topic, subtopic, cluster), id="member_parties")
    common_lobbyists = dash.html.Div(get_common_lobbyists(topic, subtopic, cluster), id="common_lobbyists")
    common_committees = dash.html.Div(get_common_committees(topic, subtopic, cluster), id="common_committees")
    return [member_parties, common_lobbyists, common_committees]

@app.callback(
    Output("current_topic_text", "children"),
    Input("current_topic", "data"),
    prevent_initial_call=True
)
def update_topic_text(topic=None):
    if topic == None:
        raise PreventUpdate
    topic_text = dash.html.P(topic, className="header_element", style={"font-size":"small"})
    return topic_text

@app.callback(
    Output("current_subtopic_text", "children"),
    Input("current_subtopic", "data"),
    prevent_initial_call=True
)
def update_subtopic_text(subtopic=None):
    if subtopic == None:
        raise PreventUpdate
    subtopic = subtopic["label"]
    topic_text = dash.html.P(subtopic, className="header_element", style={"font-size":"small"})
    return topic_text

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
    details = dash.html.Div([], id="details", className="container")
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
        dash.dcc.Store(id="current_subtopic", data=None),
        dash.dcc.Store(id="current_cluster", data=None),
        dash.dcc.Store(id="current_topic", data=None),
        # Banner for top of the page
        dash.html.Div([
            dash.html.Div([
                dash.html.H1("REP-G", id="title", className="header_element")
                ], style={"width":"100%"}),
            dash.html.Div([
                dash.html.P("Select a topic to explore!", className="header_element")
                ], style={"width":"100%"}),
            dash.html.Div([
                dash.dcc.Dropdown(SUBJECTS, SUBJECTS[0], id="topic_dropdown")
                ],className="dd-container", style={"width":"150%", "padding-left":"1rem"}),
            dash.html.B("Current topic:", className="header_element", style={"padding-left":"1rem"}),
            dash.html.Div([], id="current_topic_text", style={"width":"100%"}),
            dash.html.B("Current subtopic:", className="header_element", style={"padding-left":"1rem"}),
            dash.html.Div([], id="current_subtopic_text", style={"width":"100%"}),
            dash.html.P("Help", className="header_element", id="help")],
            id="banner"),
        # Main container that holds each of the main application views
        dash.html.Div(render_parent_container(), id="parent_container"),
        dash.html.Div(id="footer"),
        render_instructions()
    ], 
    id="main-container")

app.layout = render_layout()

if __name__ == '__main__':
    app.run_server(debug=False)
