import os
import uuid
file_name = 'blender_assets.cats.txt'

def get_catalogue_id(path, asset_file):
    with open(path + file_name, 'r') as f:
        for line in f.readlines():
            if line.startswith(("#", "VERSION", "\n")):
                continue
            name = line.split(":")[2].split("\n")[0]
            if name == asset_file:
                file_uuid = line.split(":")[0]
                return file_uuid

def append_catalogue(path, id):
    if not os.path.exists(path +  file_name):
        with open(path + file_name, 'w') as f:
            f.writelines("VERSION 1"+'\n')

    with open(path + file_name, 'a') as f:
        f.writelines(str(uuid.uuid1())+':'+id+':'+id+'\n')

def reset_catalogue(path):
    if os.path.isfile(path +  file_name):
        os.remove(path +  file_name)