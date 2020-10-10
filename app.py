#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from datetime import datetime # Added this to calculate the current time
from forms import *
from wtforms import Form, validators

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# Added this because of the error: 'The CSRF token is missing.' (Reference: https://flask-wtf.readthedocs.io/en/v0.12/csrf.html)
csrf.init_app(app)
db = SQLAlchemy(app)

migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

"""
******************* Notes about the 'Venue' model *******************
1- The 'name, city, and state' attributes shouldn't be null (according to show_venue.html)
2- The 'seeking_talent, seeking_description, and website' should be added (according to show_venue.html)
3- The 'genre' attribute should be added (according to show_venue.html)
4- Since the 'genre' is a multivalued atribute, it should be in another model called 'Venues_Genres' (according to new_venue.html)
5- The 'Venue' model has a One-to-Many relationship with the 'Show' model.
"""
class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String())
    # This is to define the 'Venue' and 'Genre' relationship
    genres = db.relationship('Venues_Genres', backref='venue', lazy=True)
    # This is to define the 'Venue' and 'Show' relationship
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
      return f'<Venue ID: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}>'

    # This function finds the number of the upcoming shows for a venue
    def upcoming_shows_number(self):
      # Get all the shows for the venue by its ID
      shows = Show.query.filter_by(venue_id=self.id).all()
      # Get the current time
      today = datetime.now()
      # Initialize the number of shows to zero for each venue
      num_shows = 0
      # Loop all the venue's shows
      for s in shows:
        # Check if the show is upcoming
        if s.start_time >= today:
          # Increase the number of shows
          num_shows = num_shows + 1
      return num_shows

    # This function finds the number of the past shows for a venue
    def past_shows_number(self):
      # Get all the shows for the venue by its ID
      shows = Show.query.filter_by(venue_id=self.id).all()
      # Get the current time
      today = datetime.now()
      # Initialize the number of shows to zero for each venue
      num_shows = 0
      # Loop all the venue's shows
      for s in shows:
        # Check if the show is upcoming
        if s.start_time < today:
          # Increase the number of shows
          num_shows = num_shows + 1
      return num_shows
      
    # This function finds all the upcoming shows for a venue
    def upcoming_shows(self):
      # Get all the shows for the venue by its ID
      shows = Show.query.filter_by(venue_id=self.id).all()
      # Get the current time
      today = datetime.now()
      # Initialize the shows list
      shows_list = []
      # Loop all the venue's shows
      for s in shows:
        # Check if the show is upcoming
        if s.start_time >= today:
          # Add the show in the shows list
          shows_list.append(s)
      return shows_list

    # This function finds all the past shows for a venue
    def past_shows(self):
      # Get all the shows for the venue by its ID
      shows = Show.query.filter_by(venue_id=self.id).all()
      # Get the current time
      today = datetime.now()
      # Initialize the shows list
      shows_list = []
      # Loop all the venue's shows
      for s in shows:
        # Check if the show is upcoming
        if s.start_time < today:
          # Add the show in the shows list
          shows_list.append(s)
      return shows_list

    # This function gets all the genres of the venue
    def genres_types(self):
      # Get all the genres for the venue by its ID
      genres = Venues_Genres.query.filter_by(venue_id=self.id).all()
      # Initialize the genres list
      genres_list = []
      # Loop all the genres
      for g in genres:
        # Add the genre type in the genres list
        genres_list.append(g.genre)
      return genres_list
      
"""
******************* Notes about the 'Venues_Genres' model *******************
1- Since the 'Venue' model has one or more genres, it is a multivalued attribute and it should 
    be in another model, 'Venues_Genres', (according to new_venue.html).
    (Reference:
      https://www.sciencedirect.com/topics/computer-science/multivalued-attribute#:~:text=Multivalued%20Attributes,them%20possibly%20in%20different%20cities.
    )
2- The 'Venue' model has One-to-Many relationship with the 'Venues_Genres' model.
3- To ensure thst the genre doesn't duplicate, the primary key should be a composition of the 
    'Venue' ID and the genre
"""
class Venues_Genres(db.Model):
    __tablename__ = 'venues_genres'

    # This is to define the foreign key of the 'Venue' model
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id'), primary_key=True)
    genre = db.Column(db.String(), primary_key=True)

    def __repr__(self):
      return f'<Venue ID: {self.venue_id}, genre: {self.genre}>'

