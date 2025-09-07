from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from datetime import datetime
from flask_login import login_user, logout_user, login_required, current_user
from models import UserModel, User
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, template_folder='templates')

# Flask-WTF Form for Login
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

# Flask-WTF Form for Registration
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    accept_terms = BooleanField('I accept the <a href="/general/terms" target="_blank">Terms of Service</a>', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

# Flask-WTF Form for Settings
class SettingsForm(FlaskForm):
    notifications = BooleanField('Enable Notifications')
    theme = SelectField('Theme', choices=[
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('retro', 'Retro'),
        ('neon', 'Neon'),
        ('anime', 'Anime')
    ])
    timer_sound = BooleanField('Enable Timer Sound')
    default_timer_duration = IntegerField('Default Timer Duration (minutes)', validators=[DataRequired()])
    submit = SubmitField('Save Settings')

# Flask-WTF Form for Change Password
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data

            logger.info(f"Login attempt for email: {email}")
            user = UserModel.authenticate_user(email, password)

            if user:
                login_user(User(user))  # Set Flask-Login session
                session['user_id'] = str(user['_id'])  # Keep for legacy support
                session['username'] = user['username']
                session['email'] = user['email']
                session['is_admin'] = user.get('is_admin', False)
                session.permanent = True  # Ensure session persists
                logger.info(f"Login successful for user_id: {session['user_id']}")
                flash('Login successful!', 'success')
                return redirect(url_for('general.home'))
            else:
                # Check why authentication failed
                user_exists = current_app.mongo.db.users.find_one({
                    '$or': [
                        {'email': {'$regex': f'^{email}$', '$options': 'i'}},
                        {'username': {'$regex': f'^{email}$', '$options': 'i'}}
                    ]
                })
                if not user_exists:
                    logger.warning(f"Login failed for email: {email} - User not found")
                    flash('Email or username not registered', 'error')
                else:
                    logger.warning(f"Login failed for email: {email} - Incorrect password")
                    flash('Incorrect password', 'error')
        else:
            logger.warning(f"Login form validation failed: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{field}: {error}", 'error')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        accept_terms = form.accept_terms.data

        logger.info(f"Registration attempt for email: {email}, terms accepted: {accept_terms}")
        if not accept_terms:
            logger.warning(f"Registration failed for email: {email} - Terms not accepted")
            flash('You must accept the Terms of Service to register', 'error')
            return render_template('auth/register.html', form=form)

        user_id, error = UserModel.create_user(username, email, password, accepted_terms=accept_terms)
        if error:
            logger.warning(f"Registration failed for email: {email} - {error}")
            flash(error, 'error')
            return render_template('auth/register.html', form=form)

        # Create welcome reward entry
        from blueprints.rewards.services import RewardService
        RewardService.award_points(
            user_id=user_id,
            points=10,
            source='registration',
            description='Welcome to Nook & Hook!',
            category='milestone'
        )

        logger.info(f"Registration successful for user_id: {user_id}")
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()  # Clear Flask-Login session
    session.clear()  # Clear custom session data
    logger.info("User logged out")
    flash('You have been logged out', 'info')
    return redirect(url_for('general.landing'))

@auth_bp.route('/profile')
@login_required
def profile():
    stats = {
        'total_books': current_app.mongo.db.books.count_documents({'user_id': ObjectId(current_user.id)}),
        'finished_books': current_app.mongo.db.books.count_documents({
            'user_id': ObjectId(current_user.id),
            'status': 'finished'
        }),
        'total_tasks': current_app.mongo.db.completed_tasks.count_documents({'user_id': ObjectId(current_user.id)}),
        'total_rewards': current_app.mongo.db.rewards.count_documents({'user_id': ObjectId(current_user.id)})
    }
    
    return render_template('auth/profile.html', user=current_user, stats=stats)

@auth_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        preferences = {
            'notifications': form.notifications.data,
            'theme': form.theme.data,
            'timer_sound': form.timer_sound.data,
            'default_timer_duration': form.default_timer_duration.data
        }
        
        current_app.mongo.db.users.update_one(
            {'_id': ObjectId(current_user.id)},
            {'$set': {'preferences': preferences}}
        )
        
        logger.info(f"Settings updated for user_id: {current_user.id}")
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('auth.settings'))
    
    # Flash validation errors if form submission fails
    if request.method == 'POST':
        logger.warning(f"Settings form validation failed for user_id: {current_user.id} - {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", 'error')
    
    # Pre-populate form with existing user preferences
    user = current_app.mongo.db.users.find_one({'_id': ObjectId(current_user.id)})
    if user and 'preferences' in user:
        form.notifications.data = user['preferences'].get('notifications', False)
        form.theme.data = user['preferences'].get('theme', 'light')
        form.timer_sound.data = user['preferences'].get('timer_sound', False)
        form.default_timer_duration.data = user['preferences'].get('default_timer_duration', 25)
    
    return render_template('auth/settings.html', user=user, form=form, change_password_form=ChangePasswordForm())

@auth_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        user = current_app.mongo.db.users.find_one({'_id': ObjectId(current_user.id)})
        
        if not user or 'password_hash' not in user:
            logger.error(f"Change password failed for user_id: {current_user.id} - User account error")
            flash('User account error. Please contact support.', 'error')
            return redirect(url_for('auth.settings'))
        
        if not check_password_hash(user['password_hash'], form.current_password.data):
            logger.warning(f"Change password failed for user_id: {current_user.id} - Incorrect current password")
            flash('Current password is incorrect', 'error')
            return redirect(url_for('auth.settings'))
        
        # Update password
        current_app.mongo.db.users.update_one(
            {'_id': ObjectId(current_user.id)},
            {'$set': {'password_hash': generate_password_hash(form.new_password.data)}}
        )
        
        logger.info(f"Password changed successfully for user_id: {current_user.id}")
        flash('Password changed successfully!', 'success')
        return redirect(url_for('auth.settings'))
    
    # If form validation fails, flash errors
    logger.warning(f"Change password form validation failed for user_id: {current_user.id} - {form.errors}")
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{field}: {error}", 'error')
    return redirect(url_for('auth.settings'))
