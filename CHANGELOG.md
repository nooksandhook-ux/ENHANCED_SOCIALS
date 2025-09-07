NOOKS: Social Reading & Productivity Hub
NOOKS is a modular Flask web application designed to promote reading, productivity, and learning through gamification, social engagement, and a tailored reward system for Nigerian readers. It combines reading tracking (Nook), productivity timing (Hook), book clubs (Nooks Club), learning tools (Mini Modules), and a Progressive Web App (PWA) experience with a modern, accessible UI/UX.
Key Features

Authentication & Permissions:

Secure user registration, login, and session management with password hashing (Werkzeug).
User profiles with customizable preferences, including avatar styles.
Admin role management with access to a dedicated panel (/admin).
Password change functionality via /change_password.


Nook (Reading Tracker):

Book Management: Add books via Google Books API, manual entry, or secure device uploads (new feature).
Secure Book Uploads: Users can upload books (e.g., PDFs) from their devices, stored privately and encrypted. Only the uploader and admins (for quote verification) can access them, with downloads disabled to prevent unauthorized sharing.
Progress Tracking: Track page numbers, categorize books ("To Read," "Reading," "Finished"), and log quotes/takeaways.
Custom Book Covers: Upload custom covers for manually added or device-uploaded books.
AI Integration: Ready for AI-powered summaries (LLM API).
Analytics: Reading streaks, progress visualizations (Chart.js), and insights.
Social Sharing: Export notes/takeaways and share progress.
Rating System: Rate and review completed books.


Hook (Productivity Timer):

Pomodoro-style (25min work, 5min break) and custom timers (1–120 minutes).
Task categorization with icons, mood tracking (emoji check-ins), and productivity analytics.
Themes: Light, Dark, Retro, Neon, Anime, Forest, Ocean, Sunset, Zen, plus timer-specific themes (e.g., Focus, Space).
Audio features: Notification and ambient sounds.
Presets: Pomodoro, Short Break, Long Break, Deep Work, Quick Task.


Nooks Club (Social Features):

Create/join book clubs with descriptions, topics, and group reading goals.
WebSocket-powered real-time chatrooms (Flask-SocketIO).
Discussion threads and admin/moderator roles for content management.
Track member progress and contributions.


Mini Modules (Learning Tools):

Flashcards: Create and organize flashcards (e.g., quote + meaning).
Daily Quizzes: Book-based or community-driven challenges with leaderboards and analytics.
Quiz Review: View answers and correct solutions.
Modular design for adding new mini-apps.


Rewards & Gamification:

Points System:

5 points for adding a book, 1 point per page read (max 20/session).
50 points for book completion, 2–3 points for quotes/takeaways.
1 point per 5 minutes of focus time, plus streak and level-up bonuses.


Badge System: 25+ badges (e.g., Bookworm, Task Master, 7/30/100-day streaks, Quote Collector).
Level System: Level = floor(sqrt(points / 100)) + 1.
Leaderboards: Compare reading, productivity, and quiz performance.
Quote-Based Rewards (Nigerian Readers): Earn ₦10 per verified quote (10–1000 characters, verbatim, with page number). Tracks pending, verified, or rejected quotes and earnings.


Dashboard & Analytics:

Unified overview of reading, productivity, and quiz stats.
Interactive Chart.js charts for streaks, goals, and time analytics.
Goal setting and data export functionality.


Theme System:

8 main themes: Light, Dark, Retro, Neon, Anime, Forest, Ocean, Sunset.
9 timer themes: Default, Focus, Dark Focus, Retro Timer, etc.
Customizable with live previews, import/export, and accessibility features (high-contrast fonts, responsive design).


PWA Features:

Offline support via Service Worker, with cached resources and background sync.
Native app installation on mobile/desktop with push notifications for timers/streaks.
Optimized for performance and touch interactions.


Avatar Style Updates:

New styles: Lorelei (🎨, 500 points), Bottts (🤖, 500 points), Adventurer (⚔, 750 points).
Available via shop; small mystery box drops Lorelei/Botts, large box drops all three.
Recorded as avatar_style with zero cost for ownership tracking.
Prevents duplicate purchases via non-consumables check.
UI Changes:

AvatarForm uses single-selection SelectField for hair/background color, stored as lists for schema consistency.
/settings handles avatar customization, preloads preferences (defaults to avataaars).
settings.html includes avatar form with style, hair, color, flip options, and live SVG preview via /themes/api/avatar_preview/<style>.
profile.html displays DiceBear-generated avatar using user preferences and username seed.
JavaScript updates preview on style change (hair/color/flip preview pending API enhancement).





Quote-Based Reward System (Nigerian Readers)

Purpose: Incentivizes reading by rewarding Nigerian users ₦10 per verified book quote, supporting small expenses (e.g., airtime, data, snacks).
User Workflow:

