"""
FILE:           controller_class_NodeObj.py
DESCRIPTION:
Responsible passing Node Model data to the database.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class NodeModel(db.Model):
    # SQL Model instances
    id = db.Column(db.String(80), primary_key=True, unique=True, nullable=False)    
    connections = db.Column(db.String(80), nullable=False)


    def __repr__(self) -> str:
        # Return string of object related data to console when requested
        return f"{self.id} - {self.connections}"
    

    def get_item(item_id):
        # Send query of item ID to the data base and return the instance of that model
        return NodeModel.query.get(item_id)


    def get_all_items():
        # Send a query get of instances within the database
        return NodeModel.query.all()


    def add_item(node_id, connections):
        # Add item to the database, id and connections must be provided
        node = NodeModel(id=node_id, connections=connections)
        db.session.add(node)
        db.session.commit()


    def delete_item(item):
        # Delete Item from the database whose id matches 'item'
        db.session.delete(item)
        db.session.commit()


    def update_connection(node_instance, new_connections):
        # Update the connections of node instance in the database
        node_instance.connections = new_connections
        db.session.commit()


# db.create_all()