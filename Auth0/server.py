import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for

#configure .env file
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

#configure flask
app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

#configure Authlib to handle your application's authentication with Auth0
oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

#When visitors to your app visit the /login route,
# they'll be redirected to Auth0 to begin the authentication flow.
@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

#After your users finish logging in with Auth0, they'll 
# be returned to your application at the /callback route.
# This route is responsible for actually saving the session
# for the user, so when they visit again later, they won't
# have to sign back in all over again.
@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")

#This route handles signing a user out from your application.
# It will clear the user's session in your app, and briefly
# redirect to Auth0's logout endpoint to ensure their session
# is completely clear, before they are returned to your home route
@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

#Your home route will serve as a place to either render an
# authenticated user's details, or offer to allow visitors to sign in.
@app.route("/")
def home():
    return render_template("home.html", session=session.get('user'),
                           pretty=json.dumps(session.get('user'), indent=4))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))

    