import threading
import json
import time
from os import name
from flask import Flask, request
from flask.scaffold import F
from flask_sqlalchemy import SQLAlchemy

WATCH_FLAG = False
STOP_LIMIT = 0

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

NODE_LIST = []

class Node(db.Model):

    # id = db.Column(db.String(80), unique=True, primary_key=True, nullable=False)
    node_id = db.Column(db.String(80), primary_key=True, unique=True, nullable=False)    
    connections = db.Column(db.String(80), nullable=False)


    def __repr__(self) -> str:
        return f"{self.node_id} - {self.connections}"


class NodeAsset:

    def __init__(self, node_name: str, connections: list) -> None:
        '''instances variables are initialized here'''

        # Instance variables
        self.node_name = node_name
        self.connections = connections
        self.discovered_connections = []
        self.buffer = []
        self.null_list = []
        self.transmitted = 0
        self.received = 0

    def reset(self):
        self.buffer = []
        self.null_list = []
        self.transmitted = 0
        self.received = 0

    def inject_packet(self, packet: dict):
        """Pass in the first packet"""
        self.buffer.append(packet.copy())


    def get_connected_node_obj(self):
        """ return the object of the node"""
        count = 0
        for connected_node in self.connections:
            for index, node_obj in enumerate(list(NODE_LIST)):
                if connected_node is node_obj.node_name:
                    count += 1
                    yield index


    def find_depleted_packets(self):
        self.null_list = []
        for c in range(0, len(self.buffer)):
            if self.buffer[c]['hop_lim'] == 0:
                self.null_list.append(c)
        

    def remove_depleted_packets(self):
        for decrement, packet_index in enumerate(self.null_list):
            self.buffer.pop(packet_index - decrement) 


    def next_hop(self):
        """ Send the packet to the next connections"""  

        self.get_new_connections()
        self.find_depleted_packets()
        self.remove_depleted_packets()

        if self.buffer:     # Check if there's anything in THIS nodes buffer

            self.buffer[0]['history'] += self.node_name + '>'
            self.buffer[0]['hop_lim'] -= 1

            for node_index in list(self.get_connected_node_obj()):
                if self.buffer[0]['hop_lim'] >= 0:
                    NODE_LIST[node_index].buffer.append(self.buffer[0].copy())         # Move value to the next object
                    NODE_LIST[node_index].received += 1        
                    self.transmitted += 1

            self.buffer.pop(0)                                  # Remove this value from this object


    def get_congestion(self) -> int:
        return len(self.buffer)
    

    def get_new_connections(self):

        recent_node_list = []
        history_list = list(str(self.buffer[i]['history'])[:-1:] for i in range(self.get_congestion()))
        
        try:
            for i in range(self.get_congestion()):
                index = str(str(self.buffer[i]['history'])[::-1])[1::].index('>')                # Index of the last seperator
                recent_node_list.append(str(history_list[i])[len(history_list[i]) - index::])       # Perform string slice and return latest Node ID

            sorted_node_name_list = list(set(recent_node_list))   # Remove any duplicates

            # Append any new connections to the discovery list
            for node in sorted_node_name_list:        
                if node not in self.connections and node not in self.discovered_connections:
                    self.discovered_connections.append(node)

        except ValueError:
            """ Avoid a fail when the history is empty"""
            pass


    def get_duplicates(self) -> int:
        duplicate_messages = {}
        contains_duplicates = 0

        all_messages = list(self.buffer[i]['message'] for i in range(self.get_congestion()))

        sorted_messages = list(set(all_messages))
        
        for key in sorted_messages:
            duplicate_messages[key] = ''

        for message_ in sorted_messages:
            contains_duplicates += all_messages.count(message_)-1
            duplicate_messages[message_] = all_messages.count(message_)-1
                
        return contains_duplicates, duplicate_messages

    def get_status(self) -> dict:
        return {
            f"id": f"{self.node_name}",
            f"connections": f"{self.connections}",
            f"discovered": f"{self.discovered_connections}",
            f"total_sent": f"{self.transmitted}",
            f"total_received": f"{self.received}",
            f"congestion": f"{self.get_congestion()}"
            }


