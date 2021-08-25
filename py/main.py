#!/usr/bin/python3

import builtins
import time
import sys
import datetime


# instance methods
# class methods
# static methods

NODE_LIST = []

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

if __name__ == '__main__':

    class Node:

        def __init__(self, node_id: str, connections: list) -> None:
            '''instances variables are initialized here'''

            # Instance variables
            self.node_id = node_id
            self.connections = connections
            self.discovered_connections = []
            self.buffer = []
            self.null_list = []


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


        def find_depleted_packets(self):
            self.null_list = []
            for c in range(0, len(self.buffer)):
                if self.buffer[c]['HOP_LIM'] == 0:
                    self.null_list.append(c)
            

        def remove_depleted_packets(self):
            for decrement, packet_index in enumerate(self.null_list):
                self.buffer.pop(packet_index - decrement) 


        def next_hop(self):
            """ Send the packet to the next connections"""  
            print("I am <{}> and I'm connected to {}". format(self.node_id, self.connections))

            self.get_new_connections()
            self.find_depleted_packets()
            self.remove_depleted_packets()

            if self.buffer:     # Check if there's anything in THIS nodes buffer

                self.buffer[0]['HISTORY[x]'] += self.node_id + '>'
                self.buffer[0]['HOP_LIM'] -= 1

                for node_index in list(self.get_connected_node_obj()):
                    print("I need to send to >>>>>", node_index)
                    if self.buffer[0]['HOP_LIM'] >= 0:
                        NODE_LIST[node_index].buffer.append(self.buffer[0].copy())         # Move value to the next object

                self.buffer.pop(0)                                  # Remove this value from this object


        def get_congestion(self) -> int:
            return len(self.buffer)
        

        def get_new_connections(self):

            recent_node_list = []
            history_list = list(str(self.buffer[i]['HISTORY[x]'])[:-1:] for i in range(self.get_congestion()))
            
            try:
                for i in range(self.get_congestion()):
                    index = str(str(self.buffer[i]['HISTORY[x]'])[::-1])[1::].index('>')                # Index of the last seperator
                    recent_node_list.append(str(history_list[i])[len(history_list[i]) - index::])       # Perform string slice and return latest Node ID

                sorted_node_id_list = list(set(recent_node_list))   # Remove any duplicates

                # Append any new connections to the discovery list
                for node in sorted_node_id_list:        
                    if node not in self.connections and node not in self.discovered_connections:
                        self.discovered_connections.append(node)

            except ValueError:
                """ Avoid a fail when the history is empty"""
                pass



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


    def watch():
        total = 0
        while total != len(NODE_LIST):
            total = 0
            for x in range(len(NODE_LIST)):
                NODE_LIST[x].next_hop()
                print(NODE_LIST[x].get_node_info())
                if NODE_LIST[x].get_congestion() == 0: 
                    total += 1
    
    # Network Map
    NODE_LIST.append(Node('A', ['BBB', 'C']))
    NODE_LIST.append(Node('BBB', ['C', 'A']))
    NODE_LIST.append(Node('C', ['A', 'BBB', 'D']))
    NODE_LIST.append(Node('D', ['A', 'BBB']))

    NODE_LIST[0].inject_packet(set_data())

    watch()


    """Activate this to do a sequenced debug"""
    debug = False

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
        print('>>>>>>>>>>>>>>', NODE_LIST[3].get_node_info())

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

        
        print('>>>>>>>>>>>>>>', NODE_LIST[0].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[1].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[2].get_node_info())
        print('>>>>>>>>>>>>>>', NODE_LIST[3].get_node_info())

        print('########################################################### - MOVE HELLO PACKET')