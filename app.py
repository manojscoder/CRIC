from flask import Flask, render_template, request, redirect, url_for
from markupsafe import Markup
import pymysql as sql

app = Flask(__name__)

db = sql.connect(host="localhost", user="root", password="root", database="cricket")
cursor = db.cursor()


@app.route('/')
def home():
    cursor = db.cursor()
    cursor.execute('select * from live_match')
    match = cursor.fetchone()

    if match:
        cursor.execute('select * from score_table')
        data = list(cursor.fetchone())

        cursor.execute(f'select * from {match[2]}_batting limit 2')
        batting_scores = cursor.fetchall()

        cursor.execute(f'select * from {match[3]}_bowling limit 1')
        bowling_figures = list(cursor.fetchone())
        bowling_figures[2] = cal_over(bowling_figures[2])
        print(data[4], data[2])
        balls, data[2], data[3], data[4] = data[4], cal_over(data[2]), cal_over(data[3]), cal_over(data[4])
        return render_template('home.html', d = match, d1 = data, balls = balls, bat = batting_scores, bowl = bowling_figures)
    else:
        return render_template('home1.html')
    # return render_template('home.html')

@app.route('/admin_login')
def login():
    restart()
    return render_template('admin_login.html')

@app.route('/match')
def match():
    cursor.execute('select * from previous_matches')
    data = cursor.fetchall()

    return render_template('Match.html', d = data)

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/table')
def table():
    return render_template('table.html')

@app.route('/players')
def players():
    return render_template('players.html')


