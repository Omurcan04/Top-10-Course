from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

MYAPI = "4562f0e18c224b28e0b33f8540c04fe4"
MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

db = SQLAlchemy()
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies-last.db"
db.init_app(app)
Bootstrap(app)


class MyForm(FlaskForm):
    rating = StringField('Rating', validators=[DataRequired()])
    overview = StringField('Overview', validators=[DataRequired()])
    submit = SubmitField("Submit")

class AddForm(FlaskForm):
    movie_title = StringField("Movie Title",validators=[DataRequired()])
    submit = SubmitField("Submit")


class Movie(db.Model):
    id  = db.Column(db.Integer,primary_key=True)
    title =db.Column(db.String)
    year = db.Column(db.Integer)
    description = db.Column(db.String)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String)
    img_url = db.Column(db.String)

with app.app_context():
    db.create_all()

    # new_movie = Movie(
    #     id=1,
    #     title="Phone Booth",
    #     year=2002,
    #     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    #     rating=7.3,
    #     ranking=10,
    #     review="My favourite character was the caller.",
    #     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
    # )
    # db.session.add(new_movie)
    # db.session.commit()
@app.route("/")
def home():
    movies=Movie.query.order_by(Movie.rating).all()
    for i in range(len(movies)):
        movies[i].ranking = len(movies) - i
        db.session.commit()
    return render_template("index.html",movies = movies)


@app.route("/update",methods=["GET","POST"])
def update():
    myform = MyForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if myform.validate_on_submit():
        movie.rating = request.form.get("rating")
        movie.review = request.form.get("overview")
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("edit.html",form=myform,movie=movie)


@app.route("/delete")
def delete():

    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/add",methods=["GET","POST"])
def add():
    myform = AddForm()

    if myform.validate_on_submit():
        parameters = {
            "api_key":MYAPI,
            "query":request.form.get("movie_title")
        }
        response=requests.get("https://api.themoviedb.org/3/search/movie",params=parameters).json()
        data = response["results"]
        print(data)
        print(request.form.get("movie_title"))

        return render_template("select.html",data=data)
    return render_template("add.html",form=myform)


@app.route("/find",methods=["GET","POST"])
def find():
    movie_api_id = request.args.get("id")
    print(movie_api_id)
    if movie_api_id:
        parameters = {
            "api_key":MYAPI,
            "movie_id":int(movie_api_id),
            "language": "en-US"
        }
        response = requests.get(f"{MOVIE_DB_INFO_URL}/{movie_api_id}",params=parameters).json()
        print(response)
        new_Movie = Movie(
            title=response["title"],
            year=response["release_date"],
            description=response["overview"],
            rating=response["vote_average"],
            img_url=f'{MOVIE_DB_IMAGE_URL}{response["poster_path"]}'
        )

        db.session.add(new_Movie)
        db.session.commit()

        return redirect(url_for("update",id=new_Movie.id))



# @app.route("/select",methods=["GET","POST"])
# def select():
#
#
#     return render_template("select.html")


if __name__ == '__main__':
    app.run(debug=True)
