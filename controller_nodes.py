"""
FILE:           controller_nodes.py
DESCRIPTION:
/nodes endpoints contained here.
/nodes/connections is also available here.
"""


from flask import request
from model_class_NodeModel import NodeModel
from model_class_NodeModel import *
from controller_class_NodeObj import *
from data_transfer_object import DataTransferObject as dto


"""
REQUEST STRUCTURE:
"node_id": "<str>",
"connections": "<str>"
NOTE: connections need ',' between each node_id connection. i.e. 'a,b,c,d'
"""
@app.route('/nodes', methods=['POST'])
def add_node():
    # Add a node to the session - will call model to add an instance to the database

    from main_app import NODE_LIST

    # Assign and Request 'node_id' from json request.
    node_id = request.json['node_id']

    # Query database to get object instances from the database
    all_nodes = NodeModel.get_all_items()

    # Check if the requested node is already with the database
    for db_node in all_nodes:
        if node_id == db_node.id:
            # CANCEL and return an error if the node is already in the database
            return dto.error_message("node already created") 
    
    # Call node model, add item
    NodeModel.add_item(node_id, request.json['connections'])

    # Get this new item from the database,
    node = NodeModel.get_item(node_id)

    # Append new item to the NODE_LIST in the form of a Node Object
    NODE_LIST.append(NodeObj(node_name=node.id, connections=str(node.connections).split(',')))

    return dto.nodeId_contents(node.id, node.connections)


@app.route('/nodes/<node_id>', methods=['PUT'])
def update_node_connections(node_id):
    # Update connections of a requested node

    from main_app import return_one_node_obj

    node_obj = return_one_node_obj(node_id)

    if type(node_obj).__name__ == 'dict':
        # Return the Error message 
        return node_obj
    else:
        node = NodeModel.get_item(node_id)      # db
        NodeModel.update_connection(node, request.json['connections'])
        node_obj.connections = str(request.json['connections']).split(',')

        return dto.good_message("node connection's updated")


@app.route('/nodes/<node_id>', methods=['GET'])
def get_node(node_id):
    # Get the node with its ID and Connections

    node = NodeModel.get_item(node_id)
    if node is None: 
        return dto.error_message("node not found") 
    return dto.nodeId_contents(node.id, node.connections)
 

@app.route('/nodes', methods=['GET'])
def get_nodes():
    # Get all the nodes with their IDs and connections

    nodes = NodeModel.get_all_items()
    output = []

    for node in nodes:
        node_data = {"node_id":node.id, "connections":node.connections}
        output.append(node_data)
    
    return {"nodes": output}


@app.route('/nodes/<node_id>', methods=['DELETE'])
def delete_node(node_id):
    # Delete requested node from the Database and NODE_LIST

    from main_app import NODE_LIST

    nodes = NodeModel.get_item(node_id)

    if nodes is None:
        return dto.error_message("node not found") 
    NodeModel.delete_item(nodes)

    # Look into the list 
    # See which ones id matches then delete
    for i in range(0, len(NODE_LIST)):
        if NODE_LIST[i].node_name == node_id:
            NODE_LIST.pop(i)
            break
        
    return dto.good_message("node deleted") 


@app.route('/nodes', methods=['DELETE'])
def delete_nodes():
    # Delete all nodes from database and clear the local NODE_LIST
    from main_app import clear_nodes

    nodes = NodeModel.get_all_items()

    if nodes:
        for node in nodes:
            NodeModel.delete_item(node)
        
        clear_nodes()

        return dto.good_message("all nodes deleted")
    return dto.error_message("no nodes to delete") 


@app.route('/nodes/connections')
def get_connections():
    # Present the connections of each node
    from main_app import NODE_LIST

    output = {}

    for i in range(0, len(NODE_LIST)):
        output[NODE_LIST[i].node_name] = NODE_LIST[i].connections
    return dto.good_message_as_dict(output)