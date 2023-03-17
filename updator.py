import os
import shutil
import datetime

# Define the code to be added or updated in each file
maya_utils_code = '''
from maya import cmds

def create_camera_node(name='camera'):
    camera = cmds.camera(name=name)
    return camera[0]
'''

maya_init_code = '''
from .maya_utils import create_camera_node
'''

nuke_utils_code = '''
import nuke

def create_camera_node(name='camera'):
    camera = nuke.createNode('Camera2', inpanel=False)
    camera.setName(name)
    return camera
'''

nuke_init_code = '''
from .nuke_utils import create_camera_node
'''

# Define the paths to the files to be updated
services_path = 'P:/pipeline/templates/packages/services'
maya_utils_path = os.path.join(services_path, 'maya/maya_utils.py')
maya_init_path = os.path.join(services_path, 'maya/__init__.py')

nuke_utils_path = os.path.join(services_path, 'nuke/nuke_utils.py')
nuke_init_path = os.path.join(services_path, 'nuke/__init__.py')

# Function to update a file with new code
def update_file(file_path, code):
    with open(file_path, 'a') as f:
        f.write(code)

# Create a backup of the services package
bak_path = 'P:/pipeline/templates/packages/bak'
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = os.path.join(bak_path, timestamp)

shutil.copytree(services_path, backup_path)
print(f"Backup created at {backup_path}")

# Update the files
update_file(maya_utils_path, maya_utils_code)
update_file(maya_init_path, maya_init_code)

update_file(nuke_utils_path, nuke_utils_code)
update_file(nuke_init_path, nuke_init_code)

print("Files have been updated.")