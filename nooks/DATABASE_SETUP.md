# Database Setup and Models Documentation

## Overview

The Nook & Hook application uses MongoDB as its primary database with a comprehensive model system that handles user management, book tracking, productivity tasks, and gamification features.

## Database Architecture

### Collections

1. **users** - User accounts and profiles
2. **books** - User's book library
3. **reading_sessions** - Reading activity tracking
4. **completed_tasks** - Productivity task records
5. **rewards** - Points and reward system
6. **user_badges** - Achievement badges
7. **user_goals** - Personal goals and targets
8. **themes** - UI themes and customization
9. **user_preferences** - User settings
10. **notifications** - System notifications
11. **activity_log** - User activity tracking (auto-expires after 30 days)

### Key Features

- **Robust Initialization**: Checks for existing data before creating to prevent duplicates
- **Automatic Indexing**: Creates optimal database indexes for performance
- **Admin User Setup**: Automatically creates admin user from environment variables
- **Activity Logging**: Comprehensive activity tracking with automatic cleanup
- **Data Validation**: Schema validation and error handling
- **Bulk Operations**: Admin tools for managing multiple users

## Environment Variables

Set these environment variables for proper database initialization:

```bash
# Required
MONGO_URI=mongodb://localhost:27017/nook_hook_app

# Admin User (will be created automatically)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_EMAIL=admin@nookhook.com

# Optional
SECRET_KEY=your-secret-key-here
GOOGLE_BOOKS_API_KEY=your-api-key-here
PORT=5000
```

## Database Initialization

### Method 1: Automatic (Recommended)
The database initializes automatically when the Flask app starts:

```python
python app.py
```

### Method 2: Manual Initialization
Run the dedicated initialization script:

```python
python init_db.py
```

### Method 3: Programmatic
```python
from models import DatabaseManager
from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_URI'] = 'your-mongodb-uri'
mongo = PyMongo(app)
app.mongo = mongo

with app.app_context():
    DatabaseManager.initialize_database()
```

## Model Classes

### DatabaseManager
Handles database initialization, collection creation, and indexing.

```python
from models import DatabaseManager

# Initialize entire database
DatabaseManager.initialize_database()
```

### UserModel
User account management with authentication and profile handling.

```python
from models import UserModel

# Create new user
user_id, error = UserModel.create_user(
    username="john_doe",
    email="john@example.com",
    password="secure_password",
    display_name="John Doe"
)

# Authenticate user
user = UserModel.authenticate_user("john_doe", "secure_password")

# Update user
UserModel.update_user(user_id, {"profile.bio": "Updated bio"})
```

### BookModel
Book library management with reading progress tracking.

```python
from models import BookModel

# Add new book
book_id = BookModel.create_book(
    user_id=user_id,
    title="The Great Gatsby",
    authors=["F. Scott Fitzgerald"],
    genre="Classic Literature",
    total_pages=180
)

# Update reading status
BookModel.update_book_status(book_id, "reading", user_id)
```

### TaskModel
Productivity task tracking and completion records.

```python
from models import TaskModel

# Record completed task
task_id = TaskModel.create_completed_task(
    user_id=user_id,
    title="Complete project proposal",
    duration=90,  # minutes
    category="work"
)
```

### ReadingSessionModel
Reading session tracking with progress updates.

```python
from models import ReadingSessionModel

# Log reading session
session_id = ReadingSessionModel.create_session(
    user_id=user_id,
    book_id=book_id,
    pages_read=25,
    duration=45  # minutes
)
```

### AdminUtils
Administrative tools for user and system management.

```python
from models import AdminUtils

# Get system statistics
stats = AdminUtils.get_system_statistics()

# Get all users with pagination
users, total = AdminUtils.get_all_users(page=1, per_page=50, search="john")

# Award points to user
AdminUtils.update_user_points(user_id, 100, "Admin bonus")

# Reset user progress
AdminUtils.reset_user_progress(user_id, reset_type="rewards")
```

### ActivityLogger
Comprehensive activity logging system.

```python
from models import ActivityLogger

# Log user activity
ActivityLogger.log_activity(
    user_id=user_id,
    action="book_completed",
    description="Finished reading The Great Gatsby",
    metadata={"book_id": str(book_id), "pages": 180}
)
```

## Admin Features

### Default Admin User
- **Username**: Set via `ADMIN_USERNAME` environment variable (default: "admin")
- **Password**: Set via `ADMIN_PASSWORD` environment variable (default: "admin123")
- **Email**: Set via `ADMIN_EMAIL` environment variable (default: "admin@nookhook.com")

