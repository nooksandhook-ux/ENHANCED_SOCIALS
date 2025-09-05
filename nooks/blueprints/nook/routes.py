@nook_bp.route('/edit_book/<book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    user_id = ObjectId(session['user_id'])
    book = current_app.mongo.db.books.find_one({'_id': ObjectId(book_id), 'user_id': user_id})
    if not book:
        flash('Book not found.', 'danger')
        return redirect(url_for('nook.my_uploads'))
    if request.method == 'POST':
        title = request.form['title']
        authors = [a.strip() for a in request.form['authors'].split(',')]
        page_count = int(request.form.get('page_count', 0))
        description = request.form.get('description', '')
        status = request.form['status']
        update = {
            'title': title,
            'authors': authors,
            'page_count': page_count,
            'description': description,
            'status': status
        }
        pdf_file = request.files.get('pdf_file')
        if pdf_file and pdf_file.filename != '':
            if not pdf_file.filename.lower().endswith('.pdf'):
                flash('Only PDF files are allowed.', 'danger')
                return redirect(request.url)
            if pdf_file.mimetype != 'application/pdf':
                flash('Invalid file type.', 'danger')
                return redirect(request.url)
            pdf_file.seek(0, 2)
            file_size = pdf_file.tell()
            pdf_file.seek(0)
            if file_size > 10 * 1024 * 1024:
                flash('File size exceeds 10MB limit.', 'danger')
                return redirect(request.url)
            import os
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', str(user_id))
            os.makedirs(upload_dir, exist_ok=True)
            pdf_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{pdf_file.filename}"
            pdf_path = os.path.join(upload_dir, pdf_filename)
            pdf_file.save(pdf_path)
            update['pdf_path'] = f"uploads/{user_id}/{pdf_filename}"
        current_app.mongo.db.books.update_one({'_id': ObjectId(book_id)}, {'$set': update})
        flash('Book updated successfully!', 'success')
        return redirect(url_for('nook.my_uploads'))
    return render_template('nook/edit_book.html', book=book)
nook_bp.route('/my_uploads')
@login_required
def my_uploads():
    user_id = ObjectId(session['user_id'])
    books = list(current_app.mongo.db.books.find({'user_id': user_id, 'pdf_path': {'$ne': None}}).sort('added_at', -1))
    return render_template('nook/my_uploads.html', books=books)
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from bson import ObjectId
from datetime import datetime
import requests
from utils.decorators import login_required
from utils.google_books import search_books, get_book_details
from blueprints.rewards.services import RewardService

nook_bp = Blueprint('nook', __name__, template_folder='templates')

@nook_bp.route('/')
@login_required
def index():
    user_id = ObjectId(session['user_id'])
    books = list(current_app.mongo.db.books.find({'user_id': user_id}).sort('added_at', -1))
    
    # Calculate stats
    total_books = len(books)
    finished_books = len([b for b in books if b['status'] == 'finished'])
    reading_books = len([b for b in books if b['status'] == 'reading'])
    to_read_books = len([b for b in books if b['status'] == 'to_read'])
    
    # Calculate reading statistics
    total_pages_read = sum([b.get('current_page', 0) for b in books])
    avg_rating = sum([b.get('rating', 0) for b in books if b.get('rating', 0) > 0]) / max(1, len([b for b in books if b.get('rating', 0) > 0]))
    
    # Get recent activity
    recent_sessions = list(current_app.mongo.db.reading_sessions.find({
        'user_id': user_id
    }).sort('date', -1).limit(5))
    
    stats = {
        'total_books': total_books,
        'finished_books': finished_books,
        'reading_books': reading_books,
        'to_read_books': to_read_books,
        'total_pages_read': total_pages_read,
        'avg_rating': round(avg_rating, 1) if avg_rating > 0 else 0,
        'completion_rate': round((finished_books / total_books * 100), 1) if total_books > 0 else 0
    }
    
    return render_template('nook/index.html', 
                         books=books, 
                         stats=stats,
                         recent_sessions=recent_sessions)

@nook_bp.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():

    if request.method == 'POST':
        user_id = ObjectId(session['user_id'])
        # Enforce upload limit: max 10 books with PDF per user per month
        from datetime import timedelta
        month_ago = datetime.utcnow() - timedelta(days=30)
        upload_count = current_app.mongo.db.books.count_documents({
            'user_id': user_id,
            'pdf_path': {'$ne': None},
            'added_at': {'$gte': month_ago}
        })
        if upload_count >= 10:
            flash('Upload limit reached: Max 10 books with PDF per month.', 'danger')
            return redirect(request.url)

        pdf_file = request.files.get('pdf_file')
        pdf_path = None
        # Handle PDF upload if present
        if pdf_file and pdf_file.filename != '':
            if not pdf_file.filename.lower().endswith('.pdf'):
                flash('Only PDF files are allowed.', 'danger')
                return redirect(request.url)
            if pdf_file.mimetype != 'application/pdf':
                flash('Invalid file type.', 'danger')
                return redirect(request.url)
            pdf_file.seek(0, 2)
            file_size = pdf_file.tell()
            pdf_file.seek(0)
            if file_size > 10 * 1024 * 1024:
                flash('File size exceeds 10MB limit.', 'danger')
                return redirect(request.url)
            import os
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', str(user_id))
            os.makedirs(upload_dir, exist_ok=True)
            pdf_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{pdf_file.filename}"
            pdf_path = os.path.join(upload_dir, pdf_filename)
            pdf_file.save(pdf_path)
            # Store relative path for serving
            pdf_path = f"uploads/{user_id}/{pdf_filename}"

        # Check if it's a manual entry or from search
        if 'google_books_id' in request.form and request.form['google_books_id']:
            # From Google Books search
            book_data = {
                'user_id': user_id,
                'google_books_id': request.form['google_books_id'],
                'title': request.form['title'],
                'authors': request.form['authors'].split(','),
                'description': request.form.get('description', ''),
                'cover_image': request.form.get('cover_image', ''),
                'page_count': int(request.form.get('page_count', 0)),
                'current_page': 0,
                'status': request.form['status'],
                'added_at': datetime.utcnow(),
                'key_takeaways': [],
                'quotes': [],
                'rating': 0,
                'notes': '',
                'genre': request.form.get('genre', ''),
                'isbn': request.form.get('isbn', ''),
                'published_date': request.form.get('published_date', ''),
                'reading_sessions': [],
                'pdf_path': pdf_path
            }
        else:
            # Manual entry
            book_data = {
                'user_id': user_id,
                'title': request.form['title'],
                'authors': [author.strip() for author in request.form['authors'].split(',')],
                'description': request.form.get('description', ''),
                'page_count': int(request.form.get('page_count', 0)),
                'current_page': 0,
                'status': request.form['status'],
                'added_at': datetime.utcnow(),
                'key_takeaways': [],
                'quotes': [],
                'rating': 0,
                'notes': '',
                'genre': request.form.get('genre', ''),
                'isbn': request.form.get('isbn', ''),
                'published_date': request.form.get('published_date', ''),
                'reading_sessions': [],
                'pdf_path': pdf_path
            }

        result = current_app.mongo.db.books.insert_one(book_data)

        # Award points for adding a book
        RewardService.award_points(
            user_id=user_id,
            points=5,
            source='nook',
            description=f'Added book: {book_data["title"]}',
            category='book_management',
            reference_id=str(result.inserted_id)
        )

        flash('Book added successfully!', 'success')
        return redirect(url_for('nook.index'))

    return render_template('nook/add_book.html')

@nook_bp.route('/search_books')
@login_required
def search_books_route():
    query = request.args.get('q', '')
    if query:
        books = search_books(query)
        return jsonify(books)
    return jsonify([])

@nook_bp.route('/book/<book_id>')
@login_required
def book_detail(book_id):
    user_id = ObjectId(session['user_id'])
    book = current_app.mongo.db.books.find_one({
        '_id': ObjectId(book_id),
        'user_id': user_id
    })
    
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('nook.index'))
    
    # Get reading sessions for this book
    reading_sessions = list(current_app.mongo.db.reading_sessions.find({
        'user_id': user_id,
        'book_id': ObjectId(book_id)
    }).sort('date', -1))
    
    return render_template('nook/book_detail.html', book=book, reading_sessions=reading_sessions)

