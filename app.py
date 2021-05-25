import random
import string

from flask import Flask, abort, redirect, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///url_shortener.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class URLMapping(db.Model):
    __tablename__ = "urlmapping"

    id = db.Column(db.String, primary_key=True)
    target = db.Column(db.String, nullable=False)

    def __init__(self, id_, target):
        self.id = id_
        self.target = target

    def __str__(self):
        return f"{self.id} ({self.target})"


@app.route("/<string:id_>", methods=["GET"])
def rd(id_):
    if id_ == "new":
        abort(405)
    else:
        urlmapping = URLMapping.query.filter_by(id=id_).first()
        if urlmapping:
            return redirect(urlmapping.target)
        else:
            abort(404)


@app.route("/new", methods=["POST"])
def create_new():
    target = request.form["target"]
    if not target.startswith("http://") and not target.startswith("https://"):
        target = f"http://{target}"
    attempt_num = 0
    while True:
        try:
            try:
                id_ = request.form["id"]
                id_provided = True
            except KeyError:
                id_ = ''.join(
                    [random.choice(string.ascii_letters + string.digits + "-_") for _ in range(8)])
                id_provided = False
            db.session.add(URLMapping(id_, target))
            db.session.commit()
            return id_
        except IntegrityError:
            db.session.rollback()
            attempt_num += 1
            if id_provided or attempt_num == 3:
                abort(409)


if __name__ == "__main__":
    db.create_all()
    app.run()
