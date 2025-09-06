from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import login_required

nooks_club_bp = Blueprint('nooks_club', __name__, template_folder='templates/nooks_club', url_prefix='/nooks_club')

@nooks_club_bp.route('/api/quiz/leaderboard', methods=['GET'])
@login_required
def api_quiz_leaderboard():
    pipeline = [
        {'$group': {
            '_id': '$user_id',
            'score': {'$sum': {'$cond': ['$is_correct', 1, 0]}},
            'attempts': {'$sum': 1}
        }},
        {'$sort': {'score': -1}},
        {'$limit': 50}
    ]
    leaderboard_data = list(current_app.mongo.db.quiz_answers.aggregate(pipeline))
    leaderboard = []
    for entry in leaderboard_data:
        user = current_app.mongo.db.users.find_one({'_id': entry['_id']})
        if user:
            leaderboard.append({
                'username': user.get('username', 'User'),
                'score': entry['score'],
                'attempts': entry['attempts'],
                'is_current_user': str(entry['_id']) == str(current_user.id)
            })
    return jsonify({'leaderboard': leaderboard})

# --- Quiz Question Review ---
@nooks_club_bp.route('/api/quiz/review', methods=['GET'])
@login_required
def api_quiz_review():
    answers = QuizAnswerModel.get_user_answers(str(current_user.id))
    review = []
    for ans in answers:
        q = QuizQuestionModel.get_question_by_id(str(ans['question_id']))
        review.append({
            'question': q['question'] if q else '',
            'your_answer': ans['answer'],
            'correct_answer': q['answer'] if q else '',
            'is_correct': ans['is_correct'],
            'answered_at': ans['submitted_at']
        })
    return jsonify({'review': review})

# --- Quiz Analytics ---
@nooks_club_bp.route('/api/quiz/analytics', methods=['GET'])
@login_required
def api_quiz_analytics():
    user_id = str(current_user.id)
    total_attempts = current_app.mongo.db.quiz_answers.count_documents({'user_id': user_id})
    correct = current_app.mongo.db.quiz_answers.count_documents({'user_id': user_id, 'is_correct': True})
    accuracy = (correct / total_attempts) * 100 if total_attempts else 0
    last_10 = list(current_app.mongo.db.quiz_answers.find({'user_id': user_id}).sort('submitted_at', -1).limit(10))
    streak = 0
    for ans in last_10:
        if ans['is_correct']:
            streak += 1
        else:
            break
    return jsonify({'total_attempts': total_attempts, 'correct': correct, 'accuracy': accuracy, 'current_streak': streak})
# --- Moderation Endpoints: Delete Posts/Messages ---
@nooks_club_bp.route('/api/clubs/<club_id>/posts/<post_id>', methods=['DELETE'])
@login_required
def api_delete_club_post(club_id, post_id):
    club = ClubModel.get_club(club_id)
    if not club:
        return jsonify({'error': 'Club not found'}), 404
    if not is_club_admin(club, current_user.id):
        return jsonify({'error': 'Only club admins can delete posts'}), 403
    result = current_app.mongo.db.club_posts.delete_one({'_id': post_id if len(post_id)==24 else post_id})
    # Try ObjectId if needed
    if result.deleted_count == 0:
        from bson import ObjectId
        try:
            result = current_app.mongo.db.club_posts.delete_one({'_id': ObjectId(post_id)})
        except Exception:
            pass
    if result.deleted_count:
        return jsonify({'message': 'Post deleted'})
    return jsonify({'error': 'Post not found'}), 404

@nooks_club_bp.route('/api/clubs/<club_id>/chat/<message_id>', methods=['DELETE'])
@login_required
def api_delete_club_message(club_id, message_id):
    club = ClubModel.get_club(club_id)
    if not club:
        return jsonify({'error': 'Club not found'}), 404
    if not is_club_admin(club, current_user.id):
        return jsonify({'error': 'Only club admins can delete messages'}), 403
    result = current_app.mongo.db.club_chat_messages.delete_one({'_id': message_id if len(message_id)==24 else message_id})
    # Try ObjectId if needed
    if result.deleted_count == 0:
        from bson import ObjectId
        try:
            result = current_app.mongo.db.club_chat_messages.delete_one({'_id': ObjectId(message_id)})
        except Exception:
            pass
    if result.deleted_count:
        return jsonify({'message': 'Message deleted'})
    return jsonify({'error': 'Message not found'}), 404

from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
# --- Helper: Check if user is club admin/moderator ---
def is_club_admin(club, user_id):
    return str(user_id) in [str(a) for a in club.get('admins', [])]

from . import nooks_club_bp
from models import ClubModel, ClubPostModel, ClubChatMessageModel, FlashcardModel, QuizQuestionModel, QuizAnswerModel

# --- Web Views (unchanged) ---
@nooks_club_bp.route('/')
@login_required
def index():
    return render_template('nooks_club/index.html')