@nook_bp.route('/update_progress/<book_id>', methods=['POST'])
@login_required
def update_progress(book_id):
    user_id = ObjectId(session['user_id'])
    current_page = int(request.form['current_page'])
    session_notes = request.form.get('session_notes', '')
    
    book = current_app.mongo.db.books.find_one({
        '_id': ObjectId(book_id),
        'user_id': user_id
    })
    
    if book:
        old_page = book.get('current_page', 0)
        pages_read = max(0, current_page - old_page)
        
        # Update progress
        current_app.mongo.db.books.update_one(
            {'_id': ObjectId(book_id)},
            {'$set': {'current_page': current_page, 'last_read': datetime.utcnow()}}
        )
        
        # Log reading session
        session_data = {
            'user_id': user_id,
            'book_id': ObjectId(book_id),
            'pages_read': pages_read,
            'start_page': old_page,
            'end_page': current_page,
            'date': datetime.utcnow(),
            'notes': session_notes,
            'duration_minutes': int(request.form.get('duration_minutes', 0))
        }
        current_app.mongo.db.reading_sessions.insert_one(session_data)
        
        # Award points for reading progress
        if pages_read > 0:
            points = min(pages_read, 20)  # Max 20 points per session
            RewardService.award_points(
                user_id=user_id,
                points=points,
                source='nook',
                description=f'Read {pages_read} pages in {book["title"]}',
                category='reading_progress',
                reference_id=str(book_id)
            )
        
        # Check if book is finished
        if current_page >= book['page_count'] and book['status'] != 'finished':
            current_app.mongo.db.books.update_one(
                {'_id': ObjectId(book_id)},
                {'$set': {'status': 'finished', 'finished_at': datetime.utcnow()}}
            )
            
            # Award goal-based reward for book completion
            from blueprints.rewards.services import RewardService
            RewardService.award_points(
                user_id=ObjectId(session['user_id']),
                points=50,  # Base points for finishing a book
                source='nook',
                description=f'Finished reading "{book["title"]}"',
                category='book_completion',
                reference_id=ObjectId(book_id),
                goal_type='book_finished'  # This triggers the goal bonus
            )
            
            # Award completion points
            RewardService.award_points(
                user_id=user_id,
                points=50,
                source='nook',
                description=f'Finished reading: {book["title"]}',
                category='book_completion',
                reference_id=str(book_id)
            )
            
            flash('Congratulations! You finished the book! 🎉', 'success')
        
        flash('Progress updated!', 'success')
    
    return redirect(url_for('nook.book_detail', book_id=book_id))

