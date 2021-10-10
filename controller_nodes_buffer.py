"""
FILE:           controller_nodes_buffer.py
DESCRIPTION:
/nodes/buffer endpoints located here.
"""

from flask import request
from model_class_NodeModel import *
from controller_class_NodeObj import *
from data_transfer_object import DataTransferObject as dto

"""
REQUEST STRUCTURE:
"hop_lim": "something",
"message": "something"
"""
@app.route('/nodes/buffer/<node_id>', methods=['PUT', 'POST'])
def inject_data_packet(node_id):
    from main_app import return_one_node_obj
    
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
            
            return dto.good_message("packet added")

    except ValueError:
        return dto.error_message("non integer values entered for hop_lim")


@app.route('/nodes/buffer', methods=['GET'])
def get_all_buffer():
    from main_app import NODE_LIST

    output = {}

    # Extract all node names
    if len(NODE_LIST):
        for node in NODE_LIST:
            output[node.node_name] = node.buffer
        return dto.good_message_as_dict(output)
    return dto.error_message("no nodes")


@app.route('/nodes/buffer/<node_id>', methods=['GET'])
def get_nodes_buffer(node_id):
    from main_app import return_one_node_obj

    node = return_one_node_obj(node_id)

    if type(node).__name__ == 'dict':
        # Return the Error message 
        return node
    else:
        return dto.nodeId_contents(node_id, node.buffer)


@app.route('/nodes/buffer/<node_id>', methods=['DELETE'])
def clear_node_buffer(node_id):
    from main_app import return_one_node_obj

    node = return_one_node_obj(node_id)

    if type(node).__name__ == 'dict':
        # Return the Error message 
        return node
    else:
        node.buffer = []
        return dto.good_message("buffer cleared")


@app.route('/nodes/buffer', methods=['DELETE'])
def clear_all_buffers():
    from main_app import NODE_LIST
    
    # Extract all node names
    if len(NODE_LIST):
        for node in NODE_LIST:
            node.buffer = []
        return dto.good_message("all buffers cleared")
    return dto.error_message("no nodes")
