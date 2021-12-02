from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to the user"""
    return render_template("apology.html", message=message, code=code), code


def login_required(f):
    """ Decorate routes to require login """
    @wraps(f)
    def decorated_function(*args, **kwargs):
            if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, *kwargs)
    return decorated_function


def money(value):
    """ Format value as money """
    return f"${value:,.2f}"