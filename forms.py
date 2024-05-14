from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField,BooleanField, EmailField,PasswordField
from wtforms.validators import DataRequired


# top section of task form
class TaskForm(FlaskForm):
    description = StringField("Task description", validators=[DataRequired()])
    task_date = DateField("Date",format='%Y-%m-%d', validators=[DataRequired()])
    reminder = BooleanField("Reminder")
    submit = SubmitField("Submit task")

class RegisterUserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password",validators=[DataRequired()])
    submit = SubmitField("Login")