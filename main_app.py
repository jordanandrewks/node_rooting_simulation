import threading
import json
import time
from os import name
from flask import Flask, request
from flask.scaffold import F
from flask_sqlalchemy import SQLAlchemy
from model_class_NodeModel import NodeModel
from model_class_NodeModel import *
from controller_class_NodeObj import NodeObj
from controller_class_NodeObj import NODE_LIST

WATCH_FLAG = False
STOP_LIMIT = 0


def load_nodes():

    nodes = NodeModel.get_all_items()
    for node in nodes:
        NODE_LIST.append(NodeObj(node_name=node.id, connections=str(node.connections).split(',')))


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
    node_id = request.json['node_id']

    all_nodes = NodeModel.get_all_items()

    for i in all_nodes:
        if node_id == i.id:
            return {"error": "node already created"}
    
    NodeModel.add_item(node_id, request.json['connections'])

    node = NodeModel.get_item(node_id)

    NODE_LIST.append(NodeObj(node_name=node.id, connections=str(node.connections).split(',')))

    return {"node_id":node.id, "connections":node.connections}


@app.route('/nodes/<node_id>', methods=['PUT'])
def update_node_connections(node_id):

    node_obj = return_one_node_obj(node_id)

    if type(node_obj).__name__ == 'dict':
        # Return the Error message 
        return node_obj
    else:

        node = NodeModel.get_item(node_id)      # db
        
        NodeModel.update_connection(node, request.json['connections'])

        node_obj.connections = str(request.json['connections']).split(',')

        return {"message":"node connection's updated"}



@app.route('/nodes/<node_id>', methods=['GET'])
def get_node(node_id):

    node = NodeModel.get_item(node_id)
    if node is None: 
        return {"error":"node not found"}, 404      # alt; use get_or_404

    return {"node_id":node.node_id, "connections":node.connections}
 

@app.route('/nodes', methods=['GET'])
def get_nodes():
    nodes = NodeModel.get_all_items()
    output = []

    for node in nodes:
        node_data = {"node_id":node.id, "connections":node.connections}
        output.append(node_data)
    
    return {"nodes": output}


@app.route('/nodes/<node_id>', methods=['DELETE'])
def delete_node(node_id):
    nodes = NodeModel.get_item(node_id)

    if nodes is None:
        return {"error": "not found"}, 404  
    NodeModel.delete_item(nodes)

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

    nodes = NodeModel.get_all_items()

    if nodes:
        for node in nodes:
            NodeModel.delete_item(node)
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