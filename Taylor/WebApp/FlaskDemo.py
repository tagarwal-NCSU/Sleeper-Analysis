from flask import Flask, request, url_for, render_template, redirect
import os
import requests

app = Flask(__name__)

@app.context_processor #allows CSS to update (bypass browser cache)
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/leagues")
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

@app.route("/dash")
def dash():
    league_id = request.args.get('league_id', "-")
    if str(league_id) == "-":
        return redirect(url_for(''))

    # Get data
    # df = ...

    # Build Fig
    # fig = px ...

    # Convert to JSON
    # graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Render template
    # render_template('dash.html', graphJSON=graphJSON)

    return f"<p> VIZ FOR {league_id} HERE </p>"

if __name__ == "__main__":
    app.run(debug = True)