from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    genres = db.Column(db.ARRAY(db.String()))
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120),nullable=False)
    website = db.Column(db.String(120),default='No Website')
    seeking_talent = db.Column(db.Boolean, nullable=False,default=False)
    seeking_description = db.Column(db.String(200))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120),default='No Facebook')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    genres = db.Column(db.ARRAY(db.String()))
    website = db.Column(db.String(120),default='No Website')
    seeking_venue = db.Column(db.Boolean, nullable=False,default=False)
    seeking_description = db.Column(db.String(200))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120),default='No Facebook')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Shows(db.Model):
  __tablename__= 'shows'
  id = db.Column(db.Integer,primary_key=True)
  start_time = db.Column(db.DateTime(), nullable=False)
  artist_id = db.Column(db.Integer,db.ForeignKey(Artist.id),nullable=False)
  venue_id = db.Column(db.Integer,db.ForeignKey(Venue.id),nullable=False)
  artist = db.relationship(Artist, backref=db.backref('shows', cascade='all, delete' ))
  venue = db.relationship(Venue, backref=db.backref('shows', cascade='all, delete'))
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.