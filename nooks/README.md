# Nook & Hook - Reading Tracker & Productivity Timer

A comprehensive Flask web application that combines reading tracking (Nook) and productivity timing (Hook) with gamification, PWA support, and modern UI/UX. Built with a modular blueprint architecture for scalability and maintainability.

## 🌟 Features

### 🔐 Authentication System
- **User Registration & Login** with secure password hashing
- **Session Management** with persistent login
- **User Profiles** with customizable preferences
- **Settings Management** for personalization
- **Password Change** functionality
- **Admin Role Management** with separate access levels

### 📚 Nook (Reading Tracker)
- **Book Management**: Add books manually or via Google Books API
- **Progress Tracking**: Track current page numbers and reading sessions
- **Status Management**: "To Read," "Reading," and "Finished" categories
- **Content Collection**: Key takeaways and quote bank system
- **AI Integration**: Ready for AI-powered summaries (LLM API service)
- **Reading Analytics**: Streaks, insights, and progress visualization
- **Book Library**: Advanced filtering and sorting options
- **Rating System**: Rate and review completed books
- **Social Features**: Export notes/takeaways, social sharing ready

### ⏱️ Hook (Productivity Timer)
- **Pomodoro Technique**: 25min work, 5min break cycles
- **Custom Timers**: Flexible duration settings (1-120 minutes)
- **Task Management**: Categorization with icons by type
- **Advanced Controls**: Start, pause, reset, and complete functionality
- **Mood Tracking**: Emoji check-ins after sessions
- **Productivity Analytics**: Session history and trends analysis
- **Multiple Themes**: Light, Dark, Retro, Neon, Anime, Forest, Ocean, Space, Zen
- **Audio Features**: Notification sounds and ambient sounds
- **Session Types**: Work sessions and break periods
- **Quick Presets**: Pomodoro, Short Break, Long Break, Deep Work, Quick Task

### 🏆 Comprehensive Reward System
- **Points System**: Earn points for all activities across Nook and Hook
- **Badge System**: 25+ unique badges with different categories
  - Reading badges (First Book, Bookworm series, Quote Collector)
  - Productivity badges (Task Master series, Focus Master)
  - Streak badges (7, 30, 100-day streaks)
  - Milestone badges (Point achievements)
- **Level System**: Dynamic leveling based on total points
- **Achievement Tracking**: Progress towards next achievements
- **Reward History**: Complete history with source tracking
- **Leaderboards**: Compare with other users
- **Point Sources**: Clear attribution (Nook, Hook, System, Admin)

### 📊 Advanced Dashboard & Analytics
- **Unified Dashboard**: Overview of all activities and progress
- **Interactive Charts**: Reading progress and task analytics with Chart.js
- **Streak Tracking**: Reading and productivity streaks
- **Goal Setting**: Personal goals with progress tracking
- **Time Analytics**: Best productivity hours and patterns
- **Category Breakdown**: Detailed analysis by book genres and task categories
- **Export Functionality**: Complete user data export

### 🎨 Comprehensive Theme System
- **8 Main Themes**: Light, Dark, Retro, Neon, Anime, Forest, Ocean, Sunset
- **9 Timer Themes**: Specialized themes for focus sessions
- **Theme Customization**: Advanced preference settings
- **Theme Preview**: Live preview before applying
- **Import/Export**: Share custom theme configurations
- **Responsive Design**: Optimized for all screen sizes
- **Accessibility**: High contrast and readable fonts

### 📱 Progressive Web App (PWA)
- **Offline Support**: Service Worker for offline functionality
- **App Installation**: Install as native app on mobile/desktop
- **Push Notifications**: Timer completion and streak reminders
- **Responsive Design**: Mobile-first approach
- **App Manifest**: Complete PWA configuration
- **Caching Strategy**: Smart caching for performance

### 👨‍💼 Advanced Admin Panel
- **User Management**: View, edit, and manage all users
- **System Analytics**: Comprehensive system statistics
- **Content Moderation**: Monitor books, tasks, and user activity
- **Reward Management**: Award custom points and manage badges
- **System Health**: Monitor database and performance metrics
- **Data Export**: System-wide data export capabilities
- **User Statistics**: Detailed per-user analytics

## Tech Stack

- **Backend**: Flask, Python
- **Database**: MongoDB with PyMongo
- **Frontend**: Bootstrap 5, JavaScript, Jinja2 templates
- **APIs**: Google Books API
- **PWA**: Service Worker, Web App Manifest
- **Charts**: Chart.js
- **Deployment**: Render-ready with Gunicorn

