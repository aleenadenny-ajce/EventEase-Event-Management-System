-- EventEase SQLite Database Schema
-- Enables foreign key constraints
PRAGMA foreign_keys = ON;

-- Users table with role-based access (admin, organizer, participant)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'organizer', 'participant')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories table for event classification
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    description TEXT
);

-- Events table
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    date TEXT NOT NULL,                   -- YYYY-MM-DD
    start_time TEXT NOT NULL,             -- HH:MM (24-hour)
    end_time TEXT NOT NULL,               -- HH:MM (24-hour)
    venue TEXT NOT NULL,
    capacity INTEGER NOT NULL CHECK(capacity > 0),
    registration_deadline TEXT NOT NULL,  -- YYYY-MM-DD
    status TEXT NOT NULL DEFAULT 'Upcoming' CHECK(status IN ('Upcoming', 'Ongoing', 'Completed', 'Cancelled')),
    organizer_id INTEGER NOT NULL,
    poster_path TEXT DEFAULT 'default_event.jpg',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organizer_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Registrations table with unique participant per event constraint
CREATE TABLE IF NOT EXISTS registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_code TEXT NOT NULL UNIQUE,
    user_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'Confirmed' CHECK(status IN ('Confirmed', 'Cancelled')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    UNIQUE(user_id, event_id)
);

-- Indexes for optimized querying and search performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_events_date ON events(date);
CREATE INDEX IF NOT EXISTS idx_events_category ON events(category);
CREATE INDEX IF NOT EXISTS idx_events_status ON events(status);
CREATE INDEX IF NOT EXISTS idx_registrations_user ON registrations(user_id);
CREATE INDEX IF NOT EXISTS idx_registrations_event ON registrations(event_id);
CREATE INDEX IF NOT EXISTS idx_registrations_code ON registrations(registration_code);
