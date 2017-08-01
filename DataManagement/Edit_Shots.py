#adds a column of whether another shot occured ten seconds before or after a shot
#ran this script in a screen so no slurm file


import pandas as pd; import numpy as np

all_shots = pd.read_csv('/data/mukherjeelab/RobertsonThesis/BasketballData/2016.NBA.Raw.SportVU.Game.Logs/all_games_csv/all_shots_test.csv')
all_shots = pd.concat([all_shots, pd.DataFrame(np.unique(np.arange(0, all_shots.shape[0])))], axis=1)
all_shots.columns = ['Unnamed: 0', 'X', 'PLAY', 'quarter', 'game_clock', 'makeInd', 'BlockInd', 'player_name', 'ID', 'shot_num']

all_shots['other_shot'] = '0'
games = np.unique(all_shots['ID'])
shots = pd.DataFrame(columns = ['index', 'Unnamed: 0', 'X', 'PLAY', 'quarter', 'game_clock', 'makeInd', 'BlockInd', 'player_name', 'ID', 'shot_num', 'other_shot'])
all_shots_new = pd.DataFrame(columns = ['index', 'Unnamed: 0', 'X', 'PLAY', 'quarter', 'game_clock', 'makeInd', 'BlockInd', 'player_name', 'ID', 'shot_num', 'other_shot'])


for i in range(0, games.shape[0]):
    print(i)
    data = all_shots.loc[all_shots['ID'] == games[i]]
    for j in range(1,5):
        quarter_data = data.loc[data['quarter'] == j].reset_index()
        for k in range(0, quarter_data.shape[0]):
            shot_time = quarter_data.loc[k, 'game_clock']
            num = quarter_data.loc[k, 'shot_num']
            quarter_data.loc[(quarter_data['game_clock'] >= shot_time -10) & (quarter_data['game_clock'] <= shot_time + 10) & (quarter_data['shot_num'] != num), 'other_shot'] = '1'
        shots = shots.append(quarter_data)
    shots.drop_duplicates(subset = [ 'X', 'PLAY', 'quarter', 'game_clock', 'makeInd', 'BlockInd', 'player_name', 'ID', 'shot_num', 'other_shot'])
    all_shots_new = all_shots_new.append(shots)

shots.to_csv('/data/mukherjeelab/RobertsonThesis/BasketballData/2016.NBA.Raw.SportVU.Game.Logs/all_games_csv/all_shots_2_test.csv')
