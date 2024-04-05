#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response, g
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Plant

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///plants.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


class Plants(Resource):

    def get(self):
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        data = request.get_json()

        new_plant = Plant(
            name=data["name"],
            image=data["image"],
            price=data["price"],
        )

        db.session.add(new_plant)
        db.session.commit()

        return make_response(new_plant.to_dict(), 201)


api.add_resource(Plants, "/plants")


class PlantByID(Resource):

    def get(self, id):
        plant = Plant.query.filter_by(id=id).first().to_dict()
        return make_response(jsonify(plant), 200)

    def patch(self, id):
        try:
            if plant := db.session.get(Plant, id):
                data = request.json
                for attr, value in data.items():
                    setattr(plant, attr, value)
                db.session.commit()
                return make_response(plant.to_dict(), 200)
            return {"error": f"plant #{id} not found."}
        except Exception as e:
            db.session.rollback()
            return str(e), 422

    def delete(self, id):
        try:
            if plant := db.session.get(Plant, id):
                db.session.delete(plant)
                db.session.commit()
                return "", 204
            return {"error": f"plant #{id} not found."}
        except Exception as e:
            db.session.rollback()
            return str(e), 422


api.add_resource(PlantByID, "/plants/<int:id>")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
