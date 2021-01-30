#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
  Flask,
  render_template,
  request,
  Response,
  flash,
  redirect,
  url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import  Migrate
from models import db, Venue, Artist, Shows
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database


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
  venues = Venue.query.all()
  data = []
  for area in Venue.query.distinct(Venue.city, Venue.state).all():
    data.append({
      'city': area.city,
      'state': area.state,
      'venues':[{
        'id': venue.id,
        'name': venue.name,
      } for venue in venues if
                 venue.city == area.city and venue.state == area.state]
    })
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term=request.form.get('search_term', '')
  venueQuery = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  response = {}
  response['count'] = len(venueQuery)
  response['data']=[]
  for venue in venueQuery:
    venue_data = {
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': len(list(filter(lambda show: show.start_time> datetime.now(), venue.shows)))
    }
    response['data'].append(venue_data)
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  upcoming_shows = db.session.query(Artist,Shows).join(Shows).join(Venue).filter(Shows.venue_id == venue_id, Shows.artist_id == Artist.id, Shows.start_time > datetime.now()).all()
  past_shows = db.session.query(Artist, Shows).join(Shows).join(Venue).filter(Shows.venue_id == venue_id, Shows.artist_id == Artist.id, Shows.start_time < datetime.now()).all()  
  data = Venue.query.get(venue_id)
  
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue_data={
    "id": data.id,
    "name": data.name,
    "genres": data.genres,
    "address": data.address,
    "city": data.city,
    "state": data.state,
    "phone": data.phone,
    "website": data.website,
    "facebook_link": data.facebook_link,
    "seeking_talent": data.seeking_talent,
    "seeking_description": data.seeking_description,
    "image_link": data.image_link,
    "past_shows": [{
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      'start_time': shows.start_time.strftime("%m/%d/%Y, %H:%M")
    }for artist, shows in past_shows if shows.venue_id == data.id],
    "upcoming_shows": [{
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': shows.start_time.strftime("%m/%d/%Y, %H:%M")
      }for artist, shows in upcoming_shows if shows.venue_id == data.id],
    "past_shows_count": len(upcoming_shows),
    "upcoming_shows_count": len(past_shows)
  }
  return render_template('pages/show_venue.html', venue=venue_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  try:
    new_venue = Venue()
    form.populate_obj(new_venue)
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  delete_data = Venue.query.get(venue_id)
  db.session.delete(delete_data)
  de.session.commit()
  
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data = []
  for artist in artists:
    data.append({
      'id':artist.id,
      'name':artist.name,
      })
  # TODO: replace with real data returned from querying the database
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term=request.form.get('search_term','')
  artistQuery=db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  response = {}
  response['count'] = len(artistQuery)
  response['data'] = []
  for artist in artistQuery:
    artist_data = {
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': len(list(filter(lambda artist: artist.start_time > datetime.now(), artist.shows)))
    }
    response['data'].append(artist_data)
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  upcoming_shows = db.session.query(Venue, Shows).join(Shows).filter(Shows.artist_id == artist_id, Shows.venue_id == Venue.id, Shows.start_time > datetime.now()).all()
  past_shows = db.session.query(Venue, Shows).join(Shows).filter(Shows.artist_id == artist_id, Shows.venue_id == Venue.id, Shows.start_time < datetime.now()).all()  
  data = Artist.query.get(artist_id)
  artist_data={
    "id": data.id,
    "name": data.name,
    "genres": data.genres,
    "city": data.city,
    "state": data.city,
    "phone": data.phone,
    "website": data.website,
    "facebook_link": data.facebook_link,
    "seeking_venue": data.seeking_venue,
    "seeking_description": data.seeking_description,
    "image_link": data.image_link,
    "past_shows": [{
      "venue_id": shows.venue_id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": shows.start_time.strftime("%m/%d/%Y, %H:%M")
    }for venue, shows in past_shows if shows.artist_id == data.id],
    "upcoming_shows": [{
      'venue_id': shows.venue_id,
      'venue_name': venue.name,
      'venue_image_link': venue.image_link,
      'start_time': shows.start_time.strftime("%m/%d/%Y, %H:%M")
      }for venue, shows in upcoming_shows if shows.artist_id == data.id],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  
  return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist =Artist.query.first_or_404(artist_id)
  form = ArtistForm(obj=artist)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
      edit_artist =Artist.query.get(artist_id)
      edit_artist_name = request.form.get('name', ''),
      edit_artist_genres = request.form.get('genres', ''),
      edit_artist_city = request.form.get('city', ''),
      edit_artist_state = request.form.get('state', ''),
      edit_artist_phone = request.form.get('phone', ''),
      edit_artist_facebook_link = request.form.get('facebook_link', '')
      db.session.commit()
      flash('Artist ' + request.form('name') + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form('name') + ' could not be listed.')
  finally:
    db.session.close
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue= Venue.query.first_or_404(venue_id)
  form = VenueForm(obj=venue)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
      edit_venue =Artist.query.get(artist_id)
      edit_venue_name = request.form.get('name', ''),
      edit_venue_genres = request.form.get('genres', ''),
      edit_venue_city = request.form.get('city', ''),
      edit_venue_state = request.form.get('state', ''),
      edit_venue_phone = request.form.get('phone', ''),
      edit_venue_facebook_link = request.form.get('facebook_link', '')
      db.session.commit()
      flash('Venue ' + request.form('name') + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form('name') + ' could not be listed.')
  finally:
    db.session.close
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
  form = ArtistForm(request.form)
  try:
    new_artist = Artist()
    form.populate_obj(new_artist)
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  getShows = db.session.query(Shows).all()
  data = [{
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    }for show in getShows]
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)
    try:
      new_show = Shows()
      form.populate_obj(new_show)
      db.session.add(new_show)
      db.session.commit()
      flash('Show was successfully listed!')
    except:
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
