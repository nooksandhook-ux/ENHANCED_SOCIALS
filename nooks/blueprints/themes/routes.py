from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from bson import ObjectId
from datetime import datetime
from utils.decorators import login_required

themes_bp = Blueprint('themes', __name__, template_folder='templates')

@themes_bp.route('/')
@login_required
def index():
    user_id = ObjectId(session['user_id'])
    user = current_app.mongo.db.users.find_one({'_id': user_id})
    
    current_theme = user.get('preferences', {}).get('theme', 'light')
    
    # Available themes with their configurations
    available_themes = get_available_themes()
    
    return render_template('themes/index.html',
                         themes=available_themes,
                         current_theme=current_theme)

@themes_bp.route('/set_theme', methods=['POST'])
@login_required
def set_theme():
    user_id = ObjectId(session['user_id'])
    theme_name = request.form['theme']
    
    # Validate theme
    available_themes = get_available_themes()
    if theme_name not in [theme['name'] for theme in available_themes]:
        flash('Invalid theme selected', 'error')
        return redirect(url_for('themes.index'))
    
    # Update user preferences
    current_app.mongo.db.users.update_one(
        {'_id': user_id},
        {'$set': {'preferences.theme': theme_name}}
    )
    
    # Update session
    session['theme'] = theme_name
    
    flash(f'Theme changed to {theme_name.title()}!', 'success')
    return redirect(url_for('themes.index'))

@themes_bp.route('/customize')
@login_required
def customize():
    user_id = ObjectId(session['user_id'])
    user = current_app.mongo.db.users.find_one({'_id': user_id})
    
    preferences = user.get('preferences', {})
    
    return render_template('themes/customize.html', preferences=preferences)

@themes_bp.route('/save_customization', methods=['POST'])
@login_required
def save_customization():
    user_id = ObjectId(session['user_id'])
    
    # Get current preferences
    user = current_app.mongo.db.users.find_one({'_id': user_id})
    preferences = user.get('preferences', {})
    
    # Update preferences from form
    preferences.update({
        'theme': request.form.get('theme', 'light'),
        'timer_sound': 'timer_sound' in request.form,
        'notifications': 'notifications' in request.form,
        'animations': 'animations' in request.form,
        'compact_mode': 'compact_mode' in request.form,
        'default_timer_duration': int(request.form.get('default_timer_duration', 25)),
        'timer_theme': request.form.get('timer_theme', 'default'),
        'dashboard_layout': request.form.get('dashboard_layout', 'default')
    })
    
    # Save to database
    current_app.mongo.db.users.update_one(
        {'_id': user_id},
        {'$set': {'preferences': preferences}}
    )
    
    flash('Customization saved successfully!', 'success')
    return redirect(url_for('themes.customize'))

@themes_bp.route('/timer_themes')
@login_required
def timer_themes():
    user_id = ObjectId(session['user_id'])
    user = current_app.mongo.db.users.find_one({'_id': user_id})
    
    current_timer_theme = user.get('preferences', {}).get('timer_theme', 'default')
    
    # Available timer themes
    timer_themes = get_timer_themes()
    
    return render_template('themes/timer_themes.html',
                         timer_themes=timer_themes,
                         current_timer_theme=current_timer_theme)

@themes_bp.route('/set_timer_theme', methods=['POST'])
@login_required
def set_timer_theme():
    user_id = ObjectId(session['user_id'])
    timer_theme = request.form['timer_theme']
    
    # Update user preferences
    current_app.mongo.db.users.update_one(
        {'_id': user_id},
        {'$set': {'preferences.timer_theme': timer_theme}}
    )
    
    flash(f'Timer theme changed to {timer_theme.title()}!', 'success')
    return redirect(url_for('themes.timer_themes'))

@themes_bp.route('/api/theme_preview/<theme_name>')
@login_required
def api_theme_preview(theme_name):
    """Get theme preview data"""
    themes = get_available_themes()
    theme = next((t for t in themes if t['name'] == theme_name), None)
    
    if not theme:
        return jsonify({'error': 'Theme not found'}), 404
    
    return jsonify(theme)

@themes_bp.route('/export_theme')
@login_required
def export_theme():
    """Export user's current theme settings"""
    user_id = ObjectId(session['user_id'])
    user = current_app.mongo.db.users.find_one({'_id': user_id})
    
    preferences = user.get('preferences', {})
    
    theme_export = {
        'theme_name': f"{user['username']}'s Custom Theme",
        'exported_at': datetime.utcnow().isoformat(),
        'preferences': preferences
    }
    
    return jsonify(theme_export)

