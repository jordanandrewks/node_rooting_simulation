from os import name
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

db = SQLAlchemy(app)

class Drink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(120))

    def __repr__(self) -> str:
        return f"{self.name} - {self.description}"

class Cities(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    population = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"{self.name} - {self.population}"


@app.route('/')
def index():
    print('This is a test')
    print([i for i in range(39)])
    return 'Hello- this is a test!!'
    

@app.route('/cities')
def get_cities():
    cities = Cities.query.all()
    output = []
    for city in cities:
        city_data = {'name': city.name, 'description': city.population}
        output.append(city_data)
    return {"cities": output}


@app.route('/cities', methods=['POST'])
def add_city():
    city = Cities(name=request.json['name'], population=request.json['population'])
    db.session.add(city)
    db.session.commit()
    return {'id': city.id}, 200


@app.route('/cities/<id>')
def get_city(id):
    city = Cities.query.get_or_404(id)
    return {"name": city.name, "population":city.population}, 200


@app.route('/cities/<id>', methods=['DELETE'])
def delete_city(id):
    city = Cities.query.get(id)
    if city is None:
        return {'error': "not found"}, 404
    
    db.session.delete(city)
    db.session.commit()
    return {'success': "city deleted"}, 200



@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    output = []
    for drink in drinks:
        drink_data = {'name': drink.name, 'description': drink.description}
        output.append(drink_data)
    return {"drinks": output}, 200

@app.route('/drinks/<id>')
def get_drink(id):
    drink = Drink.query.get_or_404(id)
    return {"name": drink.name, "description": drink.description}, 200

@app.route('/drinks', methods=['POST'])
def add_drink():
    drink = Drink(name=request.json['name'], description=request.json['description'])
    db.session.add(drink)
    db.session.commit()
    return {'id': drink.id}, 200

@app.route('/drinks/<id>', methods=['DELETE'])
def delete_drink(id):
    drink = Drink.query.get(id)
    if drink is None:
        return {"error": "not found"}, 404
    
    db.session.delete(drink)
    db.session.commit()
    return {"message": "All good"}, 200

