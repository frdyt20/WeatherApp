from os import name
from flask.helpers import url_for
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import redirect 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'classified'

db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

""" Fungsi untuk mendapatkan ketersediaan data pada API 
    untuk Cuaca dengan parameter query untuk Lokasi, 
    units untuk satuan ukuran dalam metric(Celcius),
    lang untuk bahasa(Indonesia), serta appID untuk APIkey for Developer
    """
def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=metric&lang=id&appid=271d1234d3f497eed5b1d80a07b3fcd1'
    response = requests.get(url).json()
    return response

@app.route('/')
def index_get():
    cities = City.query.all()

    weather_data = []
    selected_weather_data = []

    """ Fungsi untuk memanggil data cuaca pada API
    dengan parameter nama Lokasi, lalu return data berupa dictionary
    berisikan nama Lokasi, suhu dalam format celcius,
    deskipsi mengenai cuaca saat ini, dan icon yang menggambarkan cuaca saat ini
    """

    for city in cities:

        response = get_weather_data(city.name)

        weather = {
            'city' : city.name,
            'temperature' : response['main']['temp'],
            'description' : response['weather'][0]['description'],
            'icon' : response['weather'][0]['icon'],
        }

        weather_data.append(weather)
    
    selected_weather_data.append(weather_data[0])
    return render_template('weather.html', weather_data=weather_data, selected_weather_data=selected_weather_data)

@app.route('/', methods=['POST'])
def index_post():
    error_message = ''
    new_city = request.form.get('city')

    """Fungsi untuk menambahkan data yang didapatkan dari API
    ke dalam SQlite DB. Dengan error handling berupa validasi
    pengecekan ketersediaan data yang diinginkan melalui API 
    dan duplikasi data pada database sqlite.
    """    
    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()

        if not existing_city:
            new_city_data = get_weather_data(new_city)
            if new_city_data['cod'] == 200:

                new_city_obj = City(name=new_city)

                db.session.add(new_city_obj)
                db.session.commit()
            else:
                error_message = 'Lokasi tidak ditemukan'
        else:
            error_message = 'Lokasi ini sudah ditambahkan sebelumnya'

    if error_message:
        flash(error_message, 'error')
    else:
        flash('Lokasi berhasil ditambahkan!')

    return redirect(url_for('index_get'))

@app.route('/delete/<name>/')

def delete_city(name):
    
    """Fungsi untuk menghapus data pada web view, sekaligus
    value pada SQlite DB    
    """
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()

    flash(f'Lokasi { city.name } berhasil dihapus', 'success')
    return redirect(url_for('index_get'))



@app.route('/filter_city', methods=['POST'])
def filter_city():
    # Fungsi untuk filter data    
    weather_data = []
    selected_weather_data = []
    

    city = request.form.get('city')
    selected_city_query = City.query.filter_by(name=city)
    for city in selected_city_query:
        response = get_weather_data(city.name)
        weather = {
            'city' : city.name,
            'temperature' : response['main']['temp'],
            'description' : response['weather'][0]['description'],
            'icon' : response['weather'][0]['icon'],
        }
        selected_weather_data.append(weather)
   
    cities = City.query.all()
    for city in cities:
        response = get_weather_data(city.name)
        weather = {
            'city' : city.name,
            'temperature' : response['main']['temp'],
            'description' : response['weather'][0]['description'],
            'icon' : response['weather'][0]['icon'],
        }
        weather_data.append(weather)

    return render_template('weather.html', weather_data=weather_data, selected_weather_data=selected_weather_data)
    