### Admin Capabilities
- View system statistics and analytics
- Manage all user accounts
- Award/deduct points from users
- Reset user progress (books, tasks, rewards, or all)
- Bulk user operations
- System maintenance and cleanup
- View detailed user activity logs
- Export system data

### Admin Routes
- `/admin/` - Dashboard with system overview
- `/admin/users` - User management with search and filtering
- `/admin/user/<id>` - Detailed user profile and management
- `/admin/analytics` - System analytics and insights
- `/admin/content` - Content management and statistics
- `/admin/rewards` - Reward system management
- `/admin/system_maintenance` - Database cleanup tools

## Database Indexes

The system automatically creates the following indexes for optimal performance:

### Users Collection
- `username` (unique)
- `email` (unique)
- `created_at`

### Books Collection
- `user_id + status`
- `user_id + added_at`
- `isbn` (sparse)

### Reading Sessions
- `user_id + date`
- `user_id + book_id`

### Completed Tasks
- `user_id + completed_at`
- `user_id + category`

### Rewards
- `user_id + date`
- `user_id + source`
- `user_id + category`

### User Badges
- `user_id + badge_id` (unique)
- `user_id + earned_at`

### Activity Log
- `user_id + timestamp`
- `timestamp` (TTL index - expires after 30 days)

## Data Validation

### User Schema
```python
{
    'username': str (required, unique),
    'email': str (required, unique),
    'password_hash': str (required),
    'is_admin': bool (default: False),
    'is_active': bool (default: True),
    'total_points': int (default: 0),
    'level': int (default: 1),
    'profile': {
        'display_name': str,
        'bio': str,
        'avatar_url': str,
        'timezone': str,
        'theme': str
    },
    'preferences': {
        'notifications_enabled': bool,
        'email_notifications': bool,
        'privacy_level': str,
        'reading_goal_target': int
    }
}
```

### Book Schema
```python
{
    'user_id': ObjectId (required),
    'title': str (required),
    'authors': [str],
    'isbn': str,
    'genre': str,
    'status': str ('to_read', 'reading', 'finished'),
    'total_pages': int,
    'current_page': int,
    'rating': int (1-5),
    'quotes': [str],
    'notes': [str],
    'tags': [str]
}
```

## Error Handling

All model operations include comprehensive error handling:

```python
try:
    user_id, error = UserModel.create_user(username, email, password)
    if error:
        print(f"User creation failed: {error}")
    else:
        print(f"User created successfully: {user_id}")
except Exception as e:
    print(f"Unexpected error: {str(e)}")
```

## Performance Considerations

1. **Indexes**: All frequently queried fields are indexed
2. **Pagination**: Large result sets use pagination
3. **TTL Indexes**: Activity logs auto-expire to prevent bloat
4. **Aggregation**: Complex queries use MongoDB aggregation pipeline
5. **Connection Pooling**: PyMongo handles connection pooling automatically

## Backup and Maintenance

### Regular Maintenance Tasks
1. **Activity Log Cleanup**: Automatic via TTL index (30 days)
2. **Orphaned Data Cleanup**: Admin tools available
3. **Duplicate Badge Removal**: Admin cleanup function
4. **User Statistics Updates**: Calculated on-demand

### Backup Recommendations
```bash
# Create backup
mongodump --uri="your-mongodb-uri" --out=backup-$(date +%Y%m%d)

# Restore backup
mongorestore --uri="your-mongodb-uri" backup-20231201/
```

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check MongoDB URI
   - Verify MongoDB server is running
   - Check network connectivity

2. **Admin User Not Created**
   - Verify environment variables are set
   - Check if user already exists
   - Review application logs

3. **Index Creation Failed**
   - Check MongoDB permissions
   - Verify sufficient disk space
   - Review MongoDB logs

4. **Performance Issues**
   - Check if indexes are being used
   - Monitor query performance
   - Consider adding more indexes

### Debug Mode
Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Migration and Updates

When updating the database schema:

1. **Test on Development**: Always test migrations on development data
2. **Backup First**: Create full backup before any schema changes
3. **Gradual Rollout**: Deploy changes gradually
4. **Monitor Performance**: Watch for performance impacts
5. **Rollback Plan**: Have a rollback strategy ready

The model system is designed to be backward-compatible and handles missing fields gracefully.