"""
******************* Notes about the 'Artist' model *******************
1- The 'name, city, and state' attributes shouldn't be null (according to show_artist.html)
2- The 'seeking_venue, seeking_description, and website' should be added (according to show_artist.html)
3- Since the 'genre' is a multivalued atribute, it should be in another table called 'artists_genres' (according to new_artist.html)
4- The 'Artist' model has a One-to-Many relationship with the 'Show' model.
"""
class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String())
    # This is to define the 'Artist' and 'Genre' relationship
    genres = db.relationship('Artists_Genres', backref='artist', lazy=True)
    # This is to define the 'Artist' and 'Show' relationship
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
      return f'<Artist ID: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}>'
    
    # This function finds the number of the upcoming shows for an artist
    def upcoming_shows_number(self):
      # Get all the shows for the artist by his/her ID
      shows = Show.query.filter_by(artist_id=self.id).all()
      # Get the current time
      today = datetime.now()
      # Initialize the number of shows to zero for each artist
      num_shows = 0
      # Loop all the artist's shows
      for s in shows:
        # Check if the show is upcoming
        if s.start_time >= today:
          # Increase the number of shows
          num_shows = num_shows + 1
      return num_shows

    # This function finds the number of the past shows for an artist
    def past_shows_number(self):
      # Get all the shows for the artist by his/her ID
      shows = Show.query.filter_by(artist_id=self.id).all()
      # Get the current time
      today = datetime.now()
      # Initialize the number of shows to zero for each artist
      num_shows = 0
      # Loop all the artist's shows
      for s in shows:
        # Check if the show is upcoming
        if s.start_time < today:
          # Increase the number of shows
          num_shows = num_shows + 1
      return num_shows

    # This function finds all the upcoming shows for an artist
    def upcoming_shows(self):
      # Get all the shows for the artist by his/her ID
      shows = Show.query.filter_by(artist_id=self.id).all()
      # Get the current time
      today = datetime.now()
      # Initialize the shows list
      shows_list = []
      # Loop all the artist's shows
      for s in shows:
        # Check if the show is upcoming
        if s.start_time >= today:
          # Add the show in the shows list
          shows_list.append(s)
      return shows_list

    # This function finds all the past shows for an artist
    def past_shows(self):
      # Get all the shows for the artist by his/her ID
      shows = Show.query.filter_by(artist_id=self.id).all()
      # Get the current time
      today = datetime.now()
      # Initialize the shows list
      shows_list = []
      # Loop all the artist's shows
      for s in shows:
        # Check if the show is upcoming
        if s.start_time < today:
          # Add the show in the shows list
          shows_list.append(s)
      return shows_list

    # This function gets all the genres of the artist
    def genres_types(self):
      # Get all the genres for the artist by his/her ID
      genres = Artists_Genres.query.filter_by(artist_id=self.id).all()
      # Initialize the genres list
      genres_list = []
      # Loop all the genres
      for g in genres:
        # Add the genre type in the genres list
        genres_list.append(g.genre)
      return genres_list

"""
******************* Notes about the 'Artists_Genres' model *******************
1- Since the 'Artist' model has one or more genres, it is a multivalued attribute and it should 
    be in another model, 'Venues_Genres', (according to new_venue.html).
    (Reference:
      https://www.sciencedirect.com/topics/computer-science/multivalued-attribute#:~:text=Multivalued%20Attributes,them%20possibly%20in%20different%20cities.
    )
2- The 'Artist' model has a One-to-Many relationship with the 'Artists_Genres' model.
3- To ensure thst the genre doesn't duplicate, the primary key should be a composition of the 
    'Artist' ID and the genre
"""
class Artists_Genres(db.Model):
    __tablename__ = 'artists_genres'

    # This is to define the foreign key of the 'Artist' model
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), primary_key=True)
    genre = db.Column(db.String(), primary_key=True)

    def __repr__(self):
      return f'<Artist ID: {self.artist_id}, genre: {self.genre}>'

