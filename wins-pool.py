from PandasBasketball import pandasbasketball as pb
import pandas
import config
import os

def team_fields(x) :
    historical = pb.get_team(x)
    current = historical.loc[historical[config.season] == config.nba_season][config.ind_headers]
    current = clean_up_blanks(current)
    return addGeneratedFields(current)

def addGeneratedFields(frame) :
    return getNetRating(frame)

def getNetRating(frame) :
    oRtg = frame[config.ortg].get(0)
    dRtg = frame[config.drtg].get(0)
    nRtg = round(oRtg - dRtg, 1)
    frame[config.nrtg] = pandas.Series([nRtg])
    return frame

def clean_up_blanks(frame) :
    if frame.iloc[0][config.wins] is '' :
        frame.iloc[0][config.wins] = '0'
        frame.iloc[0][config.loss] = '0'
        frame.iloc[0][config.ortg] = '0.0'
        frame.iloc[0][config.drtg] = '0.0'
        frame.iloc[0][config.wl] = '.000'

    frame.iloc[0][config.wins] = frame[config.wins].astype(int).get(0)
    frame.iloc[0][config.loss] = frame[config.loss].astype(int).get(0)
    frame.iloc[0][config.ortg] = frame[config.ortg].astype(float).get(0)
    frame.iloc[0][config.drtg] = frame[config.drtg].astype(float).get(0)

    return frame

def build_WP(s_arr) :
    mf = pandas.concat([team_fields(s_arr[0]),
                        team_fields(s_arr[1]),
                        team_fields(s_arr[2]),
                        team_fields(s_arr[3]),
                        team_fields(s_arr[4])], ignore_index=True)
    return mf.sort_values(by=[config.wl, config.wins], ascending=False)

def get_Totals(captain, teams) :
    wins = teams[config.wins].sum().astype(int)
    losses = teams[config.loss].sum().astype(int)

    nrtg = round(teams[config.nrtg].sum() / 5, 1)
    wl = str(round((wins / (wins + losses)), 3))

    return [captain, wins, losses, '.' + wl.split(".")[1], nrtg]

def get_gb_column(frame) :
    gb = [0]
    twins = frame.loc[config.first, config.wins]
    tloss = frame.loc[config.first, config.loss]
    gb.append(get_gb_val(twins, tloss, frame.loc[config.second, config.wins], frame.loc[config.second, config.loss]))
    gb.append(get_gb_val(twins, tloss, frame.loc[config.third, config.wins], frame.loc[config.third, config.loss]))
    gb.append(get_gb_val(twins, tloss, frame.loc[config.fourth, config.wins], frame.loc[config.fourth, config.loss]))
    return gb

def get_gb_val(twins, tloss, bwins, bloss) :
    return ((twins - tloss) - (bwins - bloss)) / 2

def get_master_list(t1, t2, t3, t4) :
    master = pandas.concat([t1,t2,t3,t4])
    return master.sort_values(by=[config.wl, config.wins], ascending=False)

print('Scraping NBA Data')
m_teams = build_WP(config.t_mike)
print('*')
t_teams = build_WP(config.t_turn)
print('* *')
b_teams = build_WP(config.t_bent)
print('* * *')
k_teams = build_WP(config.t_kyle)
print('* * * *')
master_frame = get_master_list(m_teams, t_teams, b_teams, k_teams)

m_totals = get_Totals(config.mike, m_teams)
t_totals = get_Totals(config.turn, t_teams)
b_totals = get_Totals(config.bent, b_teams)
k_totals = get_Totals(config.kyle, k_teams)
all_totals = [m_totals, t_totals, b_totals, k_totals]

final_frame = pandas.DataFrame(all_totals, columns = config.gl_headers)
final_frame.sort_values(by=[config.wl, config.wins], ascending=False, inplace=True)
final_frame.index = config.places
gb = get_gb_column(final_frame)
final_frame[config.gb] = gb

print('****************** GROUPS *********************')
print('MICHAEL')
print(m_teams.to_string(index=False))
print()
print('TURNER')
print(t_teams.to_string(index=False))
print()
print('KYLE')
print(k_teams.to_string(index=False))
print()
print('BENNETT')
print(b_teams.to_string(index=False))
print()
print('********** DRAFTED TEAMS STANDINGS ************')
print(master_frame.to_string(index=False))
print()
print('************** GROUP STANDINGS ****************')
print(final_frame)

html = m_teams.to_html()
text_file = open("/Users/mgoodell/Documents/side/wp/index.html", "w")
text_file.write(html)
text_file.close()
