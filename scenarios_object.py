from pathlib import Path
import json

from helper_functions import return_paths_to_files, read_from_csv_skip_first_row, get_worst_case_devc, compute_last_time_step_not_tenable, max_or_min_is_worse, find_worst_in_column
from scen_object_helper_functions import is_sprinklered, find_venting_from_fds, return_scenario_names
from fds_output_utils import find_door_opening_times


# TODO: move below to helper_functions.py
def create_scenario_object(path_to_directory="graph_generation"):
    scenario_names = return_scenario_names(path_to_directory)

    FSA_scenarios = [f for f in scenario_names if "FSA" in f]# filter names for fsa
    MoE_scenarios = [f for f in scenario_names if "FSA" not in f]

    # TODO: move below to helper_functions page
    scenarios_object = {}
    for i in range(len(scenario_names)):
        scen_key = scenario_names[i]
        scenarios_object[scen_key] = {
            "venting": {
                "mech_extract": {"number": [], "flow": []},
                # include supply and aov
                "mech_supply": {"number": [], "flow": []},
                "stair_aov": {"area": []},
                "natural_openings": [], # list areas
                # TODO: include natural inlets to model
            },
            "is_sprinklered": [],
            # TODO: add door opening times
            "door_opening_times": [],
            "end_time": [],
            "tenability": [],
            "min_pressure": []
            # TODO: add run time for sim
        }

        # path_to_directory
        path_to_hrr_file, path_to_scen_directory, path_to_fds_file, path_to_devc_file = return_paths_to_files(scenario_name=scen_key, dir_path=path_to_directory, new_folder_structure=True)


        if "FSA" in scen_key:
            firefighting = True
        else:
            firefighting = False
        # TODO: obtain max T from devc file
        devc_df = read_from_csv_skip_first_row(path_to_file=path_to_devc_file)
        max_T = devc_df["Time"].max()


    
        extract_rate_list, supply_rate_list, aov_area, extract_count, supply_count, natural_inlet_list = find_venting_from_fds(path_to_file=path_to_fds_file)
        has_sprinklers = is_sprinklered(path_to_file=path_to_fds_file)
        scenarios_object[scen_key]["venting"]["mech_extract"]["number"] = extract_count

        if not extract_rate_list:
            extract_rate = 0
        else:
            extract_rate = float(extract_rate_list[0][0])

        if not supply_rate_list:
            supply_rate = 0
        else:
            supply_rate = float(supply_rate_list[0][0])

        scenarios_object[scen_key]["venting"]["mech_extract"]["flow"] = extract_rate
        scenarios_object[scen_key]["venting"]["mech_extract"]["number"] = extract_count
        scenarios_object[scen_key]["venting"]["mech_supply"]["number"] = supply_count
        scenarios_object[scen_key]["venting"]["mech_supply"]["flow"] = supply_rate
        scenarios_object[scen_key]["venting"]["stair_aov"]["area"] = aov_area
        scenarios_object[scen_key]["venting"]["natural_openings"] = natural_inlet_list
        scenarios_object[scen_key]["is_sprinklered"] = has_sprinklers
        scenarios_object[scen_key]["door_opening_times"] = find_door_opening_times(path_to_file=path_to_fds_file)
        scenarios_object[scen_key]["end_time"] = max_T
    #     return({"opening_apartment": opening_apartment[0], "closing_apartment":closing_apartment[-1], "opening_stair":opening_stair[0], "closing_stair":closing_stair[-1]})
        moe_list = ["vis", "temp"]
        tenability_time_list = []
        # fsa_list = ["","" ,"" ] # temp xm
        # TODO: move object creation to scenario_object
        if firefighting==False:
            scenarios_object[scen_key]["worst_condition"] = {
                "stair_temp": [],
                "stair_vis": [],
                "cc_vis": [],
                "cc_temp": []
                } 
            # for current in moe_list:
            i_stair_temp = 0
            i_stair_vis = 0
            i_cc_temp = 0
            i_cc_vis = 0
            for column_name in devc_df.columns:
                # TODO: allow for stair vis and cc vis if both present
                # how to see all columns available?
                # if 'cc-temp' in column_name:
                #     pass
                if ('stair_temp' in column_name and i_stair_temp == 0 or 
                    'stair_vis' in column_name  and i_stair_vis == 0 or 
                    'cc_temp' in column_name  and i_cc_temp == 0 or 
                    'cc_vis' in column_name and i_cc_vis == 0
                    ):
                    if 'stair_temp' in column_name:
                        prefix = 'stair_temp'
                        i_stair_temp += 1
                        # if stair_temp_counter > 0: # current hack should use prefixes for columns

                        # stair_temp_counter += 1
                    elif 'stair_vis' in column_name:
                        prefix = 'stair_vis'
                        i_stair_vis += 1
                        # if stair_vis_counter > 0:
                        #     break
                        # stair_vis_counter += 1
                    # find worst from all columns
                    elif 'cc_temp' in column_name:
                        prefix = 'cc_temp'
                        i_cc_temp += 1
                    else:
                        prefix = 'cc_vis'
                        i_cc_vis += 1

                    new_df_devc = get_worst_case_devc(path_to_file=path_to_devc_file, property=prefix,firefighting=firefighting)

                    worst_condition = find_worst_in_column(df=new_df_devc, column_name="worst_case", parameter=prefix)
                    # add worst temp to object

                    # worst_condition = new_df_devc["worst_case"].min() # find worst - max or min??

                    # use prefix for object
                    # needs to change scen obj to allow for possible stair_vis etc
                    scenarios_object[scen_key]["worst_condition"][prefix] = worst_condition 
                # new_df_devc = get_worst_case_devc(path_to_file=path_to_devc_file, property=current,firefighting=firefighting)

                # ff requires tenability at different distances 
                # if moe -> needs temp and vis
                    for current in moe_list:
                        if current in prefix:
                            
                    # if "_temp" in prefix:
                    #     current = "_temp"
                            tenability_time = compute_last_time_step_not_tenable(df=new_df_devc, property=current,worst_case_column_name="worst_case", firefighting=firefighting)
                            tenability_time_list.append(tenability_time)
            # # TODO: remove below hack - required until naming convention to followed in FDS file
            # if scenarios_object[scen_key]["door_opening_times"]["closing_apartment"] == None:
            #     closing_apartment = 80
            # else:
            closing_apartment = scenarios_object[scen_key]["door_opening_times"]["closing_apartment"]
            
            tenability_time = max(tenability_time_list)- closing_apartment # should take-away door closing
            scenarios_object[scen_key]["tenability"] = {"time": tenability_time}
            # min pressure - needed for FSA!!
            current = "pres"
            new_df_devc = get_worst_case_devc(path_to_file=path_to_devc_file, property=current,firefighting=firefighting)
            min_pressure = new_df_devc["worst_case"].min() # 30 secs after door closes??
            scenarios_object[scen_key]["min_pressure"] = min_pressure
        # should trip below for FSA!!!
        else: # if firefighting fsa
            scenarios_object[scen_key]["tenability"] = {
                "2m": [],
                "4m": [],
                "15m": []
                }

            scenarios_object[scen_key]["worst_condition"] = {
                "stair_temp": [],
                "stair_vis": [],
                }           
            # loop through column names
            door_openings = scenarios_object[scen_key]["door_opening_times"]
            time = door_openings['opening_apartment'] + 30
            temp_index = devc_df['Time'].sub(time).abs().idxmin()
            stair_temp_counter = 0
            stair_vis_counter = 0
            
            current = "pres"
            new_df_devc = get_worst_case_devc(path_to_file=path_to_devc_file, property=current,firefighting=firefighting)
            min_pressure = new_df_devc["worst_case"].min()
            scenarios_object[scen_key]["min_pressure"] = min_pressure

            for column_name in devc_df.columns:
                if 'cc_FSA_temp_' in column_name:
                    # should this be worst case 30secs after door closes?
                    # new_df_devc = get_worst_case_devc(path_to_file=path_to_devc_file, property=column_name,firefighting=firefighting)
                    worst_temp = temp = devc_df[column_name][temp_index:].max()
                    tenability_key = column_name.removeprefix("cc_FSA_temp_")
                    scenarios_object[scen_key]["tenability"][tenability_key] = worst_temp
                    # add to tenable object
                # TODO: worst conditions in stair for vis and temp 
                # # if 'stair' in column_name
                # TODO: should restrict to prefixes
                if 'stair_temp' in column_name or 'stair_vis' in column_name:
                    if 'stair_temp' in column_name:
                        prefix = 'stair_temp'
                        # if stair_temp_counter > 0: # current hack should use prefixes for columns

                        # stair_temp_counter += 1
                    else:
                        prefix = 'stair_vis'
                        # if stair_vis_counter > 0:
                        #     break
                        # stair_vis_counter += 1
                    # find worst from all columns
                    new_df_devc = get_worst_case_devc(path_to_file=path_to_devc_file, property=prefix,firefighting=firefighting)

                    max_or_min = max_or_min_is_worse(parameter=prefix)
                    worst_condition = find_worst_in_column(df=new_df_devc, column_name="worst_case", parameter=prefix)
                    # add worst temp to object

                    # worst_condition = new_df_devc["worst_case"].min() # find worst - max or min??

                    # use prefix for object
                    scenarios_object[scen_key]["worst_condition"][prefix] = worst_condition 
    jsonString = json.dumps(scenarios_object)
    jsonFile = open(f"{scenario_names[0]}_etal.json", "w")
    jsonFile.write(jsonString)
    jsonFile.close()
    # 
    return scenarios_object, scenario_names, FSA_scenarios, MoE_scenarios

if __name__=='__main__':
    path_to_directory = r'C:\Users\IanShaw\Fire Dynamics Group Limited\CFD - Files\Projects CFD\31. Camp Hill Gardens Corridor'
    scenarios_object, scenario_names, FSA_scenarios, MoE_scenarios = create_scenario_object(path_to_directory)