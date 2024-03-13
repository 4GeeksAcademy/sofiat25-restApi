"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Favorites, People, Planets
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET', 'POST'])
def handle_user():
    data = request.json
    #-----------------------------------------------------
    if request.method == "POST":
        data_check = [data.get("email"), data.get("password")]
        if None in data_check:
            return jsonify({
                "message": "email and password required"
            }), 400
        user_exists = User.query.filter_by(email=data["email"]).one_or_none()
        if user_exists:
            return jsonify({
                "message": "user already exists"
            }), 400
        new_user = User(email = data["email"], password = data["password"])
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            return jsonify({
                "message": "something went wrong, try again."
            }), 500
        return jsonify({
            "message": "User has been created successfully"
        }), 201
    
    #-------------------------------------------------------------

    if request.method == 'GET':
        all_users = User.query.all()
        user_serialized = []
        for user in all_users:
            user_serialized.append(user.serialize())
        return jsonify(user_serialized), 200

@app.route("/user/<int:id>/favorites", methods=["GET", "POST"])
def handle_favorites(id):
    data = request.json
    #-------------------------------------------------------------
    if request.method == "POST":
        planet_check = data.get('planets_id')
        people_check = data.get('people_id')
        print(people_check, planet_check)
        
        if bool(planet_check) or bool(people_check) :
            return jsonify({
                "message": "Either one planet o character must be added"
            }), 400
        

        if data.get('planets_id'):
            new_favorite = Favorites(
            user_id = id,
            planets_id = data['planets_id'] 
        )
            
        if data.get('people_id'):
            new_favorite = Favorites(
            user_id = id,
            people_id = data['people_id']
        )
            
        try:
            db.session.add(new_favorite)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            return jsonify({
                "message": "something went wrong, try again."
            }), 500
        
        return jsonify({
            "message": "Favorite has been added successfully"
        }), 201
    #------------------------------------------------------------------------
    if request.method == "GET":
        def clean_nones(value):
            if isinstance(value, list):
                return [clean_nones(x) for x in value if x is not None]
            elif isinstance(value, dict):
                return {
                    key: clean_nones(val)
                    for key, val in value.items()
                    if val is not None
                }
            else:
                return value

        user_favorites = Favorites.query.filter_by(user_id=id)
        favorites_list = []
        for favorites in user_favorites:
            favorites_list.append(favorites.serialize())
        return jsonify(clean_nones(favorites_list)), 200

@app.route("/user/<int:user_id>/favorites/<int:delete_id>", methods=["DELETE"])
def handle_delete_favorite(user_id, delete_id):
    favorite = Favorites.query.get(delete_id)
    if request.method == "DELETE":
        try:
            db.session.delete(favorite)
            db.session.commit()
            return jsonify({
                "message": "Favorite has been deleted successfully"
            }), 201
        except Exception as error:
            db.session.rollback()
            return jsonify({
                "message": "something went wrong, try again."
            }), 500

@app.route("/planets", methods=['GET','POST'])
def handle_planets():
    data = request.json
    if request.method == "POST":
        data_check = [data.get("name"), data.get("population"), data.get("diameter")]
        if None in data_check:
            return jsonify({
                "message": "name, population and diameter required"
            }), 400
        planet_exists = Planets.query.filter_by(name=data["name"]).one_or_none()
        if planet_exists:
            return jsonify({
                "message": "planet already exists"
            }), 400
        new_planet = Planets(
           name = data["name"], 
           population = data["population"],
           diameter = data["diameter"],
        )

        try:
            db.session.add(new_planet)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            return jsonify({
                "message": "something went wrong, try again."
            }), 500
        return jsonify({
            "message": "Planet has been created successfully"
        }), 201
    #------------------------------------------------------------
    if request.method == 'GET':
        all_planets = Planets.query.all()
        planets_serialized = []
        for planet in all_planets:
            planets_serialized.append(planet.serialize())
        return jsonify(planets_serialized), 200
    
@app.route("/planets/<int:planets_id>", methods=["GET", "PUT", "DELETE"])
def handle_specific_planet(planets_id):
    planet = Planets.query.get(planets_id)
    data = request.json
    #----------------------------------------
    
    if request.method == "GET":
        if planet is None:
            return jsonify({
                "message": "Planet does not exist"
            }), 400
        return jsonify(planet.serialize()), 200
    
    #----------------------------------------
    
    if request.method == "PUT":
        data_check = [data.get("name"), data.get("population"), data.get("diameter")]
        if None in data_check:
            return jsonify({
                "message": "name, population and diameter required"
            }), 400
        
        planet.name = data['name']
        planet.diameter = data['diameter']
        planet.population = data['population']

        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            return jsonify({
                "message": "something went wrong, try again."
            }), 500
        
        return jsonify({
            "message": "Planet has been updated successfully"
        }), 201
    #-------------------------------------------------------------
    if request.method == "DELETE":
        try:
            db.session.delete(planet)
            db.session.commit()
            return jsonify({
                "message": "Planet has been deleted successfully"
            }), 201
        except Exception as error:
            db.session.rollback()
            return jsonify({
                "message": "something went wrong, try again."
            }), 500
        

        


@app.route("/people", methods=["GET", "POST"])
def handle_people():
    data = request.json
    #---------------------------------------------------------
    if request.method == "POST":
        data_check = [data.get("name"), data.get("age"), data.get("height") ]
        if None in data_check:
            return jsonify({
                "message": "name, age and height required"
            }), 400
        people_exists = People.query.filter_by(name=data["name"]).one_or_none()
        if people_exists:
            return jsonify({
                "message": "character already exists"
            }), 400
        new_people = People(
            name=data["name"],
            age=data["age"],
            height=data["height"],
        )
        try:
            db.session.add(new_people)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            return jsonify({
                "message": "something went wrong, try again."
            }), 500
        
        return jsonify({
            "message": "Character has been created successfully"
        }), 201
    
    #-------------------------------------------

    if request.method == "GET":
        all_people = People.query.all()
        people_serialized = []
        for people in all_people:
            people_serialized.append(people.serialize())
        return jsonify(people_serialized), 200

@app.route("/people/<int:people_id>", methods=["GET", "PUT", "DELETE"])
def handle_specific_people(people_id):
    data = request.json
    person = People.query.get(people_id)
    #---------------------------------------------

    if request.method == "GET": 
        if person is None:
            return jsonify({
                "message": "Character does not exists"
            }), 400
        return jsonify(person.serialize()), 200
    
    #-------------------------------------------

    if request.method == "PUT":
        data_check = [data.get("name"), data.get("age"), data.get("height") ]
        if None in data_check:
            return jsonify({
                "message": "name, age and height required"
            }), 400
        person.age = data['age']
        person.height = data['height']
        person.name = data['name']
        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            return jsonify({
                "message": "something went wrong, try again."
            }), 500
        
        return jsonify({
            "message": "Character has been updated successfully"
        }), 201
    
    #-------------------------------------------

    if request.method == "DELETE":
        try:
            db.session.delete(person)
            db.session.commit()
            return jsonify({
                "message": "Character has been deleted successfully"
            }), 201
        except Exception as error:
            db.session.rollback()
            return jsonify({
                "message": "something went wrong, try again."
            }), 500
    #-------------------------------------------

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)