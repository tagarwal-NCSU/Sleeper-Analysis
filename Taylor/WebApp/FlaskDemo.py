from flask import Flask, request, url_for, render_template, redirect
import dash
import os
import requests
import pandas as pd
import json
import plotly
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html

# Visualization Example Here:
# https://towardsdatascience.com/web-visualization-with-plotly-and-flask-3660abf9c946

server = Flask(__name__)
app = dash.Dash(__name__, server=server)
app.layout = html.Div()

URL = "https://api.sleeper.app/v1/players/nfl"
response = requests.get(URL)
PLAYER_DICTIONARY = response.json()

@server.context_processor #allows CSS to update (bypass browser cache)
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(server.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

@server.route("/")
def home():
    return render_template("home.html")

@server.route("/leagues")
def leagues():
    # find user's sleeper username
    username = request.args.get('username', "-")
    URL = f"https://api.sleeper.app/v1/user/{username}"

    # find their corresponding sleeper user id    
    response = requests.get(URL)
    if response.status_code != 200: #If the username is invalid
        return redirect(url_for(''))
    user_id = response.json()
    user_id = user_id['user_id']

    # set season to 2021 to look at last year's response
    season = '2021'
    sport = 'nfl' #only sport currently possible for this API
    URL = f"https://api.sleeper.app/v1/user/{user_id}/leagues/{sport}/{season}"
    response = requests.get(URL)
    leagues = response.json()

    # create loop to pull out just their league names
    length = len(leagues) # find length of their #of leagues by looking at number of items within their leagues object
    league_ids = [league['league_id'] for league in leagues]
    league_names = [league['name'] for league in leagues]
    return render_template("leagues.html", length = length, league_ids = league_ids, league_names = league_names)

@server.route("/viz")
def viz():
    league_id = request.args.get('league_id', "-")
    if str(league_id) == "-":
        return redirect(url_for(''))
    
    #stats = result of API call

    df = pd.DataFrame({"Category": ["a", "b", "c"], "Value": [1, 2, 3]})

    # Build Fig
    fig = px.bar(df, x = "Category", y = "Value")

    df = pd.DataFrame({"Category": ["a", "b", "c"], "Value": [3, 2, 1]})

    # Build Fig
    fig2 = px.bar(df, x = "Category", y = "Value")

    app.layout = html.Div(children = [
        html.H1("Hello!"),
        dcc.Graph(
            id = 'example',
            figure = fig
            ),
        dcc.Graph(
            id = 'example',
            figure = fig2
            )
    ])
    # Render template
    return app.index()

if __name__ == "__main__":
    server.run(debug = True)