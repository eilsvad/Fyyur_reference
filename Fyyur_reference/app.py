#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys, datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from sqlalchemy import func, desc   # desc is for descending order of venues & artists
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# TODO: connect to a local postgresql database

# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # moved to config.py 

db = SQLAlchemy(app)

migrate = Migrate(app, db)  # Instantiate to start using migrate commands in our application for database schema changes

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):          # columns referred from /show_venue/<venue-id> route
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)   # not null added as it is mandatorily required
    genres = db.Column(db.ARRAY(db.String)) # array of string for genres
    address = db.Column(db.String(120))
    city = db.Column(db.String(120), nullable = False)  # not null added as it is mandatorily required
    state = db.Column(db.String(120), nullable = False) # not null added as it is mandatorily required
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_talent_description = db.Column(db.String(200), default='')
    posting_date_venue = db.Column(db.DateTime, default = datetime.utcnow)
    shows_venues = db.relationship('Show', backref='venue', cascade='all, delete, delete-orphan', lazy=True)

    def __repr__(self):
        return f'<{self.id} , {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False) # not null added as it is mandatorily required
    genres = db.Column(db.ARRAY(db.String())) # array of string for genres
    city = db.Column(db.String(120), nullable = False)  # not null added as it is mandatorily required
    state = db.Column(db.String(120), nullable = False) # not null added as it is mandatorily required
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_venue_description = db.Column(db.String(200), default='')
    posting_date_artist = db.Column(db.DateTime, default = datetime.utcnow)
