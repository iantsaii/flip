import os
import string
import random

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import generate_password_hash, check_password_hash

from helpers import apology, login_required, money

#Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter(to format numeric values as money)
app.jinja_env.filters["money"] = money

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL(os.getenv("DATABASE_URL"))



@app.route("/create", methods=["GET", "POST"])
@login_required
def create_group():
    """ Allow user to create group """

    if request.method == "POST":
        # Get group name
        group_name = request.form.get("group_name")

        # Get group members' usernames. https://stackoverflow.com/questions/24808660/sending-a-form-array-to-flask
        usernames = request.form.getlist("username")

        # Create group
        group_id = db.execute("INSERT INTO groups (group_name, size) VALUES (?, ?)", group_name, len(usernames) + 1)


        # Add members to group
        for username in usernames:

            # Ensure that username was typed in
            if not username:
                return apology("must provide username(s)")

            # Check that username exists
            elif len(db.execute("SELECT * FROM users WHERE username = ?", username)) != 1:
                return apology("invalid username")

            # Add username to group
            else:
                user_id = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]
                db.execute("INSERT INTO membership (user_id, group_id) VALUES(?, ?)", user_id, group_id)

        # Add user himself to the group
        db.execute("INSERT INTO membership (user_id, group_id) VALUES(?, ?)", session["user_id"], group_id)

        # Redirect user to index
        return redirect("/")


    # Allow user to search for usernames

    return render_template("create.html")
    return apology("TODO")


@app.route("/")
@login_required
def index():
    """ Display user's groups """

    # Select group_names which the user belongs to
    groups = db.execute(
        "SELECT group_name, group_id FROM groups JOIN membership ON groups.id = membership.group_id JOIN users ON membership.user_id = users.id WHERE user_id = ?"
        , session["user_id"])

    # Add members' usernames to the "groups" variable

    # For each group that the user is part of
    for group in groups:

        # SELECT a list of dictionaries, where each dictionary is a key-value pair of "username":"member's username"
        members = db.execute("SELECT username from users JOIN membership ON users.id = membership.user_id JOIN groups ON membership.group_id = groups.id WHERE groups.id = ?", group["group_id"])

        # For each username in the list
        for i, member in enumerate(members):

            if i == 0:

                # Create a key-value pair with the first member's name
                group["string"] = member["username"]

            else:

                # Add subsequent members' names to the string
                group["string"] += ", "
                group["string"] += member["username"]

    # Show user the groups he belongs to
    return render_template("index.html", groups=groups)
    return apology("TODO")


@app.route("/transactions", methods=["GET", "POST"])
@login_required
def transactions():
    """  Display transactions """

    # Clear data associated with previous group
    session["group_info"] = None

    # User will be redirected here when he clicks on "Group History" on the index page
    if request.method == "POST":


        # *** Save group info ***
        # Get id of the relevant group
        group_id = request.form.get("group_id")

        # Get usernames of group members
        # SELECT a list of dictionaries, where each dictionary is a key-value pair of "username":"member's username"
        members = db.execute("SELECT username FROM users JOIN membership ON users.id = membership.user_id JOIN groups ON membership.group_id = groups.id WHERE groups.id = ?", group_id)
        # Change dictionary into a list
        list1 = []
        for member in members:
            list1.append(member["username"])
        members = list1

        # Get group name and size
        group_info = db.execute("SELECT group_name, size FROM groups WHERE id = ?", group_id)
        group_name = group_info[0]["group_name"]
        size = group_info[0]["size"]

        # Save group info for use later when initiating a new transaction
        session["group_info"] = {"id":group_id, "size":size, "members":members}

        # *** Get data to be displayed to user ***
        # Get transaction history of group
        transactions = db.execute("SELECT users.username, quantity, name, time FROM transactions JOIN users ON transactions.payer = users.id WHERE group_id = ?", group_id)

        # Get the total amount paid by each person
        stats = {}
        for member in members:
            stats[member] = 0
        for transaction in transactions:
            stats[transaction["username"]] += transaction["quantity"]

        # Display transactions of the group
        return render_template("transactions.html", transactions=transactions, group_name=group_name, stats=stats)
        return apology("TODO")

    return apology("TODO")


@app.route("/flip", methods=["GET", "POST"])
@login_required
def flip():
    """ Allow user to flip the coin """

    if request.method == "POST":

        # Get list of usernames of group members
        members = session["group_info"]["members"]

        # Get size of the group N
        N = session["group_info"]["size"]

        # Randomly decide who's going to pay
        result = random.randint(0, N-1)
        result = members[result]

        # Get name of transaction and money associated with it
        # https://www.w3schools.com/jquery/jquery_ajax_get_post.asp
        amount = request.form.get("amount")
        name = request.form.get("name")

        # Insert result into the database
        user_id = db.execute("SELECT id FROM users WHERE username = ?", result)[0]["id"]
        db.execute("INSERT INTO transactions (group_id, payer, quantity, name) VALUES (?, ?, ?, ?)",
            session["group_info"]["id"], user_id, amount, name)

        # Return the results in JSON format
        return result
    return apology("TODO")


@app.route("/delete_group", methods=["POST"])
@login_required
def delete_group():
    """ Delete group """
    group_id = request.form.get("group_id")
    db.execute("DELETE FROM membership WHERE group_id = ?", group_id)
    db.execute("DELETE FROM transactions WHERE group_id = ?", group_id)
    db.execute("DELETE FROM groups WHERE id = ?", group_id)
    return "OK"


@app.route("/register", methods=["GET", "POST"])
def register():
    """ Register user """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Render an apology if the user’s input is blank or the username already exists.
        if not username:
            return apology("must provide username")
        elif len(db.execute("SELECT * FROM users WHERE username = ?", username)) != 0:
            return apology("username already exists")

        # Render an apology if the user's input is blank or passwords do not match
        elif not password or not confirmation:
            return apology("please type out passwords twice")
        elif password != confirmation:
            return apology("passwords do not match")
        else:
            # Generate hash
            hashed = generate_password_hash(password)

            # Insert username and password into database
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hashed)

            # Feedback to user that he has successfully registered
            flash("registered!")

            # Redirect user to login page
            return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

       # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user logged in
        session["user_id"] = rows[0]["id"]
        
        user_id = session.get("user_id")
        print(f"\n\n{user_id}\n\n")

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("login.html")

    return apology("TODO")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/about")
def about():
    """Describe the website to the user"""
    return render_template("about.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
