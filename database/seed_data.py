"""Seed realistic demo data into EventEase database for college demonstrations and testing."""

import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash
import uuid

# Base path
DB_FILE = Path(__file__).resolve().parent / "eventease.db"

DEMO_USERS = [
    {
        "name": "System Administrator",
        "email": "admin@eventease.local",
        "password": "Admin@Password123",
        "role": "admin"
    },
    {
        "name": "Prof. Priya Sharma",
        "email": "organizer@eventease.local",
        "password": "Organizer@Password123",
        "role": "organizer"
    },
    {
        "name": "Tech Club Coordinator",
        "email": "techclub@eventease.local",
        "password": "Tech@Password123",
        "role": "organizer"
    },
    {
        "name": "Rahul Verma",
        "email": "participant@eventease.local",
        "password": "User@Password123",
        "role": "participant"
    },
    {
        "name": "Sneha Patel",
        "email": "sneha@eventease.local",
        "password": "User@Password123",
        "role": "participant"
    },
    {
        "name": "Aman Gupta",
        "email": "aman@eventease.local",
        "password": "User@Password123",
        "role": "participant"
    }
]

DEMO_CATEGORIES = [
    ("Technical", "Coding competitions, hackathons, and technical symposiums"),
    ("Workshop", "Practical hands-on training sessions and bootcamps"),
    ("Seminar", "Expert talks, panel discussions, and career guidance sessions"),
    ("Cultural", "Music, dance, theatre, art, and college festival events"),
    ("Sports", "Inter-departmental and inter-college sports tournaments")
]

DEMO_EVENTS = [
    {
        "title": "National Cloud Computing & DevOps Summit 2026",
        "description": "A premier conference exploring containerization, Kubernetes clusters, serverless computing, and microservices architecture with live industry demos.",
        "category": "Technical",
        "date": "2026-11-15",
        "start_time": "09:30",
        "end_time": "16:30",
        "venue": "Main Auditorium, Block A & Zoom Live Stream",
        "capacity": 100,
        "registration_deadline": "2026-11-14",
        "status": "Upcoming",
        "organizer_email": "organizer@eventease.local",
        "poster_path": "default_tech.jpg"
    },
    {
        "title": "InnovateX 24-Hour Hackathon",
        "description": "Collaborate, ideate, and build cutting-edge solutions for real-world problems in web, cloud, and AI. Cash prizes and internship opportunities for winners!",
        "category": "Technical",
        "date": "2026-11-20",
        "start_time": "10:00",
        "end_time": "10:00",
        "venue": "Computer Science Lab Complex",
        "capacity": 60,
        "registration_deadline": "2026-11-18",
        "status": "Upcoming",
        "organizer_email": "techclub@eventease.local",
        "poster_path": "default_hackathon.jpg"
    },
    {
        "title": "Hands-on Workshop: Docker & Kubernetes Essentials",
        "description": "Learn container packaging, multi-stage builds, Minikube deployments, Services, ConfigMaps, and Pod lifecycle through step-by-step lab exercises.",
        "category": "Workshop",
        "date": "2026-11-28",
        "start_time": "14:00",
        "end_time": "17:30",
        "venue": "Virtual Cloud Lab (Google Meet)",
        "capacity": 45,
        "registration_deadline": "2026-11-27",
        "status": "Upcoming",
        "organizer_email": "organizer@eventease.local",
        "poster_path": "default_workshop.jpg"
    },
    {
        "title": "Inter-College Cultural Fest — Tarang 2026",
        "description": "The annual extravaganza celebrating performing arts, music band wars, choreography showcases, and culinary arts across all departments.",
        "category": "Cultural",
        "date": "2026-12-05",
        "start_time": "11:00",
        "end_time": "20:00",
        "venue": "Open Air Amphitheatre (OAT)",
        "capacity": 250,
        "registration_deadline": "2026-12-03",
        "status": "Upcoming",
        "organizer_email": "organizer@eventease.local",
        "poster_path": "default_cultural.jpg"
    },
    {
        "title": "AI & Cloud Career Guidance Seminar",
        "description": "Industry leaders from top cloud providers discuss career trajectories, certifications (AWS/GCP/Azure), and resume building for BCA graduates.",
        "category": "Seminar",
        "date": "2026-09-10",
        "start_time": "10:00",
        "end_time": "12:30",
        "venue": "Seminar Hall 2",
        "capacity": 80,
        "registration_deadline": "2026-09-08",
        "status": "Completed",
        "organizer_email": "organizer@eventease.local",
        "poster_path": "default_seminar.jpg"
    },
    {
        "title": "Annual Inter-Departmental Football Trophy",
        "description": "Round-robin football tournament among computer science, IT, commerce, and science streams. Postponed due to monsoon field conditions.",
        "category": "Sports",
        "date": "2026-10-05",
        "start_time": "08:00",
        "end_time": "15:00",
        "venue": "University Sports Ground",
        "capacity": 120,
        "registration_deadline": "2026-10-03",
        "status": "Cancelled",
        "organizer_email": "techclub@eventease.local",
        "poster_path": "default_sports.jpg"
    }
]


