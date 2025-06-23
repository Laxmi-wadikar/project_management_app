from flask import Blueprint, render_template, request, redirect, url_for, abort, flash, jsonify
from app.models import db, User, Client_data, DailyEntry, WeeklyReport
from flask_login import login_required, current_user, login_user, logout_user
from datetime import datetime, date
from werkzeug.security import check_password_hash
from functools import wraps

main = Blueprint('main', __name__)

# Role-based access control decorator
def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash("Access denied", "danger")
                return redirect(url_for('main.home'))
            return f(*args, **kwargs)
        return decorated_view
    return wrapper


# LOGIN ROUTE
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('main.home'))
        else:
            flash("Invalid username or password.", "danger")

    return render_template('login.html')



# LOGOUT ROUTE
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for('main.login'))


@main.route('/', methods=['GET', 'POST'])
@login_required
def home():
    today = date.today()

    if request.method == 'POST':
        # Allow only user to add/update their own clients
        # No check needed since user_id is from current_user
        existing_client = Client_data.query.filter_by(user_id=current_user.id, today=today).first()

        if existing_client:
            existing_client.clientname = request.form['clientname']
            existing_client.company = request.form['company']
            existing_client.email = request.form['email']
            existing_client.contact = request.form['contact']
            existing_client.response = request.form['response']
            existing_client.status = request.form['status']
            existing_client.description = request.form['description']
        else:
            new_client = Client_data(
                user_id=current_user.id,
                clientname=request.form['clientname'],
                company=request.form['company'],
                email=request.form['email'],
                contact=request.form['contact'],
                response=request.form['response'],
                status=request.form['status'],
                description=request.form['description'],
                today=today
            )
            db.session.add(new_client)

        db.session.commit()
        return redirect(url_for('main.home'))

    # Filter clients based on role:
    if current_user.role == 'team_lead':
        employee_ids = [e.id for e in current_user.employees]
        allowed_ids = employee_ids + [current_user.id]
        clients = Client_data.query.filter(Client_data.user_id.in_(allowed_ids)).all()
    else:
        clients = Client_data.query.filter_by(user_id=current_user.id).all()

    return render_template('home.html', clients=clients)


