from flask import Flask, render_template, redirect, url_for, session, request, jsonify, flash
from flask_pymongo import PyMongo
from flask_login import LoginManager  # Add Flask-Login import
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from functools import wraps
import requests
from bson import ObjectId
import json

# Import models and database utilities
from models import DatabaseManager, UserModel, AdminUtils

# Import blueprints
from blueprints.auth.routes import auth_bp
from blueprints.general.routes import general_bp
from blueprints.nook.routes import nook_bp
from blueprints.hook.routes import hook_bp
from blueprints.admin.routes import admin_bp
from blueprints.rewards.routes import rewards_bp
from blueprints.dashboard.routes import dashboard_bp
from blueprints.themes.routes import themes_bp
from blueprints.api.routes import api_bp
from blueprints.quotes.routes import quotes_bp
from blueprints.nooks_club import nooks_club_bp
from blueprints.mini_modules import mini_modules_bp

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/nook_hook_app')
    
    # Initialize MongoDB
    mongo = PyMongo(app)
    app.mongo = mongo
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Redirect to auth.login for unauthorized users
    
    # User loader callback for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        try:
            # Convert string user_id to ObjectId for MongoDB
            user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return UserModel(user_data)  # Assuming UserModel takes user_data dict
            return None
        except Exception as e:
            print(f"Error loading user: {e}")
            return None
    
    # Initialize database with application context
    with app.app_context():
        DatabaseManager.initialize_database()
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(general_bp, url_prefix='/general')
    app.register_blueprint(nook_bp, url_prefix='/nook')
    app.register_blueprint(hook_bp, url_prefix='/hook')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(rewards_bp, url_prefix='/rewards')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(themes_bp, url_prefix='/themes')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(quotes_bp, url_prefix='/quotes')
    app.register_blueprint(nooks_club_bp, url_prefix='/nooks_club')
    app.register_blueprint(mini_modules_bp, url_prefix='/mini_modules')
    
    @app.route('/')
    def index():
        if 'user_id' not in session:
            return redirect(url_for('general.landing'))
        return render_template('home.html')
    
    # Dashboard route
    @app.route('/dashboard')
    def dashboard():
        return redirect(url_for('dashboard.index'))
    
    return app

def calculate_reading_streak(user_id, mongo):
    # Simple streak calculation - can be enhanced
    recent_activity = mongo.db.reading_sessions.find({
        'user_id': user_id,
        'date': {'$gte': datetime.now() - timedelta(days=30)}
    }).sort('date', -1)
    
    streak = 0
    current_date = datetime.now().date()
    
    for session in recent_activity:
        session_date = session['date'].date()
        if session_date == current_date or session_date == current_date - timedelta(days=streak):
            streak += 1
            current_date = session_date - timedelta(days=1)
        else:
            break
    
    return streak

def calculate_task_streak(user_id, mongo):
    # Simple streak calculation for tasks
    recent_tasks = mongo.db.completed_tasks.find({
        'user_id': user_id,
        'completed_at': {'$gte': datetime.now() - timedelta(days=30)}
    }).sort('completed_at', -1)
    
    streak = 0
    current_date = datetime.now().date()
    
    for task in recent_tasks:
        task_date = task['completed_at'].date()
        if task_date == current_date or task_date == current_date - timedelta(days=streak):
            streak += 1
            current_date = task_date - timedelta(days=1)
        else:
            break
    
    return streak

# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
