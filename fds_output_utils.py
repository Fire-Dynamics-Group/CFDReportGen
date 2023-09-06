import re
from scen_object_helper_functions import find_all_files_of_type
import os

def find_door_opening_times(path_to_file):
    # TODO: incorporate stair door opening on smoke detection
    # need to read SD columns in devc and use earliest timestep where > 3.28 %/m
    directory_path = os.path.dirname(path_to_file)
    # find devc file in directory
    devc_file = find_all_files_of_type(path_to_directory=directory_path, suffix="devc.csv")[0]
    apartment_door = []
    opening_apartment = []
    closing_apartment = []
    opening_stair = []
    closing_stair = []
    with open(path_to_file, "r+") as f:
        lines_list = f.readlines()
    with open(path_to_file, "r+") as f:
        regex = '[+-]?([0-9]*[.])?[0-9]+'
        for line in f:
            if line != None: 
                split_line = line.split(",")
                # TODO: Scope input_id name from ctrl id row
                # then come back up
                if 'Apt_Door_RAMP' in line:
                    pass
                if "inlet" not in line.lower():
                    if "T=" in line and ("Door_RAMP',".lower() in line.lower() or "Hole_RAMP',".lower() in line.lower() or "Apt_RAMP".lower() in line.lower()): # if door in dev_c
                        print(line)
                        # regex find floats
                        # if apartment door
                        if "Apartment" in line or "Apt" in line:
                            door_time = float(re.findall(regex, split_line[1])[0])
                            if "-" in split_line[-1]:
                                if "hole" in line.lower():
                                    door_action = "closed" 
                                    closing_apartment.append(door_time)
                                else:
                                    door_action = "open"
                                    opening_apartment.append(door_time)
                            else:
                                if "hole" in line.lower():
                                    door_action = "open"
                                    opening_apartment.append(door_time)
                                else:
                                    door_action = "closed" 
                                    closing_apartment.append(door_time)

                        if "Stair" in line:
                            door_time = float(re.findall(regex, split_line[1])[0])
                            if "-" in split_line[-1]:
                                if "hole" in line.lower():
                                    door_action = "closed" 
                                    closing_stair.append(door_time)
                                else:
                                    door_action = "open"
                                    opening_stair.append(door_time)
                            else:
                                if "hole" in line.lower():
                                    door_action = "open"
                                    opening_stair.append(door_time)
                                else:
                                    door_action = "closed" 
                                    closing_stair.append(door_time)

    for line in lines_list:
        print(line)
        if "Apt_Door" in line and "SETPOINT" in line:
            timing = [element for element in line.split(",") if "SETPOINT" in element][0]
            door_time = float(re.findall(regex, timing)[0])
            if "TRUE" in line:
                door_action = "open"
                opening_apartment.append(door_time)
            else:
                door_action = "closed" 
                closing_apartment.append(door_time)
        if "Stair_Door" in line and "SETPOINT" in line:
            print(line)
            timing = [element for element in line.split(",") if "SETPOINT" in element][0]
            door_time = float(re.findall(regex, timing)[0])
            if "TRUE" in line:
                door_action = "open"
                opening_stair.append(door_time)
            else:
                door_action = "closed" 
                closing_stair.append(door_time)
        if "Apartment" in line and 'INPUT_ID=' in line:
            input_id = [element for element in line.split(",") if "INPUT_ID" in element][0]
            # find name of input id
      
    # for debugging purposes
    if len(opening_apartment) == 0:
        opening_apartment = [0] 
    opening_apt = opening_apartment[0]
    if len(closing_apartment) == 0:
        close_apt = None
    else:
         close_apt = closing_apartment[-1]
    if close_apt and close_apt < opening_apt:
        close_apt = None
    # close_stair = closing_stair[-1]
    if len(closing_stair) == 0:
        close_stair = None
        # stand in 300
        # i.e. end of run
        # close_stair = 300
    else:
         close_stair = closing_stair[-1]
    if len(opening_stair) == 0:
        opening_stair = [0]
    if close_stair == opening_stair[0]:
        close_stair = None
         # if actioned by sd -> closing = max T or not at all; n/a perhaps??
    # close_stair = None if len(closing_apartment) is None else closing_stair[-1]
    return({"opening_apartment": opening_apt, "closing_apartment": close_apt, "opening_stair":opening_stair[0], "closing_stair":close_stair})

if __name__=='__main__':
    path_to_file = r'C:\Users\IanShaw\Fire Dynamics Group Limited\CFD - Files\Projects CFD\31. Camp Hill Gardens Corridor\FS4_FSA\FS4_FSA\FS4_FSA.fds'
    door_times = find_door_opening_times(path_to_file)