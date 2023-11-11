from flask import Flask, render_template
from pymongo import MongoClient
 
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
    return render_template("dc.html")

if __name__ == "__main__":
    app.run(debug=True)   
