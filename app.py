from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tera-super-secret-key-12345' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bug_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Bug Model - purana wala
class Bug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('signup'))
            
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Please login.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    bugs = Bug.query.all()
    return render_template('index.html', bugs=bugs, name=current_user.username)

@app.route('/submit', methods=['POST'])
@login_required
def submit():
    title = request.form['title']
    description = request.form['description']
    new_bug = Bug(title=title, description=description)
    db.session.add(new_bug)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/status/<int:bug_id>/<new_status>')
@login_required
def update_status(bug_id, new_status):
    bug = Bug.query.get_or_404(bug_id)
    bug.status = new_status
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:bug_id>')
@login_required
def delete_bug(bug_id):
    bug = Bug.query.get_or_404(bug_id)
    db.session.delete(bug)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:bug_id>', methods=['GET', 'POST'])
@login_required
def edit_bug(bug_id):
    bug = Bug.query.get_or_404(bug_id)
    if request.method == 'POST':
        bug.title = request.form['title']
        bug.description = request.form['description']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', bug=bug)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=10000)