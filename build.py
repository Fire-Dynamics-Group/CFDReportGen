# build.py
import subprocess

# # Read content from the txt file
# with open("template_base64.txt", "r") as f:
#     base64_content = f.read().strip()

# # Generate new Python code with embedded base64 content
# with open("auto_report.py", "r") as f:
#     code_template = f.read()

# new_code = code_template.replace("TEMPLATE_BASE64 = ''", f"TEMPLATE_BASE64 = '{base64_content}'")

# with open("main.py", "w") as f:
#     f.write(new_code)

# Build exe using PyInstaller
subprocess.run(["pyinstaller", "auto_report.spec"])
