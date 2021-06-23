from flask.helpers import url_for
import requests
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import redirect 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

@app.route('/')
def index_get():
    cities = City.query.all()

    """ API untuk Cuaca
    dengan parameter query untuk kota, 
    units untuk satuan ukuran dalam metric(Celcius),
    lang untuk bahasa(Indonesia), serta appID untuk APIkey for Developer
    """
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&lang=id&appid=271d1234d3f497eed5b1d80a07b3fcd1'

    weather_data = []

    """ Fungsi untuk memanggil data cuaca pada API
    dengan parameter nama kota, lalu return data berupa dictionary
    berisikan nama kota, suhu dalam format celcius,
    deskipsi mengenai cuaca saat ini, dan icon yang menggambarkan cuaca saat ini
    """
    for city in cities:

        response = requests.get(url.format(city.name)).json()

        weather = {
            'city' : city.name,
            'temperature' : response['main']['temp'],
            'description' : response['weather'][0]['description'],
            'icon' : response['weather'][0]['icon'],
        }

        weather_data.append(weather)


    return render_template('weather.html', weather_data=weather_data)

@app.route('/', methods=['POST'])
def index_post():
    new_city = request.form.get('city')
        
    if new_city:
        new_city_obj = City(name=new_city)

        db.session.add(new_city_obj)
        db.session.commit()

    return redirect(url_for(index_get))