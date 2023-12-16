import os
import subprocess
from urllib import request

from . import hpl_entity_exporter

from . import hpl_config

class HPL_TEXTURE():
    def convert_texture(root, relative_path):

        exported_textures = hpl_config.texture_default_dict.copy()

        for tex in exported_textures:
            
            FNULL = open(os.devnull, 'w')
            exe_path = os.path.dirname(os.path.realpath(__file__)) + hpl_config.texconv_subpath
            args = f'\"{exe_path}\" -r \"{hpl_config.texture_dict[tex]}\" -ft dds -f {hpl_config.texture_format_dict[tex]} -y -o \"{root + relative_path[:-1]}\"' #R8_UNORM BC1_UNORM
            p = subprocess.call(args, shell=False)
            if p != 0:
                hpl_entity_exporter.add_warning_message(' Error converting Texture, bad format? ', 'Texture', hpl_config.texture_dict[tex])
            else:
                exported_textures[tex] = relative_path + os.path.basename(hpl_config.texture_dict[tex]).split('.')[0] + '.dds'

        return exported_textures
                    
        #subprocess.call(args, stdout=FNULL, stderr=FNULL, shell=False)exported_textures