def load_nodes():
    try:
        nodes = Node.query.all()
        output = []
        for node in nodes:
            NODE_LIST.append(NodeAsset(node_name=node.node_id, connections=str(node.connections).split(',')))
    except SQLAlchemy.exc.OperationalError:
        print('No DataBase')


def return_one_node_obj(node_id):
    nodes = []
    # Extract all node names
    if len(NODE_LIST):
        for node in NODE_LIST:
            nodes.append(node.node_name)
            # Break here if found 
            if node.node_name == node_id:
                break
        # Find the index location of the node_id in the list
        try:
            index = nodes.index(node_id)
            return NODE_LIST[index]
        except:
            return {"error": "node not found"}
    return {"error": "no nodes"}


def watch():
    global WATCH_FLAG
    total = 0
    count = 0

    while total != len(NODE_LIST) and count != STOP_LIMIT and WATCH_FLAG:
        total = 0
        count += 1
        print(count, STOP_LIMIT) 
        for i in range(len(NODE_LIST)):
            NODE_LIST[i].next_hop()
            if NODE_LIST[i].get_congestion() == 0: 
                total += 1
            if WATCH_FLAG == False:
                break

    WATCH_FLAG = False


@app.route('/nodes', methods=['POST'])
def add_node():
    header = request.json['node_id']

    all_nodes = Node.query.all()

    for i in all_nodes:
        if header == i.node_id:
            return {"error": "node already created"}

    node = Node(node_id=header, connections=request.json['connections'])
    
    db.session.add(node)
    db.session.commit()

    NODE_LIST.append(NodeAsset(node_name=node.node_id, connections=str(node.connections).split(',')))

    return {"node_id":node.node_id, "connections":node.connections}


@app.route('/nodes/<node_id>', methods=['PUT'])
def update_node_connections(node_id):

    node_obj = return_one_node_obj(node_id)

    if type(node_obj).__name__ == 'dict':
        # Return the Error message 
        return node_obj
    else:

        node = Node.query.filter_by(node_id=node_id).first()
        
        node.connections = request.json['connections']
        
        db.session.commit()

        node_obj.connections = str(request.json['connections']).split(',')

        return {"message":"node connection's updated"}




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

    # Look into the list 
    # See which ones id matches then delete
    for i in range(0, len(NODE_LIST)):
        if NODE_LIST[i].node_name == node_id:
            NODE_LIST.pop(i)
            break
        
    return {"message": f"node deleted"}, 200


@app.route('/nodes', methods=['DELETE'])
def delete_nodes():
    global NODE_LIST
    nodes = Node.query.all()

    if nodes:
        for node in nodes:
            db.session.delete(node)
            db.session.commit()
        NODE_LIST = []      
        return {"message": "all nodes deleted"}, 200
    return {"message": "no nodes to delete"}, 200


@app.route('/nodes/connections')
def get_connections():

    output = {}

    for i in range(0, len(NODE_LIST)):
        output[NODE_LIST[i].node_name] = NODE_LIST[i].connections
    return output


"""
Structure___
"hop_lim": "something",
"message": "something"
"""
@app.route('/nodes/buffer/<node_id>', methods=['PUT', 'POST'])
def inject_data_packet(node_id):
    
    message = ''

    try:
        hop_limit = int(request.json['hop_lim'])  

        # Expect KeyError in case of an empty message
        try:
            message = request.json['message']
        except KeyError:
            pass

        node = return_one_node_obj(node_id)

        if type(node).__name__ == 'dict':
            # Return the Error message 
            return node
        else:

            node.inject_packet({
                "hop_lim": int(hop_limit),
                "history": "",
                "message": str(message)
                })
            
            return {"message": "packet added"}, 200

    except ValueError:
        return {"error": "non integer values entered for hop_lim"}


