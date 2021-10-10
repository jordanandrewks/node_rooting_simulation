"""
FILE:           controller_nodes_hop.py
DESCRIPTION:
/nodes/hop endpoints located here.
Make a node OR Nodes send data to the other nodes they're connected to.
"""


from model_class_NodeModel import *
from controller_class_NodeObj import *
from data_transfer_object import DataTransferObject as dto


@app.route('/nodes/hop', methods=['GET'])
def next_hop():
    # Make each node send data to it's connections 1 time.

    from main_app import NODE_LIST     

    for i in range(len(NODE_LIST)):
        NODE_LIST[i].next_hop()
    return dto.good_message("all nodes have performed 1 data hop")


@app.route('/nodes/hop/<node_id>', methods=['GET'])
def next_node_hop(node_id):
    # Make a single node send data to it's connections 1 time.
    
    from main_app import return_one_node_obj

    # Grab the Object of the node we want to access.
    node = return_one_node_obj(node_id)

    if type(node).__name__ == 'dict':
        # Return the Error message 
        return node
    else:
        node.next_hop()     # call the next hop function on this object.
        output = {
            "message": "one hop complete", 
            "congestion":f"{node.get_congestion()}"
            }
        return dto.good_message_as_dict(output)