## 🏗️ Modular Architecture

The application is built with a modular blueprint architecture for scalability:

```
nook-hook-app/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── Procfile                       # Render deployment config
├── runtime.txt                    # Python version
├── .env                          # Environment variables
├── blueprints/                   # Modular Flask blueprints
│   ├── auth/                     # Authentication module
│   │   ├── __init__.py
│   │   └── routes.py            # Auth routes & logic
│   ├── nook/                    # Reading tracker module
│   │   ├── __init__.py
│   │   └── routes.py           # Book management routes
│   ├── hook/                   # Productivity timer module
│   │   ├── __init__.py
│   │   └── routes.py          # Timer routes & logic
│   ├── rewards/               # Gamification system
│   │   ├── __init__.py
│   │   ├── routes.py         # Reward routes
│   │   └── services.py       # Reward business logic
│   ├── dashboard/            # Analytics dashboard
│   │   ├── __init__.py
│   │   └── routes.py        # Dashboard routes
│   ├── themes/              # Theme management
│   │   ├── __init__.py
│   │   └── routes.py       # Theme customization
│   ├── admin/              # Admin panel
│   │   ├── __init__.py
│   │   └── routes.py      # Admin management
│   └── api/               # REST API endpoints
│       ├── __init__.py
│       └── routes.py     # API routes
├── templates/            # Jinja2 templates (organized by feature)
│   ├── base.html        # Base template with navigation
│   ├── home.html        # Landing page
│   ├── auth/           # Authentication templates
│   ├── nook/          # Reading tracker templates
│   ├── hook/         # Timer templates
│   ├── rewards/     # Gamification templates
│   ├── dashboard/  # Analytics templates
│   └── themes/    # Theme management templates
├── static/           # Static assets
│   ├── css/
│   │   ├── style.css      # Main styles
│   │   └── themes.css     # Theme-specific styles
│   ├── js/
│   │   ├── app.js         # Main JavaScript
│   │   └── timer.js       # Timer functionality
│   ├── manifest.json      # PWA manifest
│   ├── sw.js             # Service Worker
│   └── images/          # Image assets
└── utils/              # Utility modules
    ├── decorators.py   # Custom decorators
    └── google_books.py # Google Books API integration
```

## Installation & Setup

### Prerequisites
- Python 3.11+
- MongoDB (local or cloud)
- Google Books API key (optional)

### Local Development

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd nook-hook-app
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   Create a `.env` file:
   ```env
   SECRET_KEY=your-secret-key-here
   MONGO_URI=mongodb://localhost:27017/nook_hook_app
   GOOGLE_BOOKS_API_KEY=your-google-books-api-key
   PORT=5000
   
   # Admin User Configuration
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=admin123
   ADMIN_EMAIL=admin@nookhook.com
   ```

3. **Database Setup**:
   The application includes a comprehensive database initialization system:
   
   **Option 1: Automatic (Recommended)**
   ```bash
   python app.py
   ```
   The database initializes automatically when the app starts.
   
   **Option 2: Manual Initialization**
   ```bash
   python init_db.py
   ```
   
   **What gets initialized:**
   - All required MongoDB collections
   - Database indexes for optimal performance
   - Default admin user from environment variables
   - Default themes and system data
   - Robust duplicate checking to prevent conflicts

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the app**:
   Open http://localhost:5000 in your browser
   
   **Default Admin Login:**
   - Username: `admin` (or your `ADMIN_USERNAME`)
   - Password: `admin123` (or your `ADMIN_PASSWORD`)
   - Access admin panel at `/admin/`

### Deployment on Render

1. **Connect your repository** to Render
2. **Set environment variables**:
   - `SECRET_KEY`: Strong secret key
   - `MONGO_URI`: MongoDB connection string
   - `GOOGLE_BOOKS_API_KEY`: (optional) Google Books API key
   - `ADMIN_USERNAME`: Admin username (default: admin)
   - `ADMIN_PASSWORD`: Strong admin password
   - `ADMIN_EMAIL`: Admin email address

3. **Deploy**: Render will automatically use the Procfile and requirements.txt
4. **Database**: The database will initialize automatically on first run with the admin user

### Database Features

