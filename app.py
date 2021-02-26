#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import datetime
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.recaptcha import validators
from sqlalchemy.sql import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form, FlaskForm
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
    seeking_description = db.Column(db.String(500))
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
    seeking_description = db.Column(db.String(500))
    show = db.relationship('Show', backref=db.backref('artist', lazy=True))

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)




#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  cities = [(v.city, v.state) for v in Venue.query.distinct("city").all()]
  data = []
  for c in cities:
    entry = {}
    V = Venue.query.filter_by(city=c[0]).all()
    entry["city"] = c[0]
    entry["state"] = c[1]
    entry["venues"] = [{
        "id": v.id,
        "name": v.name,
        "num_upcoming_shows": len(v.show) 
      } for v in V
    ]
    data.append(entry)

  return render_template('pages/venues.html', areas=data)



@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term')
  V = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  response = {
    "count": len(V),
    "data": [{
      "id": v.id,
      "name": v.name,
       "num_upcoming_shows": len(v.show) 
    } for v in V
    ]
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))



@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  v = Venue.query.get(venue_id)
  S = Show.query.filter_by(venue_id=v.id)
  S_b = [s for s in S if s.date < datetime.now()]
  S_a = [s for s in S if s.date > datetime.now()]

  data = {
    "id": v.id,
    "name": v.name,
    "genres": v.genres.split(","),
    "address": v.address,
    "city": v.city,
    "state": v.state,
    "phone": v.phone,
    "website": v.website_link,
    "facebook_link": v.facebook_link,
    "seeking_talent": v.seeking_flag,
    "seeking_description": v.seeking_description,
    "image_link": v.image_link,

    "past_shows": [{
      "artist_id": s.artist.id,
      "artist_name": s.artist.name,
      "artist_image_link": s.artist.image_link,
      "start_time": str(s.date)
    } for s in S_b],

    "upcoming_shows": [{
      "artist_id": s.artist.id,
      "artist_name": s.artist.name,
      "artist_image_link": s.artist.image_link,
      "start_time": str(s.date)
    } for s in S_a],
    "past_shows_count": len(S_b),
    "upcoming_shows_count": len(S_a),
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  try:
    a_venue = Venue(
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      address = request.form['address'],
      phone = request.form['phone'],
      genres = ", ".join(request.form.getlist('genres')),
      facebook_link = request.form['facebook_link'],
      seeking_flag = request.form['seeking_flag'] == "y",
      seeking_description = request.form['seeking_description'],
    )
    
    db.session.add(a_venue)
    db.session.commit()   
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. Venue ' + a_venue.name + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  
  data = [{"id": a.id, "name": a.name} for a in Artist.query.all()]

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term = request.form.get('search_term')
  A = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  response = {
    "count": len(A),
    "data": [{
      "id": a.id,
      "name": a.name,
      "num_upcoming_shows": len(a.show) 
    } for a in A
    ]
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    
  a = Artist.query.get(artist_id)
  S = Show.query.filter_by(artist_id=a.id)
  S_b = [s for s in S if s.date < datetime.now()]
  S_a = [s for s in S if s.date > datetime.now()]

  data={
    "id": a.id,
    "name": a.name,
    "genres": a.genres.split(","),
    "city": a.city,
    "state": a.state,
    "phone": a.phone,
    "website": a.website_link,
    "facebook_link": a.facebook_link,
    "seeking_venue": a.seeking_flag,
    "seeking_description": a.seeking_description,
    "image_link": a.image_link,

    "past_shows": [{
      "venue_id": s.venue.id,
      "venue_name": s.venue.name,
      "venue_image_link": s.venue.image_link,
      "start_time": str(s.date)
    } for s in S_b],

    "upcoming_shows": [{
      "venue_id": s.venue.id,
      "venue_name": s.venue.name,
      "venue_image_link": s.venue.image_link,
      "start_time": str(s.date)
    } for s in S_a],
    "past_shows_count": len(S_b),
    "upcoming_shows_count": len(S_a),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes




  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  try:
    an_artist = Artist(
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      phone = request.form['phone'],
      genres = ", ".join(request.form.getlist('genres')),
      facebook_link = request.form['facebook_link'],
      seeking_flag = request.form['seeking_flag'] == "y",
      seeking_description = request.form['seeking_description'],
    )
    
    db.session.add(an_artist)
    db.session.commit()   
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. Artist ' + an_artist.name + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = [
    {
      "venue_id": s.venue_id, 
      "artist_id": s.artist_id,
      "start_time": str(s.date),
      "venue_name": s.venue.name,
      "artist_name": s.artist.name,
      "artist_image_link": s.artist.image_link,

    } for s in Show.query.all()]

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():


  try:
    a_show = Show(
      venue_id = request.form['venue_id'],
      artist_id = request.form['artist_id'],
      date = request.form['start_time'],
    )
    
    db.session.add(a_show)
    db.session.commit()   
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except Exception as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
