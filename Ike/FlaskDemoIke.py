from flask import Flask
from flask import request
import requests
import pandas as pd

app = Flask(__name__)

@app.route("/")
def hello_world():
    html = """
            <html>
                <h1>Sleeper Analysis</h1> 
                <form action="/home"> 
                    <label for="username">Username: </label>
                    <input type="text" id = "username" name = "username"></input> 
                    <input type="submit" value="Submit">
                </form>
            </html>
            """
    

    return html

@app.route("/home")
def home():
    # find user's sleeper username
    username = request.args.get('username', "-")
    URL = f"https://api.sleeper.app/v1/user/{username}"

    # find their corresponding sleeper user id    
    response = requests.get(URL)
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
    df = []
    i = 0
    while i < length:
        league_name = leagues[i]['name']
        df.append(league_name)
        i += 1
    # return string of df to be able to display them
    df = str(df)
    
    return df

app.run(debug = True)