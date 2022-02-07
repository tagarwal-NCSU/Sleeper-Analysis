from flask import Flask, request, url_for, render_template, redirect, flash
import dash
import os
import requests
import pandas as pd
import json
import plotly
import plotly.express as px
from dash import dcc, html
import numpy as np

# Visualization Example Here:
# https://towardsdatascience.com/web-visualization-with-plotly-and-flask-3660abf9c946

server = Flask(__name__)
app = dash.Dash(__name__, server=server, url_base_pathname="/null/")
app.layout = html.Div()

URL = "https://api.sleeper.app/v1/players/nfl"
response = requests.get(URL)
PLAYER_DICTIONARY = response.json()

# Create a list of all stats that need to be fetched

# These come from the Player dictionary, and must be explicitly added to the loop @ **Position 1**
identifiers = ["Owner", "Week", "Player", "player_id", "age", "position"]

# These will automatically be added to the stats
default_stats = ["gp", "off_snp", "tm_off_snp", "pts_ppr", "pts_half_ppr", "pts_std"]
rush_stats = ["rush_att", "rush_yd", "rush_yac", "rush_rz_att", "rush_td"]
rec_stats = ["rec_tgt", "rec", "rec_yd", "rec_yar", "rec_rz_tgt", "rec_td"]
pass_stats = ['pass_att', 'pass_yd', 'pass_cmp', 'pass_rz_att', 'pass_2pt', 'pass_int', 'pass_sack_yds', 'pass_td']
kick_stats = ['xpm', 'xpa', 'fgm', 'fga']
def_stats = ['sacks', 'fum_rec', 'int', 'def_td', 'yds_allow', 'pts_allow', 'blk_kick']
fumble_stats = ['fum', 'fum_lost']

stat_list = default_stats + rush_stats + rec_stats + pass_stats + def_stats + fumble_stats

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
        flash('That username is invalid')
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
    total_leagues = len(leagues) # find length of their #of leagues by looking at number of items within their leagues object
    if total_leagues > 5:
        height = 5
        width = total_leagues % 5
    else:
        height = total_leagues
        width = 1
    league_ids = [league['league_id'] for league in leagues]
    league_names = [league['name'] for league in leagues]
    return render_template("leagues.html", height = height, width = width, total_leagues = total_leagues, league_ids = league_ids, league_names = league_names)

@server.route("/viz")
def viz():
    league_id = request.args.get('league_id', "-")
    if str(league_id) == "-":
        return redirect(url_for(''))

    stats = fetch_data(league_id)

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

def fetch_data(league_id):
    # Fetch League Metadata
    URL = f"https://api.sleeper.app/v1/league/{league_id}"
    response = requests.get(URL)
    league = response.json()

    # Fetch infomation about users in the league
    URL = f"https://api.sleeper.app/v1/league/{league_id}/users"
    response = requests.get(URL)
    users = response.json()

    # Fetch information about current rosters in the league
    URL = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
    response = requests.get(URL)
    rosters = response.json()

    # Get league name and league season
    league_name = league['name']
    season = league['season']
    playoff_week = league['settings']['playoff_week_start']

    # Create a lookup dictionary connecting owner usernames to their roster players
    owner_players = [[PLAYER_DICTIONARY[player_id] for player_id in roster['players']] for roster in rosters]
    owner_ids = [roster['owner_id'] for roster in rosters]
    ownerid2name = {owner['user_id']: owner['display_name'] for owner in users}
    owner2players = {ownerid2name[owner_ids[i]]: owner_players[i] for i in range(len(owner_ids))}
    
    # Initialize the Dataframe
    df = []

    # For each week in the regular season...
    for week in range(1, playoff_week+1):
        # Extract player stats for that week
        URL = f"https://api.sleeper.app/v1/stats/nfl/regular/{season}/{week}"
        response = requests.get(URL)
        stats = response.json()
        # For each player in owners' rosters...
        for owner, players in owner2players.items():
            for player in players:
                # Extract identifiers for the current player
                player_id = player['player_id']
                if 'age' in player:
                    player_age = player['age']
                else:
                    player_age = np.nan
                player_name = player['first_name'] + ' ' + player['last_name']
                player_position = player['position']
                # **Position 1**
                row = [owner, week, player_name, player_id, player_age, player_position]
                # Extract stats for the player, if they played that week
                if player_id in stats:
                    player_stats = stats[player_id]
                    # If the stat exists in player stats, extract the stat, otherwise put NaN
                    row += [player_stats[stat] if stat in player_stats else np.nan for stat in stat_list]
                # If the player did not play that week
                else:
                    # Make the entire row NaN
                    row += [np.nan] * len(stat_list)
                # Add the row to the Dataframe
                df.append(row)

    #Build the Dataframe
    columns = identifiers + stat_list
    df = pd.DataFrame(df, columns = columns)

    # Extract season-long stats
    URL = f"https://api.sleeper.app/v1/stats/nfl/regular/{season}"
    response = requests.get(URL)
    stats = response.json()

    # Initialize the Dataframe
    df_season = []

    # For each player in owners' rosters...
    for owner, players in owner2players.items():
        for player in players:
            # Extract identifying information
            player_id = player['player_id']
            if 'age' in player:
                player_age = player['age']
            else:
                player_age = np.nan
            player_name = player['first_name'] + ' ' + player['last_name']
            player_position = player['position']
            row = [owner, "Season", player_name, player_id, player_age, player_position]
            if player_id in stats:
                player_stats = stats[player_id]
                row += [player_stats[stat] if stat in player_stats else np.nan for stat in stat_list]
            else:
                row += [np.nan] * len(stat_list)
            df_season.append(row)

    # Build the Dataframe
    df_season = pd.DataFrame(df_season, columns = columns)

    stats = pd.concat([df, df_season])

    return stats

server.run(debug = True)