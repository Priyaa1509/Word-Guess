import os
import random
import re
import json
from datetime import datetime, date, timedelta

from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo, Regexp
from functools import wraps
from sqlalchemy import func, distinct, case

# --- Configuration ---
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_key_for_word_guess'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///guessword.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)
app.config.from_object(Config)

# --- Extensions ---
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Where to redirect if user is not logged in


# --- User Loader for Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- Database Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    games = db.relationship('GameSession', backref='player', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(5), unique=True, nullable=False)  # 5-letter word
    game_sessions = db.relationship('GameSession', backref='target_word', lazy=True)

    def __repr__(self):
        return f'<Word {self.text}>'


class GameSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    target_word_id = db.Column(db.Integer, db.ForeignKey('word.id'), nullable=False)
    date_played = db.Column(db.Date, nullable=False, default=date.today)
    guesses_made = db.Column(db.Integer, default=0)
    status = db.Column(db.String(10), default='in_progress')  # 'in_progress', 'won', 'lost'
    guesses = db.relationship('Guess', backref='game_session', lazy=True, order_by='Guess.timestamp')


    def __repr__(self):
        # protect if user deleted or not loaded
        username = self.player.username if self.player else "Unknown"
        return f'<GameSession {self.id} for {username} on {self.date_played}>'


class Guess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_session_id = db.Column(db.Integer, db.ForeignKey('game_session.id'), nullable=False)
    guessed_word = db.Column(db.String(5), nullable=False)
    result_json = db.Column(db.Text, nullable=False)  # store JSON string of colors
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Guess {self.guessed_word} in Game {self.game_session_id}>'


# --- Forms ---
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=5, max=80),
        Regexp('^[a-zA-Z1-9]{5,}$', message='Username must be at least 5 letters, upper or lower case.')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=5),
        Regexp(r'^(?=.*[a-zA-Z])(?=.*\d)(?=.*[$%*@]).{5,}$',
               message='Password must be at least 5 characters long and contain at least one letter, one number, and one of $, %, *, @.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


# --- Helper Functions ---
def is_admin():
    return current_user.is_authenticated and current_user.is_admin


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not is_admin():
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def get_word_feedback(target_word, guessed_word):
    feedback = ['grey'] * 5
    target_letters = list(target_word)
    guessed_letters = list(guessed_word)

    # First pass: check for green (correct letter and position)
    for i in range(5):
        if guessed_letters[i] == target_letters[i]:
            feedback[i] = 'green'
            target_letters[i] = None  # Mark as used
            guessed_letters[i] = None  # Mark as used

    # Second pass: check for orange (correct letter, wrong position)
    for i in range(5):
        if guessed_letters[i] is not None:  # If not already green
            if guessed_letters[i] in target_letters:
                feedback[i] = 'orange'
                target_letters[target_letters.index(guessed_letters[i])] = None  # Mark as used

    return feedback


@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}


