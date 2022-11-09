import dash
import dash_cytoscape as cyto

app = dash.Dash(__name__)
app.title = "REP-G"
server = app.server

test_graph = [
    {'data': {'id': 'one', 'label': 'Node 1'}},
    {'data': {'id': 'two', 'label': 'Node 2'}},
    {'data': {'source': 'one', 'target': 'two'}}
]

def show_instructions():
    # We should definitely have a popup on load that shows how to use the app
    # so people don't get lost in the multiple layouts
    return

def render_topic_graph():
    """
    Renders the subgraph containing topics from the knowledge graph
    """
    graph = cyto.Cytoscape(
        elements=test_graph,
        style={'width': '100%', 'height': '400px'},
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

def render_layout() -> None:
    return dash.html.Div([
        # Banner for top of the page
        dash.html.Div([
            dash.html.H1("REP-G", id="title"), 
            dash.html.A("Help"), 
            dash.html.A("About")], 
            id="banner"),
        # Main container that holds each of the main application views
        dash.html.Div([
            render_topic_graph(),
            render_community_graph(),
            render_community_details()
        ], id="parent_container"),
        dash.html.Div(id="footer")
    ], 
    id="main-container")

app.layout = render_layout()

if __name__ == '__main__':
    app.run_server(debug=True)