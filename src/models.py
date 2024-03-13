from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship


db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    favorites = relationship("Favorites", back_populates="user")

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }
class Favorites(db.Model): #Child
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = relationship("User", back_populates="favorites")
    planets_id = db.Column(db.Integer, db.ForeignKey("planets.id"), nullable=True)
    planets = relationship("Planets", back_populates="favorites")
    people_id = db.Column(db.Integer, db.ForeignKey("people.id"), nullable=True)
    people = relationship("People", back_populates="favorites")

    def __repr__(self):
        return '<User %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planets_id": self.planets_id,
            "people_id": self.people_id,
            
        }

class Planets(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    population = db.Column(db.Integer, nullable=False)
    diameter = db.Column(db.Integer, nullable=False)
    favorites = relationship("Favorites", back_populates="planets")

    def __repr__(self):
        return '<User %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population,
            "diameter": self.diameter,
        }

class People(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    favorites = relationship("Favorites", back_populates="people")

    def __repr__(self):
        return '<User %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "height": self.height,
        }