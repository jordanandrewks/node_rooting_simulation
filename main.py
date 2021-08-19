#!/usr/bin/python3

import builtins
import time
import sys
import datetime


# instance methods
# class methods
# static methods

DATA_PACKET = {
    'HOP_LIM': 5,
    'HISTORY[x]': '',
    'MESSAGE': ''
}

def set_data() -> dict:
    for key in list(DATA_PACKET.keys()):
        if '[x]' not in key: 
            needed_type = type(DATA_PACKET[key]).__name__
            print('--')
            usr_input = input(f'ENTER - {key}: >>\t')
            evaluate_str = eval(f"{needed_type}('{usr_input}')") 
            DATA_PACKET[key] = evaluate_str


    return DATA_PACKET

NODE_LIST = []


# Accessor Methods - Fetch value USE 'get_' for fetching
# Mutator Methods - Modify a value USE 'set_' for modifying something 

# Extra function make it so that an object is self aware that it knows when another node has made a connection

if __name__ == '__main__':

    class Node:

        def __init__(self, node_id: str, connections: list) -> None:
            '''instances variables are initialized here'''

            # Instance variables
            self.node_id = node_id
            self.connections = connections
            self.discovered_connections = []
            self.buffer = []


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
        
        def get_new_connections(self) -> list:

            test = []
            temp = []

            all_messages = list(str(self.buffer[i]['HISTORY[x]'])[:-1:] for i in range(self.get_congestion()))

            for i in range(self.get_congestion()):
                history_length = len(str(self.buffer[i]['HISTORY[x]']))
                index = str(str(self.buffer[i]['HISTORY[x]'])[::-1])[1::].index('>')
                test.append(str(all_messages[i])[len(all_messages[i]) - index::])

            sorted_messages = list(set(test))

            for val in sorted_messages:
                if val not in self.connections:
                    temp.append(val)
            
            self.discovered_connections = temp


        def get_duplicates(self) -> int:
            duplicate_messages = {}
            contains_duplicates = 0

            all_messages = list(self.buffer[i]['MESSAGE'] for i in range(self.get_congestion()))

            sorted_messages = list(set(all_messages))
            
            for key in sorted_messages:
                duplicate_messages[key] = ''

            for message_ in sorted_messages:
                contains_duplicates += all_messages.count(message_)-1
                duplicate_messages[message_] = all_messages.count(message_)-1
                    
            return contains_duplicates, duplicate_messages


        def get_node_info(self) -> str:
            return(
                f'\nID -                         {self.node_id}\n' \
                f'IS_EMPTY? -                  {"YES" if self.get_congestion() == 0 else "NO"}\n' \
                f'CONNECTIONS -                {self.connections}\n' \
                f'DISCOVERED  -                {self.discovered_connections}\n...\n' \
                f'ACTIVITY: \n' \
                f'             /BUFFER:        {self.buffer}\n' \
                f'             /CONGESTION:    {self.get_congestion()}\n' \
                f'             /DUPLICATES:    {self.get_duplicates()}\n'
                )

    
    packet_handler = []

    NODE_LIST.append(Node('A', ['BBB', 'C']))
    NODE_LIST.append(Node('BBB', ['C', 'A']))
    NODE_LIST.append(Node('C', ['A', 'BBB', 'D']))
    NODE_LIST.append(Node('D', ['A', 'BBB']))

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

        # NODE_LIST[0].inject_packet(set_data())
        # NODE_LIST[0].inject_packet(set_data())
        # print('>>>>>>>>>>>>>>', NODE_LIST[0].get_node_info())
        # print('>>>>>>>>>>>>>>', NODE_LIST[1].get_node_info())
        # print('>>>>>>>>>>>>>>', NODE_LIST[2].get_node_info())
        # print('>>>>>>>>>>>>>>', NODE_LIST[3].get_node_info())

        NODE_LIST[3].get_new_connections()
        print(NODE_LIST[3].discovered_connections)

        