def cal_over(n):
    return (n // 6) + (n % 6 / 10)

def restart():
    cursor.execute('select 1 from information_schema.tables where table_schema = %s and  table_name = %s', ('cricket', 'score_table'))
    result = cursor.fetchone()

    if result:
        cursor.execute('select * from live_match limit 1')
        data = cursor.fetchone()

        for i in range(2):
            cursor.execute(f'drop table {data[i]}_batting')
            cursor.execute(f'drop table {data[i]}_bowling')
        
        cursor.execute('truncate table live_match')
        cursor.execute('drop table score_table')
            

@app.route('/live_1')
def live_1():
    cursor = db.cursor()
    cursor.execute('select * from live_match')
    match = cursor.fetchone()

    if match:
        cursor.execute('select * from score_table')
        data = list(cursor.fetchone())

        cursor.execute(f'select * from {match[2]}_batting limit 9')#2
        batting_scores = cursor.fetchall()

        cursor.execute(f'select * from {match[3]}_bowling limit 5')#1
        bowling_figures = [list(d) for d in cursor.fetchall()]
        for i in range(len(bowling_figures)):
            bowling_figures[i][2] = cal_over(bowling_figures[i][2])
        print(data[4], data[2])
        balls, data[2], data[3], data[4] = data[4], cal_over(data[2]), cal_over(data[3]), cal_over(data[4])
        print(bowling_figures)
        return render_template('final.html', d = match, d1 = data, balls = balls, bat = batting_scores, bowl = bowling_figures)
    else:
        return render_template('no_live.html')
    # return render_template('live.html')

@app.route('/live_2')
def live_2():
    cursor = db.cursor()
    cursor.execute('select * from live_match')
    match = cursor.fetchone()

    if match:
        cursor.execute('select * from score_table')
        data = list(cursor.fetchone())

        cursor.execute(f'select * from {match[3]}_batting limit 9')
        batting_scores = cursor.fetchall()

        cursor.execute(f'select * from {match[2]}_bowling limit 5')
        bowling_figures = [list(d) for d in cursor.fetchall()]
        for i in range(len(bowling_figures)):
            bowling_figures[i][2] = cal_over(bowling_figures[i][2])
        print(data[4], data[2])
        balls, data[2], data[3], data[4] = data[4], cal_over(data[2]), cal_over(data[3]), cal_over(data[4])
        print(bowling_figures)
        return render_template('final_1.html', d = match, d1 = data, balls = balls, bat = batting_scores, bowl = bowling_figures)
    else:
        return render_template('no_live.html')

@app.route('/complete_match')
def complete():
    cursor.execute('select * from live_match')
    d1 = list(cursor.fetchone())
    d1[0] = str(d1[0])

    cursor.execute('select * from score_table')
    d2 = list(cursor.fetchone())

    innings_won = 0
    d2[3] = cal_over(d2[3])
    d2[4] = cal_over(d2[4])

    if d2[0] < d2[1]:
        innings_won = 2
    else:
        innings_won = 1

    
    cursor.execute('select id from previous_matches where team1 = "TBC" order by id asc limit 1')
    row_id = cursor.fetchone()
    
    if row_id is None:
        cursor.execute('delete from previous_matches where id = 1')
        cursor.execute('INSERT INTO previous_matches (id, team1, team2, innings_won, score_team1, score_team2, wicket_team1, wicket_team2, overs_team1, overs_team2)VALUES (1, "TBC", "TBC", 0, 0, 0, 0, 0, 0.0, 0.0)')
        cursor.execute('select id from previous_matches where team1 = "TBC" order by id asc limit 1')
        row_id = cursor.fetchone()
    
    
    cursor.execute('update previous_matches set team1 = %s, team2 = %s, innings_won = %s, score_team1 = %s, score_team2 = %s, wicket_team1 = %s, wicket_team2 = %s, overs_team1 = %s, overs_team2 = %s where id = %s',(d1[2], d1[3], innings_won, d2[0], d2[1], d2[5], d2[6], d2[3], d2[4], row_id[0]))
    db.commit()

    restart()
    return redirect(url_for('admin_home'))

@app.route('/admin_login', methods=['POST'])
def admin_login():
    admin_id = request.form['id']
    password = request.form['password']
    cursor.execute("SELECT * FROM admin where admin_id = %s AND password = %s", (admin_id, password))
    data = cursor.fetchone()

    if data:
        return redirect(url_for('admin_home'))
    else:
        return redirect(url_for('login'))
    

@app.route('/admin_home')
def admin_home():
    return render_template('admin_home.html')


@app.route('/select_teams')
def select_teams():
    return render_template('admin2.o.html')



@app.route('/process_toss', methods=['POST'])
def process_toss():
    restart()
    team1, team2, overs = request.form['team1'], request.form['team2'], request.form['overs']
    toss_winner, toss_decision = request.form['toss_winner'], request.form['choice']
    bat, bowl, balls = team2, team1, int(overs) * 6

    # Team stadiums
    cursor = db.cursor()
    cursor.execute('select stadium_name from team_stadium where team_name = %s', (team1))
    stadium = cursor.fetchone()[0]

    if(toss_winner == team1 and toss_decision == 'Bat') or (toss_winner == team2 and toss_decision == 'Bowl'):
        bat = team1
        bowl = team2

    cursor.execute(f'insert into live_match values(%s, %s, %s, %s, %s, %s, %s, %s)', (str(team1), str(team2), str(bat), str(bowl), str(toss_winner),str(toss_decision), str(overs), str(stadium)))
    db.commit()

    cursor.execute(f'create table score_table({str(bat)}_score int, {str(bowl)}_score int, max_balls int, {str(bat)}_balls int, {str(bowl)}_balls int, {str(bat)}_wickets int, {str(bowl)}_wickets int, winning_score int)')
    db.commit()

    cursor.execute(f'insert into score_table values({0}, {0}, {balls}, {0}, {0}, {0}, {0}, {0})')
    db.commit()

    for team in [team1, team2]:
        # Batting table for both the teams
        cursor.execute(f'create table {team}_batting(id int primary key, name varchar(20), runs int, balls int, four int, six int, out_col int, strike_rate decimal(5, 2), foreign key(id) references {team}(id))')
        db.commit()

        # Inserting details of batters of both the team
        cursor.execute(f'insert into {team}_batting(id, name, runs, balls, four, six, out_col, strike_rate)select id, name, 0, 0, 0, 0, 0, 0.0 from {team}')
        db.commit()

        # Bowling table for both the teams
        cursor.execute(f'create table {team}_bowling(id int primary key, name varchar(20), balls int, runs int, wickets int, foreign key(id) references {team}_b(id))')
        db.commit()

        # Inserting details of bowlers of both the teams
        cursor.execute(f'insert into {team}_bowling(id, name, balls, runs, wickets)select id, name, 0, 0, 0 from {team}_b')
        db.commit()

    with db.cursor() as cursor:
        # cursor.execute('update rcb set name = "John" where id = 1')
        cursor.execute(f'select id, name from {bat}')
        players = list(list(i) for i in cursor.fetchall()[:9])
        
        cursor.execute(f'select id, name from {bowl}_b')
        bowlers = list(cursor.fetchall())

        for i in range(len(bowlers)):
            players.insert(i * 2 + 1, list(bowlers[i]))

        for i in range(0, len(players)):
            if(i % 2 == 0 and i < 11) or (i > 10):
                players[i][0] += 10
        print(players)

    return render_template('admin_live_1.html', team = bat,d = players[:14], balls = balls, team2 = bowl, wickets = 8)



@app.route('/extra', methods = ['POST'])
def extra():
    run = request.form['extra']
    team1 = request.form['team1_name']
    innings = int(request.form['innings'])

    cursor.execute(f'update score_table set {team1}_score = {team1}_score + {run}')
    db.commit()

    if innings == 1:
        cursor.execute(f'update score_table set winning_score = winning_score + {run}')
        db.commit()

    return 'successful'


@app.route('/update_wicket', methods = ['POST'])
def update_wicket():
    batter_id = int(request.form['batter_id'])
    bowler_id = int(request.form['bowler_id'])
    bat_team = request.form['bat_team']
    bowl_team = request.form['bowl_team']

    cursor.execute(f'update {bowl_team}_bowling set wickets = wickets + 1, balls = balls + 1 where id = {bowler_id}')
    db.commit()

    cursor.execute(f'update {bat_team}_batting set out_col = 1, balls = balls + 1, strike_rate = round((runs / balls) * 100, 1) where id = {batter_id}')
    db.commit()

    cursor.execute(f'update score_table set {bat_team}_wickets = {bat_team}_wickets + 1, {bat_team}_balls = {bat_team}_balls + 1')
    db.commit()

    return 'successful'



@app.route('/update_runs', methods = ['POST'])
def update_runs():
    batter_id = int(request.form['id'])
    run = int(request.form['run'])
    team1 = request.form['team']
    team2 = request.form['team2_name']
    bowler_id = request.form['bowler_id']
    innings = int(request.form['innings'])
    print(innings)

    # Update four or six of particular batter
    if run == 4 or run == 6:
        if run == 4:
            cursor.execute(f'update {team1}_batting set four = four + 1 where id = {batter_id}')
        else:
            cursor.execute(f'update {team1}_batting set six = six + 1 where id = {batter_id}')
        db.commit()
    
    cursor.execute(f'update {team1}_batting set runs = runs + {run}, balls = balls + 1 where id = {batter_id}')
    db.commit()
    
    cursor.execute(f'update score_table set {team1}_score = {team1}_score + {run}, {team1}_balls = {team1}_balls + 1')
    db.commit()

    if innings == 1:
        cursor.execute(f'update score_table set winning_score = winning_score + {run}')
        db.commit()
    
    cursor.execute(f'update {team1}_batting set strike_rate = round((runs / balls) * 100, 1) where id = {batter_id}')
    db.commit()
    
    cursor.execute(f'update {team2}_bowling set runs = runs + {run}, balls = balls + 1 where id = {bowler_id}')
    db.commit()
    

    return "Successful"

@app.route('/finish_innings_1')
def innings_1():
    cursor.execute('select * from live_match')
    details = list(cursor.fetchone())
    balls = int(details[6]) * 6;team1 = details[3];team2 = details[2]

    cursor.execute(f'select id, name from {team1}')
    batters = list(list(i) for i in cursor.fetchall()[:9])

    cursor.execute(f'select id, name from {team2}_b')
    bowlers = list(cursor.fetchall())

    cursor.execute('select * from score_table')
    score = cursor.fetchone()[0]

    for i in range(len(bowlers)):
        batters.insert(i * 2 + 1, list(bowlers[i]))

    for i in range(0, len(batters)):
        if(i % 2 == 0 and i < 11) or (i > 10):
            batters[i][0] += 10
    print(batters)
    print(bowlers)

    return render_template('admin_live_2.html', team = team1,d = batters[:14], balls = balls, team2 = team2, wickets = 8, score = score + 1)





    # toss_winner = request.form['toss_winner']
    # toss_decision = request.form['choice']
    # team1 = request.form['team1']
    # team2 = request.form['team2']
    # return render_template('live.html', toss_winner = toss_winner, toss_decision = toss_decision, team1 = team1, team2 = team2)


    
# @app.route('/display_image', methods=['POSt'])
# def display_image():
#     file_name1 = request.form['file_name1']
#     file_name2 = request.form['file_name2']
#     return render_template('Match.html', file_name1 = file_name1, file_name2 = file_name2)

if __name__ == '__main__':
    app.run(debug=True)
