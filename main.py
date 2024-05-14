import time

from flask import Flask, render_template, request, url_for, redirect, flash,abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import TaskForm, RegisterUserForm, LoginForm
from functools import wraps
import os
from dotenv import load_dotenv

load_dotenv(".env")


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
Bootstrap5(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Create a user_loader callback. Connects to the User table
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI','sqlite:///task_app.db')
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CREATE TABLE IN DB
# New addition is the UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    # This will act like a List of Task objects attached to each User.
    task_list = relationship("Task", back_populates="tasks")

class Task(db.Model):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String(100))
    date: Mapped[str] = mapped_column(String(100))
    reminder: Mapped[bool] = mapped_column()
    # Create Foreign Key
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("user.id"))
    # Create reference to the User object.
    tasks = relationship("User", back_populates="task_list")


with app.app_context():
    db.create_all()

# Create user only decorator
def user_only(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        # if the user is registered
        if not current_user.is_authenticated:
            return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar_one()
        except Exception:
            flash("Email does not exist")
            return redirect("login")
        # get password and check if the hash value corresponds
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('tasks'))
        else:
            flash(message="Password Incorrect ", category="error")
    return render_template("login.html", form=form, current_user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterUserForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.email==form.email.data)).scalar()
        if user:
            print("Email exits")
            return redirect(url_for("login"))
        new_password = generate_password_hash(form.password.data,method="pbkdf2:sha256", salt_length=8)
        new_email = form.email.data
        new_name = form.name.data
        new_user = User(
            email = new_email,
            password = new_password,
            name = new_name)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("tasks"))
    return render_template('register.html', form=form, current_user=current_user)


@app.route('/tasks', methods=['GET', 'POST'])
@user_only
def tasks():
    # add SQL here to get data from database
    # text input box for description
    # text input box for date
    # reminder button to highlight task
    # list all tasks on database
    form = TaskForm()
    task_list = db.session.execute(db.select(Task)).scalars().all()

    print(task_list)
    if form.validate_on_submit():
        #check_reminder = request.form.get("reminder")
        check_reminder = form.reminder.data
        print(f"check_reminder: {check_reminder}")
        if check_reminder:
            check_reminder = True
        else:
            check_reminder = False
        # add_task = Task(
        #     description=request.form.get("description"),
        #     date=request.form.get("date"),
        #     reminder=check_reminder
        # )

        add_task = Task(
            description = form.description.data,
            date = form.task_date.data,
            reminder = check_reminder,
            user_id = current_user.id
        )
        db.session.add(add_task)
        db.session.commit()
        return redirect(url_for("tasks"))
    return render_template('tasks.html', tasks=task_list, form=form, current_user=current_user)


@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST', 'PATCH'])
@user_only
def edit_task(task_id):
    # return specific task linked to task_id
    task_to_edit = db.session.execute(db.select(Task).where(Task.id == task_id)).scalar_one()
    edit_task_field = request.form.get("description")
    edit_task_date = request.form.get("date")
    edit_task_reminder = request.form.get("reminder")
    if request.method == 'POST':
        # if the field remains unedited use the original text
        if edit_task_field == "":
            task_to_edit.description = task_to_edit.description
        # otherwise use the new updated text
        else:
            task_to_edit.description = request.form.get("description")
        # if the field remains unedited use the original text
        if edit_task_date == "":
            task_to_edit.date = task_to_edit.date
        # otherwise use the new updated text
        else:
            task_to_edit.date = request.form.get("date")
        # if the reminder is marked to return True for the dbase requirement
        if edit_task_reminder:
            task_to_edit.reminder = True
        # otherwise the reminder is marked to return False for the dbase requirement
        else:
            task_to_edit.reminder = False

        db.session.commit()
        return redirect(url_for('tasks'))
    return render_template('edit.html', task=task_to_edit)


@app.route('/delete/<int:task_id>', methods=['GET', 'POST', 'DELETE'])
@user_only
def delete_task(task_id):
    print(task_id)
    try:
        task_to_delete = db.session.execute(db.select(Task).where(Task.id == task_id)).scalar_one()
        db.session.delete(task_to_delete)
        db.session.commit()
    except Exception:
        print("error")
    return redirect(url_for('tasks'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))



if __name__ == "__main__":
    app.run(debug=True, port=5003)

