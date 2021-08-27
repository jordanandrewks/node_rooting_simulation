from flask import request
from model_class_NodeModel import NodeModel
from model_class_NodeModel import *
from controller_class_NodeObj import *
from data_transfer_object import DataTransferObject as dto


@app.route('/nodes', methods=['POST'])
def add_node():
    from main_app import NODE_LIST

    node_id = request.json['node_id']

    all_nodes = NodeModel.get_all_items()

    for i in all_nodes:
        if node_id == i.id:
            return dto.error_message("node already created") 
    
    NodeModel.add_item(node_id, request.json['connections'])
    node = NodeModel.get_item(node_id)
    NODE_LIST.append(NodeObj(node_name=node.id, connections=str(node.connections).split(',')))

    return dto.nodeId_contents(node.id, node.connections)


@app.route('/nodes/<node_id>', methods=['PUT'])
def update_node_connections(node_id):
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

    node = NodeModel.get_item(node_id)
    if node is None: 
        return dto.error_message("node not found") 
    return dto.nodeId_contents(node.id, node.connections)
 

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
    from main_app import NODE_LIST

    output = {}

    for i in range(0, len(NODE_LIST)):
        output[NODE_LIST[i].node_name] = NODE_LIST[i].connections
    return dto.good_message_as_dict(output)