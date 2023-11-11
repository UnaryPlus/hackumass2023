from flask import Flask, render_template
from pymongo import MongoClient
from datetime import datetime
 
app = Flask(__name__)

client = MongoClient("mongodb+srv://team1:Y6IsKogedLQRMQD2@umassapp.amt2nke.mongodb.net/?retryWrites=true&w=majority")
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
    return render_template("index.html", dcs=dcs)

@app.route("/dc/<name>")
def dc_page(name):
    users = db["users"]
    comments = []
    for doc in db[name + "_comments"].find():
        doc["user"] = users.find_one({ "_id": doc["user_id"] })
        comments.append(doc)
    return render_template("comments.html", dc=name, comments=comments)

def comment(dc_name, user_id, rating, text):
    users_collection = db["users"]
    user_document = users_collection.find_one({"_id": user_id})
    
    if rating != None:
        user_document["total_ratings"] = user_document.get("total_ratings", 0) + 1
    if text != None:
        user_document["total_comments"] = user_document.get("total_comments", 0) + 1

    users_collection.update_one({"_id": user_id}, {"$set": user_document})

    current_time = datetime.now()
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
    new_document = {"username": username, "email": email, "total_ratings": 0, "total_comments": 0, "friends":[],"friend_requests":[]}
    collection = db["users"]
    result = collection.insert_one(new_document)

if __name__ == "__main__":
    app.run(debug=True)