@nooks_club_bp.route('/club/<club_id>')
@login_required
def view_club(club_id):
    return render_template('nooks_club/club_detail.html', club_id=club_id)

@nooks_club_bp.route('/join/<club_id>', methods=['POST'])
@login_required
def join_club(club_id):
    ClubModel.add_member(club_id, str(current_user.id))
    flash('Joined club!')
    return redirect(url_for('nooks_club.view_club', club_id=club_id))

@nooks_club_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_club():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        topic = request.form.get('topic', '')
        ClubModel.create_club(name, description, topic, str(current_user.id))
        flash('Club created!')
        return redirect(url_for('nooks_club.index'))
    return render_template('nooks_club/create_club.html')

@nooks_club_bp.route('/club/<club_id>/post', methods=['POST'])
@login_required
def create_post(club_id):
    content = request.form.get('post')
    ClubPostModel.create_post(club_id, str(current_user.id), content)
    flash('Post created!')
    return redirect(url_for('nooks_club.view_club', club_id=club_id))

@nooks_club_bp.route('/club/<club_id>/chat')
@login_required
def club_chat(club_id):
    return render_template('nooks_club/chat.html', club_id=club_id)

# --- API Endpoints ---

# Clubs API
@nooks_club_bp.route('/api/clubs', methods=['GET'])
@login_required
def api_get_clubs():
    clubs = ClubModel.get_all_clubs()
    for c in clubs:
        c['_id'] = str(c['_id'])
        c['creator_id'] = str(c['creator_id'])
        c['members'] = [str(m) for m in c.get('members', [])]
    return jsonify({'clubs': clubs})

@nooks_club_bp.route('/api/clubs', methods=['POST'])
@login_required
def api_create_club():
    data = request.json
    name = data.get('name')
    description = data.get('description')
    topic = data.get('topic', '')
    result = ClubModel.create_club(name, description, topic, str(current_user.id))
    return jsonify({'club_id': str(result.inserted_id)}), 201

@nooks_club_bp.route('/api/clubs/<club_id>', methods=['GET'])
@login_required
def api_get_club(club_id):
    club = ClubModel.get_club(club_id)
    if not club:
        return jsonify({'error': 'Club not found'}), 404
    club['_id'] = str(club['_id'])
    club['creator_id'] = str(club['creator_id'])
    club['members'] = [str(m) for m in club.get('members', [])]
    return jsonify(club)

@nooks_club_bp.route('/api/clubs/<club_id>/join', methods=['POST'])
@login_required
def api_join_club(club_id):
    ClubModel.add_member(club_id, str(current_user.id))
    return jsonify({'message': 'Joined club'})

# Club Posts API
@nooks_club_bp.route('/api/clubs/<club_id>/posts', methods=['GET'])
@login_required
def api_get_club_posts(club_id):
    posts = ClubPostModel.get_posts(club_id)
    for p in posts:
        p['_id'] = str(p['_id'])
        p['club_id'] = str(p['club_id'])
        p['user_id'] = str(p['user_id'])
    return jsonify({'posts': posts})

@nooks_club_bp.route('/api/clubs/<club_id>/posts', methods=['POST'])
@login_required
def api_create_club_post(club_id):
    club = ClubModel.get_club(club_id)
    if not club:
        return jsonify({'error': 'Club not found'}), 404
    # Only members can post
    if str(current_user.id) not in [str(m) for m in club.get('members', [])]:
        return jsonify({'error': 'Not a club member'}), 403
    data = request.json
    content = data.get('content')
    result = ClubPostModel.create_post(club_id, str(current_user.id), content)
    return jsonify({'post_id': str(result.inserted_id)}), 201

# Club Chat API
@nooks_club_bp.route('/api/clubs/<club_id>/chat', methods=['GET'])
@login_required
def api_get_club_chat(club_id):
    messages = ClubChatMessageModel.get_messages(club_id)
    for m in messages:
        m['_id'] = str(m['_id'])
        m['club_id'] = str(m['club_id'])
        m['user_id'] = str(m['user_id'])
    return jsonify({'messages': messages})

@nooks_club_bp.route('/api/clubs/<club_id>/chat', methods=['POST'])
@login_required
def api_send_club_chat(club_id):
    club = ClubModel.get_club(club_id)
    if not club:
        return jsonify({'error': 'Club not found'}), 404
    # Only members can chat
    if str(current_user.id) not in [str(m) for m in club.get('members', [])]:
        return jsonify({'error': 'Not a club member'}), 403
    data = request.json
    message = data.get('message')
    result = ClubChatMessageModel.send_message(club_id, str(current_user.id), message)
    return jsonify({'message_id': str(result.inserted_id)}), 201
