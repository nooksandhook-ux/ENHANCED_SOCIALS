from . import mini_modules_bp
from flask_login import login_required

@mini_modules_bp.route('/quiz_leaderboard')
@login_required
def quiz_leaderboard():
    return render_template('mini_modules/quiz_leaderboard.html')

@mini_modules_bp.route('/quiz_review')
@login_required
def quiz_review():
    return render_template('mini_modules/quiz_review.html')

@mini_modules_bp.route('/quiz_analytics')
@login_required
def quiz_analytics():
    return render_template('mini_modules/quiz_analytics.html')
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from . import mini_modules_bp

@mini_modules_bp.route('/')
@login_required
def index():
    # List all mini modules
    return render_template('mini_modules/index.html')

@mini_modules_bp.route('/flashcards', methods=['GET', 'POST'])
@login_required
def flashcards():
    if request.method == 'POST':
        # Handle flashcard creation
        flash('Flashcard created!')
    return render_template('mini_modules/flashcards.html')

@mini_modules_bp.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    if request.method == 'POST':
        # Handle quiz submission
        flash('Quiz submitted!')
    return render_template('mini_modules/quiz.html')

