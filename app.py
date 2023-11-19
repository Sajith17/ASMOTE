from flask import Flask, render_template, url_for, request, redirect, session
from prediction import predict_triplets

app = Flask(__name__)
app.secret_key = "0123456789"


@app.route("/", methods=["POST", "GET"])
def main():
    if request.method == "POST":
        text = request.form["text-input"]
        if text:
            session["text"] = text
            session["triplets"] = predict_triplets(text)
            return redirect(url_for("submit"))
    return render_template("main.html")


@app.route("/submit", methods=["POST", "GET"])
def submit():
    if request.method == "POST":
        return redirect(url_for("main"))
    else:
        text = session["text"]
        triplets = session["triplets"]
        if triplets:
            return render_template("main.html", text=text, triplets=triplets)
        else:
            return redirect(url_for("main"))


if __name__ == "__main__":
    app.run(debug=True)
