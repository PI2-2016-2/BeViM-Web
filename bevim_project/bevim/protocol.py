"""
    Bevim Protocol Flags
"""

# This flag is used to inform the control system to start the experiment
START_EXPERIMENT_FLAG = bytes([1])

# This flag is used to inform the control system to stop the experiment
STOP_EXPERIMENT_FLAG = bytes([1])

# This flag is used to ask to the control system the list of the present sensors
GET_AVAILABLE_SENSORS_FLAG = bytes([2])