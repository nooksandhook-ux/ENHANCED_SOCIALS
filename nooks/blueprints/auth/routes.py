from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from datetime import datetime
from utils.decorators import login_required
from models import UserModel  # Assuming UserModel is in a 'models' module

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('auth/login.html')

        user = UserModel.authenticate_user(email, password)

        if user:
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['email'] = user['email']
            session['is_admin'] = user.get('is_admin', False)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all([username, email, password, confirm_password]):
            flash('All fields are required', 'error')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('auth/register.html')

        user_id, error = UserModel.create_user(username, email, password)
        if error:
            flash(error, 'error')
            return render_template('auth/register.html')

        # Create welcome reward entry
        from blueprints.rewards.services import RewardService
        RewardService.award_points(
            user_id=user_id,
            points=10,
            source='registration',
            description='Welcome to Nook & Hook!',
            category='milestone'
        )

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('general.landing'))

@auth_bp.route('/profile')
@login_required
def profile():
    user = current_app.mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    
    # Get user statistics
    total_books = current_app.mongo.db.books.count_documents({'user_id': ObjectId(session['user_id'])})
    finished_books = current_app.mongo.db.books.count_documents({
        'user_id': ObjectId(session['user_id']),
        'status': 'finished'
    })
    total_tasks = current_app.mongo.db.completed_tasks.count_documents({'user_id': ObjectId(session['user_id'])})
    total_rewards = current_app.mongo.db.rewards.count_documents({'user_id': ObjectId(session['user_id'])})
    
    stats = {
        'total_books': total_books,
        'finished_books': finished_books,
        'total_tasks': total_tasks,
        'total_rewards': total_rewards
    }
    
    return render_template('auth/profile.html', user=user, stats=stats)

@auth_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    user_id = ObjectId(session['user_id'])
    
    if request.method == 'POST':
        preferences = {
            'notifications': 'notifications' in request.form,
            'theme': request.form.get('theme', 'light'),
            'timer_sound': 'timer_sound' in request.form,
            'default_timer_duration': int(request.form.get('default_timer_duration', 25))
        }
        
        current_app.mongo.db.users.update_one(
            {'_id': user_id},
            {'$set': {'preferences': preferences}}
        )
        
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('auth.settings'))
    
    user = current_app.mongo.db.users.find_one({'_id': user_id})
    return render_template('auth/settings.html', user=user)

@auth_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    user_id = ObjectId(session['user_id'])
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    user = current_app.mongo.db.users.find_one({'_id': user_id})
    
    if not user or 'password_hash' not in user:
        flash('User account error. Please contact support.', 'error')
        return redirect(url_for('auth.settings'))
    
    if not check_password_hash(user['password_hash'], current_password):
        flash('Current password is incorrect', 'error')
        return redirect(url_for('auth.settings'))
    
    if new_password != confirm_password:
        flash('New passwords do not match', 'error')
        return redirect(url_for('auth.settings'))
    
    if len(new_password) < 6:
        flash('Password must be at least 6 characters long', 'error')
        return redirect(url_for('auth.settings'))
    
    # Update password
    current_app.mongo.db.users.update_one(
        {'_id': user_id},
        {'$set': {'password_hash': generate_password_hash(new_password)}}
    )
    
    flash('Password changed successfully!', 'success')
    return redirect(url_for('auth.settings'))

