"""EventEase — Event Management System
Flask backend implementing authentication, role-based access control,
event lifecycle management, registration with concurrency protection,
admin & organizer analytics, and a health endpoint for container readiness.
"""

import os
import csv
import io
import uuid
import sqlite3
from datetime import datetime, date, timezone
from functools import wraps
from pathlib import Path

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, g, jsonify, make_response, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import Config, TestConfig


def create_app(config_class=Config):
    """Application factory for EventEase."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure database and upload folders exist
    db_file = Path(app.config["DATABASE"])
    db_file.parent.mkdir(parents=True, exist_ok=True)
    app.config["UPLOAD_FOLDER"].mkdir(parents=True, exist_ok=True)

    # Auto-initialize database schema if database file does not exist or is empty
    if not db_file.exists() or db_file.stat().st_size == 0:
        try:
            from database.init_db import init_db
            init_db(db_path=db_file, seed=True)
        except Exception as e:
            app.logger.warning(f"Database auto-init skipped or failed: {e}")


    # ---------------------------------------------------------
    # Database Connection Management
    # ---------------------------------------------------------
    def get_db():
        """Returns SQLite database connection stored in application context."""
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
            g.db.execute("PRAGMA busy_timeout = 5000")
        return g.db

    @app.teardown_appcontext
    def close_db(error=None):
        """Closes SQLite database connection at the end of the request."""
        db = g.pop("db", None)
        if db is not None:
            db.close()

    # ---------------------------------------------------------
    # Context Processor (inject current user into all templates)
    # ---------------------------------------------------------
    @app.context_processor
    def inject_user_and_meta():
        user = None
        if "user_id" in session:
            user = {
                "id": session.get("user_id"),
                "name": session.get("user_name"),
                "email": session.get("user_email"),
                "role": session.get("user_role"),
                "is_authenticated": True
            }
        else:
            user = {
                "is_authenticated": False,
                "role": None
            }
        return {
            "current_user": user,
            "app_name": app.config.get("APP_NAME", "EventEase"),
            "app_version": app.config.get("APP_VERSION", "1.0.0"),
            "today_date": date.today().isoformat()
        }

    # ---------------------------------------------------------
    # Authorization Decorators
    # ---------------------------------------------------------
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("login", next=request.path))
            return f(*args, **kwargs)
        return decorated_function

    def roles_required(*allowed_roles):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if "user_id" not in session:
                    flash("Please log in to continue.", "warning")
                    return redirect(url_for("login", next=request.path))
                user_role = session.get("user_role")
                if user_role not in allowed_roles:
                    flash("Access denied: You lack permissions for this resource.", "danger")
                    abort(403)
                return f(*args, **kwargs)
            return decorated_function
        return decorator

    # ---------------------------------------------------------
    # Helper Utilities
    # ---------------------------------------------------------
    def get_event_with_stats(event_id):
        """Fetch event details along with total confirmed registrations and remaining seats."""
        db = get_db()
        cursor = db.cursor()
        query = """
            SELECT e.*, 
                   u.name as organizer_name,
                   u.email as organizer_email,
                   (SELECT COUNT(*) FROM registrations r WHERE r.event_id = e.id AND r.status = 'Confirmed') as confirmed_count
            FROM events e
            LEFT JOIN users u ON e.organizer_id = u.id
            WHERE e.id = ?
        """
        cursor.execute(query, (event_id,))
        event = cursor.fetchone()
        if not event:
            return None
        event_dict = dict(event)
        event_dict["remaining_seats"] = max(0, event_dict["capacity"] - event_dict["confirmed_count"])
        event_dict["is_full"] = event_dict["remaining_seats"] <= 0
        event_dict["is_past_deadline"] = event_dict["registration_deadline"] < date.today().isoformat()
        return event_dict

    # ---------------------------------------------------------
    # Health Endpoint (Kubernetes readiness & liveness)
    # ---------------------------------------------------------
    @app.route("/health", methods=["GET"])
    def health_check():
        """Health endpoint reporting application status and database connectivity."""
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            db_status = "connected"
            http_code = 200
            service_status = "UP"
        except Exception as exc:
            db_status = f"unhealthy: {str(exc)}"
            http_code = 503
            service_status = "DOWN"

        return jsonify({
            "service": app.config.get("APP_NAME", "EventEase"),
            "status": service_status,
            "version": app.config.get("APP_VERSION", "1.0.0"),
            "database": db_status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), http_code

    # ---------------------------------------------------------
    # Public & Discovery Routes
    # ---------------------------------------------------------
    @app.route("/")
    def index():
        """Home page displaying featured upcoming events and high-level platform stats."""
        db = get_db()
        cursor = db.cursor()

        # Stats for hero counters
        cursor.execute("SELECT COUNT(*) FROM events WHERE status != 'Cancelled'")
        total_events = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM registrations WHERE status = 'Confirmed'")
        total_registrations = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'participant'")
        total_participants = cursor.fetchone()[0]

        # Upcoming featured events
        cursor.execute("""
            SELECT e.*, 
                   (SELECT COUNT(*) FROM registrations r WHERE r.event_id = e.id AND r.status = 'Confirmed') as confirmed_count
            FROM events e
            WHERE e.status = 'Upcoming'
            ORDER BY e.date ASC
            LIMIT 6
        """)
        featured_events = []
        for row in cursor.fetchall():
            item = dict(row)
            item["remaining_seats"] = max(0, item["capacity"] - item["confirmed_count"])
            featured_events.append(item)

        cursor.execute("SELECT name FROM categories ORDER BY name ASC")
        categories = [row[0] for row in cursor.fetchall()]

        return render_template(
            "index.html",
            featured_events=featured_events,
            categories=categories,
            stats={
                "events": total_events,
                "registrations": total_registrations,
                "participants": total_participants
            }
        )

    @app.route("/about")
    def about():
        """About page explaining the project, architecture, and technology stack."""
        return render_template("about.html")

    @app.route("/events")
    def events():
        """Event discovery page with keyword search, category filter, date filter, and venue filter."""
        db = get_db()
        cursor = db.cursor()

        query_str = request.args.get("q", "").strip()
        cat_filter = request.args.get("category", "").strip()
        date_filter = request.args.get("date", "").strip()
        status_filter = request.args.get("status", "").strip()

        sql = """
            SELECT e.*, 
                   u.name as organizer_name,
                   (SELECT COUNT(*) FROM registrations r WHERE r.event_id = e.id AND r.status = 'Confirmed') as confirmed_count
            FROM events e
            LEFT JOIN users u ON e.organizer_id = u.id
            WHERE 1=1
        """
        params = []

        if query_str:
            sql += " AND (e.title LIKE ? OR e.description LIKE ? OR e.venue LIKE ?)"
            term = f"%{query_str}%"
            params.extend([term, term, term])

        if cat_filter:
            sql += " AND e.category = ?"
            params.append(cat_filter)

        if date_filter:
            sql += " AND e.date = ?"
            params.append(date_filter)

        if status_filter:
            sql += " AND e.status = ?"
            params.append(status_filter)

        sql += " ORDER BY e.date ASC"

        cursor.execute(sql, params)
        all_events = []
        for row in cursor.fetchall():
            item = dict(row)
            item["remaining_seats"] = max(0, item["capacity"] - item["confirmed_count"])
            all_events.append(item)

        cursor.execute("SELECT name FROM categories ORDER BY name ASC")
        categories = [row[0] for row in cursor.fetchall()]

        return render_template(
            "events.html",
            events=all_events,
            categories=categories,
            selected_category=cat_filter,
            selected_query=query_str,
            selected_date=date_filter,
            selected_status=status_filter
        )

    @app.route("/events/<int:event_id>")
    def event_detail(event_id):
        """Detailed view for a specific event with capacity indicator and registration form."""
        event = get_event_with_stats(event_id)
        if not event:
            abort(404)

        # Check if current user is already registered
        is_user_registered = False
        user_reg_info = None
        if "user_id" in session:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "SELECT * FROM registrations WHERE event_id = ? AND user_id = ? AND status = 'Confirmed'",
                (event_id, session["user_id"])
            )
            user_reg_info = cursor.fetchone()
            if user_reg_info:
                is_user_registered = True

        return render_template(
            "event_detail.html",
            event=event,
            is_user_registered=is_user_registered,
            user_reg=dict(user_reg_info) if user_reg_info else None
        )

    # ---------------------------------------------------------
    # Authentication Routes
    # ---------------------------------------------------------
    @app.route("/auth/register", methods=["GET", "POST"])
    def register():
        """Participant account registration."""
        if "user_id" in session:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")

            # Validation
            if not name or not email or not password:
                flash("All fields are required.", "danger")
                return render_template("register.html", name=name, email=email)

            if len(password) < 6:
                flash("Password must be at least 6 characters long.", "danger")
                return render_template("register.html", name=name, email=email)

            if password != confirm_password:
                flash("Passwords do not match.", "danger")
                return render_template("register.html", name=name, email=email)

            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                flash("An account with this email address already exists.", "danger")
                return render_template("register.html", name=name, email=email)

            pwd_hash = generate_password_hash(password, method="pbkdf2:sha256")
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, 'participant')",
                (name, email, pwd_hash)
            )
            db.commit()

            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("login"))

        return render_template("register.html")

    @app.route("/auth/login", methods=["GET", "POST"])
    def login():
        """User authentication route supporting Admin, Organizer, and Participant roles."""
        if "user_id" in session:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            next_url = request.args.get("next") or request.form.get("next")

            if not email or not password:
                flash("Please enter both email and password.", "danger")
                return render_template("login.html", email=email)

            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user["password_hash"], password):
                session.clear()
                session["user_id"] = user["id"]
                session["user_name"] = user["name"]
                session["user_email"] = user["email"]
                session["user_role"] = user["role"]
                session.permanent = True

                flash(f"Welcome back, {user['name']}!", "success")
                if next_url and next_url.startswith("/"):
                    return redirect(next_url)
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid email or password. Please verify and try again.", "danger")

        return render_template("login.html")

    @app.route("/auth/logout")
    def logout():
        """Log out current user and clear session state."""
        session.clear()
        flash("You have been successfully logged out.", "info")
        return redirect(url_for("login"))

    # ---------------------------------------------------------
    # Dashboard Router
    # ---------------------------------------------------------
    @app.route("/dashboard")
    @login_required
    def dashboard():
        """Central dashboard router redirecting to role-specific dashboard."""
        role = session.get("user_role")
        if role == "admin":
            return redirect(url_for("admin_dashboard"))
        elif role == "organizer":
            return redirect(url_for("organizer_dashboard"))
        else:
            return redirect(url_for("participant_dashboard"))

    # ---------------------------------------------------------
    # Admin Dashboard & Management
    # ---------------------------------------------------------
    @app.route("/admin/dashboard")
    @roles_required("admin")
    def admin_dashboard():
        """Admin dashboard with high-level analytics, Chart.js metrics, and quick actions."""
        db = get_db()
        cursor = db.cursor()

        # Metrics
        cursor.execute("SELECT COUNT(*) FROM events")
        total_events = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM events WHERE status = 'Upcoming'")
        upcoming_events = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM events WHERE status = 'Completed'")
        completed_events = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM registrations WHERE status = 'Confirmed'")
        total_registrations = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'participant'")
        total_participants = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'organizer'")
        total_organizers = cursor.fetchone()[0]

        # Status distribution for charts
        cursor.execute("SELECT status, COUNT(*) FROM events GROUP BY status")
        status_distribution = dict(cursor.fetchall())

        # Category distribution for charts
        cursor.execute("SELECT category, COUNT(*) FROM events GROUP BY category")
        category_distribution = dict(cursor.fetchall())

        # Recent registrations
        cursor.execute("""
            SELECT r.*, u.name as user_name, u.email as user_email, e.title as event_title
            FROM registrations r
            JOIN users u ON r.user_id = u.id
            JOIN events e ON r.event_id = e.id
            ORDER BY r.registration_date DESC
            LIMIT 10
        """)
        recent_registrations = [dict(row) for row in cursor.fetchall()]

        # Recent events
        cursor.execute("""
            SELECT e.*, u.name as organizer_name,
                   (SELECT COUNT(*) FROM registrations r WHERE r.event_id = e.id AND r.status = 'Confirmed') as confirmed_count
            FROM events e
            LEFT JOIN users u ON e.organizer_id = u.id
            ORDER BY e.created_at DESC
            LIMIT 5
        """)
        recent_events = [dict(row) for row in cursor.fetchall()]

        return render_template(
            "admin_dashboard.html",
            metrics={
                "total_events": total_events,
                "upcoming_events": upcoming_events,
                "completed_events": completed_events,
                "total_registrations": total_registrations,
                "total_participants": total_participants,
                "total_organizers": total_organizers
            },
            status_dist=status_distribution,
            category_dist=category_distribution,
            recent_registrations=recent_registrations,
            recent_events=recent_events
        )

    @app.route("/admin/users", methods=["GET", "POST"])
    @roles_required("admin")
    def manage_users():
        """User management: view, search, role updates, and user deletion."""
        db = get_db()
        cursor = db.cursor()

        if request.method == "POST":
            action = request.form.get("action")
            target_user_id = request.form.get("user_id")

            if action == "update_role":
                new_role = request.form.get("role")
                if new_role in ("admin", "organizer", "participant"):
                    cursor.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, target_user_id))
                    db.commit()
                    flash("User role updated successfully.", "success")
            elif action == "delete_user":
                if int(target_user_id) == session.get("user_id"):
                    flash("You cannot delete your own administrative account.", "danger")
                else:
                    cursor.execute("DELETE FROM users WHERE id = ?", (target_user_id,))
                    db.commit()
                    flash("User and associated records removed successfully.", "success")

            return redirect(url_for("manage_users"))

        # Fetch users
        q = request.args.get("q", "").strip()
        role_filter = request.args.get("role", "").strip()

        sql = "SELECT id, name, email, role, created_at FROM users WHERE 1=1"
        params = []
        if q:
            sql += " AND (name LIKE ? OR email LIKE ?)"
            params.extend([f"%{q}%", f"%{q}%"])
        if role_filter:
            sql += " AND role = ?"
            params.append(role_filter)
        sql += " ORDER BY id DESC"

        cursor.execute(sql, params)
        users = [dict(row) for row in cursor.fetchall()]

        return render_template("manage_users.html", users=users, selected_role=role_filter, q=q)

    # ---------------------------------------------------------
    # Organizer Dashboard & Event Actions
    # ---------------------------------------------------------
    @app.route("/organizer/dashboard")
    @roles_required("organizer", "admin")
    def organizer_dashboard():
        """Dashboard for event organizers to monitor assigned events, seat availability, and rosters."""
        db = get_db()
        cursor = db.cursor()
        user_id = session.get("user_id")
        is_admin = session.get("user_role") == "admin"

        if is_admin:
            query = """
                SELECT e.*, u.name as organizer_name,
                       (SELECT COUNT(*) FROM registrations r WHERE r.event_id = e.id AND r.status = 'Confirmed') as confirmed_count
                FROM events e
                LEFT JOIN users u ON e.organizer_id = u.id
                ORDER BY e.date ASC
            """
            cursor.execute(query)
        else:
            query = """
                SELECT e.*, u.name as organizer_name,
                       (SELECT COUNT(*) FROM registrations r WHERE r.event_id = e.id AND r.status = 'Confirmed') as confirmed_count
                FROM events e
                LEFT JOIN users u ON e.organizer_id = u.id
                WHERE e.organizer_id = ?
                ORDER BY e.date ASC
            """
            cursor.execute(query, (user_id,))

        events_list = []
        for row in cursor.fetchall():
            item = dict(row)
            item["remaining_seats"] = max(0, item["capacity"] - item["confirmed_count"])
            events_list.append(item)

        return render_template("organizer_dashboard.html", events=events_list, is_admin=is_admin)

    # ---------------------------------------------------------
    # Participant Dashboard
    # ---------------------------------------------------------
    @app.route("/participant/dashboard")
    @login_required
    def participant_dashboard():
        """Participant view showing their registered events, statuses, and registration badges."""
        db = get_db()
        cursor = db.cursor()
        user_id = session.get("user_id")

        cursor.execute("""
            SELECT r.id as registration_id, r.registration_code, r.registration_date, r.status as reg_status,
                   e.id as event_id, e.title, e.date, e.start_time, e.end_time, e.venue, e.category, e.status as event_status
            FROM registrations r
            JOIN events e ON r.event_id = e.id
            WHERE r.user_id = ?
            ORDER BY e.date ASC
        """, (user_id,))

        registrations = [dict(row) for row in cursor.fetchall()]
        return render_template("participant_dashboard.html", registrations=registrations)

    # ---------------------------------------------------------
    # Event CRUD Operations
    # ---------------------------------------------------------
    @app.route("/events/manage")
    @roles_required("organizer", "admin")
    def manage_events():
        """Table view for comprehensive event management."""
        db = get_db()
        cursor = db.cursor()
        user_id = session.get("user_id")
        is_admin = session.get("user_role") == "admin"

        q = request.args.get("q", "").strip()
        cat_filter = request.args.get("category", "").strip()
        status_filter = request.args.get("status", "").strip()

        sql = """
            SELECT e.*, u.name as organizer_name,
                   (SELECT COUNT(*) FROM registrations r WHERE r.event_id = e.id AND r.status = 'Confirmed') as confirmed_count
            FROM events e
            LEFT JOIN users u ON e.organizer_id = u.id
            WHERE 1=1
        """
        params = []
        if not is_admin:
            sql += " AND e.organizer_id = ?"
            params.append(user_id)

        if q:
            sql += " AND (e.title LIKE ? OR e.description LIKE ? OR e.venue LIKE ?)"
            params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])

        if cat_filter:
            sql += " AND e.category = ?"
            params.append(cat_filter)

        if status_filter:
            sql += " AND e.status = ?"
            params.append(status_filter)

        sql += " ORDER BY e.date ASC"
        cursor.execute(sql, params)

        events_list = []
        for row in cursor.fetchall():
            item = dict(row)
            item["remaining_seats"] = max(0, item["capacity"] - item["confirmed_count"])
            events_list.append(item)

        cursor.execute("SELECT name FROM categories ORDER BY name ASC")
        categories = [r[0] for r in cursor.fetchall()]

        return render_template(
            "manage_events.html",
            events=events_list,
            categories=categories,
            is_admin=is_admin,
            q=q,
            selected_category=cat_filter,
            selected_status=status_filter
        )


    @app.route("/events/create", methods=["GET", "POST"])
    @roles_required("organizer", "admin")
    def create_event():
        """Create a new event."""
        db = get_db()
        cursor = db.cursor()

        if request.method == "POST":
            title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()
            category = request.form.get("category", "").strip()
            event_date = request.form.get("date", "").strip()
            start_time = request.form.get("start_time", "").strip()
            end_time = request.form.get("end_time", "").strip()
            venue = request.form.get("venue", "").strip()
            capacity_raw = request.form.get("capacity", "").strip()
            deadline = request.form.get("registration_deadline", "").strip()
            status = request.form.get("status", "Upcoming").strip()
            poster_path = "default_event.jpg"

            # Form validation
            if not (title and description and category and event_date and start_time and end_time and venue and capacity_raw and deadline):
                flash("Please fill in all required event details.", "danger")
                cursor.execute("SELECT name FROM categories ORDER BY name ASC")
                cats = [r[0] for r in cursor.fetchall()]
                return render_template("create_event.html", categories=cats, form=request.form)

            try:
                capacity = int(capacity_raw)
                if capacity <= 0:
                    raise ValueError()
            except ValueError:
                flash("Capacity must be a positive integer greater than zero.", "danger")
                cursor.execute("SELECT name FROM categories ORDER BY name ASC")
                cats = [r[0] for r in cursor.fetchall()]
                return render_template("create_event.html", categories=cats, form=request.form)

            # Poster file upload handling
            if "poster" in request.files:
                file = request.files["poster"]
                if file and file.filename != "":
                    ext = file.filename.rsplit(".", 1)[-1].lower()
                    if ext in app.config["ALLOWED_EXTENSIONS"]:
                        filename = f"{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}"
                        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                        poster_path = filename

            organizer_id = session.get("user_id")

            cursor.execute("""
                INSERT INTO events (
                    title, description, category, date, start_time, end_time,
                    venue, capacity, registration_deadline, status, organizer_id, poster_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                title, description, category, event_date, start_time, end_time,
                venue, capacity, deadline, status, organizer_id, poster_path
            ))
            db.commit()

            flash(f"Event '{title}' created successfully!", "success")
            return redirect(url_for("organizer_dashboard"))

        cursor.execute("SELECT name FROM categories ORDER BY name ASC")
        categories = [r[0] for r in cursor.fetchall()]
        return render_template("create_event.html", categories=categories, form={})

    @app.route("/events/<int:event_id>/edit", methods=["GET", "POST"])
    @roles_required("organizer", "admin")
    def edit_event(event_id):
        """Edit an existing event."""
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        event = cursor.fetchone()
        if not event:
            abort(404)

        # Check authorization: user must be admin or the original organizer
        if session.get("user_role") != "admin" and event["organizer_id"] != session.get("user_id"):
            flash("You do not have permission to modify this event.", "danger")
            abort(403)

        if request.method == "POST":
            title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()
            category = request.form.get("category", "").strip()
            event_date = request.form.get("date", "").strip()
            start_time = request.form.get("start_time", "").strip()
            end_time = request.form.get("end_time", "").strip()
            venue = request.form.get("venue", "").strip()
            capacity_raw = request.form.get("capacity", "").strip()
            deadline = request.form.get("registration_deadline", "").strip()
            status = request.form.get("status", "Upcoming").strip()
            poster_path = event["poster_path"]

            try:
                capacity = int(capacity_raw)
                if capacity <= 0:
                    raise ValueError()
            except ValueError:
                flash("Capacity must be a valid positive number.", "danger")
                cursor.execute("SELECT name FROM categories ORDER BY name ASC")
                cats = [r[0] for r in cursor.fetchall()]
                return render_template("edit_event.html", event=event, categories=cats)

            # Optional new poster upload
            if "poster" in request.files:
                file = request.files["poster"]
                if file and file.filename != "":
                    ext = file.filename.rsplit(".", 1)[-1].lower()
                    if ext in app.config["ALLOWED_EXTENSIONS"]:
                        filename = f"{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}"
                        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                        poster_path = filename

            cursor.execute("""
                UPDATE events SET
                    title = ?, description = ?, category = ?, date = ?,
                    start_time = ?, end_time = ?, venue = ?, capacity = ?,
                    registration_deadline = ?, status = ?, poster_path = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                title, description, category, event_date, start_time, end_time,
                venue, capacity, deadline, status, poster_path, event_id
            ))
            db.commit()

            flash("Event updated successfully.", "success")
            return redirect(url_for("organizer_dashboard"))

        cursor.execute("SELECT name FROM categories ORDER BY name ASC")
        categories = [r[0] for r in cursor.fetchall()]
        return render_template("edit_event.html", event=dict(event), categories=categories)

    @app.route("/events/<int:event_id>/delete", methods=["POST"])
    @roles_required("organizer", "admin")
    def delete_event(event_id):
        """Delete an event and cascaded registrations."""
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT organizer_id, title FROM events WHERE id = ?", (event_id,))
        event = cursor.fetchone()
        if not event:
            abort(404)

        if session.get("user_role") != "admin" and event["organizer_id"] != session.get("user_id"):
            flash("You are not permitted to delete this event.", "danger")
            abort(403)

        cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
        db.commit()

        flash(f"Event '{event['title']}' deleted successfully.", "success")
        return redirect(url_for("organizer_dashboard"))

    # ---------------------------------------------------------
    # Event Registration Engine with Concurrency Safeguard
    # ---------------------------------------------------------
    @app.route("/events/<int:event_id>/register", methods=["POST"])
    @login_required
    def register_event(event_id):
        """Register current participant for an event, validating capacity, deadline, and duplicates."""
        user_id = session.get("user_id")
        user_role = session.get("user_role")

        db = get_db()
        cursor = db.cursor()

        # Database Transaction begins
        try:
            # 1. Fetch Event with lock / within transaction
            cursor.execute("BEGIN IMMEDIATE")
            cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
            event = cursor.fetchone()

            if not event:
                cursor.execute("ROLLBACK")
                flash("Event not found.", "danger")
                return redirect(url_for("events"))

            # 2. Check Event Status
            if event["status"] != "Upcoming":
                cursor.execute("ROLLBACK")
                flash(f"Registrations are closed because the event is '{event['status']}'.", "warning")
                return redirect(url_for("event_detail", event_id=event_id))

            # 3. Check Registration Deadline
            today_str = date.today().isoformat()
            if event["registration_deadline"] < today_str:
                cursor.execute("ROLLBACK")
                flash("The registration deadline for this event has passed.", "danger")
                return redirect(url_for("event_detail", event_id=event_id))

            # 4. Check for Existing Registration
            cursor.execute(
                "SELECT id, status FROM registrations WHERE user_id = ? AND event_id = ?",
                (user_id, event_id)
            )
            existing_reg = cursor.fetchone()
            if existing_reg:
                if existing_reg["status"] == "Confirmed":
                    cursor.execute("ROLLBACK")
                    flash("You are already registered for this event.", "info")
                    return redirect(url_for("event_detail", event_id=event_id))
                elif existing_reg["status"] == "Cancelled":
                    # Reactivate cancelled registration if seats are available
                    pass

            # 5. Check Seat Capacity
            cursor.execute(
                "SELECT COUNT(*) FROM registrations WHERE event_id = ? AND status = 'Confirmed'",
                (event_id,)
            )
            current_count = cursor.fetchone()[0]
            if current_count >= event["capacity"]:
                cursor.execute("ROLLBACK")
                flash("Sorry, this event has reached full capacity. No more seats available.", "danger")
                return redirect(url_for("event_detail", event_id=event_id))

            # 6. Generate Unique Registration Code
            reg_code = f"EVT-{uuid.uuid4().hex[:6].upper()}"

            if existing_reg and existing_reg["status"] == "Cancelled":
                cursor.execute(
                    "UPDATE registrations SET status = 'Confirmed', registration_code = ?, registration_date = CURRENT_TIMESTAMP WHERE id = ?",
                    (reg_code, existing_reg["id"])
                )
            else:
                cursor.execute(
                    "INSERT INTO registrations (registration_code, user_id, event_id, status) VALUES (?, ?, ?, 'Confirmed')",
                    (reg_code, user_id, event_id)
                )

            cursor.execute("COMMIT")

            flash("Congratulations! You have successfully registered for the event.", "success")
            return redirect(url_for("registration_success", reg_code=reg_code))

        except sqlite3.IntegrityError:
            cursor.execute("ROLLBACK")
            flash("Registration conflict: You are already registered for this event.", "warning")
            return redirect(url_for("event_detail", event_id=event_id))
        except Exception as e:
            cursor.execute("ROLLBACK")
            flash(f"An unexpected error occurred during registration: {str(e)}", "danger")
            return redirect(url_for("event_detail", event_id=event_id))

    @app.route("/registrations/success/<string:reg_code>")
    @login_required
    def registration_success(reg_code):
        """Confirmation and digital pass display for successful registration."""
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT r.*, e.title, e.date, e.start_time, e.end_time, e.venue, e.category,
                   u.name as user_name, u.email as user_email
            FROM registrations r
            JOIN events e ON r.event_id = e.id
            JOIN users u ON r.user_id = u.id
            WHERE r.registration_code = ?
        """, (reg_code,))
        reg = cursor.fetchone()
        if not reg:
            abort(404)

        return render_template("registration_success.html", reg=dict(reg))

    @app.route("/registrations/<int:reg_id>/cancel", methods=["POST"])
    @login_required
    def cancel_registration(reg_id):
        """Allow participants or organizers to cancel a registration."""
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM registrations WHERE id = ?", (reg_id,))
        reg = cursor.fetchone()
        if not reg:
            abort(404)

        user_id = session.get("user_id")
        user_role = session.get("user_role")

        # Participant can only cancel their own registration; admin/organizer can cancel any
        if user_role == "participant" and reg["user_id"] != user_id:
            abort(403)

        cursor.execute("UPDATE registrations SET status = 'Cancelled' WHERE id = ?", (reg_id,))
        db.commit()

        flash("Registration has been cancelled successfully.", "info")
        return redirect(url_for("participant_dashboard"))

    # ---------------------------------------------------------
    # Participant Rosters and CSV Export
    # ---------------------------------------------------------
    @app.route("/events/<int:event_id>/participants")
    @roles_required("organizer", "admin")
    def view_event_participants(event_id):
        """View full list of registered participants for an event."""
        db = get_db()
        cursor = db.cursor()

        event = get_event_with_stats(event_id)
        if not event:
            abort(404)

        if session.get("user_role") != "admin" and event["organizer_id"] != session.get("user_id"):
            abort(403)

        cursor.execute("""
            SELECT r.id, r.registration_code, r.registration_date, r.status,
                   u.name, u.email
            FROM registrations r
            JOIN users u ON r.user_id = u.id
            WHERE r.event_id = ?
            ORDER BY r.registration_date ASC
        """, (event_id,))

        roster = [dict(row) for row in cursor.fetchall()]
        return render_template("registrations.html", event=event, roster=roster)

    @app.route("/events/<int:event_id>/export-csv")
    @roles_required("organizer", "admin")
    def export_event_participants_csv(event_id):
        """Export participant roster as a CSV spreadsheet."""
        db = get_db()
        cursor = db.cursor()

        event = get_event_with_stats(event_id)
        if not event:
            abort(404)

        if session.get("user_role") != "admin" and event["organizer_id"] != session.get("user_id"):
            abort(403)

        cursor.execute("""
            SELECT r.registration_code, u.name, u.email, r.status, r.registration_date
            FROM registrations r
            JOIN users u ON r.user_id = u.id
            WHERE r.event_id = ?
            ORDER BY r.registration_date ASC
        """, (event_id,))
        rows = cursor.fetchall()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Registration Code", "Participant Name", "Email Address", "Status", "Registered At"])

        for row in rows:
            writer.writerow([row["registration_code"], row["name"], row["email"], row["status"], row["registration_date"]])

        csv_response = make_response(output.getvalue())
        csv_response.headers["Content-Disposition"] = f"attachment; filename=participants_event_{event_id}.csv"
        csv_response.headers["Content-Type"] = "text/csv"
        return csv_response

    # ---------------------------------------------------------
    # Error Handlers
    # ---------------------------------------------------------
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("404.html", error_code="403", error_title="Access Forbidden", error_message="You don't have permission to access this page."), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("404.html", error_code="404", error_title="Page Not Found", error_message="The page or event you are looking for does not exist or has been moved."), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("500.html", error_code="500", error_title="Internal Server Error", error_message="An unexpected system error occurred. Our engineers have been alerted."), 500

    return app


# Create default application instance for WSGI runners
app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    app.run(host=host, port=port, debug=Config.DEBUG)
