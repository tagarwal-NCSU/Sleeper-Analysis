import requests
import pandas as pd

#get league rosters
URL = 'https://api.sleeper.app/v1/league/781936337963036672/rosters'
response = requests.get(URL)
roster = response.json()
roster = pd.DataFrame(roster)
roster = roster[["owner_id", "players"]]

#get users from the league
URL = 'https://api.sleeper.app/v1/league/781936337963036672/users'
response = requests.get(URL)
users = response.json()
users = pd.DataFrame(users)

#merge DF's using user/owner ids
rosterFull = users.merge(roster, how="inner", left_on="user_id", right_on = "owner_id")
rosterFull = rosterFull[["owner_id", "user_id", "players", "display_name"]]

#get players in sleeper's database
URL = 'https://api.sleeper.app/v1/players/nfl'
response = requests.get(URL)
players = response.json()
players = pd.DataFrame(players)
#getting stuck here with players having their own index and then a dictionary of results from the json/df
players = players.T
player