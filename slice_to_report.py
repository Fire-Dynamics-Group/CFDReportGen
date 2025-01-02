from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches
import os
import fitz  # PyMuPDF
from PIL import Image
from pdfgeneration import generate_overlay, apply_overlay

'''
    TODO: place images considering the legend and spacing between cells

'''


def create_metric_temp_dirs(tmp_dir, metric):
    dirs = {
        "images": os.path.join(tmp_dir, metric, "images"),
        "overlays": os.path.join(tmp_dir, metric, "overlays"),
        "merged": os.path.join(tmp_dir, metric, "merged"),
    }

    for d in dirs:
        os.makedirs(dirs[d])

    return dirs

def add_images_to_pdf_template(template_path, images, output_path):
    # Open the existing PDF template
    pdf_document = fitz.open(template_path)
    page = pdf_document[0]

    # A3 landscape dimensions in points (1 inch = 72 points)
    page_width = 16.54 * 72  # 1190.48 points
    page_height = 11.69 * 72  # 841.68 points

    # # Define the grid dimensions and positions
    cell_width = page_width / 3
    cell_height = page_height / 3
    # templates\config\Standard Slice Files - 9.config.json

    grid_positions = [
        (cell_width * col, page_height - cell_height * (row + 1))
        for row in range(3)
        for col in range(3)
    ]
    # Convert grid positions from inches to points (1 inch = 72 points)
    grid_positions_inches = [
        [0.3507402, 21.1990402, 13.2855598, 29.3502598],
        [13.5146402, 21.1970402, 26.4860598, 29.3461598],
        [26.7190402, 21.2052402, 39.6852598, 29.3510598],
        [0.3492402, 12.1966402, 13.2849598, 20.4011598],
        [13.5134402, 12.1962402, 26.4830598, 20.4014598],
        [26.7141402, 12.1956402, 39.6836598, 20.4042598],
        [0.3541402, 3.1940402, 13.2842598, 11.4030598],
        [13.5167402, 3.1968402, 26.4853598, 11.4033598],
        [26.7120402, 3.1925402, 39.6834598, 11.4035598]
    ]
    grid_positions = [[val * 30 for val in pos] for pos in grid_positions_inches]
    cell_width = grid_positions_inches[0][2] - grid_positions_inches[0][0]
    cell_height = grid_positions_inches[0][3] - grid_positions_inches[0][1]
    cell_size = (round(30*cell_width), round(30*cell_height))  # Assuming each image is 150x150 points
    while True:
        generate_overlay(
            metric_temp_dirs,
            template_config,
            image_filenames,
            sorted_image_times[start_index: end_index],
            overlay_number,
        )

        if end_index >= num_files:
            break

        start_index = end_index
        end_index = start_index + num_images_per_template
        overlay_number += 1

    apply_overlay(TEMPLATE_DIR, template_name, metric_name, metric_temp_dirs)
    # cell_center_offset = (cell_width / 2, cell_height / 2)

    for i, img_path in enumerate(images):
        if i >= len(grid_positions):
            break  # Stop if there are more images than grid positions

        # Open and resize the image to fit the cell size
        img = Image.open(img_path)
        img = img.resize(cell_size, Image.ANTIALIAS)

        # Save the resized image to a temporary path
        img_temp_path = f"temp_img_{i}.png"
        img.save(img_temp_path)

        # Calculate the top-left corner to center the image
        center_x = grid_positions[i][0]
        center_y = grid_positions[i][3]

        # Insert the image into the PDF
        rect = fitz.Rect(center_x, center_y, center_x + cell_size[0], center_y + cell_size[1])
        page.insert_image(rect, filename=img_temp_path)

    # Save the modified PDF
    pdf_document.save(output_path)
# Paths
template_pdf_path = "templates\Standard Slice Files - 9 - Temperature.pdf"
output_pdf_path = "output.pdf"

# List of image paths (should be 9 images for a 3x3 grid)
images = ["image cleaner/test.png", 
        #   "image2.png", "image3.png",
        #   "image4.png", "image5.png", "image6.png",
        #   "image7.png", "image8.png", "image9.png"
          ]
images = [images[0] for f in range(9)]
add_images_to_pdf_template(template_pdf_path, images, output_pdf_path)


def add_slice_to_report(startup_path = "output.docx"):
    document_path = "template_9_image.docx"

    from docxtpl import DocxTemplate
    doc = DocxTemplate(document_path)
    # insert image
    def create_inline_image(image_file, template=doc, width=Inches(6), height=Inches(4)):
        return InlineImage(template, image_descriptor=image_file, width=width, height=height)
    # FDAI_grey.png
    first_chart = create_inline_image("outputSlices\FS_10_CoreB1_FSA\SOOT VISIBILITY_xslice0@60.00445secs_chart.png")

    context = {
        "IMAGE1": first_chart
        }
    
    import os
    doc.render(context)
    doc.save(startup_path) 
    os.startfile(startup_path)

# add_slice_to_report()