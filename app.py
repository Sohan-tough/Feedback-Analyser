# from flask import Flask, render_template, request
# from feedback_classifier import is_abusive

# app = Flask(__name__)

# @app.route("/", methods=["GET", "POST"])
# def index():
#     result = None
#     if request.method == "POST":
#         feedback = request.form["feedback"]
#         result = is_abusive(feedback)
#     return render_template("index.html", result=result)

# if __name__ == "__main__":
#     app.run(debug=True)


from flask import Flask, render_template, request, jsonify
from feedback_classifier import is_abusive

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/check_feedback", methods=["POST"])
def check_feedback():
    data = request.get_json()
    text = data.get("text", "")
    result = is_abusive(text)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
