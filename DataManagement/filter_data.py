import pandas as pd
import numpy as np
time_before = 5; time_before_2 = 10; time_after = 5
import pandas as pd; import numpy as np; import sklearn; import math
from sklearn.metrics.pairwise import paired_distances
from math import acos
from math import sqrt
from math import pi


#importing the schedule and shot time files
schedule = pd.read_csv('/data/mukherjeelab/RobertsonThesis/BasketballData/2016.NBA.Raw.SportVU.Game.Logs/all_games_csv/NBA_Schedule.csv')
schedule['date'] = pd.to_datetime(schedule['date'])
schedule['new_date'] = '0'
for k in range(0, schedule.shape[0]):
    schedule.loc[k, 'new_date'] = str(schedule.loc[k]['date']).split(' ')[0]
schedule['home_team'] = schedule['home_team'].map(str.strip)
schedule['away_team'] = schedule['away_team'].map(str.strip)
schedule = schedule.replace(['WSH', 'SA', 'GS', 'New  York', 'Clevaland', 'NY', 'NO', 'UTAH'], ['WAS','SAS', 'GSW', 'NYK', 'CLE', 'NYK', 'NOP', 'UTA'])


#loading data frame of all the shots and play stops
all_shots = pd.read_csv('/data/mukherjeelab/RobertsonThesis/BasketballData/2016.NBA.Raw.SportVU.Game.Logs/all_games_csv/all_shots_fixed.csv')
all_play_stops = pd.read_csv('/data/mukherjeelab/RobertsonThesis/BasketballData/2016.NBA.Raw.SportVU.Game.Logs/all_games_csv/all_play_stops_fixed.csv')

#empty data frame to store the shot data
all_game_shots = pd.DataFrame()

#function to get game data
#creates data frame with times/quarters of shots to match on  - used to filter moments
def get_game_data(game_shots, game_date):
    game_data = pd.DataFrame(columns = ['game_clock', 'time_vec', 'make', 'quarter'])
    for i in range(0, len(game_shots)):
        shot_time = game_shots.loc[i, 'game_clock']
        valid_times_1 = np.arange(game_shots.loc[i, 'game_clock'] + time_before, game_shots.loc[i, 'game_clock'] - time_after, -0.01)
        valid_times_2 = np.arange(game_shots.loc[i, 'game_clock'] + time_before_2, game_shots.loc[i, 'game_clock'] + time_before + 0.01, -0.01)
        time_vec = ['10']*len(valid_times_2) + ['5']*len(valid_times_1)
        valid_times = valid_times_2.tolist() + valid_times_1.tolist()
        make_vec = [game_shots.loc[i, 'makeInd']]*len(valid_times)
        shot_num = [game_shots.loc[i, 'shot_num']]*len(valid_times)
        quarter = [game_shots.loc[i, 'quarter']]*len(valid_times)
        gdate = [game_date]*len(valid_times)
        shooter = [game_shots.loc[i, 'player_name']]*len(valid_times)
        other_shot = [game_shots.loc[i,'other_shot']]*len(valid_times)
        shot_time = [game_shots.loc[i, 'game_clock']]*len(valid_times)
        ID_vec = [game_shots.loc[i,'ID']]*len(valid_times)
        shot_data = pd.DataFrame({'shot_num': shot_num, 'game_clock': valid_times, 'time_vec':time_vec, 'make_vec':make_vec, 'quarter':quarter, 'game_date':gdate,'other_shot':other_shot, 'shooter':shooter, 'shot_time':shot_time, 'ID':ID_vec})
        game_data = game_data.append(shot_data, ignore_index = True)
    return(game_data)

def get_stop_match(stops, time_before, time_after):
    stop_match = pd.DataFrame(columns = ['game_clock', 'quarter'])
    for i in range(0, stops.shape[0]):
        valid_times = np.arange(stops.iloc[i]['game_clock'] + time_before*100, stops.iloc[i]['game_clock'] - time_after*100 -1, -1)
        quarter = [stops.iloc[i]['quarter']]*len(valid_times)
        new = pd.DataFrame({'game_clock':valid_times, 'quarter':quarter})
        stop_match = stop_match.append(new, ignore_index = True)
    return(stop_match)

def rem_excess(all_game_shots):
    shots = all_game_shots.loc[all_game_shots['shot_ind'] == 1]
    shot_tots = pd.DataFrame(shots['shot_num'].value_counts())
    shot_tots.columns = ['total']
    more_than_one = shot_tots.loc[shot_tots['total'] > 3].index.tolist()
    all_game_shots = all_game_shots[~all_game_shots['shot_num'].isin(more_than_one)]
    return(all_game_shots)