@nook_bp.route('/add_takeaway/<book_id>', methods=['POST'])
@login_required
def add_takeaway(book_id):
    user_id = ObjectId(session['user_id'])
    takeaway = request.form['takeaway']
    page_reference = request.form.get('page_reference', '')
    
    takeaway_data = {
        'text': takeaway,
        'page_reference': page_reference,
        'date': datetime.utcnow(),
        'id': str(ObjectId())
    }
    
    current_app.mongo.db.books.update_one(
        {'_id': ObjectId(book_id), 'user_id': user_id},
        {'$push': {'key_takeaways': takeaway_data}}
    )
    
    # Award points for adding takeaway
    RewardService.award_points(
        user_id=user_id,
        points=3,
        source='nook',
        description='Added key takeaway',
        category='content_creation',
        reference_id=str(book_id)
    )
    
    flash('Key takeaway added!', 'success')
    return redirect(url_for('nook.book_detail', book_id=book_id))

@nook_bp.route('/add_quote/<book_id>', methods=['POST'])
@login_required
def add_quote(book_id):
    user_id = ObjectId(session['user_id'])
    quote = request.form['quote']
    page = request.form.get('page', '')
    context = request.form.get('context', '')
    
    quote_data = {
        'text': quote,
        'page': page,
        'context': context,
        'date': datetime.utcnow(),
        'id': str(ObjectId())
    }
    
    current_app.mongo.db.books.update_one(
        {'_id': ObjectId(book_id), 'user_id': user_id},
        {'$push': {'quotes': quote_data}}
    )
    
    # Award points for adding quote
    RewardService.award_points(
        user_id=user_id,
        points=2,
        source='nook',
        description='Added quote',
        category='content_creation',
        reference_id=str(book_id)
    )
    
    flash('Quote added!', 'success')
    return redirect(url_for('nook.book_detail', book_id=book_id))