- **Comprehensive Models**: Complete database schema with validation
- **Admin Management**: Full admin panel with user management capabilities
- **Robust Initialization**: Checks for existing data to prevent duplicates
- **Activity Logging**: Complete user activity tracking with auto-cleanup
- **Performance Optimized**: Automatic indexing for optimal query performance
- **Bulk Operations**: Admin tools for managing multiple users
- **Data Export**: Complete user and system data export capabilities

For detailed database documentation, see [DATABASE_SETUP.md](DATABASE_SETUP.md)

## Usage

### Getting Started
1. **Register** a new account or login
2. **Choose your focus**:
   - **Nook**: Track your reading journey
   - **Hook**: Boost productivity with timers

### Nook (Reading Tracker)
1. **Add books**: Search Google Books or add manually
2. **Track progress**: Update current page numbers
3. **Collect insights**: Add quotes and key takeaways
4. **Monitor streaks**: Build consistent reading habits

### Hook (Productivity Timer)
1. **Set up timer**: Choose task name, duration, and category
2. **Use presets**: Pomodoro (25min), Short break (5min), Long break (15min)
3. **Stay focused**: Timer runs with progress visualization
4. **Complete sessions**: Rate your mood and earn points

### Dashboard
- View comprehensive statistics
- Track progress over time
- Monitor streaks and achievements
- Analyze reading and productivity patterns

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout

### Nook (Reading)
- `GET /nook/` - Reading dashboard
- `POST /nook/add_book` - Add new book
- `GET /nook/search_books` - Search Google Books
- `POST /nook/update_progress/<book_id>` - Update reading progress

### Hook (Timer)
- `GET /hook/` - Timer dashboard
- `POST /hook/start_timer` - Start new timer
- `POST /hook/pause_timer` - Pause/resume timer
- `POST /hook/complete_timer` - Complete session

### Analytics API
- `GET /api/user/stats` - User statistics
- `GET /api/reading/progress` - Reading progress data
- `GET /api/tasks/analytics` - Task analytics data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, please open an issue on GitHub or contact the development team.

---

**Nook & Hook** - Track your reading journey and boost productivity, all in one beautiful, gamified experience! 📚⏱️
#
# 🔌 API Endpoints

### Authentication (`/auth/`)
- `GET|POST /login` - User login
- `GET|POST /register` - User registration  
- `GET /logout` - User logout
- `GET /profile` - User profile
- `GET|POST /settings` - User preferences
- `POST /change_password` - Password change

### Nook - Reading Tracker (`/nook/`)
- `GET /` - Reading dashboard
- `GET|POST /add_book` - Add new book
- `GET /search_books` - Search Google Books API
- `GET /book/<book_id>` - Book details
- `POST /update_progress/<book_id>` - Update reading progress
- `POST /add_takeaway/<book_id>` - Add key takeaway
- `POST /add_quote/<book_id>` - Add quote
- `POST /rate_book/<book_id>` - Rate book
- `GET /library` - Book library with filters
- `GET /analytics` - Reading analytics

### Hook - Productivity Timer (`/hook/`)
- `GET /` - Timer dashboard
- `GET /timer` - Timer interface
- `POST /start_timer` - Start new timer
- `POST /pause_timer` - Pause/resume timer
- `POST /complete_timer` - Complete session
- `POST /cancel_timer` - Cancel timer
- `GET /get_timer_status` - Get current timer status
- `GET /history` - Task history with filters
- `GET /analytics` - Productivity analytics
- `GET /themes` - Timer themes
- `POST /set_theme` - Set timer theme

### Rewards System (`/rewards/`)
- `GET /` - Rewards dashboard
- `GET /history` - Reward history with filters
- `GET /badges` - Badge collection
- `GET /leaderboard` - User leaderboard
- `GET /achievements` - Achievement progress
- `GET /analytics` - Reward analytics

### Dashboard (`/dashboard/`)
- `GET /` - Main dashboard
- `GET /analytics` - Detailed analytics
- `GET /goals` - Goal management
- `POST /set_goal` - Set new goal

### Themes (`/themes/`)
- `GET /` - Theme selection
- `POST /set_theme` - Apply theme
- `GET /customize` - Theme customization
- `POST /save_customization` - Save custom settings
- `GET /timer_themes` - Timer-specific themes
- `GET /export_theme` - Export theme config
- `POST /import_theme` - Import theme config

