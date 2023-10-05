import os
from scen_object_helper_functions import return_fds_version
from report_gen_helper_functions import round_to, scen_results_values
from variable_text import Extended_travel_1, Extended_travel_2
# TODO: have render logic only here
# move final_report to have docx logic
def add_refs_in_order(values):
    ref_order = ["SCA_1", "BRegs"]
    if values["BS9991"] == True:
        ref_order.append("BS9991")
    else:
        ref_order.append("ADB")

        # index + 3
        # values["REF_ADB"] = ref_order.index("ADB")

    # TODO: Future bring in ref's programattically from template
    # TODO: other refs
    ref_order.append("BS7974")
    ref_order.append("FDS")
    ref_order.append("NIST")
    if values["BS9991"] == False:
        ref_order.append("BS9991")

    ref_order.append("BS1366_2")
    # L5 ref??
    ref_order.append("BS5839_1")
    ref_order.append("PD7974_6")
    ref_order.append("BS12101_6")
    ref_order.append("SPFE")
    ref_order.append("SCA_2")

    ref_order.append("PD7974_1")
    ref_order.append("BS9251")
    ref_order.append("BRE_1")
    return ref_order

def ref_number(ref_order, values):
    for ref in ref_order:
        values[f'REF_{ref}']= ref_order.index(ref)+1
        return values

def render_logic(values, today, path_to_root_directory, scenarios_object, scenario_names, MoE_scenarios, FSA_scenarios):
    values["TODAYS_DATE"] = today.strftime("%d-%m-%Y")

    # TODO: get path from user - perhaps initial input before further one
    # C:\Users\IanShaw\Dropbox\Projects CFD\25. Claridges\Runs
    # path_to_root_directory = Path(r"C:\Users\IanShaw\Dropbox\Projects CFD\26. Breams Building\Runs")

    if len([ f.name for f in os.scandir(path_to_root_directory) if f.is_dir() ]):
        # path_to_root_directory = path_to_root_directory
        pass
    else:
        path_to_root_directory = os.path.dirname(path_to_root_directory) # need path?
    # go first scenario - all should be the same version
    fds_version = return_fds_version(path_to_directory=f'{path_to_root_directory}/{scenario_names[0]}')

    values["HAS_SPRINKLERS"] = scenarios_object[scenario_names[0]]["is_sprinklered"]

    def num_to_text(num, capatalise=False):
        if num < 10:
            if num == 1:
                num = 'one'
            elif num ==2:
                num = "two"
            elif num == 3:
                num = 'three'
            elif num == 4:
                num = 'four'
            elif num ==5:
                num = "five"
            elif num == 6:
                num = 'six'
            elif num == 7:
                num = 'seven'
            elif num == 8:
                num = 'eight'
            elif num ==9:
                num = "nine"
            if capatalise == True:
                num = num.capitalize()
        return num
    
    def jinja_num_and_text(jinja_name, number):
        values[jinja_name] = number
        values[f'{jinja_name}_TEXT'] = num_to_text(number) # later run through above function
    
    jinja_num_and_text("NUM_SCENARIOS", len(scenario_names))
    jinja_num_and_text("NUM_MOE_SCENARIOS", len(MoE_scenarios))
    jinja_num_and_text("NUM_FSA_SCENARIOS", len(FSA_scenarios))

    # TODO: move variable texts to own page
    def compute_fire_scen_text():
        first = f'{num_to_text(len(scenario_names), capatalise=True)} fire scenario'
        if len(scenario_names) > 1:
            first += 's have'
        else:
            first += ' has'
        first += ' been considered in this assessment'
        if len(MoE_scenarios) == 0:
            first += ' and will relate to the Fire Service Access phase only. The model'
            if len(scenario_names) > 1:
                first += 's'
            first += ' will consider the likelihood of smoke penetrating into the stair based on '
            if len(scenario_names) > 1:
                first += 'credible worst case apartment locations.'
            else:
                first += 'a credible worst case apartment location.'
        else:
            first += f', {num_to_text(len(MoE_scenarios))} Means of Escape scenario'
            if len(MoE_scenarios) > 1:
                first += 's'
            first += f' and {num_to_text(len(FSA_scenarios))} Fire Service Access scenario'
            if len(FSA_scenarios) > 1:
                first += 's'
            first += '. Fire scenarios are based on credible worst case apartment locations.'
        return first
        # if len(MoE_scenarios) == 0:
        # pass

    fire_scenario_text = compute_fire_scen_text()
    values["FIRE_SCEN_TEXT"] = fire_scenario_text
    if len(scenario_names) > 1:
        fire_scenario_sub_text = 's are'
    else:
        fire_scenario_sub_text = ' is'
    values["FIRE_SCEN_SUB_TEXT"] = fire_scenario_sub_text

    # TODO: how to auto generate charts?
    values["FDS_VERSION"] = fds_version
    # also confirm naming conventions


    ref_order = add_refs_in_order(values)
    values = ref_number(ref_order)


    print("values: ", values)
    # TODO: scope if only one of either FSA or MOE and if so input text into bullets for scen overview using jinja
    # MOE_SCENARIO 
    if len(MoE_scenarios) > 0:
        values["MOE_SCENARIO"] = True

    if len(FSA_scenarios) > 0:
        values["FSA_SCENARIO"] = True
    # values["MOE_SCENARIO"] = True
    if len(MoE_scenarios) == 1:
        values["SINGLE_MOE_SCENARIO"] = True
        # MOE_TENABLE_TIME
        # MOE_MIN_PRESSURE
        scenario = MoE_scenarios[0]
        tenable_time, max_pressure_drop, meet_criteria = scen_results_values(scenario, scenarios_object, firefighting=False)
        values["MOE_TENABLE_TIME"] = round_to(tenable_time)
        values["MOE_MIN_PRESSURE"] = round_to(max_pressure_drop)
