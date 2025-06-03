from flask import render_template, request, redirect, url_for, flash, session, jsonify
from __init__ import app, db
from models import User, Venue, Tournament, Team, Player, Match, MatchResult
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@app.route('/')
def index():
    tournaments = Tournament.query.all()
    return render_template('index.html', tournaments=tournaments)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in first')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    tournaments = Tournament.query.all()
    venues = Venue.query.all()
    teams = Team.query.all()
    matches = Match.query.all()
    
    return render_template('dashboard.html', 
                           user=user, 
                           tournaments=tournaments, 
                           venues=venues,
                           teams=teams,
                           matches=matches)

# Tournament routes
@app.route('/tournaments')
def tournaments():
    tournaments = Tournament.query.all()
    return render_template('tournaments/list.html', tournaments=tournaments)

@app.route('/tournaments/new', methods=['GET', 'POST'])
def new_tournament():
    if 'user_id' not in session:
        flash('Please log in first')
        return redirect(url_for('login'))
        
    venues = Venue.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        sport_type = request.form.get('sport_type')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        venue_id = request.form.get('venue_id')
        
        tournament = Tournament(
            name=name,
            sport_type=sport_type,
            start_date=start_date,
            end_date=end_date,
            venue_id=venue_id,
            organizer_id=session['user_id']
        )
        
        db.session.add(tournament)
        db.session.commit()
        flash('Tournament created successfully!')
        return redirect(url_for('tournaments'))
        
    return render_template('tournaments/new.html', venues=venues)

@app.route('/tournaments/<int:id>')
def tournament_details(id):
    tournament = Tournament.query.get_or_404(id)
    teams = Team.query.filter_by(tournament_id=id).all()
    matches = Match.query.filter_by(tournament_id=id).all()
    return render_template('tournaments/details.html', tournament=tournament, teams=teams, matches=matches)

@app.route('/tournaments/<int:id>/edit', methods=['GET', 'POST'])
def edit_tournament(id):
    if 'user_id' not in session:
        flash('Please log in first')
        return redirect(url_for('login'))
        
    tournament = Tournament.query.get_or_404(id)
    venues = Venue.query.all()
    
    if request.method == 'POST':
        tournament.name = request.form.get('name')
        tournament.sport_type = request.form.get('sport_type')
        tournament.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        tournament.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        tournament.venue_id = request.form.get('venue_id')
        
        db.session.commit()
        flash('Tournament updated successfully!')
        return redirect(url_for('tournament_details', id=id))
        
    return render_template('tournaments/edit.html', tournament=tournament, venues=venues)

