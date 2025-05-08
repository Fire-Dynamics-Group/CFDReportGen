from pdf_generator import GeneratePDFSlice
import os
import cv2

# Example parameters
project_text = 'Project Name'
client_text = 'Client Name'
scenario_text = 'Scenario Description'
slice_location_text = 'z = 1.8m'
date_text = '28 FEBRUARY 2024'
drawn_by_text = 'Your Name'

draw_block_input = [
    project_text,
    client_text,
    scenario_text,
    slice_location_text,
    date_text,
    drawn_by_text
]

# Variables for slice type and orientation
slice_type = "SOOT VISIBILITY"
slice_orientation = "zslice2"

img_dir = os.path.abspath(os.path.join(os.getcwd(), 'outputSlices', 'FS_10_CoreB1_FSA'))
img_paths = [
    os.path.join(img_dir, f)
    for f in os.listdir(img_dir)
    if f.startswith(f"{slice_type}_{slice_orientation}") and f.endswith('.png')
]
img_paths.sort()  # Optional: sort by filename (which usually sorts by time)

# Repeat images as needed to get 9
while len(img_paths) < 9:
    img_paths += img_paths[:9-len(img_paths)]
img_paths = img_paths[:9]

# Verify image can be read
test_img = cv2.imread(img_paths[0])
if test_img is None:
    raise ValueError(f"Failed to read test image: {img_paths[0]}")

# Create instance of PDF generator
generator = GeneratePDFSlice(
    n_slice=9,  # Number of slices per page (1, 5, or 9)
    img_loc=img_paths,  # List of 9 image paths
    slice_type=slice_type,  # Using variable slice type
    draw_block_input=draw_block_input,
    slice_min_value=0,  # Minimum value for color bar
    slice_max_value=10,  # Maximum value for color bar
    t_difference=60,  # Time difference between slices
    t_start=60,  # Start time
    output_loc='.',  # Output directory
    output_name='output.pdf',  # Output filename
    crop=True  # Whether to crop images
) 