#    albums = db.Column(db.String)     # getting list of albums as a string
#    songs = db.Column(db.String)      # getting list of songs as a string
    albumsL = db.Column(db.ARRAY(db.String()))   # album as array of string
    songsL = db.Column(db.ARRAY(db.String()))   # songs as array of string
    shows_artists = db.relationship('Show', backref='artist', cascade='all, delete, delete-orphan', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):       # Instead of association_table, since Show is an entity in itself (can post a show), created a model
  __tablename__ = 'shows'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id', ondelete='CASCADE'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id', ondelete='CASCADE'), nullable=False)
  start_time = db.Column(db.DateTime, default = datetime.utcnow, nullable=False)
  __table_args__ = tuple([db.UniqueConstraint('artist_id', 'venue_id', 'start_time', name='_artist_venue_starttime_uc')]) # Unique constraint if someone tries to add same artist_id, venue_id and start_time

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
  recent_venues = Venue.query.order_by(desc(Venue.posting_date_venue)).limit(10).all()
  latest_posted_venues = []
  for venue in recent_venues:
    latest_posted_venues.append({
      'venue_id': venue.id,
      'venue_name': venue.name,
      'venue_posting_date': venue.posting_date_venue
    })

  recent_artists = Artist.query.order_by(desc(Artist.posting_date_artist)).limit(10).all()
  latest_posted_artists = []
  for artist in recent_artists:
    latest_posted_artists.append({
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_posting_date': artist.posting_date_artist
    })
  return render_template('pages/home.html', latest_posted_venues=latest_posted_venues, latest_posted_artists=latest_posted_artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  areas = db.session.query(func.count(Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all() # SQL equivalent: select count(id), city, state from venues group by city, state;
  data = []
  for area in areas:
    area_venue = Venue.query.filter_by(city=area.city, state=area.state).all()    # filter by city and state from each area
    venue_data = []  # data of venues in each area
    for venuelist in area_venue:
      venue_data.append({
        'id': venuelist.id,
        'name': venuelist.name,
        'num_shows': db.session.query(Show).filter(Show.venue_id==venuelist.id).filter(Show.start_time>datetime.now()).count()  # count total number of shows 'upcoming'
      })
    data.append({
      'city': area.city,
      'state': area.state,
      'venues': venue_data   # in venues.html the parameter name expected in return is 'venues'
    })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST', 'GET'])   # added GET otherwise "Method not allowed" error was coming
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  # target query -- select * from venues where lower(name) like lower('%hop%');

  search_term = request.form.get('search_term', '')
#  iCaseSearch = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all() OR newer better way to use f-strings as below
  searching_venue = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()    # ilike -> ignorecase; f' -> Literal string interpolation
  data = []

  if len(searching_venue) == 0:
    response={
    'count': 0,
    'data': data
    }

  else:
    for venues in searching_venue:
      data.append({
        'id': venues.id,
        'name': venues.name,
        'num_shows': db.session.query(Show).filter(Show.venue_id == venues.id).filter(Show.start_time>datetime.now()).count()
      })
      response={
        'count': len(searching_venue),  # total count.. we can use another db query Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).count() but it will mean 2 queries to db all() and count()
        'data': data
      }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  get_venue = Venue.query.get(venue_id)
  
  if not get_venue:
    return render_template('errors/404.html')

  past_shows_details = db.session.query(Show).join(Artist).filter(Show.venue_id == get_venue.id).filter(Show.start_time<datetime.now()) # past shows
  past_shows = []
  for p_shows in past_shows_details:
    past_shows.append({
      'artist_id': p_shows.artist_id,
      'artist_name': p_shows.artist.name,
      'artist_image_link': p_shows.artist.image_link,
      'start_time': p_shows.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  upcoming_shows_details =  db.session.query(Show).join(Artist).filter(Show.venue_id == get_venue.id).filter(Show.start_time>datetime.now()) # future shows
  upcoming_shows = []
  for u_shows in upcoming_shows_details:
    upcoming_shows.append({
      'artist_id': u_shows.artist_id,
      'artist_name': u_shows.artist.name,
      'artist_image_link': u_shows.artist.image_link,
      'start_time': u_shows.start_time.strftime('%Y-%m-%d %H:%M:%S')     
    })
  
  data = {
    'id': get_venue.id,
    'name': get_venue.name,
    'genres': get_venue.genres,
    'city': get_venue.city,
    'state': get_venue.state,
    'phone': get_venue.phone,
    'website': get_venue.website,
    'facebook_link': get_venue.facebook_link,
    'seeking_talent': get_venue.seeking_talent,
    'seeking_talent_description': get_venue.seeking_talent_description,
    'image_link': get_venue.image_link,
    'upcoming_shows': upcoming_shows,
    'past_shows': past_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
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
  form = VenueForm()
  if form.validate_on_submit():
    error=False
    try:
      name = request.form['name']           # get name from dictionary
      city = request.form['city']
      state = request.form['state']
      address = request.form['address']
      phone = request.form['phone']
      genres = request.form.getlist('genres')
      image_link = request.form['image_link']
      facebook_link = request.form['facebook_link']
      website = request.form['website']
      seeking_talent = True if 'seeking_talent' in request.form else False  # seeking_talent only present when checkbox is selected and is returned a string value "y". Converting to boolean.
      seeking_talent_description = request.form['seeking_talent_description']
      posting_date_venue = datetime.now()   # add a posting date time when new venue is created
      
      # addVenue DB Object
      addVenue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, image_link=image_link,facebook_link=facebook_link, website=website, seeking_talent=seeking_talent, seeking_talent_description=seeking_talent_description, posting_date_venue=posting_date_venue)
      db.session.add(addVenue)
      db.session.commit()

#      new_venue = db.session.query(Venue.id).filter_by(name=name).order_by(desc(Venue.posting_date_venue)).first()

    except:
      error=True
      db.session.rollback()
      print(sys.exc_info())
      
    finally:
      db.session.close()

      # on successful db insert, flash success else unsuccessful
    if error:
      flash('Venue ' + request.form['name'] + ' could\'nt be listed!')

    else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

    # return name + ',' + city + ',' + str(seeking_talent)          // For testing only

  else:
    flash('Venue ' + request.form['name'] + ' failed due to validation error!')    

#  return redirect(url_for('venues'))
  return redirect(url_for('index'))

@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  error = False
  try:
    get_venue = Venue.query.get(venue_id)
    db.session.delete(get_venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

# if error: 
#    flash(f'Venue ' + venue_id + ' could not be deleted.')
#  else:
#    flash(f'Venue ' + venue_id + ' was successfully deleted.')
  
  return jsonify({'success': True})
  #return redirect(url_for('index'))

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  #return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = Artist.query.all()   # get all artists in the table
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST', 'GET'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term', '')
  searching_artist = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()    # ilike -> ignorecase; f' -> Literal string interpolation
  data = []

  if len(searching_artist) == 0:    # if not matching string or other characters, it will reeturn Number = 0 and no data instead of error earlier
    response={
      'count': 0,
      'data': data
    }

  else:
    for artists in searching_artist:
      data.append({
        'id': artists.id,
        'name': artists.name,
        'num_shows': db.session.query(Show).filter(Show.artist_id == artists.id).filter(Show.start_time>datetime.now()).count()
      })
      response={
        'count': len(searching_artist),  # total count.. we can use another db query Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).count() but it will mean 2 queries to db all() and count()
        'data': data
      }

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  get_artist = Artist.query.get(artist_id)
  
  if not get_artist:
    return render_template('errors/404.html')

  past_shows_details = db.session.query(Show).join(Venue).filter(Show.artist_id == get_artist.id).filter(Show.start_time<datetime.now()) # past shows
  past_shows = []
  for p_shows in past_shows_details:
    past_shows.append({
      'venue_id': p_shows.venue_id,
      'venue_name': p_shows.venue.name,
      'venue_image_link': p_shows.venue.image_link,
      'start_time': p_shows.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  upcoming_shows_details =  db.session.query(Show).join(Venue).filter(Show.artist_id == get_artist.id).filter(Show.start_time>datetime.now()) # future shows
  upcoming_shows = []
  for u_shows in upcoming_shows_details:
    upcoming_shows.append({
      'venue_id': u_shows.venue_id,
      'venue_name': u_shows.venue.name,
      'venue_image_link': u_shows.venue.image_link,
      'start_time': u_shows.start_time.strftime('%Y-%m-%d %H:%M:%S')     
    })
  
  data = {
    'id': get_artist.id,
    'name': get_artist.name,
    'genres': get_artist.genres,
    'city': get_artist.city,
    'state': get_artist.state,
    'phone': get_artist.phone,
    'website': get_artist.website,
    'albums': get_artist.albumsL,    
    'songs': get_artist.songsL,
    'facebook_link': get_artist.facebook_link,
    'seeking_venue': get_artist.seeking_venue,
    'seeking_venue_description': get_artist.seeking_venue_description,
    'image_link': get_artist.image_link,
    'upcoming_shows': upcoming_shows,
    'past_shows': past_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }
#  return str(get_artist.genres)
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
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form = ArtistForm()
  if form.validate_on_submit():
    error=False
    try:
      name = request.form['name']           # get name from dictionary
      city = request.form['city']
      state = request.form['state']
      phone = request.form['phone']
      genres = request.form.getlist('genres')
      image_link = request.form['image_link']
      facebook_link = request.form['facebook_link']
      website = request.form['website']
      albumlist = request.form['albums']
      albumsL = [x.strip() for x in albumlist.split(',')]    # convert to array of strings
      songlist = request.form['songs']
      songsL = [y.strip() for y in songlist.split(',')]    # convert to array of strings
      seeking_venue = True if 'seeking_venue' in request.form else False  # seeking_venue only present when checkbox is selected and is returned a string value "y". Converting to boolean.
      seeking_venue_description = request.form['seeking_venue_description']
      posting_date_artist = datetime.now()   # add a posting date time when new artist is created
      # addArtist DB Object
      addArtist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, image_link=image_link,facebook_link=facebook_link, website=website, albumsL=albumsL, songsL=songsL ,seeking_venue=seeking_venue, seeking_venue_description=seeking_venue_description, posting_date_artist=posting_date_artist)
      db.session.add(addArtist)
      db.session.commit()

    except:
      error=True
      db.session.rollback()
      print(sys.exc_info())
      
    finally:
      db.session.close()

      # on successful db insert, flash success else unsuccessful
    if error:
      flash('Artist ' + request.form['name'] + ' could\'nt be listed!')

    else:
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  else:
    flash('Artist ' + request.form['name'] + ' failed due to validation error!')    

  return redirect(url_for('index'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  shows_artist_venue = db.session.query(Show).join(Artist).join(Venue).all()
#  didn't worked -> shows_artist_venue = db.session.query(Show.venue_id, Venue.name, Show.artist_id, Artist.name, Artist.image_link, Show.start_time.strftime('%Y-%m-%d %H:%M:%S')).join(Artist).join(Venue).all()
  # target --- select * from shows join artists on shows.artist_id = artists.id join venues on shows.venue_id = venues.id
  data = []
  for show in shows_artist_venue:
    data.append({
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create', methods=['GET'])
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  error=False
  try:
    artist_id = request.form['artist_id']           
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    # addArtist DB Object
    addShow = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(addShow)
    db.session.commit()

  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
    
  finally:
    db.session.close()

    # on successful db insert, flash success else unsuccessful
  if error:
    flash('Show could\'nt be listed!')

  else:
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
  
  return redirect(url_for('index'))
#  return render_template('pages/home.html')


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
