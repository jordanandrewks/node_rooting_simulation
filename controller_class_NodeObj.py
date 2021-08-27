# from controller_global_defs import *

class NodeObj:

    def __init__(self, node_name: str, connections: list) -> None:
        '''instances variables are initialized here'''

        # Instance variables
        self.node_name = node_name
        self.connections = connections
        self.discovered_connections = []
        self.buffer = []
        self.null_list = []
        self.transmitted = 0
        self.received = 0


    def reset(self):
        self.buffer = []
        self.null_list = []
        self.transmitted = 0
        self.received = 0


    def inject_packet(self, packet: dict):
        """Pass in the first packet"""
        self.buffer.append(packet.copy())


    def get_connected_node_obj(self):
        """ return the object of the node"""
        from main_app import NODE_LIST
        count = 0
        for connected_node in self.connections:
            for index, node_obj in enumerate(list(NODE_LIST)):
                if connected_node is node_obj.node_name:
                    count += 1
                    yield index


    def find_depleted_packets(self):
        self.null_list = []
        for c in range(0, len(self.buffer)):
            if self.buffer[c]['hop_lim'] == 0:
                self.null_list.append(c)
        

    def remove_depleted_packets(self):
        for decrement, packet_index in enumerate(self.null_list):
            self.buffer.pop(packet_index - decrement) 


    def next_hop(self):
        """ Send the packet to the next connections"""  
        from main_app import NODE_LIST

        self.get_new_connections()
        self.find_depleted_packets()
        self.remove_depleted_packets()

        if self.buffer:     # Check if there's anything in THIS nodes buffer

            self.buffer[0]['history'] += self.node_name + '>'
            self.buffer[0]['hop_lim'] -= 1

            for node_index in list(self.get_connected_node_obj()):
                if self.buffer[0]['hop_lim'] >= 0:
                    NODE_LIST[node_index].buffer.append(self.buffer[0].copy())         # Move value to the next object
                    NODE_LIST[node_index].received += 1        
                    self.transmitted += 1

            self.buffer.pop(0)                                  # Remove this value from this object


    def get_congestion(self) -> int:
        return len(self.buffer)
    

    def get_new_connections(self):

        recent_node_list = []
        history_list = list(str(self.buffer[i]['history'])[:-1:] for i in range(self.get_congestion()))
        
        try:
            for i in range(self.get_congestion()):
                index = str(str(self.buffer[i]['history'])[::-1])[1::].index('>')                # Index of the last seperator
                recent_node_list.append(str(history_list[i])[len(history_list[i]) - index::])       # Perform string slice and return latest Node ID

            sorted_node_name_list = list(set(recent_node_list))   # Remove any duplicates

            # Append any new connections to the discovery list
            for node in sorted_node_name_list:        
                if node not in self.connections and node not in self.discovered_connections:
                    self.discovered_connections.append(node)

        except ValueError:
            """ Avoid a fail when the history is empty"""
            pass


    def get_duplicates(self) -> int:
        duplicate_messages = {}
        contains_duplicates = 0

        all_messages = list(self.buffer[i]['message'] for i in range(self.get_congestion()))

        sorted_messages = list(set(all_messages))
        
        for key in sorted_messages:
            duplicate_messages[key] = ''

        for message_ in sorted_messages:
            contains_duplicates += all_messages.count(message_)-1
            duplicate_messages[message_] = all_messages.count(message_)-1
                
        return contains_duplicates, duplicate_messages


    def get_status(self) -> dict:
        return {
            f"id": f"{self.node_name}",
            f"connections": f"{self.connections}",
            f"discovered": f"{self.discovered_connections}",
            f"total_sent": f"{self.transmitted}",
            f"total_received": f"{self.received}",
            f"congestion": f"{self.get_congestion()}"
            }