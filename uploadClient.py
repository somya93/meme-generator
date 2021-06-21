from flask import Flask, render_template, request

app = Flask(__name__)

#
# @app.route("/generatememe", methods=["POST"])
# def generate_meme():
#     uri = request.form["image_uri"]


@app.route("/", methods=["GET"])
def load_form():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()