#removing events
def rem_events(all_game_shots):
    games = np.unique(all_game_shots['ID'])
    for k in range(0, len(games)):
        print('Before removing events', len(np.unique(all_game_shots['shot_num'])))
        stops =  all_play_stops.loc[all_play_stops['ID'] == games[k]]
        stop_match = get_stop_match(stops, 10, 0)
        stop_match.game_clock = (stop_match.game_clock*100).astype(int)
        rem_match = all_game_shots.merge(stop_match, on=['game_clock','quarter'])
        drop_shots = np.unique(rem_match['shot_num'])
        all_game_shots = all_game_shots[~all_game_shots['shot_num'].isin(drop_shots)]
        print('After removing events:', len(np.unique(all_game_shots['shot_num'])))
    return(all_game_shots)



#looping through the games
def all_shots_get(num):
    all_game_shots = pd.DataFrame()
    for b in range(0,2):
        print(b)
        try:
            #extracting details
            home_team = schedule.loc[b, 'home_team'].strip();  away_team = schedule.loc[b, 'away_team'].strip();game_date = schedule.loc[b, 'new_date']
            ESPN_ID = int(schedule.loc[(schedule['new_date'] == game_date) & (schedule['home_team'] == home_team) & (schedule['away_team'] == away_team), 'ESPN_ID'])
            #moment ID for the game
            name = '/data/mukherjeelab/RobertsonThesis/BasketballData/2016.NBA.Raw.SportVU.Game.Logs/all_games_csv/' + game_date + '_' + home_team + '_' + away_team +'.csv'
            try:
                moments = pd.read_csv(name)
            except:
                print(name)
                continue
            #shot times for this game
            game_shots = all_shots.loc[all_shots['ID'] == ESPN_ID]; game_shots['game_clock'] = game_shots['game_clock']
            shot_num = pd.DataFrame(list(range(0, game_shots.shape[0])))
            game_shots = pd.concat([game_shots.reset_index(), shot_num], axis = 1, ignore_index = True)
            del game_shots[0]; del game_shots[1];del game_shots[2]; del game_shots[3]; del game_shots[4]; del game_shots[5]
            game_shots.columns = ['PLAY', 'quarter', 'game_clock', 'makeInd', 'BlockInd', 'player_name', 'ID', 'shot_num', 'other_shot', 'game_shot_num']
            game_shots['shot_time'] = game_shots['game_clock']
            #creating data frame of the valid times
            game_data = get_game_data(game_shots, game_date)
            game_data.game_clock = (game_data.game_clock*100).astype(int)
            moments.game_clock = (moments.game_clock*100).astype(int)
            curve_data = pd.merge(moments, game_data, how = 'inner', on = ['game_clock', 'quarter'])
            del curve_data['Unnamed: 0']
            curve_data = curve_data.drop_duplicates()
            curve_data = curve_data.reset_index()
            curve_data['shot_ind'] = '0'; del curve_data['index']
            keep_col = ['team_id', 'player_id', 'x_loc', 'y_loc', 'radius', 'game_clock', 'shot_clock', 'quarter', 'player_name', 'player_jersey', 'game_date', 'make', 'make_vec', 'shooter', 'shot_num', 'time_vec', 'shot_ind']
            curve_data = curve_data.sort('moment').drop_duplicates(subset = keep_col, take_last = True)
            #removing shots with too many observations
            print('Before dropping,', len(np.unique(curve_data['shot_num'])))
            tots = pd.DataFrame(curve_data['shot_num'].value_counts())
            drop_shots = tots.loc[tots[0] > 5000].index.tolist()
            curve_data = curve_data[~curve_data['shot_num'].isin(drop_shots)]
            #adding shot indicator
            final_num = np.unique(curve_data['shot_num'])
            player_shot_data = pd.DataFrame(columns = [])
            curve_data['shot_time'] = (curve_data['shot_time']*100).astype(int)
            for m in range(0, len(final_num)):
                shot = curve_data.loc[curve_data['shot_num'] == final_num[m]]
                shot['shot_ind'] = 0
                shooter = shot.iloc[0]['shooter']
                shot_time = shot.iloc[0]['shot_time']
                shot.loc[(shot['player_name'] == shooter) & (shot['game_clock'] <= shot_time + 2) & (shot['game_clock'] >= shot_time - 2), 'shot_ind'] = 1
                player_shot_data = player_shot_data.append(shot, ignore_index=True)
            player_shot_data = rem_excess(player_shot_data)
            player_shot_data = rem_events(player_shot_data)
            print("After dropping:", len(np.unique(player_shot_data['shot_num'])))
            all_game_shots = all_game_shots.append(player_shot_data, ignore_index=True)
        except:
            print(home_team, away_team, game_date, b)
            all_game_shots = []
    return(all_game_shots)