### Admin Panel (`/admin/`)
- `GET /` - Admin dashboard
- `GET /users` - User management
- `GET /user/<user_id>` - User details
- `GET /analytics` - System analytics
- `GET /content` - Content management
- `GET /rewards` - Reward management
- `POST /award_points` - Award custom points
- `POST /toggle_admin/<user_id>` - Toggle admin status

### REST API (`/api/`)
- `GET /user/stats` - User statistics
- `GET /reading/progress` - Reading progress data
- `GET /tasks/analytics` - Task analytics
- `GET /rewards/recent` - Recent rewards
- `GET /books/search` - Book search
- `GET /dashboard/summary` - Dashboard summary
- `GET /timer/status` - Timer status
- `GET /achievements/progress` - Achievement progress
- `GET /export/user_data` - Export user data

## 🎮 Gamification System

### Point System
- **Book Management**: 5 points for adding a book
- **Reading Progress**: 1 point per page read (max 20 per session)
- **Book Completion**: 50 points for finishing a book
- **Content Creation**: 2-3 points for quotes and takeaways
- **Task Completion**: 1 point per 5 minutes of focus time
- **Productivity Bonuses**: Based on session rating and priority
- **Streak Bonuses**: Daily and weekly streak rewards
- **Level Up Bonuses**: 10 × level points when leveling up

### Badge Categories
- **Reading Badges**: First Book, Bookworm series (5, 10, 25, 50, 100 books)
- **Productivity Badges**: Task Master series (10, 50, 100, 500, 1000 tasks)
- **Streak Badges**: 7, 30, 100-day streaks for reading and productivity
- **Milestone Badges**: Point achievements (100, 500, 1K, 5K, 10K points)
- **Special Badges**: Quote Collector, Focus Master, etc.

### Level System
- **Formula**: Level = floor(sqrt(points / 100)) + 1
- **Level 1**: 0-99 points
- **Level 2**: 100-399 points  
- **Level 3**: 400-899 points
- **And so on...**

## 🎨 Theme System

### Available Themes
1. **Light**: Clean and bright for daytime use
2. **Dark**: Easy on the eyes for low-light environments
3. **Retro**: Vintage-inspired with warm colors
4. **Neon**: Cyberpunk-style with bright accents
5. **Anime**: Colorful and playful theme
6. **Forest**: Nature-inspired with earth tones
7. **Ocean**: Calm and serene with blue tones
8. **Sunset**: Warm gradient theme

### Timer-Specific Themes
- **Default**: Clean and simple
- **Focus**: Minimal for concentration
- **Dark Focus**: Dark theme for focused work
- **Retro Timer**: Vintage-style timer
- **Neon Timer**: Cyberpunk with glowing effects
- **Nature Timer**: Calming nature-inspired
- **Space Timer**: Cosmic theme
- **Zen Timer**: Peaceful and minimalist

## 📱 PWA Features

### Installation
- **Web App Manifest**: Complete PWA configuration
- **Service Worker**: Offline functionality and caching
- **Install Prompt**: Native app installation on mobile/desktop
- **App Icons**: Multiple sizes for different devices

### Offline Support
- **Cached Resources**: Core app functionality works offline
- **Data Sync**: Automatic sync when back online
- **Offline Indicators**: Clear offline status indication
- **Background Sync**: Queue actions for when online

### Performance
- **Smart Caching**: Efficient resource caching strategy
- **Fast Loading**: Optimized for quick startup
- **Responsive Design**: Works on all screen sizes
- **Touch Optimized**: Mobile-friendly interactions

## 🔧 Technical Features

### Database Schema
- **Users**: Authentication, preferences, points, level
- **Books**: Book details, progress, quotes, takeaways
- **Completed Tasks**: Task history with analytics data
- **Reading Sessions**: Detailed reading activity logs
- **Rewards**: Point history with source attribution
- **User Badges**: Badge achievements with timestamps
- **Active Timers**: Current timer state management
- **User Goals**: Personal goal tracking

### Security
- **Password Hashing**: Werkzeug secure password hashing
- **Session Management**: Flask session handling
- **Input Validation**: Form validation and sanitization
- **Admin Protection**: Role-based access control
- **CSRF Protection**: Built-in Flask security features

### Performance
- **Database Indexing**: Optimized MongoDB queries
- **Caching Strategy**: Smart caching for static assets
- **Lazy Loading**: Efficient data loading
- **Pagination**: Large dataset handling
- **API Optimization**: Efficient data serialization