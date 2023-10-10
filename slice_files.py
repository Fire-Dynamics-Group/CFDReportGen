import fdsreader as fds
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os
import itertools
from os import listdir

from hrr_graph import save_chart_high_res

quantity_types = ["PRESSURE", "SOOT VISIBILITY", "TEMPERATURE"]
quantity_type_config = {
    "TEMPERATURE": {
        "v_max": 60,
        "v_min": 20,
        "units": "°C",
        "cbar_reverse": False,
        "chart_name": 'Temperature',
        "tenable_limit_moe": 60,
    },
    "SOOT VISIBILITY": {
        "v_max": 10,
        "v_min": 0,
        "units": "m",
        "cbar_reverse": True,
        "chart_name": 'Visibility',
        "tenable_limit_moe": 10,
    },
    "PRESSURE": {
        "v_max": 0,
        "v_min": -100,
        "units": "Pa",
        "cbar_reverse": True,
        "chart_name": 'Relative Pressure',
        "tenable_limit_moe": -60,
    }
    }
door_openings = {'opening_apartment': 150.0, 'closing_apartment': 170.0, 'opening_stair': 160.0, 'closing_stair': 180.0}
# Creates an instance of a simulation master-class which manages all data for a given simulation
# C:\Users\IanShaw\Fire Dynamics Group Limited\CFD - Files\Research CFD\1. Graph Generation\Test Cases\Test1\S1_FSA
# C:\Users\IanShaw\Fire Dynamics Group Limited\CFD - Files\Projects CFD\22. Sweet Street\Resi\Final\L1_West_Core_FSA
# C:\Users\IanShaw\Fire Dynamics Group Limited\CFD - Files\Projects CFD\22. Sweet Street\Resi\Final\L1_East_Core_FSA
def obtain_slice(path_to_directory = r"C:\Users\IanShaw\Fire Dynamics Group Limited\CFD - Files\Projects CFD\22. Sweet Street\Resi\Final\L1_East_Core_FSA", door_openings=door_openings, t_max=300, t_start=60, interval_secs=40, save_in_cfd_folder=False, save_path=None):
    # sim = fds.Simulation("./Graph_MoE_Test")
    
    sim = fds.Simulation(path_to_directory)
    def file_name_from_path(file_path):
        return os.path.splitext(os.path.basename(file_path))[0]
    # TODO: Future: obtain project name from path_to_dir
    project_name = path_to_directory.split(" CFD",1)[1]
    project_name = project_name.replace("\\", "-")
    if "office" not in project_name.lower():
        t_max = 300
    # create new folder
    if not save_in_cfd_folder:
        base_dir_path = '.\outputSlices'
        if not os.path.isdir(base_dir_path):
            os.mkdir(base_dir_path)
        new_dir_path = f'{base_dir_path}\{project_name}'
    else:
        new_dir_path = f'{save_path}\{project_name}'

    
    if not os.path.isdir(new_dir_path):
        if save_path is None:
            new_dir_path = f'.\outputSlices\{project_name}'
        if not os.path.isdir(new_dir_path):
            os.mkdir(new_dir_path)

    if "FSA" in path_to_directory:
        firefighting = True
    else: 
        firefighting = False

    # color
    color_map =  [ # RGB then fourth entry is alpha
        [0.00000000e+00, 0.00000000e+00, 9.09982175e-01, 1.00000000e+00],
        [0.00000000e+00, 2.21568627e-01, 1.00000000e+00, 1.00000000e+00],
        [0.00000000e+00, 5.82352941e-01, 1.00000000e+00, 1.00000000e+00],
        [4.74383302e-02, 9.58823529e-01, 9.20303605e-01, 1.00000000e+00],
        [3.38393422e-01, 1.00000000e+00, 6.29348514e-01, 1.00000000e+00],
        [6.29348514e-01, 1.00000000e+00, 3.38393422e-01, 1.00000000e+00],
        [9.20303605e-01, 1.00000000e+00, 4.74383302e-02, 1.00000000e+00],
        [1.00000000e+00, 6.68845316e-01, 0.00000000e+00, 1.00000000e+00],
        [1.00000000e+00, 3.34785766e-01, 0.00000000e+00, 1.00000000e+00],
        [9.09982175e-01, 7.26216412e-04, 0.00000000e+00, 1.00000000e+00]
    ]

    def array2cmpa(X):
    # Assuming array is Nx3, where x3 gives RGB values
    # Append 1's for the alpha channel, to make X Nx4
        # X = np.c_[X,np.ones(len(X))]

        return matplotlib.colors.LinearSegmentedColormap.from_list('my_colormap', X)

    #     ]
    # TODO: Future -> allow gui input from this page -> folder name
    # TODO: name folder by current time for now

    # TODO: find all quantity/parameter types
    slice_params = [x for x in list(quantity_type_config.keys()) if x in str(sim.slices)]
    # TODO: then loop through types
    for current_type in slice_params:
        print(f'starting {current_type}')
        
        color_map_reversed = color_map[::-1]
        cmap_reversed = array2cmpa(color_map_reversed)
        cmap_forward = array2cmpa(color_map)

        current_quantity_object = quantity_type_config[current_type]

        if current_quantity_object["cbar_reverse"]:
            current_cmap = cmap_reversed
        else:
            current_cmap = cmap_forward

        # TODO: save one copy of colorbar
        # norm = matplotlib.colors.Normalize(vmin=current_quantity_object["v_min"], vmax=current_quantity_object["v_max"])
        # fig = plt.figure(figsize=(0.05, 8))
        # ax = fig.add_axes([0.02, 0.045, 0.05, 0.8])
        # cb1 = matplotlib.colorbar.ColorbarBase(
        #                     ax,
        #                     cmap=current_cmap,
        #                     norm=norm

        #                     )
        # cb1.set_label(f'{current_quantity_object["chart_name"]} {current_quantity_object["units"]}')
        img = plt.imshow(
                            np.array([[0,1]]), 
                            # origin='lower',
                            vmin=current_quantity_object["v_min"],
                            vmax=current_quantity_object["v_max"],
                            cmap=current_cmap)
        img.set_visible(False)
        plt.axis('off')
        plt.colorbar(label=f'{current_quantity_object["chart_name"]} {current_quantity_object["units"]}')
        save_chart_high_res(name_of_chart=f'{current_type}_colourbar', new_dir_path=new_dir_path)
        # plt.show()
        plt.close()
        # plt.colorbar(orientation="vertical")

    # type_index = 1 # 1 = visibility
    # current_type = quantity_type_config[param]
        t_slice = sim.slices.filter_by_quantity(current_type)

        # loop through t_slice str 
        array = []
        for i in range(len(str(t_slice))-1):
        # end 1 before end
            char = str(t_slice)[i]
            next_char = str(t_slice)[i+1] 
            if char == "2" and next_char == "D":
                array.append("twoD")
            elif char == "3" and next_char == "D":
                array.append("threeD")

        
        # if char ==2 and next char == D
        # if char ==3 and next char ==D
        # add two or 3d to end of an array when met with them
        # loop through 2d slices
        print(t_slice)
    # Slice([2D] quantity=Quantity('SOOT VISIBILITY'), cell_centered=False, extent=Extent([-11.20, 14.70] x [-18.40, 12.00] x [8.10, 8.10]), extent_dirs=('x', 'y'), orientation=3)
        # select slice, by its distance to a given point
        # got to filter for 2d indexes
        for twoD_slice in [i for i, x in enumerate(array) if x == "twoD"]:
            slc = t_slice[twoD_slice]
            # save in file

            # mesh = -1 # arbitrary - globalised to include all meshes
            # slc_data = slc[mesh].data
            slc_data = slc.to_global()
            counter = 0
            # try adding nan to smaller
            if type(slc_data) is tuple:
                a, b = slc_data
                a = (a.copy().tolist())
                b = (b.copy().tolist())
                if len(a) < len(b):
                    c = b.copy()
                    c[:len(a)] += a
                else:
                    c = a.copy()
                    c[:len(b)] = b + c[:len(b)]
                slc_data = c
                # slc_data = np.array(c)
            # if len(slc_data) < 10:
            #     # TODO: need to somehow stitch lists together - may need some nan's??
            #     # loop through all entries
            #     # need to add together arrays??
            #     while counter < len(slc_data):
            #         slc_data = slc_data[counter]
                # pass

            # print(slc_data)
            # TODO: how to compute which slice has z value of 2?? -> should extend only in x and y

            
            
            # TODO: loop through timesteps
            interval_secs = 100
            for time_step in range(t_start, t_max, interval_secs):
            # if firefighting:
            #     slc = t_slice.get_nearest(z=2) # how to get programmatically??
            #     time_step = t_max
            # else:
            #     slc = t_slice.get_nearest(x=20, y=20, z=2)
                # time_step = door_openings['closing_apartment']+120
            
            # time_step = 500


                # choose and output the time step, next to t=75 s
                it = slc.get_nearest_timestep(time_step)
                print(f"Time step: {it}")
                print(f"Simulation time: {slc.times[it]}")

                current = slc_data[it]
                if type(current) == list:
                    current = np.array(current, dtype=np.float64)
                #     # data = list(map(list, zip(*current)))
                #     data = list(map(list, itertools.zip_longest(*current, fillvalue=None)))
                # else:
                #     data = current.T

                data = current.T

                # # only one mesh
                # fig, axs = plt.subplots(2,3, sharex=True, sharey=True)
                # for mesh in range(len(slc)):

                #     slc_data = slc[mesh].data
                #     print(slc_data)

                #     axs.flat[mesh].imshow(
                #             slc_data[it].T, 
                #             origin='lower',
                #             vmin=current_quantity_object["v_min"],
                #             vmax=current_quantity_object["v_max"],
                #             cmap=current_cmap,
                #             extent=slc.extent.as_list())
                # plt.axis('off')
                # plt.show()

                # # below for mapping a value with a colour
                # current_cmap.set_bad('white')
                # mask_value = current_quantity_object["tenable_limit_moe"]
                # data = np.ma.masked_equal(data, mask_value)
                for interp in ['nearest', 'bilinear', 'bicubic', 'spline16', 'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric', 'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos']:
                    plt.imshow(data, 
                                origin='lower',
                                vmin=current_quantity_object["v_min"],
                                vmax=current_quantity_object["v_max"],
                                cmap=current_cmap,
                                # interpolation='nearest',
                                interpolation=interp,
                            extent=slc.extent.as_list())
                    # plt.colorbar(label=f'{current_quantity_object["chart_name"]} {current_quantity_object["units"]}')
                    # plt.xlabel(f'{slc.extent_dirs[0]} / m')
                    # plt.ylabel(f'{slc.extent_dirs[1]} / m')    
                    plt.axis('off') 
                    name_of_chart = f'{current_type}_2dslice{twoD_slice}@{slc.times[it]}secs{interp}'
                    # TODO: create new folder each run
                    # add to project folder if ran from outwith of this script
                    # new_dir_path = './outputSlices'
                    # plt.show()
                    save_chart_high_res(name_of_chart, new_dir_path, 1200)      
                # plt.savefig(f'figs/{name_of_chart}_{i}.svg', bbox_inches='tight')
                # plt.close()
                counter += 1