@themes_bp.route('/import_theme', methods=['POST'])
@login_required
def import_theme():
    """Import theme settings"""
    user_id = ObjectId(session['user_id'])
    
    try:
        import json
        theme_data = json.loads(request.form['theme_data'])
        
        if 'preferences' in theme_data:
            # Validate and sanitize preferences
            valid_preferences = validate_preferences(theme_data['preferences'])
            
            current_app.mongo.db.users.update_one(
                {'_id': user_id},
                {'$set': {'preferences': valid_preferences}}
            )
            
            flash('Theme imported successfully!', 'success')
        else:
            flash('Invalid theme data', 'error')
    
    except (json.JSONDecodeError, KeyError):
        flash('Invalid theme file format', 'error')
    
    return redirect(url_for('themes.customize'))

def get_available_themes():
    """Get all available themes with their configurations"""
    return [
        {
            'name': 'light',
            'display_name': 'Light',
            'description': 'Clean and bright theme for daytime use',
            'preview_image': '/static/images/themes/light-preview.png',
            'colors': {
                'primary': '#0d6efd',
                'secondary': '#6c757d',
                'success': '#198754',
                'info': '#0dcaf0',
                'warning': '#ffc107',
                'danger': '#dc3545',
                'background': '#ffffff',
                'text': '#212529'
            },
            'features': ['High contrast', 'Easy reading', 'Professional look']
        },
        {
            'name': 'dark',
            'display_name': 'Dark',
            'description': 'Easy on the eyes for low-light environments',
            'preview_image': '/static/images/themes/dark-preview.png',
            'colors': {
                'primary': '#0d6efd',
                'secondary': '#6c757d',
                'success': '#198754',
                'info': '#0dcaf0',
                'warning': '#ffc107',
                'danger': '#dc3545',
                'background': '#1a1a1a',
                'text': '#ffffff'
            },
            'features': ['Reduced eye strain', 'Battery saving', 'Modern look']
        },
        {
            'name': 'retro',
            'display_name': 'Retro',
            'description': 'Vintage-inspired theme with warm colors',
            'preview_image': '/static/images/themes/retro-preview.png',
            'colors': {
                'primary': '#8B4513',
                'secondary': '#D2691E',
                'success': '#228B22',
                'info': '#4682B4',
                'warning': '#DAA520',
                'danger': '#B22222',
                'background': '#FFF8DC',
                'text': '#2F4F4F'
            },
            'features': ['Warm colors', 'Nostalgic feel', 'Unique style']
        },
        {
            'name': 'neon',
            'display_name': 'Neon',
            'description': 'Cyberpunk-inspired theme with bright accents',
            'preview_image': '/static/images/themes/neon-preview.png',
            'colors': {
                'primary': '#00FFFF',
                'secondary': '#FF00FF',
                'success': '#00FF00',
                'info': '#0080FF',
                'warning': '#FFFF00',
                'danger': '#FF0080',
                'background': '#0a0a0a',
                'text': '#00FFFF'
            },
            'features': ['High energy', 'Futuristic look', 'Vibrant colors']
        },
        {
            'name': 'anime',
            'display_name': 'Anime',
            'description': 'Colorful and playful theme inspired by anime',
            'preview_image': '/static/images/themes/anime-preview.png',
            'colors': {
                'primary': '#FF69B4',
                'secondary': '#9370DB',
                'success': '#32CD32',
                'info': '#00BFFF',
                'warning': '#FFD700',
                'danger': '#FF6347',
                'background': '#FFF0F5',
                'text': '#4B0082'
            },
            'features': ['Playful colors', 'Fun animations', 'Cheerful mood']
        },
        {
            'name': 'forest',
            'display_name': 'Forest',
            'description': 'Nature-inspired theme with earth tones',
            'preview_image': '/static/images/themes/forest-preview.png',
            'colors': {
                'primary': '#228B22',
                'secondary': '#8FBC8F',
                'success': '#32CD32',
                'info': '#4682B4',
                'warning': '#DAA520',
                'danger': '#B22222',
                'background': '#F0FFF0',
                'text': '#2F4F4F'
            },
            'features': ['Calming colors', 'Nature inspired', 'Relaxing mood']
        },
        {
            'name': 'ocean',
            'display_name': 'Ocean',
            'description': 'Calm and serene theme with blue tones',
            'preview_image': '/static/images/themes/ocean-preview.png',
            'colors': {
                'primary': '#4682B4',
                'secondary': '#5F9EA0',
                'success': '#20B2AA',
                'info': '#00BFFF',
                'warning': '#F0E68C',
                'danger': '#DC143C',
                'background': '#F0F8FF',
                'text': '#2F4F4F'
            },
            'features': ['Peaceful colors', 'Ocean inspired', 'Serene mood']
        },
        {
            'name': 'sunset',
            'display_name': 'Sunset',
            'description': 'Warm gradient theme inspired by sunsets',
            'preview_image': '/static/images/themes/sunset-preview.png',
            'colors': {
                'primary': '#FF6347',
                'secondary': '#FF7F50',
                'success': '#32CD32',
                'info': '#87CEEB',
                'warning': '#FFD700',
                'danger': '#DC143C',
                'background': '#FFF8DC',
                'text': '#2F4F4F'
            },
            'features': ['Warm gradients', 'Sunset colors', 'Cozy feeling']
        }
    ]

