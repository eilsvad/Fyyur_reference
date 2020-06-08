from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, FieldList
from wtforms.validators import DataRequired, AnyOf, URL, ValidationError, Regexp, Optional
import re

def validate_phone(form, field):                        
    if not re.search(r"^[0-9]{3}-[0-9]{3}-[0-9]{4}$", field.data):
        raise ValidationError("Invalid phone number.")

genres_choices=[
        ('Alternative', 'Alternative'),
        ('Blues', 'Blues'),
        ('Classical', 'Classical'),
        ('Country', 'Country'),
        ('Electronic', 'Electronic'),
        ('Folk', 'Folk'),
        ('Funk', 'Funk'),
        ('Hip-Hop', 'Hip-Hop'),
        ('Heavy Metal', 'Heavy Metal'),
        ('Instrumental', 'Instrumental'),
        ('Jazz', 'Jazz'),
        ('Musical Theatre', 'Musical Theatre'),
        ('Pop', 'Pop'),
        ('Punk', 'Punk'),
        ('R&B', 'R&B'),
        ('Reggae', 'Reggae'),
        ('Rock n Roll', 'Rock n Roll'),
        ('Soul', 'Soul'),
        ('Other', 'Other'),
    ]

def custom_genres_validator(form, field):                   # enum restriction validator
        genres_values = [choice[1] for choice in genres_choices]
        for value in field.data:
            if value not in genres_values:
                raise ValidationError('Invalid genres value.')

class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id', validators=[DataRequired()]
    )
    venue_id = StringField(
        'venue_id', validators=[DataRequired()]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(FlaskForm):

    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ]
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )

    phone = StringField(
        'phone', validators=[DataRequired(), validate_phone]
#       'phone', validators=[DataRequired(), Regexp("^[0-9]*$", message="Only numbers allowed in phone")]
    )
    website = StringField(
        'website', validators=[Optional(), URL()]   # only if provided check URL validation else stop validation chain
    )
    image_link = StringField(
        'image_link', validators=[Optional(), URL()]    # only if provided check URL validation else stop validation chain
    )
    seeking_talent = BooleanField(
        'seeking_talent'
    )    
    seeking_talent_description = StringField(
        'seeking_talent_description'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired(), custom_genres_validator],
        choices = genres_choices
    )
    facebook_link = StringField(
        'facebook_link', validators=[Optional(), URL()] # only if provided check URL validation else stop validation chain
    )

class ArtistForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ]
    )
    phone = StringField(
        'phone', validators=[DataRequired(), Regexp("^[0-9]{3}-[0-9]{3}-[0-9]{4}$", message="Only numbers allowed in phone")]
    )
    website = StringField(
        'website', validators=[Optional(), URL()]       # only if provided check URL validation else stop validation chain
    )
    image_link = StringField(
        'image_link', validators=[Optional(), URL()]    # only if provided check URL validation else stop validation chain
    )
    albums = StringField(
        'albums'
    )    
    songs = StringField(
        'songs'
    )
#    albums = FieldList(                <<< tried with FieldList but didn't worked
#        StringField('albums'), min_entries=0, max_entries=3
#    )    
    seeking_venue = BooleanField(
        'seeking_venue'
    )    
    seeking_venue_description = StringField(
        'seeking_venue_description'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired(), custom_genres_validator],
        choices = genres_choices
    )
    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', validators=[Optional(), URL()] # only if provided check URL validation else stop validation chain
    )

# TODO IMPLEMENT NEW ARTIST FORM AND NEW SHOW FORM
