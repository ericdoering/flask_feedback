from flask import Flask, render_template, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import Unauthorized

from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm, DeleteForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URL'] = "postgresql:///feedback_exercise"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "feeeedbackkk"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)

@app.route("/")
def homepage():
    """Main homepage of Feedback App"""

    return redirect("/register")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Allow user to sign in via a form"""

    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data

        user = User.register(username, password, first_name, last_name, email)

        db.session.commit()
        session["username"] = user.username

        return redirect(f"/users/{user.username}")

    else:
        return render_template("users/register.html", form=form)



@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login"""

    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            session['username'] = user.username
            return redirect(f"/users/{session['username']}")
        else:
            form.username.errors = ["Invalid username and/or password."]
            return render_template("user/login.html", form=form)



@app.route("/logout")
def logout():
    """Logout the user"""

    session.pop("username")
    return redirect("/login")



@app.route("/users/<username>")
def show_user(username):
    """Brings signed in user to main page"""

    if "username" not in session or username != session["username"]:
        raise Unauthorized()

    user = User.query.get(username)
    form = DeleteForm()

    return render_template("users/show.html", user=user, form=form)



@app.route("/users/<username>/delete", methods=["POST"])
def remove_user(username):
    """Removes the user and takes them to the login page"""

    if "username" not in session or username != session["username"]:
        raise Unauthorized()

    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("username")

    return redirect("/login")



@app.route("/users/<username>/feedback/new", methods=["GET", "POST"])
def new_feedback(username):
    """Allows the user to create make a post and adds it to existing posts"""

    if "username" not in session or username != session["username"]:
        raise Unauthorized()

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, username=username)

        db.session.add(feedback)
        db.session.commit()

        return redirect(f"/users/{feedback.username}")
    
    else:
        return render_template("feedback/new.html", form=form)



@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    """Allow user to edit a feedback post"""

    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session["username"]:
        raise Unauthorized()

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    return render_template("/feedback/edit.html", form=form, feedback=Feedback)



@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Allow a user to delete a feedback post"""

    feedback = Feedback.query.get(feedback_id)
    
    if "username" not in session or feedback.username != session["username"]:
        raise Unauthorized()

    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()

    return redirect(f"/users/{feedback.username}")