# if len(FSA_scenarios) == 1:
    if len(FSA_scenarios) == 1:
        values["SINGLE_FSA_SCENARIO"] = True
        # MOE_TENABLE_TIME
        # MOE_MIN_PRESSURE
        scenario = FSA_scenarios[0]
        text_list, worst_temp, worst_vis, meet_criteria, max_pressure_drop = scen_results_values(scenario, scenarios_object, firefighting=True)
        # length of text list -> if 4m or 15m available
        values["FSA_2M_TEMP"] = text_list[0]
        # TODO: do not render if 'N/A'
        if len(text_list) > 1:
            values["HAS_FSA_4M_TEMP"] = True
            values["FSA_4M_TEMP"] = text_list[1]
            if len(text_list) > 2:
                values["HAS_FSA_15M_TEMP"] = True
                values["FSA_15M_TEMP"] = text_list[2]  
        values["FSA_MIN_PRESSURE"] = max_pressure_drop
        values["FSA_STAIR_VIS"] = round_to(worst_vis)
        values["FSA_STAIR_TEMP"] = round_to(worst_temp)

    if len(MoE_scenarios) > 1:
        values["MULTIPLE_MOE_SCENARIOS"] = True
    if len(FSA_scenarios) > 1:
        values["MULTIPLE_FSA_SCENARIOS"] = True           # populate table using docx

    # perhaps only some scenarios have extended TD's?
    if values["HAS_EXTENDED_TRAVEL"] == True:
        values["EXTENDED_TD_1"] = Extended_travel_1
        values["EXTENDED_TD_2"] = Extended_travel_2
        if values["BS9991"] == True: # both TD's and 991
            pass
        else: # both TD's and ADB
            pass
    else: # no extended TD's
        if values["BS9991"] == True: # no TD's and 991
            pass
        else: # no TD's and ADB -> find out td's etc
            pass

    if values["BS9991"] == True: # below irrespective of TD's
        # inputs
    #     values["Guidance_1"] = BS9991_1
    #     values["Guidance_2"] = BS9991_2
    # else:
    #     values["Guidance_1"] = ADB_1
    #     values["Guidance_2"] = ADB_2
        pass
    # TODO: scope if sprinklers provided from fds file
    # must be after button pressed!!

    values["SCEN_1_IS_MOE"] = True

    return values


def render_doc(values, doc, output_path):
    doc.render(values)
    doc.save(output_path)

