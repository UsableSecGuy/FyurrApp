#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
#if module dateutil or six doesn't work run 'pip install --ignore-installed six' in terminal
import dateutil.parser
import datetime
import babel
from flask import Flask, abort, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from models import Artist, Venue, Show
#usgnote: import Migrate library
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database

#usgnote: instantiate migration
migrate = Migrate(app, db)

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


  #find distinct venue locations
  areas = Venue.query.distinct('city','state').order_by('state').all()

  results = []
  for area in areas:
      #get venue info
      venues= Venue.query.filter_by(city=area.city, state=area.state)
      venue_list=[]
      for venue in venues:
          #insert show loop here
          venue_list.append({"id":venue.id,
          "name":venue.name,
          })
      results.append({"city":area.city , "state":area.state , "venues":venue_list})

  return render_template('pages/venues.html', areas=results);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term=request.form.get('search_term', '')

  #use ilike to make search_term lowercase
  venue_results = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()

  results = []
  for venue_result in venue_results:

      results.append({
      "id": venue_result.id,
      "name": venue_result.name,
      "num_upcoming_shows": Show.query.filter(Show.venue_id==venue_result.id, Show.start_time > datetime.now()).count()
      })


  response={
  "count": len(venue_results),
  "data": results
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  #query venue by id
  venue = Venue.query.filter_by(id=venue_id).all()[0]

  past_shows = []
  upcoming_shows = []
  shows = Show.query.filter_by(venue_id=venue_id).join(Artist, Show.artist_id == Artist.id).all()
  for show in shows:
      venue_show = {"artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
      }

      current_date = datetime.now()

      if (current_date < show.start_time):
          #make this an upcoming show
          upcoming_shows.append(venue_show)
      else:
          #make this a past show
          past_shows.append(venue_show)

  #set data to be returned
  data = {
  "id": venue.id,
  "name": venue.name,
  "genres": venue.genres,
  "address": venue.address,
  "city": venue.city,
  "state": venue.state,
  "phone": venue.phone,
  "image_link": venue.image_link,
  "website": venue.website,
  "facebook_link": venue.facebook_link,
  "seeking_talent": venue.seeking_talent,
  "seeking_description": venue.seeking_description,
  "website": venue.website,
  "past_shows":past_shows,
  "upcoming_shows": upcoming_shows,
  "past_shows_count": len(past_shows),
  "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

#serve the form
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

#create new record in database so use post
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
    error = False
    try:

        form = VenueForm(request.form)

        venue = Venue(
        name = form.name.data, city = form.city.data,
        state = form.state.data, address = form.address.data,
        phone = form.phone.data,
        genres = form.genres.data,
        facebook_link = form.facebook_link.data,
        image_link = form.image_link.data
        )

        db.session.add(venue)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

    else:
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')


    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  error = False
  try:
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()

  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      # TODO: on unsuccessful db delete, flash an error instead.
      flash('An error occurred. Venue could not be deleted.')

  else:
      # on successful db delete, flash success
      flash('Venue was successfully deleted!')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  results = []
  artists_list = Artist.query.all()
  for artist in artists_list:
      results.append({"id": artist.id, "name":artist.name})

  return render_template('pages/artists.html', artists=results)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term=request.form.get('search_term', '')

  #use ilike to make search_term lowercase
  artist_results = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()

  results = []
  for artist_result in artist_results:

      results.append({
      "id": artist_result.id,
      "name": artist_result.name,
      "num_upcoming_shows": Show.query.filter(Show.artist_id==artist_result.id, Show.start_time > datetime.now()).count()
      })

  response={
  "count": len(artist_results),
  "data": results
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given artist_id
  # TODO: replace with real artist data from the venues table, using venue_id

  #query artist by id

  artist = Artist.query.filter_by(id=artist_id).all()[0]

  past_shows = []
  upcoming_shows = []
  shows = Show.query.filter_by(artist_id=artist_id).join(Venue, Show.venue_id == Venue.id).all()
  for show in shows:
      artist_show = {"venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
      }

      current_date = datetime.now()

      if (current_date < show.start_time):
          #make this an upcoming show
          upcoming_shows.append(artist_show)
      else:
          #make this a past show
          past_shows.append(artist_show)

  #set data to be returned
  data = {
  "id": artist.id,
  "name": artist.name,
  "genres": artist.genres,
  "city": artist.city,
  "state": artist.state,
  "phone": artist.phone,
  "seeking_venue": artist.seeking_venue,
  "image_link": artist.image_link,
  "facebook_link": artist.facebook_link,
  "seeking_description": artist.seeking_description,
  "website": artist.website,
  "past_shows":past_shows,
  "upcoming_shows": upcoming_shows,
  "past_shows_count": len(past_shows),
  "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  fromDB=show_artist(artist_id)
  artist={
    "id": fromDB.id,
    "name": fromDB.artist,
    "genres": fromDB.genres,
    "city": fromDB.city,
    "state": fromDB.state,
    "phone": fromDB.phone,
    "website": fromDB.website,
    "facebook_link": fromDB.facebook_link,
    "seeking_venue": fromDB.seeking_venue,
    "seeking_description": fromDB.seeking_description,
    "image_link": fromDB.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  error = False
  try:

      #get results from edit form
      form = ArtistForm(request.form)

      #pull for database to change
      fromDB = Artist.query.get(artist_id)

      fromDB.name = form.name.data
      fromDB.city = form.city.data
      fromDB.state = form.state.data
      fromDB.phone = form.phone.data
      fromDB.genres = form.genres.data,
      fromDB.facebook_link = form.facebook_link.data,
      fromDB.image_link = form.image_link.data

      db.session.commit()

  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      # TODO: on unsuccessful db update, flash an error instead.

      flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')

  else:
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully updated!')


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  fromDB=show_venue(venue_id)
  venue={
  "id": fromDB.id,
  "name": fromDB.artist,
  "genres": fromDB.genres,
  "address": fromDB.address,
  "city": fromDB.city,
  "state": fromDB.state,
  "phone": fromDB.phone,
  "website": fromDB.website,
  "facebook_link": fromDB.facebook_link,
  "seeking_talent": fromDB.seeking_talent,
  "seeking_description": fromDB.seeking_description,
  "image_link": fromDB.image_link
  }

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  error = False
  try:

      #get results from edit form
      form = VenueForm(request.form)

      #pull for database to change
      fromDB = Venue.query.get(venue_id)

      fromDB.name = form.name.data
      fromDB.city = form.city.data
      fromDB.state = form.state.data
      fromDB.phone = form.phone.data
      fromDB.genres = form.genres.data,
      fromDB.facebook_link = form.facebook_link.data,
      fromDB.image_link = form.image_link.data

      db.session.commit()

  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      # TODO: on unsuccessful db update, flash an error instead.

      flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')

  else:
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully updated!')

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
  # TODO: insert form data as a new Artist record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:

      form = ArtistForm(request.form)

      artist = Artist(
      name = form.name.data, city = form.city.data,
      state = form.state.data, phone = form.phone.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      image_link = form.image_link.data
      )

      db.session.add(artist)
      db.session.commit()

  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

  else:
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')


  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.


  shows=Show.query.join(Venue, Show.venue_id == Venue.id).join(Artist, Show.artist_id == Artist.id).all()
  results = []
  for show in shows:

      results.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": format_datetime(str(show.start_time), format='full')
      })

  return render_template('pages/shows.html', shows=results)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Artist record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # artist id 1 ; venue id 19
  error = False
  try:

      form = ShowForm(request.form)

      show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data
      )

      db.session.add(show)
      db.session.commit()

  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('An error occurred. Show could not be listed.')

  else:
      # on successful db insert, flash success
      flash('Show was successfully listed!')


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
