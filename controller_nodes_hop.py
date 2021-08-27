from model_class_NodeModel import *
from controller_class_NodeObj import *
from data_transfer_object import DataTransferObject as dto

@app.route('/nodes/hop', methods=['GET'])
def next_hop():
    from main_app import NODE_LIST
    for i in range(len(NODE_LIST)):
        NODE_LIST[i].next_hop()
    return dto.good_message("one hop complete")


@app.route('/nodes/hop/<node_id>', methods=['GET'])
def next_node_hop(node_id):
    from main_app import return_one_node_obj

    node = return_one_node_obj(node_id)

    if type(node).__name__ == 'dict':
        # Return the Error message 
        return node
    else:
        node.next_hop()
        output = {
            "message": "one hop complete", 
            "congestion":f"{node.get_congestion()}"
            }
        return dto.good_message_as_dict(output)
