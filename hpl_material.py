import bpy, os
from . import hpl_config
from . import hpl_property_io

class HPL_MATERIAL():

    def export_to_png(_image):
        
        png = bpy.data.images.load(_image.filepath) if _image.filepath else _image
        png.file_format = 'PNG'

        #   TODO make the temp texture save folder a setting in the preferences. So it can be changed by the user.
        blend_file_path = os.path.join(bpy.path.abspath('//'), '_export_to_png', os.path.splitext(_image.name)[0]+'.png')

        png.save_render(blend_file_path)
        return png, blend_file_path

    def find_textures(node, tex_node):
        if node.type == 'TEX_IMAGE':
            #   Skip if the texture node is empty.
            if not hasattr(node.image, 'filepath'):
                return
            
            filepath = bpy.path.abspath(node.image.filepath)

            #   Is the texture only saved internally within the .blend?
            if not filepath:
                png, filepath = HPL_MATERIAL.export_to_png(node.image)

            #   Is the texture an .exr file?
            if '.exr' in filepath:
                png, filepath = HPL_MATERIAL.export_to_png(node.image)

            hpl_config.texture_dict[tex_node] = filepath
        
        if node.name == 'Principled BSDF':
            for t in hpl_config.texture_dict:
                if not t:
                    continue
                if node.inputs[t].links:
                    HPL_MATERIAL.find_textures(node.inputs[t].links[0].from_node, t)
            return
        
        for input in node.inputs:
            if input.links:
                HPL_MATERIAL.find_textures(input.links[0].from_node, tex_node)

    def get_textures_from_material(mat):
        hpl_config.texture_dict = hpl_config.texture_default_dict.copy()
        for node in mat.node_tree.nodes:
            if node.name == 'Material Output':
                HPL_MATERIAL.find_textures(node, None)
        return hpl_config.texture_dict

    def hpl_purge_materials():
        for bpy_data_iter in (
            bpy.data.materials,
            bpy.data.images
        ):
            for id_data in bpy_data_iter:
                bpy_data_iter.remove(id_data, do_unlink=True)
        bpy.ops.outliner.orphans_purge(do_recursive=True)

    def hpl_load_images(image_info): #TODO: Better function

        def check_for_image():
            for img in bpy.data.images:
                return image_name == img.name
            
        for i in image_info:
            image_name = image_info[i].split('.')[0].split('\\')[-1]
            
            if check_for_image():
                if os.path.isfile(image_info[i]):
                    bpy.data.images.load(image_info[i], check_existing=True)

    def hpl_create_shader_for_mat(links, nodes, mat_vars, mat_file):
        dist = 300
        root = bpy.context.scene.hpl_parser.hpl_game_root_path
        imported_images_ = {'Diffuse':'Base Color', 'Specular':'IOR', 'NMap':'NormalMap'}
        imported_images = ['Base Color', 'IOR', 'NormalMap']
        texture_setup = ['ShaderNodeTexImage', 'ShaderNodeMapping', 'ShaderNodeTexCoord']
        normal_texture_setup = ['ShaderNodeNormalMap', 'ShaderNodeCombineColor', 'ShaderNodeSeparateColor', 'ShaderNodeTexImage', 'ShaderNodeMapping', 'ShaderNodeTexCoord']
        main_types = ['ShaderNodeOutputMaterial', 'ShaderNodeBsdfPrincipled',  texture_setup]

        images_link_dict = {'Base Color': {'output': 0, 'input': 0}, 'IOR': {'output': 0, 'input': 12}, 'NormalMap': {'output': 0, 'input': 5}}
        links_dict = {'ShaderNodeOutputMaterial':None, 'ShaderNodeBsdfPrincipled': {'output':[0], 'input': [0]}, 'ShaderNodeNormalMap': {'output':[0], 'input': [5]}, \
            'ShaderNodeCombineColor': {'output': [0], 'input': [1]}, 'ShaderNodeSeparateColor': {'output': [0,1,2], 'input': [0,1,2]}, \
            'ShaderNodeTexImage': {'output': [0], 'input': [0]}, 'ShaderNodeMapping': {'output': [0], 'input': [0]}, 'ShaderNodeTexCoord': {'output': [0], 'input': [0]}}
        
        def get_texture_path_from_mat():
            image_info = {}
            for ii in imported_images_:
                for mv in mat_vars:
                    if ii == mv:
                        image_info[imported_images_[mv]] = mat_file.rsplit('\\', 1)[0]+'\\'+mat_vars[mv]['File'].rsplit('/', 1)[-1] #TODO: fix, is faulty
            return image_info
        image_info = get_texture_path_from_mat() if mat_vars else None

        if image_info:
            HPL_MATERIAL.hpl_load_images(image_info)

        def create_nodes(node, prev_node, pos, tex_node):
            n = nodes.new(type=node)
            n.location = pos
            if links_dict[node]:
                if not tex_node:
                    for o, i in zip(links_dict[node]['output'], links_dict[node]['input']):
                        links.new(n.outputs[o], prev_node.inputs[i])
                else:
                    prev_node = nodes['Principled BSDF']
                    links.new(n.outputs[images_link_dict[tex_node]['output']], prev_node.inputs[images_link_dict[tex_node]['input']]) 
                    if image_info:
                        if tex_node in image_info:
                            n.image = bpy.data.images.get(image_info[tex_node].rsplit('\\')[-1]) 
            return n

        prev_node = None
        for node_count, node in enumerate(main_types):
            if isinstance(main_types[node_count], list):
                #loop through texture Types (dif, spec, nrm)
                for tt_count, tt_node in enumerate(imported_images):
                    #loop through texture nodes (imageNode, mapping node, texture coord)
                    for tn_count, tn_node in enumerate(texture_setup if 'Normal' not in tt_node else normal_texture_setup):
                        prev_node = create_nodes(tn_node, prev_node, (-(node_count+tn_count)*dist, -tt_count*dist), tt_node if tn_node == 'ShaderNodeTexImage' else None)
                    prev_node = nodes['Principled BSDF']
            else:
                prev_node = create_nodes(node, prev_node, (-node_count*dist, 0), None)

    def hpl_create_materials(category):  

        def create_material(id):
            mat = bpy.data.materials.get(id) 
            if mat is None:
                mat = bpy.data.materials.new(name=id)
            mat.use_nodes = True

            if mat.node_tree:
                mat.node_tree.links.clear()
                mat.node_tree.nodes.clear()
            return mat

        for col in bpy.data.collections:
            mat_file = hpl_config.hpl_asset_categories_dict[category][col.name]['material']
            mat_vars = hpl_property_io.hpl_properties.get_material_vars(mat_file)
            mat = create_material(col.name)

            HPL_MATERIAL.hpl_create_shader_for_mat(mat.node_tree.links, mat.node_tree.nodes, mat_vars, mat_file)

            for obj in [obj for obj in col.all_objects[:] if obj.type == 'MESH']:
                #Eventhough all materials are purged from the file, objects still can have material slots.
                #for i in range(len(obj.material_slots)):
                #    bpy.ops.object.material_slot_remove({'object': obj})

                if obj.data.materials:
                    obj.data.materials[0] = mat
                else:
                    obj.data.materials.append(mat)