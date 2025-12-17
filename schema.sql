-- ============================================================================
-- MENTAL HEALTH CHATBOT DATABASE SCHEMA
-- Phase 5: Authentication, Dialogue Management, Analytics
-- ============================================================================

-- Connect to the database first:
-- psql -U postgres -d mental_health_chatbot

-- ============================================================================
-- 1. USERS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    total_conversations INT DEFAULT 0,
    avg_mood_change FLOAT DEFAULT 0,
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- ============================================================================
-- 2. SESSIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    start_time TIMESTAMP DEFAULT NOW(),
    end_time TIMESTAMP,
    pre_mood_score INT,
    post_mood_score INT,
    mood_change INT,
    total_messages INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_token ON sessions(session_token);

-- ============================================================================
-- 3. CONVERSATIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    session_id INT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    user_sentiment VARCHAR(50),
    bot_sentiment VARCHAR(50),
    emotion_category VARCHAR(100),
    mental_state VARCHAR(100),
    crisis_detected BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_conversations_timestamp ON conversations(timestamp);

-- ============================================================================
-- 4. MOOD_TRACKING TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS mood_tracking (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id INT REFERENCES sessions(id) ON DELETE SET NULL,
    mood_score INT NOT NULL CHECK (mood_score >= 1 AND mood_score <= 10),
    emotion_label VARCHAR(50),
    notes TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_mood_tracking_user_id ON mood_tracking(user_id);
CREATE INDEX idx_mood_tracking_timestamp ON mood_tracking(timestamp);

-- ============================================================================
-- 5. FEEDBACK TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id INT REFERENCES sessions(id) ON DELETE SET NULL,
    helpfulness_score INT CHECK (helpfulness_score >= 1 AND helpfulness_score <= 5),
    relevance_score INT CHECK (relevance_score >= 1 AND relevance_score <= 5),
    comments TEXT,
    would_recommend BOOLEAN,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_feedback_user_id ON feedback(user_id);
CREATE INDEX idx_feedback_session_id ON feedback(session_id);

-- ============================================================================
-- 6. ANALYTICS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS analytics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT,
    user_count INT,
    avg_session_duration INT,
    avg_mood_change FLOAT,
    crisis_incidents INT,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_analytics_metric ON analytics(metric_name);

-- ============================================================================
-- INITIAL DATA (Optional Test Data)
-- ============================================================================

-- Sample user for testing
INSERT INTO users (username, email, password_hash, first_name, last_name)
VALUES ('testuser', 'test@example.com', 'hashed_password_here', 'John', 'Doe')
ON CONFLICT (email) DO NOTHING;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================