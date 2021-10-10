"""
FILE:           controller_nodes_congestion.py
DESCRIPTION:
/nodes/congestion endpoints contained here.
"""

from model_class_NodeModel import *
from controller_class_NodeObj import *
from data_transfer_object import DataTransferObject as dto

@app.route('/nodes/congestion/<node_id>', methods=['GET'])
def get_node_congestion(node_id):
    from main_app import return_one_node_obj

    node = return_one_node_obj(node_id)

    if type(node).__name__ == 'dict':
        # Return the Error message 
        return node
    else:
        return dto.nodeId_contents(node_id, node.get_congestion())
    

@app.route('/nodes/congestion', methods=['GET'])
def get_congestion():
    from main_app import NODE_LIST

    output = {}

    # Extract all node names
    if len(NODE_LIST):
        for node in NODE_LIST:
            output[node.node_name] = node.get_congestion()
        return dto.good_message_as_dict(output)
    return dto.error_message("no nodes")