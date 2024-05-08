from flask import Flask, Response, render_template
from constants import KEYWORDS, PKEYWORDS
from scrape import scrape
import json

# when the app first starts, get latest data
json_data = scrape(False)

data = json.loads(json_data)

ages = []
total = 0
dui = 0
p = 0
for inmate in data["inmates"]:
    ages.append(inmate["age"])
    for offense in inmate["offenses"]:
        if any(keyword in offense for keyword in KEYWORDS):
            dui = dui + 1
            continue
        if any (pkeyword in offense for pkeyword in PKEYWORDS):
            p = p + 1
            continue
    total = total + 1
    
average_age = sum(ages) / len(ages) if ages else 0
drunk_driving_arrests_percent = ((dui / total) * 100)
last_updated = data["last_updated"]
p_percent = ((p / total) * 100)

app = Flask(__name__)

@app.route("/", methods=['GET'])
def index():
    return render_template("index.html", avg=average_age, dc=drunk_driving_arrests_percent, pp=p_percent, lu=last_updated)

@app.route("/api/", methods=['GET'])
def api():
    return render_template("api.html")

@app.route('/api/latest.json', methods=['GET'])
def scrape_route():
    return Response(json_data, mimetype='text/json')

@app.route('/api/stats.json', methods=['GET'])
def duiroute():

    return_object = {
        "last_updated": str(last_updated),
        "age_average": float(average_age),
        "drunk_driving_percentage": float(drunk_driving_arrests_percent),
        "predator_percentage": float(p_percent)
    }

    json_return_object = json.dumps(return_object)
    
    return Response(json_return_object, mimetype='text/json')

if __name__ == '__main__':
    app.run("127.0.0.1", 80, True)