#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_flag = db.Column(db.Boolean())
    show = db.relationship('Show', backref=db.backref('venue', lazy=True))

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_flag = db.Column(db.Boolean())
    show = db.relationship('Show', backref=db.backref('artist', lazy=True))

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)

df_venues = pd.read_csv("venue_data.csv", delimiter=";")
df_artists = pd.read_csv("artist_data.csv", delimiter=";")
df_shows = pd.read_csv("show_data.csv", delimiter=";")


for v in df_venues.iterrows():
    v = v[1]
    venue = Venue(
        id = v["id"],
        name = v["name"],
        city = v["city"],
        state = v["state"],
        address = v["address"],
        phone = v["phone"],
        genres = v["genres"],
        image_link = v["image_link"],
        website_link = v["website_link"],
        facebook_link = v["facebook_link"],
        seeking_flag = v["seeking_flag"],
    )
    db.session.add(venue)


for a in df_artists.iterrows():
    a = a[1]
    artist = Artist(
        id = a["id"],
        name = a["name"],
        city = a["city"],
        state = a["state"],
        phone = a["phone"],
        genres = v["genres"],
        image_link = a["image_link"],
        website_link = a["website_link"],
        facebook_link = a["facebook_link"],
        seeking_flag = a["seeking_flag"],
    )
    db.session.add(artist)

for s in df_shows.iterrows():
    s = s[1]
    show = Show(
        id = s["id"],
        date = s["date"],
        venue_id = s["venue_id"],
        artist_id = s["artist_id"],
    )
    db.session.add(show)
    

db.session.commit()