Add books via Google Books API, manual entry, or secure device upload.
Submit verbatim quotes (10–1000 characters) with page numbers.
Track status (pending, verified, rejected) and earnings in dashboard.


Admin Workflow:

Review quotes in verification queue, cross-reference with books.
Approve/reject with reasons, using bulk operations.
Monitor stats and transaction history.


Security & Anti-Fraud:

User authentication and book ownership verification.
Duplicate quote detection, page number validation, manual verification.
Rate limiting, IP-based fraud detection, and audit trail.


Database:

Quotes Collection: Stores quote text, page number, user/book IDs, status, reward amount (default: ₦10).
Transactions Collection: Logs reward type, amount, and status.




Technical Details

Backend: Flask, Flask-PyMongo, Flask-Login, Flask-SocketIO, Gunicorn (production).
Database: MongoDB with collections for users, books, quotes, tasks, clubs, flashcards, quizzes, rewards, etc.
Frontend: Jinja2, Bootstrap 5, custom CSS/JS, Socket.IO, Chart.js.
Security:

Password hashing, CSRF protection, role-based access.
Encrypted book uploads, private access (uploader/admins only), no download/share links.


Performance: Database indexing, lazy loading, smart caching, pagination.
API Endpoints:

Auth: /auth/register, /auth/login, /change_password.
Nook: /nook/add_book, /nook/update_progress/<book_id>, /quotes/submit.
Hook: /hook/start_timer, /hook/analytics.
Nooks Club: Club creation, chat, and discussion endpoints.
Rewards: /rewards/, /quotes/admin/pending.
Analytics: /api/user/stats, /api/reading/progress.



Setup Instructions

Clone Repository:
bashgit clone <repo-url>
cd NOOKS

Install Dependencies:
bashpip install -r requirements.txt

Set Environment Variables (.env):
bashSECRET_KEY=your_secret_key
MONGO_URI=your_mongodb_uri
GOOGLE_BOOKS_API_KEY=your_api_key # Optional
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_EMAIL=admin@example.com

Initialize Database:
bashpython init_db.py
python init_quotes_db.py

Run App:

Development: python app.py
Real-time chat: python socketio_server.py
Production: gunicorn -k eventlet -w 1 socketio_server:socketio_app


Access:

Open http://localhost:5000.
Admin panel: /admin (default: admin/admin123).



Deployment (Render):

Connect repository to Render.
Set .env variables (as above).
Deploy using Procfile and requirements.txt.
Database initializes automatically with admin user.


Secure Book Upload Feature

Functionality: Users can upload books (e.g., PDFs) from their devices via a secure, private interface.
Security:

Files are encrypted during upload and storage.
Access restricted to the uploader and admins (for quote verification).
Downloads disabled; books viewable only in secure in-app reader.
CSRF-protected activity logging to track usage.


Implementation:

Integrated into /nook/add_book endpoint with file upload handling.
Stored in MongoDB (e.g., GridFS for large files) with metadata (title, author, uploader ID).
UI includes file picker and progress indicator.


User Experience:

Upload option alongside Google Books API and manual entry.
Clear status indicators for uploaded books (e.g., “Private”, “Encrypted”).
Quotes from uploaded books follow the same verification process.




Impact and Goals

For Nigerian Readers:

The quote-based reward system (₦10 per verified quote) incentivizes reading while providing financial support for small expenses.
Encourages active engagement through quote selection, improving comprehension.
Builds a community of readers via Nooks Club and shared quotes.


General Users:

Combines reading, productivity, and learning in a gamified, social platform.
PWA support ensures accessibility, even offline.
Customizable themes and avatars enhance engagement.


Cultural Impact:

Preserves knowledge through quote sharing.
Promotes literacy and productivity in a community-driven ecosystem.




Future Enhancements

Quote Verification:

OCR or ML for automated quote checking.
Community verification by trusted users.
Publisher partnerships for direct book access.


Funding Sustainability:

Bookstore commissions, educational/corporate sponsorships.
Premium features (e.g., advanced analytics, exclusive themes).


Mobile App: Wrap with React Native/Flutter for native experience.
Accessibility: Add ARIA roles, keyboard navigation, enhanced contrast.
API Expansion: Open APIs for third-party mini-apps or integrations.
Notifications: Real-time/email alerts for club activity, quiz results, or quote approvals.


Conclusion
NOOKS is a versatile, user-centric Flask application that seamlessly integrates reading tracking, productivity tools, social features, and learning modules with a focus on engaging Nigerian readers through a quote-based reward system. The new secure book upload feature enhances flexibility, allowing users to privately add personal books while maintaining anti-piracy measures. With its modular architecture, PWA support, and recent avatar style updates, NOOKS delivers a polished, gamified experience that promotes literacy and productivity. Future enhancements like automated quote verification and sustainable funding could further amplify its impact, particularly for Nigerian users.
