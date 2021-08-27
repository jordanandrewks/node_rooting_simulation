from model_class_NodeModel import *
from data_transfer_object import DataTransferObject as dto


@app.route('/nodes/status/<node_id>', methods=['GET'])
def get_node_status(node_id):
    from main_app import return_one_node_obj

    node = return_one_node_obj(node_id)

    if type(node).__name__ == 'dict':
        # Return the Error message 
        return node
    else:
        return dto.good_message_as_dict(node.get_status())


@app.route('/nodes/status', methods=['GET'])
def get_nodes_status():
    from main_app import NODE_LIST
    
    output = {}

    # Extract all node names
    if len(NODE_LIST):
        for node in NODE_LIST:
            output[node.node_name] = node.get_status()
        return dto.good_message_as_dict(output)
    return dto.error_message("no nodes")