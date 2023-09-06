import re
import pandas as pd
import numpy as np
from constants import devc_chart_constants
from pathlib import Path
# from scen_object_helper_functions import find_all_files_of_type
import os
from os import listdir
from pathlib import Path

def return_all_subfolders(path_to_dir):
    return [ item for item in os.listdir(path_to_dir) if os.path.isdir(os.path.join(path_to_dir, item)) ]

def return_paths_to_files(scenario_name, dir_path='graph_generation', new_folder_structure=False):
    if new_folder_structure == False:
        path_to_scen_directory = f'./{dir_path}/{scenario_name}/Graph_{scenario_name}'
        path_to_fds_file = f'{path_to_scen_directory}/Graph_{scenario_name}.fds'
        path_to_devc_file = f'{path_to_scen_directory}/Graph_{scenario_name}_devc.csv'
        path_to_hrr_file = f'graph_generation\{scenario_name}\Graph_{scenario_name}\Graph_{scenario_name}_hrr.csv'

    else:
        path_to_scen_directory = f'{dir_path}/{scenario_name}'
        # TODO: check if intermediate folder
        has_nested_folder = return_all_subfolders(path_to_scen_directory)
        if len(has_nested_folder) > 0:
            path_to_scen_directory += f'/{has_nested_folder[0]}'
        fds_name = find_all_files_of_type(path_to_directory=path_to_scen_directory, suffix=".fds")[0]
        devc_name = find_all_files_of_type(path_to_directory=path_to_scen_directory, suffix="devc.csv")
        if len(devc_name) > 0 :
            devc_name = devc_name[0]
        hrr_name = find_all_files_of_type(path_to_directory=path_to_scen_directory, suffix="hrr.csv")[0]

        # find all files - ones with x and y ending
        path_to_hrr_file = f'{path_to_scen_directory}/{hrr_name}'
        path_to_fds_file = f'{path_to_scen_directory}/{fds_name}'
        path_to_devc_file = f'{path_to_scen_directory}/{devc_name}'

    return path_to_hrr_file, path_to_scen_directory, path_to_fds_file, path_to_devc_file

def find_all_files_of_type(path_to_directory, suffix=".csv"):
    filenames = listdir(path_to_directory)
    return [ f for f in filenames if f.endswith( suffix )]

# TODO: move to misc utils
def round_to(value, closest_to=0.1):
        return round(value, 1) 

def filter_dataframe_by_column_starting_with_string(df, string):
    return df.loc[:, df.columns.str.startswith(string)]

def filter_dataframe_by_column_contains_string(df, string):
    return df.loc[:, df.columns.str.contains(string)]

def find_worst_case_column_name(worst_case_max_or_min, column_names, df, is_stair=False, firefighting=False):
    # create new df
    # need time column
    # TODO: if column names contains 'stair' -> have second worst_case column -> worst_case_b
    # TODO: allow both stair and corridor columns
    is_stair = any("stair" in x for x in column_names)
    new_df = df.copy()
        
    def return_worst_case_column(worst_case_label, new_df, column_names):
        if worst_case_max_or_min == "min":
            # need to create new df: time & worst case at each time step
            new_df[worst_case_label] = new_df[column_names].min(axis=1)
            # return find_column_name_with_min(data_columns=data_for_columns)
        else:
            new_df[worst_case_label] = new_df[column_names].max(axis=1)
            # return find_column_name_with_max(data_columns=data_for_columns)
        return new_df  

    worst_case_labels = ["worst_case", "worst_case_b"]
    
    def find_all_elements_endwith(list, suffix):
        return [ f for f in list if f.endswith( suffix ) ]

    if is_stair:
        ordered_col_list = []
    # split columns in two
    # IS Note: range was 10 in past
        range_max = len(column_names)
        half_range = int(range_max / 2)
        # for index in range(10):
        for index in range(range_max):
            # if len(find_all_elements_endwith(column_names, f'_{index+1}')) == 0:
            #     print("break")
            current = find_all_elements_endwith(column_names, f'_{index+1}')[0]
            ordered_col_list.append(current)
        # new_df = return_worst_case_column(worst_case_label="worst_case", new_df=new_df, column_names=ordered_col_list[:5])
        # new_df = return_worst_case_column(worst_case_label="worst_case_b", new_df=new_df, column_names=ordered_col_list[5:])
        new_df = return_worst_case_column(worst_case_label="worst_case", new_df=new_df, column_names=ordered_col_list[:half_range])
        new_df = return_worst_case_column(worst_case_label="worst_case_b", new_df=new_df, column_names=ordered_col_list[half_range:])
    else:
        new_df = return_worst_case_column(worst_case_label="worst_case", new_df=new_df, column_names=column_names)
        # 1-5
        # 6-10
    # go twice
    # second run worst_case_b
    return new_df    


