"""
Database Models and Initialization for Nook & Hook Application

This module contains all database schemas, initialization functions,
and setup utilities for the MongoDB-based Nook & Hook application.
"""

from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from bson import ObjectId
import os
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database initialization and schema creation"""
    
    @staticmethod
    def initialize_database():
        """Initialize database with all collections and indexes"""
        try:
            logger.info("Starting database initialization...")
            
            # Create collections and indexes
            DatabaseManager._create_collections()
            DatabaseManager._create_indexes()
            
            # Initialize default data
            DatabaseManager._create_default_admin()
            DatabaseManager._initialize_default_data()
            
            logger.info("Database initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            return False
    
    @staticmethod
    def _create_collections():
        """Create all required collections if they don't exist"""
        collections = [
            'users', 'books', 'reading_sessions', 'completed_tasks',
            'rewards', 'user_badges', 'user_goals', 'themes',
            'user_preferences', 'notifications', 'activity_log',
            'quotes', 'transactions', 'user_purchases',
            'clubs', 'club_posts', 'club_chat_messages',
            'flashcards', 'quiz_questions', 'quiz_answers', 'user_progress'
        ]
        existing_collections = current_app.mongo.db.list_collection_names()
        
        for collection in collections:
            if collection not in existing_collections:
                current_app.mongo.db.create_collection(collection)
                logger.info(f"Created collection: {collection}")
    
    @staticmethod
    def _create_indexes():
        """Create database indexes for optimal performance"""
        try:
            # Users collection indexes
            try:
                current_app.mongo.db.users.drop_index("username_1")
                logger.info("Dropped existing username_1 index")
            except Exception as e:
                logger.warning(f"No existing username_1 index to drop or error dropping: {str(e)}")

            null_username_docs = current_app.mongo.db.users.find({
                '$or': [
                    {'username': None},
                    {'username': {'$exists': False}}
                ]
            })
            for doc in null_username_docs:
                user_id = str(doc['_id'])
                current_app.mongo.db.users.delete_one({'_id': doc['_id']})
                logger.info(f"Deleted user document with null username, ID: {user_id}")

            current_app.mongo.db.users.create_index("username", unique=True)
            logger.info("Created unique index on users.username")

            current_app.mongo.db.users.create_index("email", unique=True)
            current_app.mongo.db.users.create_index("created_at")
            current_app.mongo.db.users.create_index("is_admin")  # Added for admin queries
            
            # Books collection indexes
            current_app.mongo.db.books.create_index([("user_id", 1), ("status", 1)])
            current_app.mongo.db.books.create_index([("user_id", 1), ("added_at", -1)])
            current_app.mongo.db.books.create_index("isbn", sparse=True)
            current_app.mongo.db.books.create_index("pdf_path", sparse=True)  # Added for encrypted PDF queries
            
            # Reading sessions indexes
            current_app.mongo.db.reading_sessions.create_index([("user_id", 1), ("date", -1)])
            current_app.mongo.db.reading_sessions.create_index([("user_id", 1), ("book_id", 1)])
            
            # Completed tasks indexes
            current_app.mongo.db.completed_tasks.create_index([("user_id", 1), ("completed_at", -1)])
            current_app.mongo.db.completed_tasks.create_index([("user_id", 1), ("category", 1)])
            
            # Rewards collection indexes
            current_app.mongo.db.rewards.create_index([("user_id", 1), ("date", -1)])
            current_app.mongo.db.rewards.create_index([("user_id", 1), ("source", 1)])
            current_app.mongo.db.rewards.create_index([("user_id", 1), ("category", 1)])
            
            # User badges indexes
            current_app.mongo.db.user_badges.create_index([("user_id", 1), ("badge_id", 1)], unique=True)
            current_app.mongo.db.user_badges.create_index([("user_id", 1), ("earned_at", -1)])
            
            # User goals indexes
            current_app.mongo.db.user_goals.create_index([("user_id", 1), ("is_active", 1)])
            current_app.mongo.db.user_goals.create_index([("user_id", 1), ("created_at", -1)])
            
            # Activity log indexes
            current_app.mongo.db.activity_log.create_index([("user_id", 1), ("timestamp", -1)])
            current_app.mongo.db.activity_log.create_index("timestamp", expireAfterSeconds=2592000)  # 30 days
            current_app.mongo.db.activity_log.create_index("action")  # Added for action-based queries
            
            # Quotes collection indexes
            current_app.mongo.db.quotes.create_index([("user_id", 1), ("status", 1)])
            current_app.mongo.db.quotes.create_index([("user_id", 1), ("submitted_at", -1)])
            current_app.mongo.db.quotes.create_index([("book_id", 1), ("user_id", 1)])
            current_app.mongo.db.quotes.create_index("status")
            current_app.mongo.db.quotes.create_index("submitted_at")
            
            # Transactions collection indexes
            current_app.mongo.db.transactions.create_index([("user_id", 1), ("timestamp", -1)])
            current_app.mongo.db.transactions.create_index([("user_id", 1), ("status", 1)])
            current_app.mongo.db.transactions.create_index("quote_id", sparse=True)
            current_app.mongo.db.transactions.create_index("reward_type")
            
            # User purchases collection indexes
            current_app.mongo.db.user_purchases.create_index([("user_id", 1), ("purchased_at", -1)])
            current_app.mongo.db.user_purchases.create_index([("user_id", 1), ("item_id", 1)])
            current_app.mongo.db.user_purchases.create_index([("user_id", 1), ("type", 1)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")
            raise
    
    @staticmethod
    def _create_default_admin():
        """Create default admin user from environment variables"""
        try:
            admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@nookhook.com')
            
            existing_admin = current_app.mongo.db.users.find_one({
                '$or': [
                    {'username': admin_username},
                    {'email': admin_email},
                    {'is_admin': True}
                ]
            })
            
            if existing_admin:
                logger.info("Admin user already exists, skipping creation")
                return
            
            admin_data = {
                'username': admin_username,
                'email': admin_email,
                'password_hash': generate_password_hash(admin_password),
                'is_admin': True,
                'is_active': True,
                'accepted_terms': True,  # Admin auto-accepts terms
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'total_points': 0,
                'level': 1,
                'profile': {
                    'display_name': 'Administrator',
                    'bio': 'System Administrator',
                    'avatar_url': None,
                    'timezone': 'UTC',
                    'theme': 'default'
                },
                'preferences': {
                    'notifications_enabled': True,
                    'email_notifications': True,
                    'privacy_level': 'private',
                    'default_book_status': 'to_read',
                    'reading_goal_type': 'books',
                    'reading_goal_target': 12
                },
                'statistics': {
                    'books_read': 0,
                    'pages_read': 0,
                    'reading_streak': 0,
                    'tasks_completed': 0,
                    'productivity_streak': 0,
                    'total_focus_time': 0
                }
            }
            
            result = current_app.mongo.db.users.insert_one(admin_data)
            
            ActivityLogger.log_activity(
                user_id=result.inserted_id,
                action='admin_created',
                description='Default admin user created',
                metadata={'username': admin_username}
            )
            
            logger.info(f"Default admin user created: {admin_username}")
            
        except Exception as e:
            logger.error(f"Error creating default admin: {str(e)}")
    
    @staticmethod
    def _initialize_default_data():
        """Initialize default application data"""
        try:
            default_themes = [
                {
                    'name': 'Default',
                    'slug': 'default',
                    'description': 'Clean and modern default theme',
                    'is_default': True,
                    'is_active': True,
                    'colors': {
                        'primary': '#007bff',
                        'secondary': '#6c757d',
                        'success': '#28a745',
                        'danger': '#dc3545',
                        'warning': '#ffc107',
                        'info': '#17a2b8',
                        'light': '#f8f9fa',
                        'dark': '#343a40'
                    },
                    'created_at': datetime.utcnow()
                },
                {
                    'name': 'Dark Mode',
                    'slug': 'dark',
                    'description': 'Easy on the eyes dark theme',
                    'is_default': False,
                    'is_active': True,
                    'colors': {
                        'primary': '#0d6efd',
                        'secondary': '#6c757d',
                        'success': '#198754',
                        'danger': '#dc3545',
                        'warning': '#ffc107',
                        'info': '#0dcaf0',
                        'light': '#212529',
                        'dark': '#f8f9fa'
                    },
                    'created_at': datetime.utcnow()
                }
            ]
            
            for theme in default_themes:
                existing_theme = current_app.mongo.db.themes.find_one({'slug': theme['slug']})
                if not existing_theme:
                    current_app.mongo.db.themes.insert_one(theme)
                    logger.info(f"Created default theme: {theme['name']}")
            
            logger.info("Default data initialization completed")
            
        except Exception as e:
            logger.error(f"Error initializing default data: {str(e)}")

class ClubModel:
    @staticmethod
    def create_club(name, description, topic, creator_id, **kwargs):
        club = {
            'name': name,
            'description': description,
            'topic': topic,
            'creator_id': creator_id,
            'members': [creator_id],
            'created_at': datetime.utcnow(),
            'admins': [creator_id],
            'goals': [],
            'shared_quotes': [],
            'is_active': True,
            **kwargs
        }
        return current_app.mongo.db.clubs.insert_one(club)

    @staticmethod
    def add_member(club_id, user_id):
        return current_app.mongo.db.clubs.update_one({'_id': ObjectId(club_id)}, {'$addToSet': {'members': user_id}})

    @staticmethod
    def add_admin(club_id, user_id):
        return current_app.mongo.db.clubs.update_one({'_id': ObjectId(club_id)}, {'$addToSet': {'admins': user_id}})

    @staticmethod
    def get_club(club_id):
        return current_app.mongo.db.clubs.find_one({'_id': ObjectId(club_id)})

    @staticmethod
    def get_all_clubs():
        return list(current_app.mongo.db.clubs.find({'is_active': True}))

class ClubPostModel:
    @staticmethod
    def create_post(club_id, user_id, content):
        post = {
            'club_id': ObjectId(club_id),
            'user_id': user_id,
            'content': content,
            'created_at': datetime.utcnow(),
            'comments': [],
            'likes': []
        }
        return current_app.mongo.db.club_posts.insert_one(post)

    @staticmethod
    def get_posts(club_id):
        return list(current_app.mongo.db.club_posts.find({'club_id': ObjectId(club_id)}).sort('created_at', -1))

class ClubChatMessageModel:
    @staticmethod
    def send_message(club_id, user_id, message):
        msg = {
            'club_id': ObjectId(club_id),
            'user_id': user_id,
            'message': message,
            'timestamp': datetime.utcnow()
        }
        return current_app.mongo.db.club_chat_messages.insert_one(msg)

    @staticmethod
    def get_messages(club_id, limit=50):
        return list(current_app.mongo.db.club_chat_messages.find({'club_id': ObjectId(club_id)}).sort('timestamp', -1).limit(limit))

class FlashcardModel:
    @staticmethod
    def create_flashcard(user_id, front, back, tags=None):
        card = {
            'user_id': user_id,
            'front': front,
            'back': back,
            'tags': tags or [],
            'created_at': datetime.utcnow(),
            'review_count': 0
        }
        return current_app.mongo.db.flashcards.insert_one(card)

    @staticmethod
    def get_user_flashcards(user_id):
        return list(current_app.mongo.db.flashcards.find({'user_id': user_id}))

class QuizQuestionModel:
    @staticmethod
    def create_question(question, options, answer, creator_id, tags=None):
        q = {
            'question': question,
            'options': options,
            'answer': answer,
            'creator_id': creator_id,
            'tags': tags or [],
            'created_at': datetime.utcnow()
        }
        return current_app.mongo.db.quiz_questions.insert_one(q)

    @staticmethod
    def get_daily_questions(limit=5):
        return list(current_app.mongo.db.quiz_questions.aggregate([{'$sample': {'size': limit}}]))

class QuizAnswerModel:
    @staticmethod
    def submit_answer(user_id, question_id, answer, is_correct):
        ans = {
            'user_id': user_id,
            'question_id': ObjectId(question_id),
            'answer': answer,
            'is_correct': is_correct,
            'submitted_at': datetime.utcnow()
        }
        return current_app.mongo.db.quiz_answers.insert_one(ans)

    @staticmethod
    def get_user_answers(user_id):
        return list(current_app.mongo.db.quiz_answers.find({'user_id': user_id}))

class UserProgressModel:
    @staticmethod
    def update_progress(user_id, module, data):
        return current_app.mongo.db.user_progress.update_one(
            {'user_id': user_id, 'module': module},
            {'$set': {'data': data, 'updated_at': datetime.utcnow()}},
            upsert=True
        )

    @staticmethod
    def get_progress(user_id, module):
        return current_app.mongo.db.user_progress.find_one({'user_id': user_id, 'module': module})

class UserModel:
    """User model with CRUD operations and utilities"""
    
    @staticmethod
    def create_user(username, email, password, **kwargs):
        """Create a new user with validation"""
        try:
            existing_user = current_app.mongo.db.users.find_one({
                '$or': [
                    {'username': username},
                    {'email': email}
                ]
            })
            
            if existing_user:
                return None, "Username or email already exists"
            
            user_data = {
                'username': username,
                'email': email,
                'password_hash': generate_password_hash(password),
                'is_admin': kwargs.get('is_admin', False),
                'is_active': kwargs.get('is_active', True),
                'accepted_terms': kwargs.get('accepted_terms', False),  # Track terms agreement
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'last_login': None,
                'total_points': 0,
                'level': 1,
                'profile': {
                    'display_name': kwargs.get('display_name', username),
                    'bio': kwargs.get('bio', ''),
                    'avatar_url': kwargs.get('avatar_url'),
                    'timezone': kwargs.get('timezone', 'UTC'),
                    'theme': kwargs.get('theme', 'default')
                },
                'preferences': {
                    'notifications_enabled': True,
                    'email_notifications': True,
                    'privacy_level': 'public',
                    'default_book_status': 'to_read',
                    'reading_goal_type': 'books',
                    'reading_goal_target': 12
                },
                'statistics': {
                    'books_read': 0,
                    'pages_read': 0,
                    'reading_streak': 0,
                    'tasks_completed': 0,
                    'productivity_streak': 0,
                    'total_focus_time': 0
                }
            }
            
            result = current_app.mongo.db.users.insert_one(user_data)
            
            ActivityLogger.log_activity(
                user_id=result.inserted_id,
                action='user_registered',
                description='New user account created',
                metadata={'accepted_terms': user_data['accepted_terms']}
            )
            
            return result.inserted_id, None
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def authenticate_user(username, password):
        """Authenticate user credentials"""
        try:
            user = current_app.mongo.db.users.find_one({
                '$or': [
                    {'username': username},
                    {'email': username}
                ],
                'is_active': True
            })
            
            if user and check_password_hash(user['password_hash'], password):
                if not user.get('accepted_terms', False):
                    return None  # Deny login if terms not accepted
                
                current_app.mongo.db.users.update_one(
                    {'_id': user['_id']},
                    {'$set': {'last_login': datetime.utcnow()}}
                )
                
                ActivityLogger.log_activity(
                    user_id=user['_id'],
                    action='user_login',
                    description='User logged in'
                )
                
                return user
            
            return None
            
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return None
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        try:
            return current_app.mongo.db.users.find_one({'_id': ObjectId(user_id)})
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            return None
    
    @staticmethod
    def update_user(user_id, update_data):
        """Update user data"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            
            result = current_app.mongo.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                ActivityLogger.log_activity(
                    user_id=ObjectId(user_id),
                    action='user_updated',
                    description='User profile updated',
                    metadata={'updated_fields': list(update_data.keys())}
                )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return False
    
    @staticmethod
    def delete_user(user_id):
        """Soft delete user (deactivate)"""
        try:
            result = current_app.mongo.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        'is_active': False,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                ActivityLogger.log_activity(
                    user_id=ObjectId(user_id),
                    action='user_deactivated',
                    description='User account deactivated'
                )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return False

class BookModel:
    """Book model with CRUD operations"""
    
    @staticmethod
    def create_book(user_id, title, authors=None, **kwargs):
        """Create a new book entry"""
        try:
            book_data = {
                'user_id': ObjectId(user_id),
                'title': title,
                'authors': authors or [],
                'isbn': kwargs.get('isbn'),
                'genre': kwargs.get('genre', 'General'),
                'description': kwargs.get('description', ''),
                'cover_url': kwargs.get('cover_url'),
                'total_pages': kwargs.get('total_pages', 0),
                'current_page': kwargs.get('current_page', 0),
                'status': kwargs.get('status', 'to_read'),
                'rating': kwargs.get('rating'),
                'review': kwargs.get('review', ''),
                'quotes': kwargs.get('quotes', []),
                'notes': kwargs.get('notes', []),
                'tags': kwargs.get('tags', []),
                'added_at': datetime.utcnow(),
                'started_at': kwargs.get('started_at'),
                'finished_at': kwargs.get('finished_at'),
                'updated_at': datetime.utcnow(),
                'pdf_path': kwargs.get('pdf_path'),
                'is_encrypted': kwargs.get('is_encrypted', False)  # Track encryption status
            }
            
            result = current_app.mongo.db.books.insert_one(book_data)
            
            ActivityLogger.log_activity(
                user_id=ObjectId(user_id),
                action='book_added',
                description=f'Added book: {title}',
                metadata={'book_id': str(result.inserted_id), 'has_pdf': bool(book_data['pdf_path']), 'is_encrypted': book_data['is_encrypted']}
            )
            
            return result.inserted_id
            
        except Exception as e:
            logger.error(f"Error creating book: {str(e)}")
            return None
    
    @staticmethod
    def update_book_status(book_id, status, user_id):
        """Update book reading status"""
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.utcnow()
            }
            
            if status == 'reading' and not current_app.mongo.db.books.find_one({'_id': ObjectId(book_id)}).get('started_at'):
                update_data['started_at'] = datetime.utcnow()
            elif status == 'finished':
                update_data['finished_at'] = datetime.utcnow()
            
            result = current_app.mongo.db.books.update_one(
                {'_id': ObjectId(book_id), 'user_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                if status == 'finished':
                    from blueprints.rewards.services import RewardService
                    book = current_app.mongo.db.books.find_one({'_id': ObjectId(book_id)})
                    if book:
                        RewardService.award_points(
                            user_id=ObjectId(user_id),
                            points=50,
                            source='nook',
                            description=f'Finished reading "{book["title"]}"',
                            category='book_completion',
                            reference_id=ObjectId(book_id),
                            goal_type='book_finished'
                        )
                
                ActivityLogger.log_activity(
                    user_id=ObjectId(user_id),
                    action='book_status_updated',
                    description=f'Book status changed to: {status}',
                    metadata={'book_id': book_id}
                )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating book status: {str(e)}")
            return False

class TaskModel:
    """Task model for productivity tracking"""
    
    @staticmethod
    def create_completed_task(user_id, title, duration, **kwargs):
        """Create a completed task record"""
        try:
            task_data = {
                'user_id': ObjectId(user_id),
                'title': title,
                'description': kwargs.get('description', ''),
                'category': kwargs.get('category', 'general'),
                'duration': duration,
                'priority': kwargs.get('priority', 'medium'),
                'tags': kwargs.get('tags', []),
                'completed_at': kwargs.get('completed_at', datetime.utcnow()),
                'created_at': datetime.utcnow()
            }
            
            result = current_app.mongo.db.completed_tasks.insert_one(task_data)
            
            ActivityLogger.log_activity(
                user_id=ObjectId(user_id),
                action='task_completed',
                description=f'Completed task: {title}',
                metadata={'task_id': str(result.inserted_id), 'duration': duration}
            )
            
            return result.inserted_id
            
        except Exception as e:
            logger.error(f"Error creating completed task: {str(e)}")
            return None

class ReadingSessionModel:
    """Reading session model"""
    
    @staticmethod
    def create_session(user_id, book_id, pages_read, **kwargs):
        """Create a reading session record"""
        try:
            session_data = {
                'user_id': ObjectId(user_id),
                'book_id': ObjectId(book_id) if book_id else None,
                'pages_read': pages_read,
                'duration': kwargs.get('duration', 0),
                'notes': kwargs.get('notes', ''),
                'date': kwargs.get('date', datetime.utcnow()),
                'created_at': datetime.utcnow()
            }
            
            result = current_app.mongo.db.reading_sessions.insert_one(session_data)
            
            if book_id:
                current_app.mongo.db.books.update_one(
                    {'_id': ObjectId(book_id)},
                    {'$inc': {'current_page': pages_read}}
                )
            
            ActivityLogger.log_activity(
                user_id=ObjectId(user_id),
                action='reading_session',
                description=f'Read {pages_read} pages',
                metadata={'session_id': str(result.inserted_id), 'pages': pages_read}
            )
            
            return result.inserted_id
            
        except Exception as e:
            logger.error(f"Error creating reading session: {str(e)}")
            return None

class ActivityLogger:
    """Activity logging utility"""
    
    @staticmethod
    def log_activity(user_id, action, description, metadata=None):
        """Log user activity"""
        try:
            activity_data = {
                'user_id': ObjectId(user_id),
                'action': action,
                'description': description,
                'metadata': metadata or {},
                'timestamp': datetime.utcnow(),
                'ip_address': None,
                'user_agent': None
            }
            
            current_app.mongo.db.activity_log.insert_one(activity_data)
            
        except Exception as e:
            logger.error(f"Error logging activity: {str(e)}")

class AdminUtils:
    """Admin utilities for user and data management"""
    
    @staticmethod
    def get_all_users(page=1, per_page=50, search=None):
        """Get paginated list of all users"""
        try:
            query = {}
            if search:
                query = {
                    '$or': [
                        {'username': {'$regex': search, '$options': 'i'}},
                        {'email': {'$regex': search, '$options': 'i'}},
                        {'profile.display_name': {'$regex': search, '$options': 'i'}}
                    ]
                }
            
            skip = (page - 1) * per_page
            users = list(current_app.mongo.db.users.find(query)
                        .sort('created_at', -1)
                        .skip(skip)
                        .limit(per_page))
            
            total_users = current_app.mongo.db.users.count_documents(query)
            
            return users, total_users
            
        except Exception as e:
            logger.error(f"Error getting users: {str(e)}")
            return [], 0
    
    @staticmethod
    def update_user_points(user_id, points, description="Admin adjustment"):
        """Admin function to update user points"""
        try:
            from blueprints.rewards.services import RewardService
            
            RewardService.award_points(
                user_id=ObjectId(user_id),
                points=points,
                source='admin',
                description=description,
                category='admin_adjustment'
            )
            
            ActivityLogger.log_activity(
                user_id=ObjectId(user_id),
                action='admin_points_adjustment',
                description=f'Admin adjusted points by {points}',
                metadata={'points': points, 'description': description}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating user points: {str(e)}")
            return False
    
    @staticmethod
    def reset_user_progress(user_id, reset_type='all'):
        """Admin function to reset user progress"""
        try:
            user_id = ObjectId(user_id)
            
            if reset_type in ['all', 'rewards']:
                current_app.mongo.db.rewards.delete_many({'user_id': user_id})
                current_app.mongo.db.user_badges.delete_many({'user_id': user_id})
                current_app.mongo.db.users.update_one(
                    {'_id': user_id},
                    {'$set': {'total_points': 0, 'level': 1}}
                )
            
            if reset_type in ['all', 'books']:
                current_app.mongo.db.books.delete_many({'user_id': user_id})
                current_app.mongo.db.reading_sessions.delete_many({'user_id': user_id})
            
            if reset_type in ['all', 'tasks']:
                current_app.mongo.db.completed_tasks.delete_many({'user_id': user_id})
            
            if reset_type in ['all', 'goals']:
                current_app.mongo.db.user_goals.delete_many({'user_id': user_id})
            
            current_app.mongo.db.users.update_one(
                {'_id': user_id},
                {
                    '$set': {
                        'statistics': {
                            'books_read': 0,
                            'pages_read': 0,
                            'reading_streak': 0,
                            'tasks_completed': 0,
                            'productivity_streak': 0,
                            'total_focus_time': 0
                        },
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            ActivityLogger.log_activity(
                user_id=user_id,
                action='admin_progress_reset',
                description=f'Admin reset user progress: {reset_type}',
                metadata={'reset_type': reset_type}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error resetting user progress: {str(e)}")
            return False
    
    @staticmethod
    def get_system_statistics():
        """Get system-wide statistics"""
        try:
            stats = {
                'users': {
                    'total': current_app.mongo.db.users.count_documents({}),
                    'active': current_app.mongo.db.users.count_documents({'is_active': True}),
                    'admins': current_app.mongo.db.users.count_documents({'is_admin': True}),
                    'terms_accepted': current_app.mongo.db.users.count_documents({'accepted_terms': True})
                },
                'books': {
                    'total': current_app.mongo.db.books.count_documents({}),
                    'finished': current_app.mongo.db.books.count_documents({'status': 'finished'}),
                    'reading': current_app.mongo.db.books.count_documents({'status': 'reading'}),
                    'with_pdf': current_app.mongo.db.books.count_documents({'pdf_path': {'$ne': None}}),
                    'encrypted': current_app.mongo.db.books.count_documents({'is_encrypted': True})
                },
                'tasks': {
                    'total': current_app.mongo.db.completed_tasks.count_documents({}),
                    'today': current_app.mongo.db.completed_tasks.count_documents({
                        'completed_at': {'$gte': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}
                    })
                },
                'rewards': {
                    'total_points': list(current_app.mongo.db.rewards.aggregate([
                        {'$group': {'_id': None, 'total': {'$sum': '$points'}}}
                    ]))[0].get('total', 0),
                    'total_rewards': current_app.mongo.db.rewards.count_documents({}),
                    'badges_earned': current_app.mongo.db.user_badges.count_documents({})
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting system statistics: {str(e)}")
            return {}

# Database validation schemas
USER_SCHEMA = {
    'username': {'type': 'string', 'required': True, 'unique': True},
    'email': {'type': 'string', 'required': True, 'unique': True},
    'password_hash': {'type': 'string', 'required': True},
    'is_admin': {'type': 'boolean', 'default': False},
    'is_active': {'type': 'boolean', 'default': True},
    'accepted_terms': {'type': 'boolean', 'default': False},  # Added for terms agreement
    'created_at': {'type': 'datetime', 'required': True},
    'updated_at': {'type': 'datetime', 'required': True},
    'last_login': {'type': 'datetime'},
    'total_points': {'type': 'integer', 'default': 0},
    'level': {'type': 'integer', 'default': 1}
}

BOOK_SCHEMA = {
    'user_id': {'type': 'objectid', 'required': True},
    'title': {'type': 'string', 'required': True},
    'authors': {'type': 'list'},
    'isbn': {'type': 'string'},
    'genre': {'type': 'string'},
    'status': {'type': 'string', 'allowed': ['to_read', 'reading', 'finished']},
    'total_pages': {'type': 'integer'},
    'current_page': {'type': 'integer'},
    'added_at': {'type': 'datetime', 'required': True},
    'pdf_path': {'type': 'string'},  # Path to encrypted PDF
    'is_encrypted': {'type': 'boolean', 'default': False}  # Track encryption status
}

TASK_SCHEMA = {
    'user_id': {'type': 'objectid', 'required': True},
    'title': {'type': 'string', 'required': True},
    'description': {'type': 'string'},
    'category': {'type': 'string'},
    'duration': {'type': 'integer', 'required': True},
    'completed_at': {'type': 'datetime', 'required': True}
}

QUOTE_SCHEMA = {
    'user_id': {'type': 'objectid', 'required': True},
    'book_id': {'type': 'objectid', 'required': True},
    'quote_text': {'type': 'string', 'required': True},
    'page_number': {'type': 'integer', 'required': True},
    'status': {'type': 'string', 'allowed': ['pending', 'verified', 'rejected'], 'default': 'pending'},
    'submitted_at': {'type': 'datetime', 'required': True},
    'verified_at': {'type': 'datetime'},
    'verified_by': {'type': 'objectid'},
    'rejection_reason': {'type': 'string'},
    'reward_amount': {'type': 'integer', 'default': 10}
}

TRANSACTION_SCHEMA = {
    'user_id': {'type': 'objectid', 'required': True},
    'amount': {'type': 'integer', 'required': True},
    'reward_type': {'type': 'string', 'required': True},
    'quote_id': {'type': 'objectid'},
    'description': {'type': 'string'},
    'timestamp': {'type': 'datetime', 'required': True},
    'status': {'type': 'string', 'allowed': ['pending', 'completed', 'failed'], 'default': 'completed'}
}

REWARD_SCHEMA = {
    'user_id': {'type': 'objectid', 'required': True},
    'points': {'type': 'integer', 'required': True},
    'source': {'type': 'string', 'required': True},
    'description': {'type': 'string', 'required': True},
    'category': {'type': 'string'},
    'date': {'type': 'datetime', 'required': True}
}

class QuoteModel:
    """Quote model for managing book quotes and verification"""
    
    @staticmethod
    def submit_quote(user_id, book_id, quote_text, page_number):
        """Submit a new quote for verification"""
        try:
            book = current_app.mongo.db.books.find_one({
                '_id': ObjectId(book_id),
                'user_id': ObjectId(user_id)
            })
            
            if not book:
                return None, "Book not found or doesn't belong to user"
            
            if book.get('total_pages', 0) > 0 and page_number > book['total_pages']:
                return None, f"Page number {page_number} exceeds book's total pages ({book['total_pages']})"
            
            existing_quote = current_app.mongo.db.quotes.find_one({
                'user_id': ObjectId(user_id),
                'book_id': ObjectId(book_id),
                'quote_text': quote_text.strip(),
                'status': {'$in': ['pending', 'verified']}
            })
            
            if existing_quote:
                return None, "This quote has already been submitted"
            
            quote_data = {
                'user_id': ObjectId(user_id),
                'book_id': ObjectId(book_id),
                'quote_text': quote_text.strip(),
                'page_number': page_number,
                'status': 'pending',
                'submitted_at': datetime.utcnow(),
                'verified_at': None,
                'verified_by': None,
                'rejection_reason': None,
                'reward_amount': 10
            }
            
            result = current_app.mongo.db.quotes.insert_one(quote_data)
            
            ActivityLogger.log_activity(
                user_id=ObjectId(user_id),
                action='quote_submitted',
                description=f'Submitted quote from "{book["title"]}" page {page_number}',
                metadata={
                    'quote_id': str(result.inserted_id),
                    'book_title': book['title'],
                    'book_id': str(book_id),
                    'page_number': page_number,
                    'quote_text': quote_text.strip()
                }
            )
            
            return result.inserted_id, None
            
        except Exception as e:
            logger.error(f"Error submitting quote: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def get_pending_quotes(page=1, per_page=20):
        """Get paginated list of pending quotes for admin verification"""
        try:
            skip = (page - 1) * per_page
            
            pipeline = [
                {'$match': {'status': 'pending'}},
                {'$lookup': {
                    'from': 'users',
                    'localField': 'user_id',
                    'foreignField': '_id',
                    'as': 'user'
                }},
                {'$lookup': {
                    'from': 'books',
                    'localField': 'book_id',
                    'foreignField': '_id',
                    'as': 'book'
                }},
                {'$unwind': '$user'},
                {'$unwind': '$book'},
                {'$sort': {'submitted_at': 1}},
                {'$skip': skip},
                {'$limit': per_page}
            ]
            
            quotes = list(current_app.mongo.db.quotes.aggregate(pipeline))
            total_pending = current_app.mongo.db.quotes.count_documents({'status': 'pending'})
            
            return quotes, total_pending
            
        except Exception as e:
            logger.error(f"Error getting pending quotes: {str(e)}")
            return [], 0
    
    @staticmethod
    def verify_quote(quote_id, admin_id, approved=True, rejection_reason=None):
        """Admin function to verify or reject a quote"""
        try:
            quote = current_app.mongo.db.quotes.find_one({'_id': ObjectId(quote_id)})
            if not quote:
                return False, "Quote not found"
            
            if quote['status'] != 'pending':
                return False, "Quote has already been processed"
            
            update_data = {
                'verified_at': datetime.utcnow(),
                'verified_by': ObjectId(admin_id)
            }
            
            if approved:
                update_data['status'] = 'verified'
                
                from blueprints.rewards.services import RewardService
                
                RewardService.award_points(
                    user_id=quote['user_id'],
                    points=quote['reward_amount'],
                    source='quotes',
                    description=f'Quote verified from page {quote["page_number"]}',
                    category='quote_verified',
                    reference_id=ObjectId(quote_id),
                    goal_type='quote_reflection'
                )
                
                TransactionModel.create_transaction(
                    user_id=quote['user_id'],
                    amount=quote['reward_amount'],
                    reward_type='quote_verified',
                    quote_id=ObjectId(quote_id),
                    description=f"Quote verification reward - Page {quote['page_number']}"
                )
                
                ActivityLogger.log_activity(
                    user_id=quote['user_id'],
                    action='quote_verified',
                    description=f'Quote verified and rewarded ₦{quote["reward_amount"]}',
                    metadata={
                        'quote_id': str(quote_id),
                        'reward_amount': quote['reward_amount'],
                        'verified_by': str(admin_id),
                        'book_id': str(quote['book_id']),
                        'page_number': quote['page_number']
                    }
                )
                
            else:
                update_data['status'] = 'rejected'
                update_data['rejection_reason'] = rejection_reason or "Quote could not be verified"
                
                ActivityLogger.log_activity(
                    user_id=quote['user_id'],
                    action='quote_rejected',
                    description=f'Quote rejected: {rejection_reason or "Could not be verified"}',
                    metadata={
                        'quote_id': str(quote_id),
                        'rejection_reason': rejection_reason,
                        'verified_by': str(admin_id),
                        'book_id': str(quote['book_id']),
                        'page_number': quote['page_number']
                    }
                )
            
            result = current_app.mongo.db.quotes.update_one(
                {'_id': ObjectId(quote_id)},
                {'$set': update_data}
            )
            
            return result.modified_count > 0, None
            
        except Exception as e:
            logger.error(f"Error verifying quote: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def get_user_quotes(user_id, status=None, page=1, per_page=20):
        """Get user's quotes with optional status filter"""
        try:
            query = {'user_id': ObjectId(user_id)}
            if status:
                query['status'] = status
            
            skip = (page - 1) * per_page
            
            pipeline = [
                {'$match': query},
                {'$lookup': {
                    'from': 'books',
                    'localField': 'book_id',
                    'foreignField': '_id',
                    'as': 'book'
                }},
                {'$unwind': '$book'},
                {'$sort': {'submitted_at': -1}},
                {'$skip': skip},
                {'$limit': per_page}
            ]
            
            quotes = list(current_app.mongo.db.quotes.aggregate(pipeline))
            total_quotes = current_app.mongo.db.quotes.count_documents(query)
            
            return quotes, total_quotes
            
        except Exception as e:
            logger.error(f"Error getting user quotes: {str(e)}")
            return [], 0
    
    @staticmethod
    def get_quote_statistics(user_id=None):
        """Get quote statistics for user or system-wide"""
        try:
            match_stage = {}
            if user_id:
                match_stage = {'user_id': ObjectId(user_id)}
            
            pipeline = [
                {'$match': match_stage},
                {'$group': {
                    '_id': '$status',
                    'count': {'$sum': 1},
                    'total_reward': {'$sum': '$reward_amount'}
                }}
            ]
            
            results = list(current_app.mongo.db.quotes.aggregate(pipeline))
            
            stats = {
                'pending': {'count': 0, 'total_reward': 0},
                'verified': {'count': 0, 'total_reward': 0},
                'rejected': {'count': 0, 'total_reward': 0}
            }
            
            for result in results:
                status = result['_id']
                if status in stats:
                    stats[status] = {
                        'count': result['count'],
                        'total_reward': result['total_reward']
                    }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting quote statistics: {str(e)}")
            return {}

class TransactionModel:
    """Transaction model for tracking all financial transactions"""
    
    @staticmethod
    def create_transaction(user_id, amount, reward_type, description, quote_id=None, status='completed'):
        """Create a new transaction record"""
        try:
            transaction_data = {
                'user_id': ObjectId(user_id),
                'amount': amount,
                'reward_type': reward_type,
                'quote_id': ObjectId(quote_id) if quote_id else None,
                'description': description,
                'timestamp': datetime.utcnow(),
                'status': status
            }
            
            result = current_app.mongo.db.transactions.insert_one(transaction_data)
            
            ActivityLogger.log_activity(
                user_id=ObjectId(user_id),
                action='transaction_created',
                description=f'Transaction: {description}',
                metadata={
                    'transaction_id': str(result.inserted_id),
                    'amount': amount,
                    'reward_type': reward_type,
                    'quote_id': str(quote_id) if quote_id else None
                }
            )
            
            return result.inserted_id
            
        except Exception as e:
            logger.error(f"Error creating transaction: {str(e)}")
            return None
    
    @staticmethod
    def get_user_transactions(user_id, page=1, per_page=20):
        """Get user's transaction history"""
        try:
            skip = (page - 1) * per_page
            
            pipeline = [
                {'$match': {'user_id': ObjectId(user_id)}},
                {'$lookup': {
                    'from': 'quotes',
                    'localField': 'quote_id',
                    'foreignField': '_id',
                    'as': 'quote'
                }},
                {'$sort': {'timestamp': -1}},
                {'$skip': skip},
                {'$limit': per_page}
            ]
            
            transactions = list(current_app.mongo.db.transactions.aggregate(pipeline))
            total_transactions = current_app.mongo.db.transactions.count_documents({'user_id': ObjectId(user_id)})
            
            return transactions, total_transactions
            
        except Exception as e:
            logger.error(f"Error getting user transactions: {str(e)}")
            return [], 0
    
    @staticmethod
    def get_user_balance(user_id):
        """Get user's current balance from transactions"""
        try:
            pipeline = [
                {'$match': {'user_id': ObjectId(user_id), 'status': 'completed'}},
                {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
            ]
            
            result = list(current_app.mongo.db.transactions.aggregate(pipeline))
            return result[0]['total'] if result else 0
            
        except Exception as e:
            logger.error(f"Error getting user balance: {str(e)}")
            return 0

class GoogleBooksAPI:
    """Google Books API integration for book verification"""
    
    @staticmethod
    def search_books(query, max_results=10):
        """Search for books using Google Books API"""
        try:
            url = "https://www.googleapis.com/books/v1/volumes"
            params = {
                'q': query,
                'maxResults': max_results,
                'printType': 'books',
                'langRestrict': 'en'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            books = []
            
            for item in data.get('items', []):
                volume_info = item.get('volumeInfo', {})
                
                book = {
                    'google_id': item.get('id'),
                    'title': volume_info.get('title', 'Unknown Title'),
                    'authors': volume_info.get('authors', []),
                    'description': volume_info.get('description', ''),
                    'page_count': volume_info.get('pageCount', 0),
                    'published_date': volume_info.get('publishedDate', ''),
                    'isbn': None,
                    'cover_url': None
                }
                
                for identifier in volume_info.get('industryIdentifiers', []):
                    if identifier.get('type') in ['ISBN_13', 'ISBN_10']:
                        book['isbn'] = identifier.get('identifier')
                        break
                
                image_links = volume_info.get('imageLinks', {})
                book['cover_url'] = image_links.get('thumbnail') or image_links.get('smallThumbnail')
                
                books.append(book)
            
            return books
            
        except Exception as e:
            logger.error(f"Error searching Google Books: {str(e)}")
            return []
    
    @staticmethod
    def get_book_details(google_id):
        """Get detailed book information by Google Books ID"""
        try:
            url = f"https://www.googleapis.com/books/v1/volumes/{google_id}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            volume_info = data.get('volumeInfo', {})
            
            book = {
                'google_id': data.get('id'),
                'title': volume_info.get('title', 'Unknown Title'),
                'authors': volume_info.get('authors', []),
                'description': volume_info.get('description', ''),
                'page_count': volume_info.get('pageCount', 0),
                'published_date': volume_info.get('publishedDate', ''),
                'publisher': volume_info.get('publisher', ''),
                'language': volume_info.get('language', 'en'),
                'isbn': None,
                'cover_url': None
            }
            
            for identifier in volume_info.get('industryIdentifiers', []):
                if identifier.get('type') in ['ISBN_13', 'ISBN_10']:
                    book['isbn'] = identifier.get('identifier')
                    break
            
            image_links = volume_info.get('imageLinks', {})
            book['cover_url'] = image_links.get('thumbnail') or image_links.get('smallThumbnail')
            
            return book
            
        except Exception as e:
            logger.error(f"Error getting book details: {str(e)}")
            return None
