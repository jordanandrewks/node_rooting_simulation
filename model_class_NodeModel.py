from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

NODE_LIST = []

class NodeModel(db.Model):

    id = db.Column(db.String(80), primary_key=True, unique=True, nullable=False)    
    connections = db.Column(db.String(80), nullable=False)


    def __repr__(self) -> str:
        return f"{self.id} - {self.connections}"
    

    def get_item(item_id):
        return NodeModel.query.get(item_id)


    def get_all_items():
        return NodeModel.query.all()


    def add_item(node_id, connections):
        node = NodeModel(id=node_id, connections=connections)
        db.session.add(node)
        db.session.commit()


    def delete_item(item):
        db.session.delete(item)
        db.session.commit()


    def update_connection(node_instance, new_connections):
        node_instance.connections = new_connections
        db.session.commit()



db.create_all()