@app.route('/tournaments/<int:id>/delete', methods=['POST'])
def delete_tournament(id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('You do not have permission to delete tournaments')
        return redirect(url_for('tournaments'))
        
    tournament = Tournament.query.get_or_404(id)
    db.session.delete(tournament)
    db.session.commit()
    
    flash('Tournament deleted successfully')
    return redirect(url_for('tournaments'))

# Team routes
@app.route('/teams')
def teams():
    teams = Team.query.all()
    tournaments = Tournament.query.all()
    return render_template('teams/list.html', teams=teams, tournaments=tournaments)

@app.route('/teams/new', methods=['GET', 'POST'])
def new_team():
    if 'user_id' not in session:
        flash('Please log in first')
        return redirect(url_for('login'))
    
    tournaments = Tournament.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        tournament_id = request.form.get('tournament_id')
        
        team = Team(
            name=name,
            tournament_id=tournament_id
        )
        
        db.session.add(team)
        db.session.commit()
        flash('Team created successfully!')
        return redirect(url_for('teams'))
        
    return render_template('teams/new.html', tournaments=tournaments)

@app.route('/teams/<int:id>')
def team_details(id):
    team = Team.query.get_or_404(id)
    players = Player.query.filter_by(team_id=id).all()
    return render_template('teams/details.html', team=team, players=players)

@app.route('/teams/<int:id>/edit', methods=['GET', 'POST'])
def edit_team(id):
    if 'user_id' not in session:
        flash('Please log in first')
        return redirect(url_for('login'))
        
    team = Team.query.get_or_404(id)
    tournaments = Tournament.query.all()
    
    if request.method == 'POST':
        team.name = request.form.get('name')
        team.tournament_id = request.form.get('tournament_id')
        
        db.session.commit()
        flash('Team updated successfully!')
        return redirect(url_for('team_details', id=id))
        
    return render_template('teams/edit.html', team=team, tournaments=tournaments)

@app.route('/teams/<int:id>/delete', methods=['POST'])
def delete_team(id):
    if 'user_id' not in session:
        flash('Please log in first')
        return redirect(url_for('login'))
        
    team = Team.query.get_or_404(id)
    db.session.delete(team)
    db.session.commit()
    
    flash('Team deleted successfully')
    return redirect(url_for('teams'))

# Match routes
@app.route('/matches')
def matches():
    matches = Match.query.all()
    tournaments = Tournament.query.all()
    return render_template('matches/list.html', matches=matches, tournaments=tournaments)

@app.route('/matches/new', methods=['GET', 'POST'])
def new_match():
    if 'user_id' not in session:
        flash('Please log in first')
        return redirect(url_for('login'))
    
    tournaments = Tournament.query.all()
    teams = Team.query.all()
    
    if request.method == 'POST':
        tournament_id = request.form.get('tournament_id')
        team1_id = request.form.get('team1_id')
        team2_id = request.form.get('team2_id')
        match_date = datetime.strptime(request.form.get('match_date'), '%Y-%m-%d')
        
        match = Match(
            tournament_id=tournament_id,
            team1_id=team1_id,
            team2_id=team2_id,
            match_date=match_date,
            status='Scheduled'
        )
        
        db.session.add(match)
        db.session.commit()
        flash('Match created successfully!')
        return redirect(url_for('matches'))
        
    return render_template('matches/new.html', tournaments=tournaments, teams=teams)

@app.route('/matches/<int:id>/result', methods=['GET', 'POST'])
def match_result(id):
    match = Match.query.get_or_404(id)
    
    if request.method == 'POST':
        team1_score = int(request.form.get('team1_score'))
        team2_score = int(request.form.get('team2_score'))
        
        result = MatchResult(
            match_id=id,
            team1_score=team1_score,
            team2_score=team2_score
        )
        
        match.status = 'Completed'
        
        # Update team records
        team1 = Team.query.get(match.team1_id)
        team2 = Team.query.get(match.team2_id)
        
        if team1_score > team2_score:
            team1.wins += 1
            team2.losses += 1
        elif team2_score > team1_score:
            team2.wins += 1
            team1.losses += 1
        else:
            team1.draws += 1
            team2.draws += 1
        
        db.session.add(result)
        db.session.commit()
        flash('Match result recorded!')
        return redirect(url_for('matches'))
        
    return render_template('matches/result.html', match=match)

# Player routes
@app.route('/players/new', methods=['GET', 'POST'])
def new_player():
    if 'user_id' not in session:
        flash('Please log in first')
        return redirect(url_for('login'))
        
    teams = Team.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        position = request.form.get('position')
        team_id = request.form.get('team_id')
        
        player = Player(
            name=name,
            position=position,
            team_id=team_id
        )
        
        db.session.add(player)
        db.session.commit()
        flash('Player added successfully!')
        return redirect(url_for('team_details', id=team_id))
        
    return render_template('players/new.html', teams=teams)

# Venue routes
@app.route('/venues')
def venues():
    venues = Venue.query.all()
    return render_template('venues/list.html', venues=venues)

@app.route('/venues/new', methods=['GET', 'POST'])
def new_venue():
    if 'user_id' not in session:
        flash('Please log in first')
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        capacity = request.form.get('capacity')
        
        venue = Venue(
            name=name,
            address=address,
            capacity=capacity
        )
        
        db.session.add(venue)
        db.session.commit()
        flash('Venue added successfully!')
        return redirect(url_for('venues'))
        
    return render_template('venues/new.html')

# API endpoints
@app.route('/api/tournaments/<int:id>/teams')
def get_tournament_teams(id):
    teams = Team.query.filter_by(tournament_id=id).all()
    return jsonify([{'id': team.id, 'name': team.name} for team in teams])

@app.route('/api/matches/<int:id>/score')
def get_match_score(id):
    match_result = MatchResult.query.filter_by(match_id=id).first()
    if match_result:
        return jsonify({
            'team1_score': match_result.team1_score,
            'team2_score': match_result.team2_score
        })
    return jsonify({'team1_score': 0, 'team2_score': 0})
