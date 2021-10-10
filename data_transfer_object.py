"""
FILE:           data_transfer_object.py
DESCRIPTION:
class for defining structured data objects messages.
"""

import json

class DataTransferObject:

    def nodeId_contents(id_, contents):
        return {id_ : contents}, 200

    def good_message(output_message):
        return {"message": output_message}, 200
    
    def good_message_as_dict(dictionary):
        return dictionary, 200
            
    def good_message_as_list(list_):
        return list_, 200

    def error_message(output_message):
        return {"error": output_message}, 404

    def error_message_as_dict(dictionary):
        return dictionary, 404

    def good_message_as_list(list_):
        return list_, 404

    