# --- Admin/Moderator Management Endpoints ---
@nooks_club_bp.route('/api/clubs/<club_id>/admins', methods=['POST'])
@login_required
def api_add_club_admin(club_id):
    club = ClubModel.get_club(club_id)
    if not club:
        return jsonify({'error': 'Club not found'}), 404
    if not is_club_admin(club, current_user.id):
        return jsonify({'error': 'Only club admins can promote others'}), 403
    data = request.json
    user_id = data.get('user_id')
    ClubModel.add_admin(club_id, user_id)
    return jsonify({'message': 'User promoted to admin'})

@nooks_club_bp.route('/api/clubs/<club_id>/admins/<user_id>', methods=['DELETE'])
@login_required
def api_remove_club_admin(club_id, user_id):
    club = ClubModel.get_club(club_id)
    if not club:
        return jsonify({'error': 'Club not found'}), 404
    if not is_club_admin(club, current_user.id):
        return jsonify({'error': 'Only club admins can demote others'}), 403
    # Prevent removing last admin
    if len(club.get('admins', [])) <= 1:
        return jsonify({'error': 'Cannot remove last admin'}), 400
    current_app.mongo.db.clubs.update_one({'_id': club['_id']}, {'$pull': {'admins': user_id}})
    return jsonify({'message': 'User demoted from admin'})

# Flashcards API
@nooks_club_bp.route('/api/flashcards', methods=['GET'])
@login_required
def api_get_flashcards():
    cards = FlashcardModel.get_user_flashcards(str(current_user.id))
    for c in cards:
        c['_id'] = str(c['_id'])
        c['user_id'] = str(c['user_id'])
    return jsonify({'flashcards': cards})

@nooks_club_bp.route('/api/flashcards', methods=['POST'])
@login_required
def api_create_flashcard():
    data = request.json
    front = data.get('front')
    back = data.get('back')
    tags = data.get('tags', [])
    result = FlashcardModel.create_flashcard(str(current_user.id), front, back, tags)
    return jsonify({'flashcard_id': str(result.inserted_id)}), 201


# Quiz API with timed questions, scoring, and progress
from datetime import datetime, timedelta

QUIZ_TIME_LIMIT_SECONDS = 60  # 1 minute per quiz session

@nooks_club_bp.route('/api/quiz/start', methods=['POST'])
@login_required
def api_start_quiz():
    # Start a quiz session: store start time in user_progress
    now = datetime.utcnow()
    UserProgressModel.update_progress(str(current_user.id), 'quiz', {'start_time': now, 'score': 0, 'completed': False})
    questions = QuizQuestionModel.get_daily_questions()
    for q in questions:
        q['_id'] = str(q['_id'])
        q['creator_id'] = str(q['creator_id'])
        q.pop('answer', None)  # Don't send answer to client
    return jsonify({'questions': questions, 'start_time': now.isoformat(), 'time_limit': QUIZ_TIME_LIMIT_SECONDS})

@nooks_club_bp.route('/api/quiz/answer', methods=['POST'])
@login_required
def api_submit_quiz_answer():
    data = request.json
    question_id = data.get('question_id')
    answer = data.get('answer')
    # Get correct answer
    question = QuizQuestionModel.get_question_by_id(question_id)
    is_correct = False
    if question and answer:
        is_correct = (answer == question.get('answer'))
    result = QuizAnswerModel.submit_answer(str(current_user.id), question_id, answer, is_correct)
    # Update score in user_progress
    progress = UserProgressModel.get_progress(str(current_user.id), 'quiz') or {}
    score = progress.get('data', {}).get('score', 0)
    if is_correct:
        score += 1
    UserProgressModel.update_progress(str(current_user.id), 'quiz', {'score': score, 'last_answered': datetime.utcnow()})
    return jsonify({'answer_id': str(result.inserted_id), 'is_correct': is_correct, 'score': score}), 201

@nooks_club_bp.route('/api/quiz/finish', methods=['POST'])
@login_required
def api_finish_quiz():
    # Mark quiz as completed and return final score
    progress = UserProgressModel.get_progress(str(current_user.id), 'quiz') or {}
    score = progress.get('data', {}).get('score', 0)
    start_time = progress.get('data', {}).get('start_time')
    completed = False
    if start_time:
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)
        elapsed = (datetime.utcnow() - start_time).total_seconds()
        if elapsed <= QUIZ_TIME_LIMIT_SECONDS:
            completed = True
    UserProgressModel.update_progress(str(current_user.id), 'quiz', {'score': score, 'completed': completed, 'finished_at': datetime.utcnow()})
    return jsonify({'score': score, 'completed': completed})

# Helper to get question by id
def get_question_by_id(question_id):
    from bson import ObjectId
    try:
        return current_app.mongo.db.quiz_questions.find_one({'_id': ObjectId(question_id)})
    except Exception:
        return None
QuizQuestionModel.get_question_by_id = staticmethod(get_question_by_id)