@app.route('/nodes/buffer', methods=['GET'])
def get_all_buffer():

    output = {}

    # Extract all node names
    if len(NODE_LIST):
        for node in NODE_LIST:
            output[node.node_name] = node.buffer
        return output
    return {"error": "no nodes"}


@app.route('/nodes/buffer/<node_id>', methods=['GET'])
def get_nodes_buffer(node_id):

    node = return_one_node_obj(node_id)

    if type(node).__name__ == 'dict':
        # Return the Error message 
        return node
    else:
        return {f"{node_id}":node.buffer}


@app.route('/nodes/buffer/<node_id>', methods=['DELETE'])
def clear_node_buffer(node_id):

    node = return_one_node_obj(node_id)

    if type(node).__name__ == 'dict':
        # Return the Error message 
        return node
    else:
        node.buffer = []
        return {"message":"buffer cleared"}


@app.route('/nodes/buffer', methods=['DELETE'])
def clear_all_buffers():
    global NODE_LIST
    # Extract all node names
    if len(NODE_LIST):
        for node in NODE_LIST:
            node.buffer = []
        return {"message":"all buffers cleared"}
    return {"error": "no nodes"}


@app.route('/nodes/hop', methods=['GET'])
def next_hop():
    for i in range(len(NODE_LIST)):
                NODE_LIST[i].next_hop()
    return {"message": "one hop complete"}


@app.route('/nodes/hop/<node_id>', methods=['GET'])
def next_node_hop(node_id):

    node = return_one_node_obj(node_id)

    if type(node).__name__ == 'dict':
        # Return the Error message 
        return node
    else:
        node.next_hop()
        return {
            "message": "one hop complete", 
            "congestion":f"{node.get_congestion()}"
            }


@app.route('/nodes/status/<node_id>', methods=['GET'])
def get_node_status(node_id):

    node = return_one_node_obj(node_id)

    if type(node).__name__ == 'dict':
        # Return the Error message 
        return node
    else:
        return node.get_status()


@app.route('/nodes/status', methods=['GET'])
def get_nodes_status():
    
    output = {}

    # Extract all node names
    if len(NODE_LIST):
        for node in NODE_LIST:
            output[node.node_name] = node.get_status()
        return output
    return {"error": "no nodes"}


@app.route('/nodes/congestion/<node_id>', methods=['GET'])
def get_node_congestion(node_id):

    node = return_one_node_obj(node_id)

    if type(node).__name__ == 'dict':
        # Return the Error message 
        return node
    else:
        return {"congestion":f"{node.get_congestion()}"}
    

@app.route('/nodes/congestion', methods=['GET'])
def get_congestion():

    output = {}

    # Extract all node names
    if len(NODE_LIST):
        for node in NODE_LIST:
            output[node.node_name] = node.get_congestion()
        return output
    return {"error": "no nodes"}


open_threads = []

@app.route('/simulate/start', methods=['POST'])
def start_simulation():
    global WATCH_FLAG
    global STOP_LIMIT

    # Close the thread if it's open
    if WATCH_FLAG:
        WATCH_FLAG = False

    time.sleep(1)
    
    WATCH_FLAG = True
    STOP_LIMIT = 0

    try:
        # Return a valid number
        STOP_LIMIT = int(request.json['stop_lim'])
    except ValueError:
        # Return false value... i.e. Continue until done
        STOP_LIMIT = -1


    simulate_thread = threading.Thread(target=watch)
    simulate_thread.start()

    return {"message":"simulation running"}


@app.route('/simulate/start', methods=['PUT'])
def update_stop_limit():
    global STOP_LIMIT
    STOP_LIMIT = request.json['stop_lim']
    return {"message": "stop limit updated"}


"""Return Total Time spent"""
@app.route('/simulate/stop', methods=['GET'])
def stop_simulation():
    global WATCH_FLAG
    WATCH_FLAG = False
    return {"message":"simulation stop"}


load_nodes()