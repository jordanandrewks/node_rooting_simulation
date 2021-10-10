"""
FILE:           main_app.py
DESCRIPTION:
Main file used to load out of the database,
and run threads for simulation tasks.
"""

import threading
from model_class_NodeModel import *
from controller_nodes import *
from controller_nodes_buffer import *
from controller_nodes_congestion import *
from controller_nodes_hop import *
from controller_nodes_status import *
from controller_simulate import *
from data_transfer_object import DataTransferObject as dto

# Globals
NODE_LIST = []          # Store database instances that have been converted into NodeObj classes.
THREAD_FLAG = False      # Thread run/stop flag -> most relevant in def watch()
STOP_LIMIT = 0          # Thread iteration limit -> most relevant in def watch()


def clear_nodes() -> None:
    NODE_LIST = []

def load_nodes() -> None:
    # USAGE - Load Node instances from local database

    nodes = NodeModel.get_all_items()
    for node in nodes:
        NODE_LIST.append(NodeObj(node_name=node.id, connections=str(node.connections).split(',')))


def return_one_node_obj(node_id):
    # USAGE - 

    nodes = []
    # Extract all node names
    if len(NODE_LIST):
        for node in NODE_LIST:
            nodes.append(node.node_name)
            # Break here if the node_id is found
            if node.node_name == node_id:
                break

        # Find the index location of the node_id in the list
        try:
            index = nodes.index(node_id)

            # Send back the object -> class
            return NODE_LIST[index]     
        except:
            # Send back a DTO response
            return dto.error_message("node not found")
    return dto.error_message("no nodes")


def watch():
    global THREAD_FLAG
    total = 0
    count = 0

    # Loop if any nodes are congested, stop limit not reached and watch flag is active
    while total != len(NODE_LIST) and count != STOP_LIMIT and THREAD_FLAG:
        total = 0
        count += 1
        print(count, STOP_LIMIT)                #  Debug purposes only
        for i in range(len(NODE_LIST)):     
            NODE_LIST[i].next_hop()             # Perform a next hop on the node in focus
            if NODE_LIST[i].get_congestion() == 0: 
                total += 1
            if THREAD_FLAG == False:
                break
    
    # Reset the flag
    THREAD_FLAG = False


def set_flag(bool):
    global THREAD_FLAG
    THREAD_FLAG = bool

def get_flag():
    return THREAD_FLAG

def set_stop_limit(stop_lim_int):
    global STOP_LIMIT
    STOP_LIMIT = stop_lim_int

def get_stop_limit():
    return THREAD_FLAG

def open_simulation_thread():
    simulate_thread = threading.Thread(target=watch)
    simulate_thread.start()


if __name__ == "main_app":
    load_nodes()
