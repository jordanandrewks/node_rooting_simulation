#!/usr/bin/python3

import builtins
import time
import sys
import datetime
import collections
import math
from typing import Dict



# instance methods
# class methods
# static methods

DATA_PACKET = {
    'HOP_LIM': 5,
    'HISTORY[x]': '',
    'MESSAGE': ''
}

def set_data() -> Dict:
    for key in list(DATA_PACKET.keys()):
        if '[x]' not in key: 
            needed_type = type(DATA_PACKET[key]).__name__
            print('--')
            usr_input = input(f'ENTER - {key}: >>\t')
            evaluate_str = eval(f"{needed_type}('{usr_input}')") 
            DATA_PACKET[key] = evaluate_str


    return DATA_PACKET

NODE_LIST = []


# Accesor Methods - Fetch value USE 'get_' for fetching
# Mutator Methods - Modify a value USE 'set_' for modifying something 

# Extra function make it so that an object is self aware that it knows when another node has made a connection

if __name__ == '__main__':

    class Node:

        def __init__(self, node_id: str, connections: list) -> None:
            '''instances variables are initialized here'''

            # Instance variables
            self.node_id = node_id
            self.connections = connections
            self.buffer = []
            self.duplication_activity = []


        def inject_packet(self, packet: dict):
            """Pass in the first packet"""
            self.buffer.append(packet.copy())


        def get_connected_node_obj(self):
            """ return the object of the node"""
            count = 0
            for connected_node in self.connections:
                for index, node_obj in enumerate(list(NODE_LIST)):
                    if connected_node is node_obj.node_id:
                        count += 1
                        # yield index, node_obj.node_id
                        yield index


        def next_hop(self):
            """ Send the packet to the next connections"""  
            print("I am <{}> and I'm connected to {}". format(self.node_id, self.connections))
    
            if self.buffer:     # Check if there's anything in THIS nodes buffer

                self.buffer[0]['HISTORY[x]'] += self.node_id + '>'
                self.buffer[0]['HOP_LIM'] -= 1

                for node_index in list(self.get_connected_node_obj()):

                    if self.buffer[0]['HOP_LIM'] >= 0:
                        NODE_LIST[node_index].buffer.append(self.buffer[0].copy())         # Move value to the next object

                self.buffer.pop(0)                                  # Remove this value from this object


        def get_congestion(self) -> int:
            return len(self.buffer)


        def get_duplicates(self) -> int:
            x = []

            for i in range(0, self.get_congestion()):
                x.append(self.buffer[i]['HISTORY[x]'])

            contains_duplicates = 0

            for j in range(self.get_congestion()):
                contains_duplicates += x.count(x[j])-1 if x.count(x[j]) > 1 else 0

            return contains_duplicates, x


        def get_node_info(self) -> str:
            return(
                f'\nID -                         {self.node_id}\n' \
                f'IS_EMPTY? -                  {"YES" if self.get_congestion() == 0 else "NO"}\n' \
                f'CONNECTIONS -                {self.connections}\n...\n' \
                f'ACTIVITY: \n' \
                f'             /BUFFER:        {self.buffer}\n' \
                f'             /CONGESTION:    {self.get_congestion()}\n' \
                f'             /DUPLICATES:    {self.duplication_activity}\n'
                )

    
    packet_handler = []

    NODE_LIST.append(Node('A', ['B', 'C']))
    NODE_LIST.append(Node('B', ['C', 'A']))
    NODE_LIST.append(Node('C', ['A', 'B', 'D']))
    NODE_LIST.append(Node('D', ['A', 'B']))

    print(list(NODE_LIST[0].get_connected_node_obj()))

    debug = True

    if debug:
        print('########################################################### - NOTHING')
        print('>>>>>>>>>>>>>>', NODE_LIST[0].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[1].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[2].get_node_info())

        print('########################################################### - INJECT HELLO PACKET')

        NODE_LIST[0].inject_packet(set_data())
        print('>>>>>>>>>>>>>>', NODE_LIST[0].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[1].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[2].get_node_info())

        print('########################################################### - MOVE HELLO PACKET')
        NODE_LIST[0].next_hop()     # Should be in node b's buffer

        print('>>>>>>>>>>>>>>', NODE_LIST[0].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[1].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[2].get_node_info())


        print('########################################################### - MOVE HELLO PACKET')
        NODE_LIST[1].next_hop()     # Should be in node b's buffer

        print('>>>>>>>>>>>>>>', NODE_LIST[0].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[1].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[2].get_node_info())


        print('########################################################### - MOVE HELLO PACKET')
        NODE_LIST[2].next_hop()     # Should be in node b's buffer

        print('>>>>>>>>>>>>>>', NODE_LIST[0].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[1].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[2].get_node_info())

        print('########################################################### - MOVE HELLO PACKET')
        NODE_LIST[2].next_hop()     # Should be in node b's buffer

        print('>>>>>>>>>>>>>>', NODE_LIST[0].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[1].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[2].get_node_info())



        print('########################################################### - MOVE HELLO PACKET')
        NODE_LIST[1].next_hop()     # Should be in node b's buffer

        print('>>>>>>>>>>>>>>', NODE_LIST[0].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[1].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[2].get_node_info())



        print('########################################################### - MOVE HELLO PACKET')
        NODE_LIST[1].next_hop()     # Should be in node b's buffer

        print('>>>>>>>>>>>>>>', NODE_LIST[0].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[1].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[2].get_node_info())

        print('########################################################### - MOVE HELLO PACKET')
        NODE_LIST[0].next_hop()     # Should be in node b's buffer

        print('>>>>>>>>>>>>>>', NODE_LIST[0].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[1].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[2].get_node_info())

        print('########################################################### - MOVE HELLO PACKET')
        NODE_LIST[1].next_hop()     # Should be in node b's buffer

        print('>>>>>>>>>>>>>>', NODE_LIST[0].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[1].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[2].get_node_info())

        print('########################################################### - MOVE HELLO PACKET')
        NODE_LIST[2].next_hop()     # Should be in node b's buffer

        print('>>>>>>>>>>>>>>', NODE_LIST[0].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[1].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[2].get_node_info())

        print('########################################################### - MOVE HELLO PACKET')
        NODE_LIST[2].next_hop()     # Should be in node b's buffer

        NODE_LIST[0].inject_packet(set_data())
        NODE_LIST[0].inject_packet(set_data())
        print('>>>>>>>>>>>>>>', NODE_LIST[0].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[1].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[2].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[3].get_node_info())

        print(NODE_LIST[0].get_duplicates())

        
