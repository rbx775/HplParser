import bpy
import os
import subprocess
from urllib import request

from . import hpl_config

class HPL_TEXTURE():
    def convert_texture(file_path, file_destination):

        FNULL = open(os.devnull, 'w')
        exe_path = os.path.dirname(os.path.realpath(__file__)) + hpl_config.texconv_subpath
        args = f'\"{os.path.dirname(os.path.realpath(__file__)) + hpl_config.texconv_subpath}\" -r \"{file_path}\" -ft dds -f R8_UNORM -y -o \"{file_destination[:-1]}\"'
        
        subprocess.call(args, stdout=FNULL, stderr=FNULL, shell=False)