# Creates an instance of a simulation master-class which manages all data for a given simulation
test_resi = r'C:\Users\IanShaw\Fire Dynamics Group Limited\CFD - Files\Research CFD\1. Graph Generation\Test Cases\Test1\S1_FSA'
new_resi = r'C:\Users\IanShaw\Dropbox\Projects CFD\22. Sweet Street\Resi\Final\L1_West_Core_FSA'
latest_resi = r'C:\Users\IanShaw\Dropbox\Projects CFD\22. Sweet Street\Resi\Final\L1_East_Core_FSA'
desktop_resi = r'C:\Users\IanShaw\Dropbox\Projects CFD\22. Sweet Street\Resi\Final\L1_West_Core_FSA-DESKTOP-NASJ970'
west_l2 = r'C:\Users\IanShaw\Dropbox\Projects CFD\22. Sweet Street\Resi\Final\L2_West_Core_FSA'
path_to_root_directory = (r"C:\Users\IanShaw\Dropbox\Projects CFD\9. 100 Avenue Road\Jan 2023 Corridor Models")
fsa1 = r"C:\Users\IanShaw\Dropbox\Projects CFD\9. 100 Avenue Road\Jan 2023 Corridor Models\FS02-T-FSA"
sensitivity = r"C:\Users\IanShaw\Dropbox\Projects CFD\9. 100 Avenue Road\sensitivity run fs16\FS16_CoreB1_FSA"
black_horse = r"C:\Users\IanShaw\Dropbox\Projects CFD\38. No1 Blackhorse Lane\Models for report 2" #\FS1_MOE
test = r"C:\Users\IanShaw\OneDrive - Fire Dynamics Group Limited\Desktop\Test CFD Common Corridor"
# setup loop for path_to_root_directory
def run_slice_loop(
            path_to_root_directory,
            save_path=None,
            runs_to_skip=None,
            runs_to_not_skip=None,
            save_in_cfd_folder=True
):

    filenames = listdir(path_to_root_directory)
    for run in filenames:
        current_path = (f'{path_to_root_directory}\{run}')
        # if runs_to_skip is None or runs_to_skip not in run:
        if runs_to_not_skip is None or len([f for f in (runs_to_not_skip) if f in run]) > 0 or runs_to_skip is None:
            obtain_slice(
                path_to_directory=current_path, 
                save_in_cfd_folder=save_in_cfd_folder, 
                save_path=save_path
                )

# run_slice_loop(
#             path_to_root_directory=path_to_root_directory,
#             save_path=r'C:\Users\IanShaw\Fire Dynamics Group Limited\CFD - Files\Projects CFD\9. 100 Avenue Road\Jan 2023 Report',
#             # runs_to_skip="FS01-T-MoE"
#             # runs_to_not_skip=["FS14", "FS15", "FS16"]
#             runs_to_not_skip=["FS08"]

# )
run_slice_loop(
            path_to_root_directory=black_horse,
            # save_path=r'outputSlices/No1 Blackhorse Lane',
            # runs_to_skip="FS01-T-MoE"
            # runs_to_not_skip=["FS14", "FS15", "FS16"]
            save_in_cfd_folder=True

)
# obtain_slice(path_to_directory=test)
# was on FS14