@main.route('/client/<int:client_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_client(client_id):
    client = Client_data.query.get_or_404(client_id)

    # Permission: only owner or team_lead can edit
    if current_user.id != client.user_id and current_user.role != 'team_lead':
        abort(403)

    if request.method == 'POST':
        client.clientname = request.form['clientname']
        client.company = request.form['company']
        client.email = request.form['email']
        client.contact = request.form['contact']
        client.response = request.form['response']
        client.status = request.form['status']
        client.description = request.form['description']
        client.today = date.today()

        db.session.commit()
        return redirect(url_for('main.client_detail', client_id=client.client_id))

    return render_template('edit_client.html', client=client)


@main.route('/client/<int:client_id>/detail')
@login_required
def client_detail(client_id):
    # Use correct PK field client_id
    client = Client_data.query.filter_by(client_id=client_id).first_or_404()

    # Optionally: permission check to only show if user owns or is team lead of client owner
    if current_user.role != 'team_lead' and current_user.id != client.user_id:
        abort(403)

    return render_template('client_detail.html', client=client)



@main.route('/clients')
@login_required
def client_list():
    # List clients depending on role
    if current_user.role == 'team_lead':
        employee_ids = [e.id for e in current_user.employees]
        allowed_ids = employee_ids + [current_user.id]
        clients = Client_data.query.filter(Client_data.user_id.in_(allowed_ids)).all()
    else:
        clients = Client_data.query.filter_by(user_id=current_user.id).all()

    return render_template('client_list.html', clients=clients)


@main.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        new_client = Client_data(
            user_id=current_user.id,
            clientname=request.form.get('clientname'),
            company=request.form.get('company'),
            email=request.form.get('email'),
            contact=request.form.get('contact'),
            response=request.form.get('response'),
            status=request.form.get('status'),
            description=request.form.get('description'),
            today=date.today()
        )
        db.session.add(new_client)
        db.session.commit()
        flash("Client added!", "success")
        return redirect(url_for('main.index'))

    if current_user.role == 'team_lead':
        employee_ids = [e.id for e in current_user.employees]
        allowed_ids = employee_ids + [current_user.id]
        clients = Client_data.query.filter(Client_data.user_id.in_(allowed_ids)).all()
    else:
        clients = Client_data.query.filter_by(user_id=current_user.id).all()

    return render_template('index.html', clients=clients)


@main.route('/add-client')
@login_required
def add_client():
    return render_template('add_client.html')


@main.route('/daily_counts', methods=['GET', 'POST'])
@login_required
def daily_counts():
    if request.method == 'POST':
        daily_data = request.form.get('daily_data')
        daily_email = request.form.get('daily_email')
        daily_reminders = request.form.get('daily_reminders')

        new_entry = DailyEntry(
            user_id=current_user.id,
            daily_data=int(daily_data) if daily_data else None,
            daily_email=int(daily_email) if daily_email else None,
            daily_reminders=int(daily_reminders) if daily_reminders else None
        )
        db.session.add(new_entry)
        db.session.commit()
        flash("Daily entry added!", "success")
        return redirect(url_for('main.daily_counts'))

    visible_ids = [current_user.id]
    if current_user.role == 'team_lead':
        visible_ids += [e.id for e in current_user.employees]

    entries = DailyEntry.query.filter(DailyEntry.user_id.in_(visible_ids))\
                .order_by(DailyEntry.created_at.desc()).all()

    # Add per-user sequence number
    entries_by_user = {}
    for entry in reversed(entries):  # reverse to get oldest first
        entries_by_user.setdefault(entry.user_id, []).append(entry)
    user_entries_numbered = []
    for user_id, user_entries in entries_by_user.items():
        for i, e in enumerate(user_entries, 1):
            e.per_user_count = i
            user_entries_numbered.append(e)

    return render_template('daily_counts.html', daily_entries=sorted(user_entries_numbered, key=lambda x: x.created_at, reverse=True))




@main.route('/daily-entry/<int:entry_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_daily_entry(entry_id):
    entry = DailyEntry.query.get_or_404(entry_id)

    if current_user.role != 'team_lead' and entry.user_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        entry.daily_data = int(request.form.get('daily_data') or 0)
        entry.daily_email = int(request.form.get('daily_email') or 0)
        entry.daily_reminders = int(request.form.get('daily_reminders') or 0)
        db.session.commit()
        flash("Daily entry updated.", "success")
        return redirect(url_for('main.daily_counts'))

    return render_template('edit_daily_entry.html', entry=entry)



@main.route('/weekly_data', methods=['GET', 'POST'])
@login_required
def weekly_data():
    if request.method == 'POST':
        report = WeeklyReport(
            week_start=request.form['week_start'],
            user_id=request.form['user_id'],
            closer_amount=request.form['closer_amount'],
            payment_recived=request.form['payment_recived'],
            cancallation=request.form['cancallation'],
            magazine_publised=request.form['magazine_publised'],
            client_closed=request.form['client_closed'],
            currency=request.form['currency']
        )
        db.session.add(report)
        db.session.commit()
        flash("Weekly report added.", "success")
        return redirect(url_for('main.weekly_data'))

    if current_user.role == 'team_lead':
        employee_ids = [e.id for e in current_user.employees]
        allowed_ids = employee_ids + [current_user.id]
        weekly_reports = WeeklyReport.query.filter(WeeklyReport.user_id.in_(allowed_ids)).all()
    else:
        weekly_reports = WeeklyReport.query.filter_by(user_id=current_user.id).all()

    return render_template('weekly_data.html', weekly_reports=weekly_reports)


@main.route('/weeklyreport/<int:weeklyreport_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('team_lead')
def edit_weeklyreport(weeklyreport_id):
    report = WeeklyReport.query.get_or_404(weeklyreport_id)

    def to_integer(value, default):
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    if request.method == 'POST':
        report.week_start = request.form.get('week_start', report.week_start)
        report.closer_amount = to_integer(request.form.get('closer_amount'), report.closer_amount_usd)
        report.payment_recived = to_integer(request.form.get('payment_recived'), report.payment_recived_usd)
        report.cancallation = to_integer(request.form.get('cancallation'), report.cancallation)
        report.magazine_publised = to_integer(request.form.get('magazine_publised'), report.magazine_publised)
        report.client_closed = to_integer(request.form.get('client_closed'), report.client_closed)

        db.session.commit()
        return redirect(url_for('main.weekly_data'))

    return render_template('edit_weeklyreport.html', report=report)

@main.route('/dashboard')
@login_required
def dashboard():
    employees = User.query.with_entities(User.id, User.username).all()
    departments = db.session.query(User.department).distinct().all()
    return render_template('dashboard.html', employees=employees, departments=departments)

@main.route('/api/weekly_data')
@login_required
def get_weekly_data():
    user_id = request.args.get('user_id', type=int)
    department = request.args.get('department')
    week_start = request.args.get('week_start')

    query = WeeklyReport.query.join(User).filter(WeeklyReport.user_id == User.id)

    if user_id:
        query = query.filter(User.id == user_id)
    if department:
        query = query.filter(User.department == department)
    if week_start:
        query = query.filter(WeeklyReport.week_start == week_start)

    report = query.order_by(WeeklyReport.week_start.desc()).first()

    if not report:
        return jsonify({'error': 'No data found'}), 404

    return jsonify({
        'client_closed': report.client_closed or 0,
        'cancellation': report.cancallation or 0,
        'magazine_published': report.magazine_publised or 0,
        'closer_amount': report.closer_amount or 0,
        'payment_received': report.payment_recived or 0,
        'payable_amount': report.payable_amount or 0,
        'week_start': str(report.week_start),
        'username': report.user.username
    })
