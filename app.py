from flask import Flask, render_template
 
app = Flask(__name__)

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
 
if __name__ == "__main__":
    app.run(debug=True)   
