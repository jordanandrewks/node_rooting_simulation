"""
FILE:           controller_nodes_status.py
DESCRIPTION:
/nodes/status endpoints located here.
The status and statistics of each node will be presented.
"""


from model_class_NodeModel import *
from data_transfer_object import DataTransferObject as dto



@app.route('/nodes/status/<node_id>', methods=['GET'])
def get_node_status(node_id):
    from main_app import return_one_node_obj

    # Grab the Object of the node we want to access.
    node = return_one_node_obj(node_id)

    if type(node).__name__ == 'dict':
        # Return the Error message from node 
        return node 
    else:
        # Return the status from the node object
        return dto.good_message_as_dict(node.get_status())


@app.route('/nodes/status', methods=['GET'])
def get_nodes_status():
    from main_app import NODE_LIST
    
    output = {}

    if len(NODE_LIST):

        # For each object get the status
        for node in NODE_LIST:
            output[node.node_name] = node.get_status()
        
        return dto.good_message_as_dict(output)
    return dto.error_message("no nodes")