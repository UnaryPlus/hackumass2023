from flask import Flask, render_template, redirect, request, session, url_for
from pymongo import MongoClient
from datetime import datetime
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from urllib.parse import quote_plus, urlencode
from os import environ as env
import pytz

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={ "scope": "openid profile email" },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

client = MongoClient(env.get("MONGO_URI"))
db = client["dining"]

def average_stars(dc):
    data = db[dc + "_comments"].find({ "rating": { "$ne": None } })
    ratings = [ doc["rating"] for doc in data ]
    avg_stars = sum(ratings) / len(ratings)
    return avg_stars

@app.route("/")
def main_page():
    dcs = [
        { "name": name, "avg_stars": average_stars(name) }
        for name in [ "woo", "hamp", "berk", "frank" ]
    ]
    dcs.sort(key=lambda dc: -dc["avg_stars"])
    return render_template("index.html", dcs=dcs, user=session.get("user"))

@app.route("/dc/<dc_name>")
def dc_page(dc_name):
    users = db["users"]
    comments = []
    for doc in db[dc_name + "_comments"].find():
        doc["user"] = users.find_one({ "_id": doc["user_id"] })
        comments.append(doc)
    comments.reverse()
    return render_template("comments.html", dc=dc_name, comments=comments, user=session.get("user"))

@app.route("/comment/<dc_name>", methods=["POST"])
def comment_action(dc_name):
    email = session.get("user")["email"]
    rating = int(request.form["rating"])
    if rating == 0: rating = None
    comment(dc_name, email, rating, request.form["text"])
    return redirect('/dc/' + dc_name)

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)    
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    username = token["userinfo"]["nickname"] # fix this
    email = token["userinfo"]["name"]

    users = db["users"]
    user = users.find_one({ "email": email })
    if user == None:
        new_user(username, email)
    session["user"] = { "username": username, "email": email }
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode({
                "returnTo": url_for("main_page", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

def comment(dc_name, email, rating, text):
    users_collection = db["users"]
    user_document = users_collection.find_one({"email": email})
    user_id = user_document["_id"]
    
    if rating != None:
        user_document["total_ratings"] = user_document.get("total_ratings", 0) + 1
    if text != None:
        user_document["total_comments"] = user_document.get("total_comments", 0) + 1

    users_collection.update_one({"_id": user_id}, {"$set": user_document})

    est_timezone = pytz.timezone("America/New_York")

    current_time = datetime.now(est_timezone)
    hour = current_time.hour
    minute = current_time.minute

    new_comment = {
        "user_id": user_id,
        "rating": rating,
        "text": text,
        "time": {
            "hour": hour,
            "minute": minute
        }
    }
    comments_collection = db[dc_name + "_comments"]
    result = comments_collection.insert_one(new_comment)

def new_user(username, email):
    new_document = {"username": username, "email": email, "total_ratings": 0, "total_comments": 0, "friends":[], "friend_requests":[]}
    collection = db["users"]
    result = collection.insert_one(new_document)

if __name__ == "__main__":
    app.run(debug=True)