#fixing the moments
def same_team(data):
    shooter_df = data.loc[data['shot_ind'] == 1, 'player_name'].to_frame().reset_index()
    if shooter_df.shape[0] == 0:
        return(shooter_df, False)
    shooter = shooter_df.loc[0, 'player_name']
    team_id_df = pd.DataFrame(data.loc[data['player_name'] == shooter, 'team_id']).reset_index()
    team_id = team_id_df.loc[0, 'team_id']
    data['shooter_team'] = 0
    data.loc[data['team_id'] == team_id, 'shooter_team'] = 1
    return(data, shooter)
 
def fix_moments(mom_data):
    num = np.unique(mom_data['shot_num'])
    new_data = pd.DataFrame(columns =  ['team_id', 'player_id', 'x_loc', 'y_loc', 'radius', 'old_moment', 'game_clock', 'shot_clock', 'quarter', 'player_name', 'player_jersey', 'game_date', 'make', 'make_vec', 'other_shot', 'shooter', 'shot_num', 'shot_time', 'shot_ind', 'shooter_team', 'moment'])
    for i in range(0, len(num)):
        print(i)
        data = mom_data.loc[mom_data['shot_num'] == num[i]]
        #del data['Unnamed: 0']
        data, shooter = same_team(data)
        data = data.reset_index()
        del data['index']; del data['time_vec']
        data = data.drop_duplicates()
        data = data.sort(['quarter', 'game_clock'], ascending = [True, False])
        moment_vec = np.repeat(np.arange(0, data.shape[0]/11), 11)
        data  = pd.concat([data.reset_index(), pd.DataFrame(moment_vec).reset_index()], axis = 1, ignore_index=True)
        del data[0]; del data[21]
        data.columns = ['team_id', 'player_id', 'x_loc', 'y_loc', 'radius', 'old_moment', 'game_clock', 'shot_clock', 'quarter', 'player_name', 'player_jersey', 'game_date', 'make', 'make_vec', 'other_shot', 'shooter', 'shot_num', 'shot_time', 'shot_ind', 'shooter_team', 'moment']
        new_data = new_data.append(data, ignore_index=True)
    return(new_data)

#identifying the new shot time
def find_shot_time(data):
    num = np.unique(data['shot_num'])
    for u in range(0, 1):
        one_shot = data.loc[data['shot_num'] == num[u]]
        orig_shot_time = one_shot.loc[one_shot['shot_ind'] == 1]['game_clock'].item()
        shooter = one_shot.iloc[0]['shooter']
        time_range = one_shot.loc[(one_shot['game_clock'] <= orig_shot_time) & (one_shot['game_clock'] >= orig_shot_time - 500)]
        player_ball = time_range.loc[(time_range['player_name'] == 'ball') | (time_range['player_name'] == shooter)]
        moms = np.unique(player_ball['moment'])
        time_dist = pd.DataFrame(columns = ['moment', 'distance'], index = np.arange(len(moms)))
        for p in range(0, len(moms)):
            sub = player_ball.loc[player_ball['moment'] == moms[p]]
            player_x = sub.loc[sub['player_name'] == shooter, ]['x_loc'].item()
            player_y = sub.loc[sub['player_name'] == shooter, ]['y_loc'].item()
            ball_x = sub.loc[sub['player_name'] == 'ball', ]['x_loc'].item()
            ball_y = sub.loc[sub['player_name'] == 'ball', ]['y_loc'].item()
            dist = paired_distances([player_x, player_y],[ball_x, ball_y])
            time_dist.loc[p, 'moment'] = moms[p]
            time_dist.loc[p, 'distance'] = dist
        return(time_dist)


all_game_shots = all_shots_get(schedule.shape[0]) 
all_game_shots.to_csv('/data/mukherjeelab/RobertsonThesis/BasketballData/2016.NBA.Raw.SportVU.Game.Logs/all_games_csv/motherfucker.csv')
new_data = fix_moments(al_game_shots)



#moments that need to be fixed
#some moments are missing the ball

shot_totals = pd.DataFrame(all_game_shots['shot_num'].value_counts())

