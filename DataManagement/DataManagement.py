#packages to import
import pandas as pd
import numpy as np
import os
import json

char_games = [21500026, 21500039, 21500053, 21500072, 21500090,21500111, 21500113, 21500147, 21500162, 21500165, 21500178, 21500202, 21500215, 21500227, 21500246, 21500268, 21500292, 21500304, 21500320, 21500338, 21500372, 21500382, 21500399, 21500415, 21500443, 21500458, 21500474, 21500492, 21500497, 21500520, 21500533, 21500550, 21500563, 21500577, 21500598, 21500616, 21500636, 21500645, 21500655]
#loop through all the games


for k in range(0, len(char_games)):
    
    game_num = str(char_games[k])
    print(game_num)
    #reading the json file
    name = '/data/mukherjeelab/RobertsonThesis/BasketballData/2016.NBA.Raw.SportVU.Game.Logs/json_games/' + game_num.zfill(10) + '.json'
    print(name) 
    try: 
        with open(name) as data_file:
            dict_1 = json.load(data_file)

    except FileNotFoundError: 
        print('except')
        continue


    #creating a pandas data frame for the game
    headers = ["team_id", "player_id", "x_loc", "y_loc", "radius", "moment", "game_clock", "shot_clock", "quarter", "player_name", "player_jersey"]
    headersShort = ["team_id", "player_id", "x_loc", "y_loc", "radius", "moment", "game_clock", "shot_clock", "quarter"]
    a = np.zeros(shape = (1,11))
    game = pd.DataFrame(a, columns = headers)


    game_date = dict_1['gamedate']
    game_id = dict_1['gameid']
    events = dict_1['events'] #list of dictionaries

    #getting the team information and the players
    home = events[0]['home']; visitor = events[0]['visitor']
    home_team = home['abbreviation']; away_team = visitor['abbreviation']
    players = home["players"]
    players.extend(visitor["players"])

    #creating a dictionary for player information
    id_dict = {}
    for player in players:
        id_dict[player['playerid']] = [player["firstname"]+" "+player["lastname"], player["jersey"]]
    id_dict.update({-1: ['ball', np.nan]}) #adding ID for the ball

    #looping through all of the events
    for i in range(0, len(events)):
        print(i)
        current_event = events[i]

        #going through all of the moments in each event
        moments = current_event['moments']

        #checking that moment is non-empty
        if len(moments) == 0:
            pass
        else:

            #create a separate list for the moments data for each player
            # Initialize our new list
            player_moments = []

            for moment in moments:
                # For each player/ball in the list found within each moment
                for player in moment[5]:
                    player.extend((moments.index(moment), moment[2], moment[3], moment[0]))
                    player_moments.append(player)
    
            df = pd.DataFrame(player_moments, columns = headersShort)

            #adding player information to the data frame
            try:
                df["player_name"] = df.player_id.map(lambda x: id_dict[x][0])
                df["player_jersey"] = df.player_id.map(lambda x: id_dict[x][1])
            except KeyError:
                continue

            #adding the new moment data frame to the rest of the game
            game = np.vstack((game, df))
            game = pd.DataFrame(game)


    game = game.ix[0:]
    game.columns = headers
    print('write file')
    file_name = '/data/mukherjeelab/RobertsonThesis/BasketballData/2016.NBA.Raw.SportVU.Game.Logs/all_games_csv/' + game_date + '_' + home_team + '_' + away_team  + '.csv' 
    game.to_csv(file_name)