"""
******************* Notes about the 'Show' model *******************
1- The 'Show' model has two Many-to-One relationships with the 'Venue' and 'Artist' models.
    o Each show has one venue -> Each venue has many shows
    o Each show has one artist -> Each artist has many shows 
    (References: 
        - https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html
        - https://www.pythoncentral.io/sqlalchemy-association-tables/
    )
2- It has an attribute 'start_time' and it shouldn't be null (according to new_show.html) 
"""
class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    # This is to define the foreign key of the 'Venue' model
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id'), nullable=False)
    # This is to define the foreign key of the 'Artist' model
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Show ID: {self.id}, venue:{self.venue_id}, artist:{self.artist_id}, start time: {self.start_time}>'

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
  # Retrieve all the venues in the database
  all_venues = Venue.query.all() 
  
  # Create a set of cities and states without multiple occurrences of the same element
  cities_and_states = set()
  # Retrieve all cities and states from the venues
  for v in all_venues:
    cities_and_states.add((v.city, v.state))

  data = [] # Declare the dictionary to store the locations and their venues

  # Loop all the locations (city in state)
  for location in cities_and_states:
    venues = [] # Empty the list whenever it is done from a location
    for v in all_venues:
      # Find all the venues in the location and add them to the venues list
      if (v.city == location[0] and v.state == location[1]):
        # num_shows is aggregated based on the number of upcoming shows per venue 
        # by calling the function 'upcoming_shows_number'
        num_shows = v.upcoming_shows_number()
        # Add the venue to the list
        venues.append({"id": v.id, "name": v.name,
                       "num_upcoming_shows": num_shows})
    # Add the location (city and state) and its venues list to the data
    data.append({"city": location[0], "state": location[1], "venues": venues})

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # Get the 'search_term' the user entered
  search_term = request.form.get('search_term')
  # Retrieve all venues by using ilike function for the search term 
  # (Reference: https://prodevsblog.com/questions/146983/case-insensitive-flask-sqlalchemy-query/)
  venues = Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all()

  # Declare the result_venues to store all the venues required details
  result_venues = []

  # Initilize the count to zero, so it count the result venues
  count = 0

  # Loop the the venues
  for v in venues:
    # Increase the count
    count = count + 1
    # Find the venue's upcoming shows count by calling the 'upcoming_shows_number' function
    upcoming_shows_count = v.upcoming_shows_number()
    # Add the venue's details to the result_venues data dictionary
    result_venues.append({
      "id": v.id,
      "name": v.name,
      "num_upcoming_shows": upcoming_shows_count
    })
  # Add the count and result_venues to the response data dictionary
  response={
    "count": count,
    "data": result_venues
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # Retrive the venue details from the database by its ID
  venue = Venue.query.get(venue_id)
  # Retrive the venue's genres from the database by calling the function 'genres_types'
  genres = venue.genres_types()
  
  # Get the upcoming shows count by calling the function 'upcoming_shows_number'
  upcoming_shows_count = venue.upcoming_shows_number()
  # Get the past shows count by calling the function 'past_shows_number'
  past_shows_count = venue.past_shows_number()
  # Get the upcoming shows details by calling the function 'upcoming_shows'
  upcoming_shows = venue.upcoming_shows()
  # Get the past shows details by calling the function 'past_shows'
  past_shows = venue.past_shows()

  # Declare the 'up_shows_details' and 'past_shows_details' lists
  up_shows_details = []
  past_shows_details = []

  # Loop all the upcoming shows
  for us in upcoming_shows:
    # Add the show's details to the 'up_shows_details' dictionary
    up_shows_details.append({
        "artist_id": us.artist_id,
        "artist_name": us.artist.name,
        "artist_image_link": us.artist.image_link,
        # Converting the datetime object to string (Reference: https://www.programiz.com/python-programming/datetime/current-time)
        "start_time": us.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })

  # Loop all the past shows
  for ps in past_shows:
    # Add the show's details to the 'past_shows_details' dictionary
    past_shows_details.append({
        "artist_id": ps.artist_id,
        "artist_name": ps.artist.name,
        "artist_image_link": ps.artist.image_link,
        # Converting the datetime object to string (Reference: https://www.programiz.com/python-programming/datetime/current-time)
        "start_time": ps.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })

  # Add all the required details in the 'data' dictionary
  data={
    "id": venue_id,
    "name": venue.name,
    "genres": genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows_details,
    "upcoming_shows": up_shows_details,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count
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
  # Get the data from the formand store them in variables to access them later
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  image_link = request.form['image_link']
  facebook_link = request.form['facebook_link']
  website = request.form['website']
  seeking_talent = False
  # Check if the venue seeks talent set it as True (boolean value)
  if request.form['seeking_talent'] == 'Yes':
    seeking_talent = True
  seeking_description = request.form['seeking_description']
  # Using 'getlist' to retrive all the genres (Reference: https://stackoverflow.com/questions/34852011/get-all-items-inside-multiple-select-in-flask-python)
  genres = request.form.getlist('genres')

  
  form = VenueForm() # Create instance of VenueForm() to validate the form's data
  # Check the form validation
  if form.validate():
    error = False
    try:
      # Create an instance of the 'Venue' with the form data
      venue = Venue(name = name,
                    city = city,
                    state = state,
                    address = address,
                    phone = phone,
                    image_link = image_link,
                    facebook_link = facebook_link,
                    website = website,
                    seeking_talent = seeking_talent,
                    seeking_description=seeking_description)
      db.session.add(venue)
      # Create instances of the 'Venues_Genres'
      for g in genres:
        new_genre = Venues_Genres(genre = g)
        new_genre.venue = venue
        db.session.add(new_genre)
      db.session.commit()
    except():
      db.session.rollback()
      error = True
    finally:
      db.session.close()
    if error:
      # on unsuccessful db insert, flash an error.
      flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      abort(500)
    else:
      # on successful db insert, flash success.
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
  else:
    # If the user entered invalid data, an error message will be shown with the fields that are invalid
    # (Reference: https://wtforms.readthedocs.io/en/2.3.x/crash_course/)
    flash(form.errors)
    # Redirect to the new_venue.html page with the error message in the above line
    return redirect(url_for('create_venue_submission'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except():
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    # on unsuccessful db delete, flash an error.
    flash('An error occurred. Venue could not be deleted.')
    #return redirect(url_for('show_venue', venue_id=venue_id))
    abort(500)
  else:
    # on successful db delete, flash success.
    flash('Venue was successfully deleted!')
    return render_template('pages/home.html')

  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # Retrieve all artists details from the database
  artists = Artist.query.all()

  data = []  # Declare the dictionary to store the artists' ids and names

  # Loop all the artists
  for a in artists:
    # Add the artist's id and name to the data dictionary
    data.append({
      "id": a.id,
      "name": a.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # Get the 'search_term' the user entered
  search_term = request.form.get('search_term')

  # Retrieve all artists by using ilike function for the search term
  # (Reference: https://prodevsblog.com/questions/146983/case-insensitive-flask-sqlalchemy-query/)
  artists = Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).all()
  
  # Declare the result_artists to store all the artists' required details
  result_artists = []

  # Initilize the count to zero, so it count the result artists
  count = 0

  # Loop the the venues
  for a in artists:
    # Increase the count
    count = count + 1
    # Find the artist's upcoming shows count by calling the 'upcoming_shows_number' function
    upcoming_shows_count = a.upcoming_shows_number()
    # Add the artist's details to the result_artists data dictionary
    result_artists.append({
        "id": a.id,
        "name": a.name,
        "num_upcoming_shows": upcoming_shows_count
    })

  # Add the count and result_artists to the response data dictionary
  response = {
      "count": count,
      "data": result_artists
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # Retrive the artist details from the database by his/her ID
  artist = Artist.query.get(artist_id)
  # Retrive the artist's genres from the database by calling the function 'genres_types'
  genres = artist.genres_types()

  # Get the upcoming shows count by calling the function 'upcoming_shows_number'
  upcoming_shows_count = artist.upcoming_shows_number()
  # Get the past shows count by calling the function 'past_shows_number'
  past_shows_count = artist.past_shows_number()
  # Get the upcoming shows details by calling the function 'upcoming_shows'
  upcoming_shows = artist.upcoming_shows()
  # Get the past shows details by calling the function 'past_shows'
  past_shows = artist.past_shows()

  # Declare the 'up_shows_details' and 'past_shows_details' lists
  up_shows_details = []
  past_shows_details = []

  # Loop all the upcoming shows
  for us in upcoming_shows:
    # Add the show's details to the 'up_shows_details' dictionary
    up_shows_details.append({
        "venue_id": us.venue_id,
        "venue_name": us.venue.name,
        "venue_image_link": us.venue.image_link,
        # Converting the datetime object to string (Reference: https://www.programiz.com/python-programming/datetime/current-time)
        "start_time": us.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })

  # Loop all the past shows
  for ps in past_shows:
    # Add the show's details to the 'past_shows_details' dictionary
    past_shows_details.append({
        "venue_id": ps.venue_id,
        "venue_name": ps.venue.name,
        "venue_image_link": ps.venue.image_link,
        # Converting the datetime object to string (Reference: https://www.programiz.com/python-programming/datetime/current-time)
        "start_time": ps.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })

  # Add all the required details in the 'data' dictionary
  data = {
    "id": artist_id,
    "name": artist.name,
    "genres": genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows_details,
    "upcoming_shows": up_shows_details,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  # Retrieve the artist's details from the database by her/his id
  artist = Artist.query.get(artist_id)

  # Populate the form's fields with the artist's details
  form.name.data= artist.name
  # Get the genres types by calling the function 'genres_types'
  form.genres.data= artist.genres_types()
  form.city.data= artist.city
  form.state.data= artist.state
  form.phone.data = artist.phone
  form.website.data= artist.website
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  # Get the data from the form and store them in variables to access them later
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  image_link = request.form['image_link']
  facebook_link = request.form['facebook_link']
  website = request.form['website']
  seeking_venue = False
  # Check if the artist seeks venue set it as True (boolean value)
  if request.form['seeking_venue'] == 'Yes':
    seeking_venue = True
  seeking_description = request.form['seeking_description']
  # Using 'getlist' to retrive all the genres (Reference: https://stackoverflow.com/questions/34852011/get-all-items-inside-multiple-select-in-flask-python)
  genres = request.form.getlist('genres')

  form = ArtistForm()  # Create instance of ArtistForm() to validate the form's data
  # Check the form validation
  if form.validate():
    error = False
    try:
      # Create an instance of the 'Artist' by her/his id
      artist = Artist.query.get(artist_id)

      # Set the artist's data with the new data from the form
      artist.name=name
      artist.city=city
      artist.state = state
      artist.phone = phone
      artist.image_link=image_link
      artist.facebook_link=facebook_link
      artist.website=website
      artist.seeking_venue=seeking_venue
      artist.seeking_description=seeking_description

      # Delete all genres to avoid duplicating
      old_genres = artist.genres
      for og in old_genres:
        db.session.delete(og)

      # Add new genres to the database
      for g in genres:
        new_genre = Artists_Genres(genre=g)
        new_genre.artist = artist
        db.session.add(new_genre)

      db.session.commit()
    except():
      db.session.rollback()
      error = True
    finally:
      db.session.close()
    if error:
      # on unsuccessful db insert, flash an error.
      flash('An error occurred. Artist ' +
            request.form['name'] + ' could not be updated.')
      abort(500)
    else:
      # on successful db insert, flash success.
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
      return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    # If the user entered invalid data, an error message will be shown with the fields that are invalid
    # (Reference: https://wtforms.readthedocs.io/en/2.3.x/crash_course/)
    flash(form.errors)
    # Redirect to the edit_artist.html page with the error message in the above line
    return redirect(url_for('edit_artist_submission'))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  # Retrieve the venue's details from the database by its id
  venue = Venue.query.get(venue_id)

  # Populate the form's fields with the artist's details
  form.name.data = venue.name
  # Get the genres types by calling the function 'genres_types'
  form.genres.data = venue.genres_types()
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.website.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # Get the data from the form and store them in variables to access them later
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  image_link = request.form['image_link']
  facebook_link = request.form['facebook_link']
  website = request.form['website']
  seeking_talent = False
  # Check if the venue seeks talent set it as True (boolean value)
  if request.form['seeking_talent'] == 'Yes':
    seeking_talent = True
  seeking_description = request.form['seeking_description']
  # Using 'getlist' to retrive all the genres (Reference: https://stackoverflow.com/questions/34852011/get-all-items-inside-multiple-select-in-flask-python)
  genres = request.form.getlist('genres')

  form = VenueForm()  # Create instance of VenueForm() to validate the form's data
  # Check the form validation
  if form.validate():
    error = False
    try:
      # Create an instance of the 'Venue' by its id
      venue = Venue.query.get(venue_id)

      # Set the venue's data with the new data from the form
      venue.name = name
      venue.city = city
      venue.state = state
      venue.address= address
      venue.phone = phone
      venue.image_link = image_link
      venue.facebook_link = facebook_link
      venue.website = website
      venue.seeking_talent = seeking_talent
      venue.seeking_description = seeking_description

      # Delete all genres to avoid duplicating
      old_genres = venue.genres
      for og in old_genres:
        db.session.delete(og)

      # Add new genres to the database
      for g in genres:
        new_genre = Venues_Genres(genre=g)
        new_genre.venue = venue
        db.session.add(new_genre)

      db.session.commit()
    except():
      db.session.rollback()
      error = True
    finally:
      db.session.close()
    if error:
      # on unsuccessful db insert, flash an error.
      flash('An error occurred. Venue ' +
            request.form['name'] + ' could not be updated.')
      abort(500)
    else:
      # on successful db insert, flash success.
      flash('Venue ' + request.form['name'] + ' was successfully updated!')
      return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    # If the user entered invalid data, an error message will be shown with the fields that are invalid
    # (Reference: https://wtforms.readthedocs.io/en/2.3.x/crash_course/)
    flash(form.errors)
    # Redirect to the edit_venue.html page with the error message in the above line
    return redirect(url_for('edit_venue_submission'))



#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # Get the data from the form and store them in variables to access them later
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  image_link = request.form['image_link']
  facebook_link = request.form['facebook_link']
  website = request.form['website']
  seeking_venue = False
  # Check if the artist seeks venue set it as True (boolean value)
  if request.form['seeking_venue'] == 'Yes':
    seeking_venue = True
  seeking_description = request.form['seeking_description']
  # Using 'getlist' to retrive all the genres (Reference: https://stackoverflow.com/questions/34852011/get-all-items-inside-multiple-select-in-flask-python)
  genres = request.form.getlist('genres')

  form = ArtistForm()  # Create instance of ArtistForm() to validate the form's data
  # Check the form validation
  if form.validate():
    error = False
    try:
      # Create an instance of the 'Artist' with the form data
      artist = Artist(name=name,
                      city=city,
                      state=state,
                      phone=phone,
                      image_link=image_link,
                      facebook_link=facebook_link,
                      website=website,
                      seeking_venue=seeking_venue,
                      seeking_description=seeking_description)
      db.session.add(artist)
      # Create instances of the 'Artists_Genres'
      for g in genres:
        new_genre = Artists_Genres(genre=g)
        new_genre.artist = artist
        db.session.add(new_genre)
      db.session.commit()
    except():
      db.session.rollback()
      error = True
    finally:
      db.session.close()
    if error:
      # on unsuccessful db insert, flash an error.
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      abort(500)
    else:
      # on successful db insert, flash success.
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
  else:
    # If the user entered invalid data, an error message will be shown with the fields that are invalid
    # (Reference: https://wtforms.readthedocs.io/en/2.3.x/crash_course/)
    flash(form.errors)
    # Redirect to the new_venue.html page with the error message in the above line
    return redirect(url_for('create_artist_submission'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # Retrieve all shows details from the database
  shows = Show.query.all()

  data = [] 

  for s in shows:
    data.append({
      "venue_id": s.venue.id,
      "venue_name": s.venue.name,
      "artist_id": s.artist.id,
      "artist_name": s.artist.name,
      "artist_image_link": s.artist.image_link,
      # Converting the datetime object to string (Reference: https://www.programiz.com/python-programming/datetime/current-time)
      "start_time": s.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # Get the data from the form and store them in variables to access them later
  artist_id = request.form['artist_id']
  venue_id = request.form['venue_id']
  start_time = request.form['start_time']

  form = ShowForm()  # Create instance of ShowForm() to validate the form's data
  # Check the form validation
  if form.validate():
    error = False
    venue = Venue.query.get(venue_id)
    artist = Artist.query.get(artist_id)

    # Check if the venue id exists or not. 
    if venue is None:
      # Inform the user that the id doesn't exist
      flash('The venue id:'+venue_id+' does not exist')
      # Redirect to the new_show.html page with the error message in the above line
      return redirect(url_for('create_show_submission'))

    # Check if the artist id exists or not. 
    if artist is None:
      # Inform the user that the id doesn't exist
      flash('The artist id:'+artist_id+' does not exist')
      # Redirect to the new_show.html page with the error message in the above line
      return redirect(url_for('create_show_submission'))

    try:
      # Create an instance of the 'Show' with the form data
      show = Show(venue_id=venue_id,
                  artist_id=artist_id,
                  start_time=start_time)
      db.session.add(show)
      db.session.commit()
    except():
      db.session.rollback()
      error = True
    finally:
      db.session.close()
    if error:
      # on unsuccessful db insert, flash an error.
      flash('An error occurred. Show could not be listed.')
      abort(500)
    else:
      # on successful db insert, flash success.
      flash('Show was successfully listed!')
      return render_template('pages/home.html')
  else:
    # If the user entered invalid data, an error message will be shown with the fields that are invalid
    # (Reference: https://wtforms.readthedocs.io/en/2.3.x/crash_course/)
    flash(form.errors)
    # Redirect to the new_venue.html page with the error message in the above line
    return redirect(url_for('create_show_submission'))


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