#removing events
def rem_events(all_game_shots):
    games = np.unique(all_game_shots['ID'])
    for k in range(0, len(games)):
        print('Before removing events', len(np.unique(all_game_shots['shot_num'])))
        stops =  all_play_stops.loc[all_play_stops['ID'] == games[k]]
        stop_match = get_stop_match(stops, 10, 0)
        stop_match.game_clock = (stop_match.game_clock*100).astype(int)
        rem_match = all_game_shots.merge(stop_match, on=['game_clock','quarter'])
        drop_shots = np.unique(rem_match['shot_num'])
        all_game_shots = all_game_shots[~all_game_shots['shot_num'].isin(drop_shots)]
        print('After removing events:', len(np.unique(all_game_shots['shot_num'])))
    return(all_game_shots)

all_game_shots = rem_events(all_game_shots)

#need to fix moments
num = np.unique(all_game_shots['shot_num'])
shots_to_drop = []
for i in range(0, len(num)):
    data = all_game_shots.loc[all_game_shots['shot_num'] == num[i]]
    clock_tots = pd.DataFrame(data['game_clock'].value_counts())
    extra = clock_tots.loc[clock_tots[0] > 11].index.tolist()
    if len(extra) > 0:
        print(num[i])
        #check how many repeated times
        if max(clock_tots[0] > 33):
            shots_to_drop.append(num[i])
all_game_shots = all_game_shots[~all_game_shots['shot_num'].isin(shots_to_drop)]

for k in range(0, len(shots_to_fix)):
    print(k)

#need to identify the "true" shot time
num = np.unique(all_game_shots['shot_num'])
fixed_data = pd.DataFrame()
for m in range(0, len(num)):
    print(m)
    one_shot = all_game_shots.loc[all_game_shots['shot_num'] == num[m]]
    orig_shot_time_df = one_shot.loc[one_shot['shot_ind'] == 1]
    orig_shot_time = orig_shot_time_df.iloc[0]['game_clock'].item()
    shooter = one_shot.iloc[0]['shooter']
    time_range = one_shot.loc[(one_shot['game_clock'] <= orig_shot_time + 500) & (one_shot['game_clock'] >= orig_shot_time - 500)]
    tr = time_range.loc[(time_range['player_name'] == 'ball') | (time_range['player_name'] == shooter)]
    moms = np.unique(tr['moment'])
    dist_mat = pd.DataFrame(columns = ['moment', 'dist', 'shot_clock'], index = np.arange(len(moms)))
    for k in range(0, len(moms)):
        print(k)
        print(diff_data.shape)
        diff_data = tr.loc[tr['moment'] == moms[k]]
        if diff_data.shape[0] > 2:
            diffs = []
            shot_clock = np.unique(diff_data['shot_clock'])
            for p in range(0, len(shot_clock)):
                diff_shot = diff_data.loc[diff_data['shot_clock'] == shot_clock[p]]
                ball_loc = diff_shot.loc[diff_shot['player_name'] == 'ball', ['x_loc', 'y_loc']]
                shooter_loc = diff_shot.loc[diff_shot['player_name'] == shooter, ['x_loc', 'y_loc']]
                diffs.append(paired_distances(ball_loc, shooter_loc))
            dist_mat.loc[k, 'moment'] = moms[k]
            dist_mat.loc[k, 'dist'] = min(diffs)
            dist_mat.loc[k, 'shot_clock'] = shot_clock[np.argmin(diffs)]
        else:
            ball_loc = diff_data.loc[diff_data['player_name'] == 'ball', ['x_loc', 'y_loc']]
            shooter_loc = diff_data.loc[diff_data['player_name'] == shooter, ['x_loc', 'y_loc']]
            dist = paired_distances(ball_loc, shooter_loc)
            dist_mat.loc[k, 'moment'] = moms[k]
            dist_mat.loc[k, 'dist'] = dist
            dist_mat.loc[k, 'shot_clock'] = diff_data.iloc[0]['shot_clock']
    #getting the new shot time that is the minimum distance during the time
    shot_mom_df = dist_mat.loc[dist_mat['dist'] == min(dist_mat['dist'])[0]]['moment'].item()
    shot_time = one_shot.loc[one_shot['moment'] == shot_mom, 'game_clock'].iloc[0]
    new_data = one_shot.loc[(one_shot['game_clock'] >= shot_time) & (one_shot['game_clock'] <= shot_time + 10*100)]
    new_data.loc[(new_data['game_clock'] == shot_time) & (new_data['player_name'] == shooter), 'shot_ind'] = 1
    fixed_data  = fixed_data.append(new_data, ignore_index = True)
#what about fixing moments?

fixed_data.to_csv('/data/mukherjeelab/RobertsonThesis/BasketballData/2016.NBA.Raw.SportVU.Game.Logs/all_games_csv/fixed_data.csv')