def seed_database(db_path=None):
    """Populates the database with initial categories, users, events, and sample registrations."""
    target_path = Path(db_path) if db_path else DB_FILE
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(target_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    print(f"[*] Seeding database at {target_path}...")

    # 1. Seed Categories
    for name, desc in DEMO_CATEGORIES:
        cursor.execute(
            "INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)",
            (name, desc)
        )

    # 2. Seed Users
    user_id_map = {}
    for u in DEMO_USERS:
        pwd_hash = generate_password_hash(u["password"], method="pbkdf2:sha256")
        cursor.execute(
            """
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                name=excluded.name,
                password_hash=excluded.password_hash,
                role=excluded.role
            """,
            (u["name"], u["email"], pwd_hash, u["role"])
        )
        cursor.execute("SELECT id FROM users WHERE email = ?", (u["email"],))
        user_id_map[u["email"]] = cursor.fetchone()[0]

    # 3. Seed Events
    event_id_map = {}
    for ev in DEMO_EVENTS:
        org_id = user_id_map.get(ev["organizer_email"])
        cursor.execute(
            """
            INSERT OR IGNORE INTO events 
            (title, description, category, date, start_time, end_time, venue, capacity, registration_deadline, status, organizer_id, poster_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ev["title"], ev["description"], ev["category"], ev["date"],
                ev["start_time"], ev["end_time"], ev["venue"], ev["capacity"],
                ev["registration_deadline"], ev["status"], org_id, ev["poster_path"]
            )
        )
        cursor.execute("SELECT id FROM events WHERE title = ?", (ev["title"],))
        row = cursor.fetchone()
        if row:
            event_id_map[ev["title"]] = row[0]

    # 4. Seed Registrations for demo participants
    rahul_id = user_id_map.get("participant@eventease.local")
    sneha_id = user_id_map.get("sneha@eventease.local")
    summit_id = event_id_map.get("National Cloud Computing & DevOps Summit 2026")
    hackathon_id = event_id_map.get("InnovateX 24-Hour Hackathon")

    if rahul_id and summit_id:
        cursor.execute(
            """
            INSERT OR IGNORE INTO registrations (registration_code, user_id, event_id, status)
            VALUES (?, ?, ?, 'Confirmed')
            """,
            ("EVT-REG-1001", rahul_id, summit_id)
        )

    if sneha_id and summit_id:
        cursor.execute(
            """
            INSERT OR IGNORE INTO registrations (registration_code, user_id, event_id, status)
            VALUES (?, ?, ?, 'Confirmed')
            """,
            ("EVT-REG-1002", sneha_id, summit_id)
        )

    if rahul_id and hackathon_id:
        cursor.execute(
            """
            INSERT OR IGNORE INTO registrations (registration_code, user_id, event_id, status)
            VALUES (?, ?, ?, 'Confirmed')
            """,
            ("EVT-REG-1003", rahul_id, hackathon_id)
        )

    conn.commit()
    conn.close()
    print("[+] Seeding completed successfully.")


if __name__ == "__main__":
    seed_database()
