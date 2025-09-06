from flask import Blueprint, render_template, session, redirect, url_for

general_bp = Blueprint('general', __name__, template_folder='templates')

@general_bp.route('/')
def index():
    """Handle the root URL and redirect first-time visitors to the landing page"""
    if 'user_id' not in session:  # First-time or non-logged-in user
        return redirect(url_for('general.landing'))
    return redirect(url_for('index'))  # Redirect logged-in users to the main app (e.g., dashboard)

@general_bp.route('/landing')
def landing():
    """Landing page for new visitors"""
    return render_template('general/landingpage.html')

@general_bp.route('/about')
def about():
    """About page"""
    return render_template('general/about.html')

@general_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('general/contact.html')

@general_bp.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('general/privacy.html')

@general_bp.route('/terms')
def terms():
    """Terms of service page"""
    return render_template('general/terms.html')

@general_bp.route('/fair-use')
def fair_use():
    """Fair use policy page"""
    return render_template('general/fair_use.html')
