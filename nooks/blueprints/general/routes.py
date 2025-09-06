from flask import Blueprint, render_template, session, redirect, url_for
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

general_bp = Blueprint('general', __name__, template_folder='templates')

@general_bp.route('/')
def index():
    """Handle the root URL and redirect first-time visitors to the landing page"""
    if 'user_id' in session:
        logger.info(f"Authenticated user {session['user_id']} accessing root, redirecting to home")
        return redirect(url_for('general.home'))
    logger.info("Unauthenticated user accessing root, redirecting to landing")
    return redirect(url_for('general.landing'))

@general_bp.route('/home')
def home():
    """Home page for authenticated users"""
    logger.info(f"Rendering home page for user_id: {session.get('user_id', 'unknown')}")
    return render_template('home.html')

@general_bp.route('/landing')
def landing():
    """Landing page for new visitors"""
    logger.info("Rendering landing page")
    return render_template('general/landingpage.html')

@general_bp.route('/about')
def about():
    """About page"""
    logger.info("Rendering about page")
    return render_template('general/about.html')

@general_bp.route('/contact')
def contact():
    """Contact page"""
    logger.info("Rendering contact page")
    return render_template('general/contact.html')

@general_bp.route('/privacy')
def privacy():
    """Privacy policy page"""
    logger.info("Rendering privacy policy page")
    return render_template('general/privacy.html')

@general_bp.route('/terms')
def terms():
    """Terms of service page"""
    logger.info("Rendering terms of service page")
    return render_template('general/terms.html')

@general_bp.route('/fair-use')
def fair_use():
    """Fair use policy page"""
    logger.info("Rendering fair use policy page")
    return render_template('general/fair_use.html')