@nook_bp.route('/rate_book/<book_id>', methods=['POST'])
@login_required
def rate_book(book_id):
    user_id = ObjectId(session['user_id'])
    rating = int(request.form['rating'])
    review = request.form.get('review', '')
    
    current_app.mongo.db.books.update_one(
        {'_id': ObjectId(book_id), 'user_id': user_id},
        {'$set': {
            'rating': rating,
            'review': review,
            'rated_at': datetime.utcnow()
        }}
    )
    
    # Award points for rating
    RewardService.award_points(
        user_id=user_id,
        points=5,
        source='nook',
        description='Rated a book',
        category='engagement',
        reference_id=str(book_id)
    )
    
    flash('Book rated successfully!', 'success')
    return redirect(url_for('nook.book_detail', book_id=book_id))

@nook_bp.route('/library')
@login_required
def library():
    user_id = ObjectId(session['user_id'])
    
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    genre_filter = request.args.get('genre', 'all')
    sort_by = request.args.get('sort', 'added_at')
    
    # Build query
    query = {'user_id': user_id}
    if status_filter != 'all':
        query['status'] = status_filter
    if genre_filter != 'all':
        query['genre'] = genre_filter
    
    # Get books with sorting
    sort_options = {
        'added_at': [('added_at', -1)],
        'title': [('title', 1)],
        'rating': [('rating', -1)],
        'progress': [('current_page', -1)]
    }
    
    books = list(current_app.mongo.db.books.find(query).sort(sort_options.get(sort_by, [('added_at', -1)])))
    
    # Get unique genres for filter
    all_books = list(current_app.mongo.db.books.find({'user_id': user_id}))
    genres = list(set([book.get('genre', '') for book in all_books if book.get('genre')]))
    
    return render_template('nook/library.html', 
                         books=books, 
                         genres=genres,
                         current_status=status_filter,
                         current_genre=genre_filter,
                         current_sort=sort_by)

@nook_bp.route('/analytics')
@login_required
def analytics():
    user_id = ObjectId(session['user_id'])
    
    # Get reading analytics data
    books = list(current_app.mongo.db.books.find({'user_id': user_id}))
    sessions = list(current_app.mongo.db.reading_sessions.find({'user_id': user_id}))
    
    # Calculate analytics
    analytics_data = {
        'total_books': len(books),
        'books_by_status': {},
        'books_by_genre': {},
        'reading_trend': {},
        'avg_rating': 0,
        'total_pages': sum([book.get('current_page', 0) for book in books]),
        'reading_streak': calculate_reading_streak(user_id)
    }
    
    # Books by status
    for book in books:
        status = book.get('status', 'unknown')
        analytics_data['books_by_status'][status] = analytics_data['books_by_status'].get(status, 0) + 1
    
    # Books by genre
    for book in books:
        genre = book.get('genre', 'Unknown')
        if genre:
            analytics_data['books_by_genre'][genre] = analytics_data['books_by_genre'].get(genre, 0) + 1
    
    # Average rating
    rated_books = [book for book in books if book.get('rating', 0) > 0]
    if rated_books:
        analytics_data['avg_rating'] = sum([book['rating'] for book in rated_books]) / len(rated_books)
    
    return render_template('nook/analytics.html', analytics=analytics_data)

def calculate_reading_streak(user_id):
    """Calculate current reading streak"""
    sessions = list(current_app.mongo.db.reading_sessions.find({
        'user_id': user_id
    }).sort('date', -1))
    
    if not sessions:
        return 0
    
    streak = 0
    current_date = datetime.now().date()
    
    # Group sessions by date
    session_dates = set()
    for session in sessions:
        session_dates.add(session['date'].date())
    
    # Calculate streak
    while current_date in session_dates:
        streak += 1
        current_date -= timedelta(days=1)
    
    return streak
