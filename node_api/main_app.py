
import re
import threading
import json
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

DATA_PACKET = {
    'hop_lim': 5,
    'history': '',
    'message': ''
}

# Next Steps:
# - Link Inject Packet function COMPLETE
# - 

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






def load_nodes():
    try:
        nodes = Node.query.all()
        output = []
        for node in nodes:
            NODE_LIST.append(NodeAsset(node_name=node.node_id, connections=str(node.connections).split(',')))
    except SQLAlchemy.exc.OperationalError:
        print('No DataBase')



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
def debugger():
    print('LENGTH OF NODE LIST =======', len(NODE_LIST))
    output = {}
    for i in range(0, len(NODE_LIST)):
        print(f'<<<<<<<<<?>>>>', NODE_LIST[i].node_name, NODE_LIST[i].connections)
        output[NODE_LIST[i].node_name] = NODE_LIST[i].connections
    return output



"""
Structure___

"hop_lim": "something",
"message": "something"

"""

@app.route('/nodes/buffer/<node_id>', methods=['PUT', 'POST'])
def inject_data_packet(node_id):
    
    if len(NODE_LIST):
        try:
            nodes = []
            message = ''
            index = False

            # Expect KeyError in case of an empty message
            try:
                message = request.json['message']
            except KeyError:
                pass

            hop_limit = int(request.json['hop_lim'])        

            # Extract all node names
            for node in NODE_LIST:
                nodes.append(node.node_name)
                if node.node_name == node_id:
                    break

            # Find the index location of the node_id in the list
            try:
                index = nodes.index(node_id)
                NODE_LIST[index].inject_packet({
                        "hop_lim": int(hop_limit),
                        "history": "",
                        "message": str(message)
                        })
                print(NODE_LIST[index].buffer)
                return {"message": "packet added"}, 200
            except ValueError:
                return {"error": "node not found"}
        except ValueError:
            return {"error": "non integer values entered for hop_lim"}
    return {"error": "no nodes"}




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
            node_buffer = NODE_LIST[index].buffer
            print(node_buffer)
            return {f"{node_id}":node_buffer}
        except:
            return {"error": "node not found"}
    return {"error": "no nodes"}


@app.route('/nodes/buffer/<node_id>', methods=['DELETE'])
def clear_node_buffer(node_id):
    global NODE_LIST
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
            NODE_LIST[index].buffer = []
            return {"message":"buffer cleared"}
        except:
            return {"error": "node not found"}
    return {"error": "no nodes"}


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
            NODE_LIST[index].next_hop()
            print(NODE_LIST[index].buffer)
            return {"message": "one hop complete", "congestion":f"{NODE_LIST[index].get_congestion()}"}
        except:
            return {"error": "node not found"}


    return {"error": "no nodes"}



"""
Should present the following:

node_name:
connections:
discovered_nodes:
total_sent:
total_received:
congestion:
"""
@app.route('/nodes/status/<node_id>', methods=['GET'])
def get_node_status(node_id):
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
            node_ = NODE_LIST[index]
            return {
                f"id": f"{node_id}",
                f"connections": f"{node_.connections}",
                f"discovered": f"{node_.discovered_connections}",
                f"total_sent": f"{node_.transmitted}",
                f"total_received": f"{node_.received}",
                f"congestion": f"{node_.get_congestion()}"
                }
        except:
            return {"error": "node not found"}
    return {"error": "no nodes"}


@app.route('/nodes/status', methods=['GET'])
def get_nodes_status():
    pass



"""
Should return:
- congestion only
"""
@app.route('/nodes/congestion/<node_id>', methods=['GET'])
def get_node_congestion(node_id):
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
            congestion = NODE_LIST[index].get_congestion()
            return {f"{node_id}":congestion}
        except:
            return {"error": "node not found"}
    return {"error": "no nodes"}
    

@app.route('/nodes/congestion', methods=['GET'])
def get_congestion():
    output = {}
    # Extract all node names
    if len(NODE_LIST):
        for node in NODE_LIST:
            output[node.node_name] = node.get_congestion()
        return output
    return {"error": "no nodes"}



def watch():
    global WATCH_FLAG
    total = 0
    count = 0

    while total != len(NODE_LIST) and count != STOP_LIMIT and WATCH_FLAG:
        total = 0
        count += 1
        print(count, STOP_LIMIT) 
        for x in range(len(NODE_LIST)):
            NODE_LIST[x].next_hop()
            if NODE_LIST[x].get_congestion() == 0: 
                total += 1

    WATCH_FLAG = False



@app.route('/simulate/start', methods=['POST'])
def start_simulation():
    global WATCH_FLAG
    global STOP_LIMIT

    WATCH_FLAG = True
    STOP_LIMIT = 0

    try:
        # Return a valid number
        STOP_LIMIT = int(request.json['stop_lim'])
    except ValueError:
        # Return false value... i.e. Continue until done
        STOP_LIMIT = -1

    x = threading.Thread(target=watch)
    x.start()
    return {"message":"simulation running"}

@app.route('simulate/start', methods=['PUT'])
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
