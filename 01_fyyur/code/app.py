#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from configparser import ConfigParser
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
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
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)
    shows = db.relationship("Show", backref='venue', cascade='all, delete-orphan')
    
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)
    dates = db.Column(db.String)    
    # added extra task requirment availble dates
    shows = db.relationship("Show", backref='artist', cascade='all, delete-orphan')

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime)
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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  # SQLAlchemy queries 
  areas = Venue.query.distinct(Venue.city, Venue.state).all()
  venues = Venue.query.all()
  recent_venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
  upcoming_shows = Show.query.with_entities(Show.venue_id, func.count(Show.venue_id)).filter(Show.start_time >= func.now()).group_by(Show.venue_id).all()

  # structring queried data to desired schema
  data = []
  for area in areas:
    venues_list = []
    for venue in venues:
      if venue.city == area.city:
        # looping on aggregated shows to find the desired show count
        num_upcoming_shows = next((item for item in upcoming_shows if item.venue_id == venue.id), (venue.id,0))
        venue_dictionary = {
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": num_upcoming_shows[1]
        }
        venues_list.append(venue_dictionary)
    data_dictionary={
      "city": area.city,
      "state": area.state,
      "venues": venues_list
    }
    data.append(data_dictionary)
  return render_template('pages/venues.html', areas=data, recent_venues=recent_venues);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  # SQLAlchemy queries
  search_term = request.form.get('search_term', '')
  if ", " in search_term:
    if search_term[-2:] in state_list:
      search_result = Venue.query.filter(Venue.city+", "+Venue.state == search_term).all()
  else:
    search_result = Venue.query.filter(Venue.name.ilike("%{}%".format(search_term))).all()  
  upcoming_shows = Show.query.with_entities(Show.venue_id, func.count(Show.venue_id)).filter(Show.start_time >= func.now()).group_by(Show.venue_id).all()

  # structring queried data to desired schema
  count = len(search_result) # count the number of upcomig shows by returning the length of the returned list
  data = []  
  for result in search_result:
    data_dictionary={
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": next((item for item in upcoming_shows if item.venue_id == result.id), (result.id,0))[1],
    }  
    data.append(data_dictionary)
  response={
    "count": count,
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  # SQLAlchemy queries
  venue = Venue.query.get(venue_id)
  shows = Show.query.filter(Show.venue_id==venue.id).all()
  # past and upcoming shows count aggregating
  past_shows = Show.query.with_entities(Show.venue_id, func.count(Show.venue_id)).filter(Show.start_time <= func.now()).filter(Show.venue_id==venue.id).group_by(Show.venue_id).all()  
  upcoming_shows = Show.query.with_entities(Show.venue_id, func.count(Show.venue_id)).filter(Show.start_time > func.now()).filter(Show.venue_id==venue.id).group_by(Show.venue_id).all()
  # for show in list if show not found return zero
  past_shows_count = next((show for show in past_shows if show[0] is not 0), (venue.id,0)) 
  upcoming_shows_count = next((show for show in upcoming_shows if show[0] is not 0), (venue.id,0))

  # structring queried data to desired schema
  past_shows_list = []  
  upcoming_shows_list = []  
  for show in shows:
    if show.start_time <= datetime.now():
      artist = show.artist
      past_shows_dict= {
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.start_time)}
      past_shows_list.append(past_shows_dict)
    elif show.start_time > datetime.now():
      artist = show.artist
      upcoming_shows_dict= {
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.start_time)}
      upcoming_shows_list.append(upcoming_shows_dict)          
  data={
  "id": venue.id,
  "name": venue.name,
  "genres": venue.genres.split(","),
  "address": venue.address,
  "city": venue.city,
  "state": venue.state,
  "phone": venue.phone,
  "website": venue.website,
  "facebook_link": venue.facebook_link,
  "seeking_talent": venue.seeking_talent,
  "seeking_description": venue.seeking_description,
  "image_link": venue.image_link,
  "past_shows": past_shows_list,
  "upcoming_shows": upcoming_shows_list,
  "past_shows_count": past_shows_count[1],
  "upcoming_shows_count": upcoming_shows_count[1],
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  req = request.form
  # db insertion   
  try:
    new_venue = Venue(
      name=req['name'], 
      genres=req['genres'],
      address=req['address'], 
      city=req['city'], 
      state=req['state'], 
      phone=req['phone'], 
      facebook_link=req['facebook_link'])
    db.session.add(new_venue)
    db.session.commit()  
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  finally:
    db.session.close()   
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  print('test')
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    deleted_venue = Venue.query.get(venue_id)
    db.session.delete(deleted_venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:    
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # SQLAlchemy queries
  data = Artist.query.with_entities(Artist.id, Artist.name).all()
  recent_artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()
  # for this part artist model is the same as desired schema
  return render_template('pages/artists.html', artists=data, recent_artists=recent_artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  # SQLAlchemy queries
  search_term = request.form.get('search_term', '')
  if ", " in search_term:
    if search_term[-2:] in state_list:
      search_result = Artist.query.filter(Artist.city+", "+Artist.state == search_term).all()
  else:
    search_result = Artist.query.filter(Artist.name.ilike("%{}%".format(search_term))).all()  
  upcoming_shows = Show.query.with_entities(Show.artist_id, func.count(Show.artist_id)).filter(Show.start_time >= func.now()).group_by(Show.artist_id).all()

  # structring queried data to desired schema
  count = len(search_result) # count the number of upcomig shows by returning the length of the returned list
  data = []  
  for result in search_result:
    data_dictionary={
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": next((item for item in upcoming_shows if item.artist_id == result.id), (result.id,0))[1],
    }
    data.append(data_dictionary)
  response={
    "count": count,
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  # SQLAchemy queries
  artist = Artist.query.get(artist_id)
  shows = Show.query.filter(Show.artist_id==artist.id).all()
  # past and upcoming shows count aggregating
  past_shows = Show.query.with_entities(Show.artist_id, func.count(Show.artist_id)).filter(Show.start_time <= func.now()).filter(Show.artist_id==artist.id).group_by(Show.artist_id).all()  
  upcoming_shows = Show.query.with_entities(Show.artist_id, func.count(Show.artist_id)).filter(Show.start_time > func.now()).filter(Show.artist_id==artist.id).group_by(Show.artist_id).all()
  # for show in list if show not found return zero
  past_shows_count = next((show for show in past_shows if show[0] is not 0), (artist.id,0)) 
  upcoming_shows_count = next((show for show in upcoming_shows if show[0] is not 0), (artist.id,0))

  # structring queried data to desired schema
  past_shows_list = []  
  upcoming_shows_list = []  
  for show in shows:
    if show.start_time < datetime.now():
      venue = show.venue
      past_shows_dict= {
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(show.start_time)}
      past_shows_list.append(past_shows_dict)
    elif show.start_time >= datetime.now():
      venue = show.venue
      upcoming_shows_dict= {
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(show.start_time)}
      upcoming_shows_list.append(upcoming_shows_dict)          
  data={
  "id": artist.id,
  "name": artist.name,
  "genres": artist.genres.split(","),
  "city": artist.city,
  "state": artist.state,
  "phone": artist.phone,
  "website": artist.website,
  "facebook_link": artist.facebook_link,
  "seeking_venue": artist.seeking_venue,
  "seeking_description": artist.seeking_description,
  "image_link": artist.image_link,
  "past_shows": past_shows_list,
  "upcoming_shows": upcoming_shows_list,
  "past_shows_count": past_shows_count[1],
  "upcoming_shows_count": upcoming_shows_count[1],
  }
  return render_template('pages/show_artist.html', artist=data)
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  req = request.form
  try:
    artist = Artist.query.get(artist_id)
    artist.name=req['name'] 
    artist.genres=req['genres']
    artist.city=req['city'] 
    artist.state=req['state'] 
    artist.phone=req['phone'] 
    artist.facebook_link=req['facebook_link']
    db.session.commit()  
    flash('Artist ' + request.form['name'] + ' was successfully edited!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist could not be edited.')
    print(sys.exc_info())
  finally:
    db.session.close()  
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  req = request.form
  try:
    venue = Venue.query.get(venue_id)
    venue.name=req['name'] 
    venue.genres=req['genres']
    venue.address=req['address']
    venue.city=req['city'] 
    venue.state=req['state'] 
    venue.phone=req['phone'] 
    venue.facebook_link=req['facebook_link']
    db.session.commit()  
    flash('Venue ' + request.form['name'] + ' was successfully edited!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue could not be edited.')
    print(sys.exc_info())
  finally:
    db.session.close()  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  req = request.form
  try:
    new_artist = Artist(
      name=req['name'], 
      genres=req['genres'], 
      city=req['city'], 
      state=req['state'], 
      phone=req['phone'], 
      facebook_link=req['facebook_link'],
      dates=req['availble_dates'])
    db.session.add(new_artist)
    db.session.commit()  
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist could not be listed.')
  finally:
    db.session.close()   
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # SQLAchemy queires
  shows = Show.query.all()

  # structring queried data to desired schema
  data = []
  for show in shows:
    data_dictionary= {
    "venue_id": show.venue.id,
    "venue_name": show.venue.name,
    "artist_id": show.artist.id,
    "artist_name": show.artist.name,
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": str(show.start_time)
    }
    data.append(data_dictionary)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  req = request.form
  try:
    artist = Artist.query.get(req['artist_id'])
    if str(req['start_time']) in artist.dates.split(','):
      new_show = Show(
        venue_id = req['venue_id'],
        artist_id = req['artist_id'],
        start_time = req['start_time'])
      db.session.add(new_show)
      db.session.commit()  
      flash('Show was successfully listed!')
    else:
      flash('Date not availble please choose another one')  
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close() 
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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

# list of US states for search check
state_list =['AL',
            'AK',
            'AZ',
            'AR',
            'CA',
            'CO',
            'CT',
            'DE',
            'DC',
            'FL',
            'GA',
            'HI',
            'ID',
            'IL',
            'IN',
            'IA',
            'KS',
            'KY',
            'LA',
            'ME',
            'MT',
            'NE',
            'NV',
            'NH',
            'NJ',
            'NM',
            'NY',
            'NC',
            'ND',
            'OH',
            'OK',
            'OR',
            'MD',
            'MA',
            'MI',
            'MN',
            'MS',
            'MO',
            'PA',
            'RI',
            'SC',
            'SD',
            'TN',
            'TX',
            'UT',
            'VT',
            'VA',
            'WA',
            'WV',
            'WI',
            'WY']