import time
from flask import request
from model_class_NodeModel import app
from data_transfer_object import DataTransferObject as dto

@app.route('/simulate/start', methods=['POST'])
def start_simulation():
    from main_app import open_simulation_thread
    from main_app import set_flag
    from main_app import get_flag
    from main_app import set_stop_limit

    # Close the thread if it's open
    if get_flag():
        set_flag(False)

    time.sleep(1)
    
    set_flag(True)
    set_stop_limit(0)

    try:
        # Return a valid number
        set_stop_limit(int(request.json['stop_lim']))
    except ValueError:
        # Return false value... i.e. Continue until done
        set_stop_limit(-1)

    open_simulation_thread()

    return dto.good_message("simulation running")


@app.route('/simulate/start', methods=['PUT'])
def update_stop_limit():
    global STOP_LIMIT
    STOP_LIMIT = request.json['stop_lim']
    return dto.good_message("stop limit updated")


"""Return Total Time spent"""
@app.route('/simulate/stop', methods=['GET'])
def stop_simulation():
    global THREAD_FLAG
    THREAD_FLAG = False
    return dto.good_message("simulation stopped")