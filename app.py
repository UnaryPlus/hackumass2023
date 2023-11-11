from flask import Flask, render_template
from pymongo import MongoClient
 
app = Flask(__name__)

client = MongoClient("mongodb+srv://team1:Y6IsKogedLQRMQD2@umassapp.amt2nke.mongodb.net/?retryWrites=true&w=majority")
db = client["dining"]
users = db["users"]

@app.route("/")
def main_page():
    dcs = [
        { "name": "worcester", "avg_stars": 4 },
        { "name": "hamp", "avg_stars": 2.6 },
        { "name": "berk", "avg_stars": 4.55 },
        { "name": "frank", "avg_stars": 1 },
    ]
    return render_template("index.html", dcs=dcs)

@app.route("/dc/<name>")
def dc_page(name):
    return render_template("dc.html")

def average_rating(hall_name):
    hall = db[f"{hall_name}_comments"]
    data = hall.find({}, {"rating": 1, "_id": 0})
    
    ratings = [doc["rating"] for doc in data if doc.get("rating") is not None]

    average_rating = sum(ratings) / len(ratings)
    
    return average_rating

if __name__ == "__main__":
    app.run(debug=True)   
