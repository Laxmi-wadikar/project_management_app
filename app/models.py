from . import db
from flask_login import UserMixin
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20))  # 'admin', 'manager', 'team_lead', 'employee'
    email = db.Column(db.String(150), unique=True)
    department = db.Column(db.String(100))

    # Self-referential leader relationship
    leader_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    employees = db.relationship('User', backref=db.backref('leader', remote_side=[id]))


    # Correct relationship for WeeklyReport
    weekly_reports = db.relationship('WeeklyReport', back_populates='user')

    def set_password(self, password):
      self.password = generate_password_hash(password)

    def check_password(self, password):
       return check_password_hash(self.password, password)


   

class Client_data(db.Model):
    __tablename__ = 'client_data'

    client_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Replace sales_id + id with one proper user_id foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    clientname = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    contact = db.Column(db.String(10))
    response = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))  # Corrected spelling
    today = db.Column(db.Date, default=date.today, nullable=False)

    # Optional relationship
    user = db.relationship('User', backref='clients')


class DailyEntry(db.Model):
    __tablename__ = 'daily_entry'

    dailyentry_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ✅ Add this
    daily_data = db.Column(db.Integer)
    daily_email = db.Column(db.Integer)
    daily_reminders = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to access the user
    user = db.relationship('User', backref='daily_entries')

class WeeklyReport(db.Model):
    WeeklyReport_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    week_start = db.Column(db.Date, nullable=False, default=date.today)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # FK corrected
    user = db.relationship('User', back_populates='weekly_reports')  # No "employee" relationship
    closer_amount = db.Column(db.Integer)
    payment_received = db.Column(db.Integer)
    cancallation = db.Column(db.Integer)
    magazine_publised = db.Column(db.Integer)
    currency = db.Column(db.String(3))
    client_closed = db.Column(db.Integer)

    @property
    def payable_amount(self):
        return (self.closer_amount or 0) - (self.payment_received or 0)


     # Conversion rates relative to USD (You can update dynamically)
    # _conversion_rates = {
    #     'USD': 1.0,
    #     'INR': 0.01205,
    #     # add more if needed
    # }

    # @property
    # def payable_amount(self):
    #     return (self.closer_amount or 0) - (self.payment_recived or 0)

    # @property
    # def closer_amount_usd(self):
    #     rate = self._conversion_rates.get(self.currency, 1)
    #     return (self.closer_amount or 0) * rate

    # @property
    # def payment_recived_usd(self):
    #     rate = self._conversion_rates.get(self.currency, 1)
    #     return (self.payment_recived or 0) * rate
