"""
FILE:           controller_class_NodeObj.py
DESCRIPTION:
Responsible for Node Object data. IS NOT related NOR responsible
for communicating with the database.
"""

class NodeObj:

    def __init__(self, node_name: str, connections: list) -> None:
        # Instances variables are initialized here

        self.node_name = node_name
        self.connections = connections
        self.discovered_connections = []
        self.buffer = []
        self.null_list = []
        self.transmitted = 0
        self.received = 0


    def reset(self):
        # Reset contents of the node
        self.buffer = []
        self.null_list = []
        self.transmitted = 0
        self.received = 0


    def inject_packet(self, packet: dict):
        # Pass in the first packet
        self.buffer.append(packet.copy())


    def get_connected_node_obj(self):
        # Return the object of the node

        from main_app import NODE_LIST
        count = 0
        for connected_node in self.connections:
            for index, node_obj in enumerate(list(NODE_LIST)):
                if connected_node is node_obj.node_name:
                    count += 1  
                    # Yield the location of the node from the NODE_LIST
                    yield index 


    def find_depleted_packets(self):
        # Update the locations of of empty packets in the buffer and assign to null_list
        self.null_list = []
        for c in range(0, len(self.buffer)):
            if self.buffer[c]['hop_lim'] == 0:
                self.null_list.append(c)
        

    def remove_depleted_packets(self):
        # Remove packets with 0 hops left
        for decrement, packet_index in enumerate(self.null_list):
            self.buffer.pop(packet_index - decrement) 


    def next_hop(self) -> None:
        # Send the packet to the next connection(s)  
        from main_app import NODE_LIST

        self.get_new_connections()
        self.find_depleted_packets()
        self.remove_depleted_packets()

        if self.buffer:     # Check if there's anything in THIS node's buffer

            # Append the ID/name of the THIS node to the history string in the data packet
            self.buffer[0]['history'] += self.node_name + '>'

            # Deduct 1 from the hop limit
            self.buffer[0]['hop_lim'] -= 1      

            # Send first packet in the buffer to all connected nodes 
            for node_index in list(self.get_connected_node_obj()):

                # Hop limit of the first packet mustn't be 0! 
                if self.buffer[0]['hop_lim'] >= 0:
                    NODE_LIST[node_index].buffer.append(self.buffer[0].copy())          # Transfer the packet to the buffer of the connected Node
                    NODE_LIST[node_index].received += 1                                 # Increment the received variable for the connected Node
                    self.transmitted += 1                                               # Increment the transmitted variable for THIS connected Node 

            self.buffer.pop(0)      # Now remove the packet from THIS node's buffer


    def get_congestion(self) -> int:
        # Return how many packets are within the buffer
        return len(self.buffer)
    

    def get_new_connections(self):
        # Obtain any unknown connections for THIS node

        recent_node_list = []

        # Create a list with the ending '>' seperator removed.
        history_list = list(str(self.buffer[i]['history'])[:-1:] for i in range(self.get_congestion()))
        
        try:
            for i in range(self.get_congestion()):
                
                # Ignore the ending '>' seperator and find the next '>' seperator. 
                index = str(str(self.buffer[i]['history'])[::-1])[1::].index('>')                

                # Perform a string slice to get the last nodes name. Use index to pinpoint its location.
                recent_node_list.append(str(history_list[i])[len(history_list[i]) - index::])       

            # Remove any duplicates
            sorted_node_name_list = list(set(recent_node_list))   

            # Append any new connections to the discovery list
            for node in sorted_node_name_list:        
                if node not in self.connections and node not in self.discovered_connections:
                    self.discovered_connections.append(node)

        except ValueError:
            # EXCEPTION USAGE - To Avoid a crash when the history is empty
            pass


    def get_duplicates(self):
        # Find any packets with duplicated messages

        duplicate_messages = {}
        contains_duplicates = 0

        # Create a list of messages from the packets within the buffer
        all_messages = list(self.buffer[i]['message'] for i in range(self.get_congestion()))

        # Store a unique reference of each message - use set to remove duplicates and sort order.
        sorted_messages = list(set(all_messages))
        
        # Use each unique message a key in the duplicated message dictionary variable.
        for key in sorted_messages:
            duplicate_messages[key] = ''

        
        for single_message in sorted_messages:
            # Increment duplicate count by the amount of time it is counted in the all_message list.
            contains_duplicates += all_messages.count(single_message)-1

            # Create a dictionary/table of the message and the amount of times it's duplicated in the THIS buffer.
            duplicate_messages[single_message] = all_messages.count(single_message)-1
                
        return contains_duplicates, duplicate_messages


    def get_status(self) -> dict:
        # Return dictionary of results
        return {
            f"id": f"{self.node_name}",
            f"connections": f"{self.connections}",
            f"discovered": f"{self.discovered_connections}",
            f"total_sent": f"{self.transmitted}",
            f"total_received": f"{self.received}",
            f"congestion": f"{self.get_congestion()}"
            }