def get_worst_case_devc(path_to_file, property="temp",firefighting=False):
    devc_df = read_from_csv_skip_first_row(path_to_file)
    devc_keys = devc_chart_constants.keys()
    current = property
    data_columns = filter_dataframe_by_column_contains_string(devc_df, current)
    if any(current in x for x in devc_keys):
        current_key = [f for f in devc_keys if current in f][0]
    else:
    # do temp and vis for moe
        current_key = [f for f in devc_keys if f[:-1] in current][0]

    column_config = devc_chart_constants[current_key]
    # May need to limit columns for ff?
    new_df = find_worst_case_column_name(
    worst_case_max_or_min=column_config["worst_case"], 
    column_names=list(data_columns.columns),
    df=devc_df
)
    # scope through worst case column for temp and vis
    return new_df
def find_current_devc_key(current):
    devc_keys = devc_chart_constants.keys()
    if any(current in x for x in devc_keys):
        current_key = [f for f in devc_keys if current in f][0]
    else:
    # do temp and vis for moe
        current_key = [f for f in devc_keys if f[:-1] in current][0]
    return current_key

def find_column_config(parameter):
    key = find_current_devc_key(current=parameter)
    column_config = devc_chart_constants[key]
    return column_config

def max_or_min_is_worse(parameter):
    column_config = find_column_config(parameter)
    max_or_min = column_config["worst_case"]
    return max_or_min

def find_worst_in_column(df, column_name, parameter):
    max_or_min = max_or_min_is_worse(parameter)
    if max_or_min == "max":
        return df[column_name].max()
    else:
        return df[column_name].min()

def compute_last_time_step_not_tenable(df, property="temp",worst_case_column_name="worst_case", firefighting=False):
    column_config = find_column_config(property)
    # get tenable limit
    if firefighting:
        return 0
    # only for moe
    tenable_limit = column_config["tenable_limit_moe"]

    # use max or min
    max_or_min = column_config[worst_case_column_name]
    if max_or_min == "max":
       df["is_worse"] = np.where(df[worst_case_column_name] > tenable_limit,
       True,
       False) 
    if max_or_min == "min":
       df["is_worse"] = np.where(df[worst_case_column_name] < tenable_limit,
       True,
       False) 
    print(df["is_worse"])
    # find last true
    # scope if only false
    last_time_step_untenable = df.where(df["is_worse"]).last_valid_index()
    if last_time_step_untenable and last_time_step_untenable < (len(df["is_worse"])-1):

        tenability_step = last_time_step_untenable + 1
        time_tenable = df["Time"][tenability_step]
        return time_tenable
    else:
        return 0
    # then return last time step when true + 1 timestep
        # df["is_worse"] = df.worst_case.apply(lambda x: True if x >= tenable_limit)
    # get from last entry forwards first worse than that
    # add 1 timestep

    # print(df)
def read_from_csv_skip_first_row(path_to_file, rows_to_skip=[0]):
    return pd.read_csv(path_to_file, skiprows=rows_to_skip)





# \graph_generation\FSA_Test\Graph_FSA_Test\
