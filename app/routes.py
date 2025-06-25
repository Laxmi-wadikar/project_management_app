from flask import Blueprint, render_template, request, redirect, url_for, abort, flash, jsonify
from app.models import db, User, Client_data, DailyEntry, WeeklyReport
from datetime import date
from functools import wraps
from flask_login import login_user, logout_user, current_user, login_required

main = Blueprint('main', __name__)

# Role-based access control decorator
def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash("Access denied.", "danger")
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated_view
    return wrapper


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for('main.login'))


@main.route('/', methods=['GET', 'POST'])
@login_required
def home():
    today = date.today()
    user_id = current_user.id
    role = current_user.role

    if request.method == 'POST':
        existing_client = Client_data.query.filter_by(user_id=user_id, today=today).first()
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
                user_id=user_id,
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

    if role == 'team_lead':
        employee_ids = [emp.id for emp in User.query.filter_by(leader_id=user_id).all()]
        allowed_ids = employee_ids + [user_id]
        clients = Client_data.query.filter(Client_data.user_id.in_(allowed_ids)).all()
    else:
        clients = Client_data.query.filter_by(user_id=user_id).all()

    return render_template('home.html', clients=clients)


@main.route('/client/<int:client_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_client(client_id):
    client = Client_data.query.get_or_404(client_id)
    user_id = current_user.id
    role = current_user.role

    if user_id != client.user_id and role != 'team_lead':
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
    client = Client_data.query.get_or_404(client_id)
    user_id = current_user.id
    role = current_user.role

    if role != 'team_lead' and user_id != client.user_id:
        abort(403)

    return render_template('client_detail.html', client=client)


@main.route('/clients')
@login_required
def client_list():
    user_id = current_user.id
    role = current_user.role

    if role == 'team_lead':
        employee_ids = [emp.id for emp in User.query.filter_by(leader_id=user_id).all()]
        allowed_ids = employee_ids + [user_id]
        clients = Client_data.query.filter(Client_data.user_id.in_(allowed_ids)).all()
    else:
        clients = Client_data.query.filter_by(user_id=user_id).all()

    return render_template('client_list.html', clients=clients)


@main.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    user_id = current_user.id
    role = current_user.role

    if request.method == 'POST':
        new_client = Client_data(
            user_id=user_id,
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

    if role == 'team_lead':
        employee_ids = [emp.id for emp in User.query.filter_by(leader_id=user_id).all()]
        allowed_ids = employee_ids + [user_id]
        clients = Client_data.query.filter(Client_data.user_id.in_(allowed_ids)).all()
    else:
        clients = Client_data.query.filter_by(user_id=user_id).all()

    return render_template('index.html', clients=clients)


@main.route('/add-client')
@login_required
def add_client():
    return render_template('add_client.html')


@main.route('/daily_counts', methods=['GET', 'POST'])
@login_required
def daily_counts():
    user_id = current_user.id
    role = current_user.role

    if request.method == 'POST':
        daily_data = request.form.get('daily_data')
        daily_email = request.form.get('daily_email')
        daily_reminders = request.form.get('daily_reminders')

        new_entry = DailyEntry(
            user_id=user_id,
            daily_data=int(daily_data) if daily_data else None,
            daily_email=int(daily_email) if daily_email else None,
            daily_reminders=int(daily_reminders) if daily_reminders else None
        )
        db.session.add(new_entry)
        db.session.commit()
        flash("Daily entry added!", "success")
        return redirect(url_for('main.daily_counts'))

    visible_ids = [user_id]
    if role == 'manager':
        visible_ids += [emp.id for emp in User.query.filter_by(leader_id=user_id).all()]

    entries = DailyEntry.query.filter(DailyEntry.user_id.in_(visible_ids))\
                .order_by(DailyEntry.created_at.desc()).all()

    entries_by_user = {}
    for entry in reversed(entries):
        entries_by_user.setdefault(entry.user_id, []).append(entry)

    user_entries_numbered = []
    for uid, user_entries in entries_by_user.items():
        for i, e in enumerate(user_entries, 1):
            e.per_user_count = i
            user_entries_numbered.append(e)

    return render_template('daily_counts.html', daily_entries=sorted(user_entries_numbered, key=lambda x: x.created_at, reverse=True))


@main.route('/daily-entry/<int:entry_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_daily_entry(entry_id):
    entry = DailyEntry.query.get_or_404(entry_id)
    user_id = current_user.id
    role = current_user.role

    if role != 'manager' and entry.user_id != user_id:
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
    user_id = current_user.id
    role = current_user.role

    if request.method == 'POST':
        report = WeeklyReport(
            week_start=request.form['week_start'],
            user_id=user_id,
            closer_amount=request.form['closer_amount'],
            payment_received=request.form['payment_received'],
            cancallation=request.form['cancallation'],
            magazine_publised=request.form['magazine_publised'],
            client_closed=request.form['client_closed'],
            currency=request.form['currency']
        )
        db.session.add(report)
        db.session.commit()
        flash("Weekly report added.", "success")
        return redirect(url_for('main.weekly_data'))

    if role == 'team_lead':
        employee_ids = [emp.id for emp in User.query.filter_by(leader_id=user_id).all()]
        allowed_ids = employee_ids + [user_id]
        weekly_reports = WeeklyReport.query.filter(WeeklyReport.user_id.in_(allowed_ids)).all()
    else:
        weekly_reports = WeeklyReport.query.filter_by(user_id=user_id).all()

    return render_template('weekly_data.html', weekly_reports=weekly_reports)


@main.route('/weeklyreport/<int:weeklyreport_id>/edit', methods=['GET', 'POST'])
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
        report.closer_amount = to_integer(request.form.get('closer_amount'), report.closer_amount)
        report.payment_received = to_integer(request.form.get('payment_received'), report.payment_recived)
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
        'payment_received': report.payment_received or 0,
        'payable_amount': report.payable_amount or 0,
    })


@main.route('/add-user', methods=['GET', 'POST'])
@roles_required('admin', 'manager')  # Only admin/manager can access
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        department = request.form['department']
        role = request.form['role']
        password = request.form['password']
        leader_id = request.form.get('leader_id')

        new_user = User(
            username=username,
            email=email,
            department=department,
            role=role,
            leader_id=leader_id if leader_id else None
        )
        new_user.set_password(password)  # 🔐 Hashing happens here

        db.session.add(new_user)
        db.session.commit()
        flash("User added successfully", "success")
        return redirect(url_for('main.dashboard'))

    users = User.query.all()  # For selecting leader_id optionally
    return render_template('add_user.html', users=users)



# from flask import Blueprint, render_template, request, redirect, url_for, abort, flash, jsonify, session
# from app.models import db, User, Client_data, DailyEntry, WeeklyReport
# from datetime import datetime, date
# from functools import wraps
# from flask_login import login_user



# main = Blueprint('main', __name__)




# @main.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')

#         user = User.query.filter_by(username=username).first()

#         if user and user.check_password(password):
#             login_user(user)  # This line is critical!
#             flash('Login successful!', 'success')
#             return redirect(url_for('main.home'))  # Adjust as needed
#         else:
#             flash('Invalid username or password', 'danger')

#     return render_template('login.html')


# # Role-based access control decorator (will always deny now because no user info)
# def roles_required(*roles):
#     def wrapper(f):
#         @wraps(f)
#         def decorated_view(*args, **kwargs):
#             flash("Access denied", "danger")
#             return redirect(url_for('main.home'))
#         return decorated_view
#     return wrapper

# # LOGOUT route removed as it depends on login
# @main.route('/logout')
# def logout():
#     session.clear()
#     flash("Logged out successfully.", "info")
#     return redirect(url_for('main.login'))


# @main.route('/', methods=['GET', 'POST'])
# def home():
#     if 'user_id' not in session:
#         return redirect(url_for('main.login'))  # redirect to login if not logged in

#     today = date.today()
#     user_id = session['user_id']
#     role = session.get('role', 'user')

#     if request.method == 'POST':
#         existing_client = Client_data.query.filter_by(user_id=user_id, today=today).first()

#         if existing_client:
#             existing_client.clientname = request.form['clientname']
#             existing_client.company = request.form['company']
#             existing_client.email = request.form['email']
#             existing_client.contact = request.form['contact']
#             existing_client.response = request.form['response']
#             existing_client.status = request.form['status']
#             existing_client.description = request.form['description']
#         else:
#             new_client = Client_data(
#                 user_id=user_id,
#                 clientname=request.form['clientname'],
#                 company=request.form['company'],
#                 email=request.form['email'],
#                 contact=request.form['contact'],
#                 response=request.form['response'],
#                 status=request.form['status'],
#                 description=request.form['description'],
#                 today=today
#             )
#             db.session.add(new_client)

#         db.session.commit()
#         return redirect(url_for('main.home'))

#     # Query client data based on role
#     if role == 'team_lead':
#         # Get employees assigned to this team lead
#         employee_ids = [emp.id for emp in User.query.filter_by(leader_id=user_id).all()]
#         allowed_ids = employee_ids + [user_id]
#         clients = Client_data.query.filter(Client_data.user_id.in_(allowed_ids)).all()
#     else:
#         clients = Client_data.query.filter_by(user_id=user_id).all()

#     return render_template('home.html', clients=clients)
# # @main.route('/', methods=['GET', 'POST'])
# # def home():
# #     today = date.today()
# #     user_id = 1  # Hardcoded user ID
# #     role = 'user'  # Hardcoded role; change as needed

# #     if request.method == 'POST':
# #         existing_client = Client_data.query.filter_by(user_id=user_id, today=today).first()

# #         if existing_client:
# #             existing_client.clientname = request.form['clientname']
# #             existing_client.company = request.form['company']
# #             existing_client.email = request.form['email']
# #             existing_client.contact = request.form['contact']
# #             existing_client.response = request.form['response']
# #             existing_client.status = request.form['status']
# #             existing_client.description = request.form['description']
# #         else:
# #             new_client = Client_data(
# #                 user_id=user_id,
# #                 clientname=request.form['clientname'],
# #                 company=request.form['company'],
# #                 email=request.form['email'],
# #                 contact=request.form['contact'],
# #                 response=request.form['response'],
# #                 status=request.form['status'],
# #                 description=request.form['description'],
# #                 today=today
# #             )
# #             db.session.add(new_client)

# #         db.session.commit()
# #         return redirect(url_for('main.home'))

# #     if role == 'team_lead':
# #         # No employee info without current_user, so empty list
# #         employee_ids = []
# #         allowed_ids = employee_ids + [user_id]
# #         clients = Client_data.query.filter(Client_data.user_id.in_(allowed_ids)).all()
# #     else:
# #         clients = Client_data.query.filter_by(user_id=user_id).all()

# #     return render_template('home.html', clients=clients)

# @main.route('/client/<int:client_id>/edit', methods=['GET', 'POST'])
# def edit_client(client_id):
#     user_id = 1
#     role = 'user'

#     client = Client_data.query.get_or_404(client_id)

#     if user_id != client.user_id and role != 'team_lead':
#         abort(403)

#     if request.method == 'POST':
#         client.clientname = request.form['clientname']
#         client.company = request.form['company']
#         client.email = request.form['email']
#         client.contact = request.form['contact']
#         client.response = request.form['response']
#         client.status = request.form['status']
#         client.description = request.form['description']
#         client.today = date.today()

#         db.session.commit()
#         return redirect(url_for('main.client_detail', client_id=client.client_id))

#     return render_template('edit_client.html', client=client)

# @main.route('/client/<int:client_id>/detail')
# def client_detail(client_id):
#     user_id = 1
#     role = 'user'

#     client = Client_data.query.filter_by(client_id=client_id).first_or_404()

#     if role != 'team_lead' and user_id != client.user_id:
#         abort(403)

#     return render_template('client_detail.html', client=client)

# @main.route('/clients')
# def client_list():
#     user_id = 1
#     role = 'user'

#     if role == 'team_lead':
#         employee_ids = []
#         allowed_ids = employee_ids + [user_id]
#         clients = Client_data.query.filter(Client_data.user_id.in_(allowed_ids)).all()
#     else:
#         clients = Client_data.query.filter_by(user_id=user_id).all()

#     return render_template('client_list.html', clients=clients)

# @main.route('/index', methods=['GET', 'POST'])
# def index():
#     user_id = 1
#     role = 'user'

#     if request.method == 'POST':
#         new_client = Client_data(
#             user_id=user_id,
#             clientname=request.form.get('clientname'),
#             company=request.form.get('company'),
#             email=request.form.get('email'),
#             contact=request.form.get('contact'),
#             response=request.form.get('response'),
#             status=request.form.get('status'),
#             description=request.form.get('description'),
#             today=date.today()
#         )
#         db.session.add(new_client)
#         db.session.commit()
#         flash("Client added!", "success")
#         return redirect(url_for('main.index'))

#     if role == 'team_lead':
#         employee_ids = []
#         allowed_ids = employee_ids + [user_id]
#         clients = Client_data.query.filter(Client_data.user_id.in_(allowed_ids)).all()
#     else:
#         clients = Client_data.query.filter_by(user_id=user_id).all()

#     return render_template('index.html', clients=clients)

# @main.route('/add-client')
# def add_client():
#     return render_template('add_client.html')

# @main.route('/daily_counts', methods=['GET', 'POST'])
# def daily_counts():
#     user_id = 1
#     role = 'user'

#     if request.method == 'POST':
#         daily_data = request.form.get('daily_data')
#         daily_email = request.form.get('daily_email')
#         daily_reminders = request.form.get('daily_reminders')

#         new_entry = DailyEntry(
#             user_id=user_id,
#             daily_data=int(daily_data) if daily_data else None,
#             daily_email=int(daily_email) if daily_email else None,
#             daily_reminders=int(daily_reminders) if daily_reminders else None
#         )
#         db.session.add(new_entry)
#         db.session.commit()
#         flash("Daily entry added!", "success")
#         return redirect(url_for('main.daily_counts'))

#     visible_ids = [user_id]
#     if role == 'team_lead':
#         visible_ids += []

#     entries = DailyEntry.query.filter(DailyEntry.user_id.in_(visible_ids))\
#                 .order_by(DailyEntry.created_at.desc()).all()

#     entries_by_user = {}
#     for entry in reversed(entries):
#         entries_by_user.setdefault(entry.user_id, []).append(entry)

#     user_entries_numbered = []
#     for uid, user_entries in entries_by_user.items():
#         for i, e in enumerate(user_entries, 1):
#             e.per_user_count = i
#             user_entries_numbered.append(e)

#     return render_template('daily_counts.html', daily_entries=sorted(user_entries_numbered, key=lambda x: x.created_at, reverse=True))

# @main.route('/daily-entry/<int:entry_id>/edit', methods=['GET', 'POST'])
# def edit_daily_entry(entry_id):
#     user_id = 1
#     role = 'user'

#     entry = DailyEntry.query.get_or_404(entry_id)

#     if role != 'team_lead' and entry.user_id != user_id:
#         abort(403)

#     if request.method == 'POST':
#         entry.daily_data = int(request.form.get('daily_data') or 0)
#         entry.daily_email = int(request.form.get('daily_email') or 0)
#         entry.daily_reminders = int(request.form.get('daily_reminders') or 0)
#         db.session.commit()
#         flash("Daily entry updated.", "success")
#         return redirect(url_for('main.daily_counts'))

#     return render_template('edit_daily_entry.html', entry=entry)

# @main.route('/weekly_data', methods=['GET', 'POST'])
# def weekly_data():
#     user_id = 1
#     role = 'user'

#     if request.method == 'POST':
#         report = WeeklyReport(
#             week_start=request.form['week_start'],
#             user_id=request.form['user_id'],
#             closer_amount=request.form['closer_amount'],
#             payment_recived=request.form['payment_recived'],
#             cancallation=request.form['cancallation'],
#             magazine_publised=request.form['magazine_publised'],
#             client_closed=request.form['client_closed'],
#             currency=request.form['currency']
#         )
#         db.session.add(report)
#         db.session.commit()
#         flash("Weekly report added.", "success")
#         return redirect(url_for('main.weekly_data'))

#     if role == 'team_lead':
#         employee_ids = []
#         allowed_ids = employee_ids + [user_id]
#         weekly_reports = WeeklyReport.query.filter(WeeklyReport.user_id.in_(allowed_ids)).all()
#     else:
#         weekly_reports = WeeklyReport.query.filter_by(user_id=user_id).all()

#     return render_template('weekly_data.html', weekly_reports=weekly_reports)

# @main.route('/weeklyreport/<int:weeklyreport_id>/edit', methods=['GET', 'POST'])
# @roles_required('team_lead')
# def edit_weeklyreport(weeklyreport_id):
#     report = WeeklyReport.query.get_or_404(weeklyreport_id)

#     def to_integer(value, default):
#         try:
#             return int(value)
#         except (ValueError, TypeError):
#             return default

#     if request.method == 'POST':
#         report.week_start = request.form.get('week_start', report.week_start)
#         report.closer_amount = to_integer(request.form.get('closer_amount'), report.closer_amount)
#         report.payment_recived = to_integer(request.form.get('payment_recived'), report.payment_recived)
#         report.cancallation = to_integer(request.form.get('cancallation'), report.cancallation)
#         report.magazine_publised = to_integer(request.form.get('magazine_publised'), report.magazine_publised)
#         report.client_closed = to_integer(request.form.get('client_closed'), report.client_closed)

#         db.session.commit()
#         return redirect(url_for('main.weekly_data'))

#     return render_template('edit_weeklyreport.html', report=report)

# @main.route('/dashboard')
# def dashboard():
#     employees = User.query.with_entities(User.id, User.username).all()
#     departments = db.session.query(User.department).distinct().all()
#     return render_template('dashboard.html', employees=employees, departments=departments)

# @main.route('/api/weekly_data')
# def get_weekly_data():
#     user_id = request.args.get('user_id', type=int)
#     department = request.args.get('department')
#     week_start = request.args.get('week_start')

#     query = WeeklyReport.query.join(User).filter(WeeklyReport.user_id == User.id)

#     if user_id:
#         query = query.filter(User.id == user_id)
#     if department:
#         query = query.filter(User.department == department)
#     if week_start:
#         query = query.filter(WeeklyReport.week_start == week_start)

#     report = query.order_by(WeeklyReport.week_start.desc()).first()

#     if not report:
#         return jsonify({'error': 'No data found'}), 404

#     return jsonify({
#         'client_closed': report.client_closed or 0,
#         'cancellation': report.cancallation or 0,
#         'magazine_published': report.magazine_publised or 0,
#         'closer_amount': report.closer_amount or 0,
#         'payment_received': report.payment_recived or 0,
#         'payable_amount': report.payable_amount or 0,
#         'week_start': str(report.week_start),
#         'username': report.user.username
#     })

# @main.route('/totals')
# def totals():
#     reports = WeeklyReport.query.all()
#     total_closer_usd = sum(r.closer_amount_usd or 0 for r in reports)
#     total_payment_usd = sum(r.payment_recived_usd or 0 for r in reports)
#     return render_template('totals.html', total_closer_usd=total_closer_usd, total_payment_usd=total_payment_usd)