def get_timer_themes():
    """Get available timer-specific themes"""
    return [
        {
            'name': 'default',
            'display_name': 'Default',
            'description': 'Clean and simple timer design',
            'background': 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
            'text_color': '#333333',
            'accent_color': '#0d6efd'
        },
        {
            'name': 'focus',
            'display_name': 'Focus',
            'description': 'Minimal design for maximum concentration',
            'background': '#ffffff',
            'text_color': '#000000',
            'accent_color': '#28a745'
        },
        {
            'name': 'dark_focus',
            'display_name': 'Dark Focus',
            'description': 'Dark theme for focused work sessions',
            'background': 'linear-gradient(135deg, #2c3e50 0%, #34495e 100%)',
            'text_color': '#ffffff',
            'accent_color': '#3498db'
        },
        {
            'name': 'retro_timer',
            'display_name': 'Retro Timer',
            'description': 'Vintage-style timer with warm colors',
            'background': 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%)',
            'text_color': '#8B4513',
            'accent_color': '#D2691E'
        },
        {
            'name': 'neon_timer',
            'display_name': 'Neon Timer',
            'description': 'Cyberpunk-style timer with glowing effects',
            'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'text_color': '#00FFFF',
            'accent_color': '#FF00FF'
        },
        {
            'name': 'nature_timer',
            'display_name': 'Nature Timer',
            'description': 'Calming nature-inspired timer',
            'background': 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
            'text_color': '#2F4F4F',
            'accent_color': '#228B22'
        },
        {
            'name': 'space_timer',
            'display_name': 'Space Timer',
            'description': 'Cosmic theme for out-of-this-world focus',
            'background': 'linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%)',
            'text_color': '#ffffff',
            'accent_color': '#00BFFF'
        },
        {
            'name': 'zen_timer',
            'display_name': 'Zen Timer',
            'description': 'Peaceful and minimalist design',
            'background': 'linear-gradient(135deg, #f7f7f7 0%, #e8e8e8 100%)',
            'text_color': '#555555',
            'accent_color': '#9370DB'
        }
    ]

def validate_preferences(preferences):
    """Validate and sanitize user preferences"""
    valid_themes = [theme['name'] for theme in get_available_themes()]
    valid_timer_themes = [theme['name'] for theme in get_timer_themes()]
    
    validated = {}
    
    # Theme validation
    if 'theme' in preferences and preferences['theme'] in valid_themes:
        validated['theme'] = preferences['theme']
    else:
        validated['theme'] = 'light'
    
    # Timer theme validation
    if 'timer_theme' in preferences and preferences['timer_theme'] in valid_timer_themes:
        validated['timer_theme'] = preferences['timer_theme']
    else:
        validated['timer_theme'] = 'default'
    
    # Boolean preferences
    boolean_prefs = ['timer_sound', 'notifications', 'animations', 'compact_mode']
    for pref in boolean_prefs:
        validated[pref] = bool(preferences.get(pref, False))
    
    # Numeric preferences
    validated['default_timer_duration'] = max(1, min(120, 
        int(preferences.get('default_timer_duration', 25))))
    
    # String preferences with validation
    valid_layouts = ['default', 'compact', 'detailed']
    if 'dashboard_layout' in preferences and preferences['dashboard_layout'] in valid_layouts:
        validated['dashboard_layout'] = preferences['dashboard_layout']
    else:
        validated['dashboard_layout'] = 'default'
    
    return validated