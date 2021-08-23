from re import split
import sys

import json
from os import name
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

db = SQLAlchemy(app)

NODE_LIST = []

DATA_PACKET = {
    'HOP_LIM': 5,
    'HISTORY[x]': '',
    'MESSAGE': ''
}

# Problem 1 - Ideally need to assign a list to the connections 
# Problem 2 - We cannot access the instance variables in the class 
# Problem 3 - Struggled to get connections with the same decalarations in SOLVED
# Problem 4 - Id was a number, yet we still had the node_id variable, one is enough - SOLVED



class Test:
    def __init__(self, node_id, connections) -> None:
        self.node_id = node_id
        self.connections = connections
        self.data_test = []


    def print_info(self):
        print(self.node_id)
        print(self.connections)
        self.data_test = ['f', 'w']
        print(self.data_test)


class Node(db.Model):

    # id = db.Column(db.String(80), unique=True, primary_key=True, nullable=False)
    node_id = db.Column(db.String(80), primary_key=True, unique=True, nullable=False)    
    connections = db.Column(db.String(80), nullable=False)

    def __repr__(self) -> str:
        return f"{self.node_id} - {self.connections}"

    def __init__(self, node_id: str, connections: list) -> None:
        '''instances variables are initialized here'''

        # Instance variables
        self.node_id = node_id
        self.connections = connections
        self.discovered_connections = []
        self.buffer = []
        self.null_list = []


    def inject_packet(self, packet: dict):
        """Pass in the first packet"""
        self.buffer.append(packet.copy())


    def get_connected_node_obj(self):
        """ return the object of the node"""
        count = 0
        for connected_node in self.connections:
            for index, node_obj in enumerate(list(NODE_LIST)):
                if connected_node is node_obj.node_id:
                    count += 1
                    # yield index, node_obj.node_id
                    yield index


    def find_depleted_packets(self):
        self.null_list = []
        for c in range(0, len(self.buffer)):
            if self.buffer[c]['HOP_LIM'] == 0:
                self.null_list.append(c)
        

    def remove_depleted_packets(self):
        for decrement, packet_index in enumerate(self.null_list):
            self.buffer.pop(packet_index - decrement) 


    def next_hop(self):
        """ Send the packet to the next connections"""  
        print("I am <{}> and I'm connected to {}". format(self.node_id, self.connections))

        self.get_new_connections()
        self.find_depleted_packets()
        self.remove_depleted_packets()

        if self.buffer:     # Check if there's anything in THIS nodes buffer

            self.buffer[0]['HISTORY[x]'] += self.node_id + '>'
            self.buffer[0]['HOP_LIM'] -= 1

            for node_index in list(self.get_connected_node_obj()):
                print("I need to send to >>>>>", node_index)
                if self.buffer[0]['HOP_LIM'] >= 0:
                    NODE_LIST[node_index].buffer.append(self.buffer[0].copy())         # Move value to the next object

            self.buffer.pop(0)                                  # Remove this value from this object


    def get_congestion(self) -> int:
        return len(self.buffer)
    

    def get_new_connections(self):

        recent_node_list = []
        history_list = list(str(self.buffer[i]['HISTORY[x]'])[:-1:] for i in range(self.get_congestion()))
        
        try:
            for i in range(self.get_congestion()):
                index = str(str(self.buffer[i]['HISTORY[x]'])[::-1])[1::].index('>')                # Index of the last seperator
                recent_node_list.append(str(history_list[i])[len(history_list[i]) - index::])       # Perform string slice and return latest Node ID

            sorted_node_id_list = list(set(recent_node_list))   # Remove any duplicates

            # Append any new connections to the discovery list
            for node in sorted_node_id_list:        
                if node not in self.connections and node not in self.discovered_connections:
                    self.discovered_connections.append(node)

        except ValueError:
            """ Avoid a fail when the history is empty"""
            pass


    def get_duplicates(self) -> int:
        duplicate_messages = {}
        contains_duplicates = 0

        all_messages = list(self.buffer[i]['MESSAGE'] for i in range(self.get_congestion()))

        sorted_messages = list(set(all_messages))
        
        for key in sorted_messages:
            duplicate_messages[key] = ''

        for message_ in sorted_messages:
            contains_duplicates += all_messages.count(message_)-1
            duplicate_messages[message_] = all_messages.count(message_)-1
                
        return contains_duplicates, duplicate_messages


    def get_node_info(self) -> str:
        return(
            f'\nID -                         {self.node_id}\n' \
            f'IS_EMPTY? -                  {"YES" if self.get_congestion() == 0 else "NO"}\n' \
            f'CONNECTIONS -                {self.connections}\n' \
            f'DISCOVERED  -                {self.discovered_connections}\n...\n' \
            f'ACTIVITY: \n' \
            f'             /BUFFER:        {self.buffer}\n' \
            f'             /CONGESTION:    {self.get_congestion()}\n' \
            f'             /DUPLICATES:    {self.get_duplicates()}\n'
            )
    
    def node_info(self):
        return {
            "node_id": self.node_id,
            "empty":  r"{'YES' if self.get_congestion() == 0 else 'NO'}",
            "connections": self.connections
        }

def watch():
    total = 0
    while total != len(NODE_LIST):
        total = 0
        for x in range(len(NODE_LIST)):
            NODE_LIST[x].next_hop()
            print(NODE_LIST[x].get_node_info())
            if NODE_LIST[x].get_congestion() == 0: 
                total += 1



@app.route('/nodes', methods=['POST'])
def add_node():
    header = request.json['node_id']

    all_nodes = Node.query.all()

    for i in all_nodes:
        if header in i.node_id:
            return {"error": "node already created"}

    node = Node(node_id=header, connections=request.json['connections'])
    db.session.add(node)
    db.session.commit()
    NODE_LIST.append(Test(node_id=header, connections=request.json['connections']))
    return {"node_id":node.node_id, "connections":node.connections}


@app.route('/nodes/<node_id>', methods=['GET'])
def get_node(node_id):

    node = Node.query.get(node_id)
    if node is None: 
        return {"error":"node not found"}, 404      # alt; use get_or_404

    return {"node_id":node.node_id, "connections":node.connections}


@app.route('/nodes', methods=['GET'])
def get_nodes():
    nodes = Node.query.all()
    output = []

    for node in nodes:
        node_data = {"node_id":node.node_id, "connections":node.connections}
        output.append(node_data)
    
    return {"nodes": output}


@app.route('/nodes/<node_id>', methods=['DELETE'])
def delete_node(node_id):
    nodes = Node.query.get(node_id)

    if nodes is None:
        return {"error": "not found"}, 404  
    db.session.delete(nodes)
    db.session.commit()
    return {"message": f"node deleted"}, 200


@app.route('/nodes', methods=['DELETE'])
def delete_nodes():
    nodes = Node.query.all()

    if nodes:
        for node in nodes:
            db.session.delete(node)
            db.session.commit()
        return {"message": "all nodes deleted"}, 200
    return {"message": "no nodes to delete"}, 200


