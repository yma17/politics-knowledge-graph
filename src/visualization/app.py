import dash

app = dash.Dash(__name__)

app.layout = dash.html.Div([
    dash.html.H1("test")
])

if __name__ == '__main__':
    app.run_server(debug=True)