# --- Routes ---
@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('play'))
    return render_template('index.html', title='Welcome')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles user registration with a form.
    
    This function processes the registration form submission. It first checks if the
    user is already authenticated. If a form is submitted and passes validation,
    it performs an additional check to ensure the username is not already
    in the database before creating a new user record.
    """
    if current_user.is_authenticated:
        return redirect(url_for('play'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Retrieve the username from the form and convert it to uppercase
        username_upper = form.username.data.upper()
        
        # Check if a user with the same uppercase username already exists in the database
        existing_user = User.query.filter_by(username=username_upper).first()
        
        if existing_user:
            # If the user exists, flash an error message and re-render the form
            flash('Username is already taken. Please choose a different one.', 'danger')
            return render_template('register.html', title='Register', form=form)
            
        # If the username is unique, create the new user
        user = User(username=username_upper) 
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            flash('Congratulations, you are now a registered user!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            # Handle potential database errors and roll back the session
            db.session.rollback()
            flash('An unexpected error occurred during registration. Please try again.', 'danger')
            # You can log the error 'e' for debugging purposes
            return render_template('register.html', title='Register', form=form)
            
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('play'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.upper()).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        
        # --- ADDED CHECK HERE ---
        if user.is_admin:
            return redirect(url_for('admin_dashboard'))
        
        next_page = request.args.get('next')
        return redirect(next_page or url_for('play'))
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# In the play() route
@app.route("/play")
@login_required
def play():

    # Define the daily game limit
    DAILY_GAME_LIMIT = 3
    
    # 1. First, check for an existing game that is currently in progress.
    # We only want one active game at a time.
    game_session = GameSession.query.filter_by(
        user_id=current_user.id,
        date_played=date.today(),
        status='in_progress'
    ).first()

    # 2. If no in-progress game is found, check if a new one can be created.
    if not game_session:
        # Count all game sessions (won, lost, or in_progress) for today.
        games_played_today = GameSession.query.filter_by(
            user_id=current_user.id,
            date_played=date.today()
        ).count()
        
        # Check if the user has any remaining daily games.
        if games_played_today < DAILY_GAME_LIMIT:
            # Get a random word for the new game
            target_word = Word.query.order_by(db.func.random()).first()
            if not target_word:
                flash("No words available to play.", "danger")
                return redirect(url_for('index'))
            
            # Create a new game session
            game_session = GameSession(
                user_id=current_user.id,
                target_word_id=target_word.id,
                guesses_made=0,
                status='in_progress'
            )
            db.session.add(game_session)
            db.session.commit()
        else:
            # If the daily limit has been reached, set game_over to true.
            game_over = True
            message = "You have used all your daily game attempts. Check back tomorrow!"
            return render_template(
                "play.html",
                game_over=game_over,
                message=message,
                # These are needed for the template even if no new game starts
                game_session_id=None,
                guesses_made=0,
                previous_guesses=[],
                games_played_today=games_played_today
            )

    # 3. Handle the case where a game session (new or existing) is available.
    # Fetch previous guesses for the game session
    guesses = Guess.query.filter_by(game_session_id=game_session.id).all()
    previous_guesses = [
        {
            "word": g.guessed_word,
            "feedback": json.loads(g.result_json) # Load the stored JSON string
        } for g in guesses
    ]
    
    # Check if the game is over
    game_over = game_session.status in ['won', 'lost']
    message = None
    if game_session.status == 'won':
        message = '✅CONGRATULATIONS! You guessed the word!'
    elif game_session.status == 'lost':
        message = f'❌Better luck next time! The word was {game_session.target_word.text}.'

    # Calculate number of games played for the day
    games_played_today = GameSession.query.filter_by(
        user_id=current_user.id,
        date_played=date.today()
    ).count()

    return render_template(
        "play.html",
        game_session_id=game_session.id,
        guesses_made=game_session.guesses_made,
        previous_guesses=previous_guesses,
        game_over=game_over,
        message=message,
        games_played_today=games_played_today
    )
# In the guess() route
@app.route('/guess', methods=['POST'])
@login_required
def guess():
    data = request.get_json()
    game_session_id = data.get('game_session_id')
    guessed_word = data.get('word', '').upper()

    game_session = GameSession.query.get(game_session_id)

    if not game_session or game_session.user_id != current_user.id or game_session.status != 'in_progress':
        return jsonify({'error': 'Invalid game session or game is over.'}), 400

    if len(guessed_word) != 5 or not guessed_word.isalpha():
        return jsonify({'error': 'Guess must be a 5-letter English word.'}), 400

    target_word_text = game_session.target_word.text
    feedback = get_word_feedback(target_word_text, guessed_word)

    # Save the guess
    new_guess = Guess(
        game_session_id=game_session.id,
        guessed_word=guessed_word,
        result_json=json.dumps(feedback)
    )
    db.session.add(new_guess)
    game_session.guesses_made += 1

    game_over = False
    message = None

    if guessed_word == target_word_text:
        game_session.status = 'won'
        message = 'Congratulations! You guessed the word!'
        game_over = True
    elif game_session.guesses_made >= 5:
        game_session.status = 'lost'
        message = f'Better luck next time! The word was {target_word_text}.'
        game_over = True
    else:
        message = f'You have {5 - game_session.guesses_made} guesses remaining.'

    db.session.commit()

    return jsonify({
        'guessed_word': guessed_word,
        'feedback': feedback,
        'guesses_made': game_session.guesses_made,
        'game_over': game_over,
        'message': message,
        'status': game_session.status
    })


# --- IMPROVED ADMIN ROUTES ---
@app.route('/admin')
@admin_required
def admin_dashboard():
    # This route now fetches all data needed for the admin dashboard
    
    # Daily game stats
    daily_stats = db.session.query(
        GameSession.date_played.label('date'),
        func.count(distinct(GameSession.user_id)).label('users_played'),
        func.sum(case((GameSession.status == 'won', 1), else_=0)).label('total_wins')
    ).group_by(GameSession.date_played).order_by(GameSession.date_played.desc()).all()
    
    # User stats
    users_with_stats = db.session.query(
        User.id,
        User.username,
        func.count(GameSession.id).label('words_tried'),
        func.sum(case((GameSession.status == 'won', 1), else_=0)).label('correct_guesses'),
        func.max(GameSession.date_played).label('last_played')
    ).outerjoin(GameSession).group_by(User.id).order_by(func.count(GameSession.id).desc()).all()
    
    return render_template(
        'admin_reports.html',
        title='Admin Reports',
        daily=daily_stats,  # Pass the daily summary data
        users=users_with_stats, # Pass the user list with stats
    )

@app.route('/admin/words')
@admin_required
def admin_words():
    words = Word.query.all()
    # Convert SQLAlchemy objects to a list of dictionaries for JSON serialization
    out = [{"id": w.id, "text": w.text} for w in words]
    return jsonify(out)

@app.route('/admin/reports/daily', methods=['GET'])
@admin_required
def daily_report():
    report_date_str = request.args.get('date', date.today().isoformat())
    report_date = datetime.strptime(report_date_str, '%Y-%m-%d').date()

    # Number of unique users who played
    unique_users_played = db.session.query(GameSession.user_id).filter_by(date_played=report_date).distinct().count()

    # Number of correct guesses (wins)
    correct_guesses = GameSession.query.filter_by(date_played=report_date, status='won').count()

    # List of all games for the day
    games_for_day = GameSession.query.filter_by(date_played=report_date).all()

    return render_template('pdf_report.html',
                           title=f'Daily Report for {report_date}',
                           report_type='daily',
                           report_date=report_date,
                           unique_users_played=unique_users_played,
                           correct_guesses=correct_guesses,
                           games_for_day=games_for_day)

@app.route('/admin/reports/user/<int:user_id>', methods=['GET'])
@admin_required
def user_report(user_id):
    user = User.query.get_or_404(user_id)

    user_game_sessions = GameSession.query.filter_by(user_id=user.id).order_by(GameSession.date_played.desc()).all()

    report_data = []
    for session in user_game_sessions:
        report_data.append({
            'date': session.date_played,
            'target_word': session.target_word.text,
            'status': session.status,
            'guesses_made': session.guesses_made,
            'guesses': [guess.guessed_word for guess in session.guesses]
        })

    return render_template('pdf_report.html',
                           title=f'User Report for {user.username}',
                           report_type='user',
                           user=user,
                           report_data=report_data)


# --- Error Handlers (Optional) ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404  # You'd need to create a 404.html template


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500  # You'd need to create a 500.html template


if __name__ == '__main__':
    # This block is for development only.
    # In production, you'd use a WSGI server like Gunicorn.
    with app.app_context():
        db.create_all()
    app.run(debug=True)