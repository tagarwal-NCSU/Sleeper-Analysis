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
    username = request.args.get('username', "-")

    URL = f"https://api.sleeper.app/v1/user/{username}"
    response = requests.get(URL)
    user_id = response.json()
    user_id = user_id['user_id']

    season = '2021'
    sport = 'nfl'
    URL = f"https://api.sleeper.app/v1/user/{user_id}/leagues/{sport}/{season}"
    response = requests.get(URL)
    leagues = response.json()    
    
    length = len(leagues)
    df = []
    i = 0
    while i < length:
        league = leagues[i]['name']
        df.append(league)
        i += 1
    df = str(df)
    
    return df

app.run(debug = True)