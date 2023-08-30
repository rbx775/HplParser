import bpy
import os
from mathutils import Vector
import xml.etree.ElementTree as xtree
from . import hpl_config

class hpl_properties():
            
    def traverse_tree_headers(xml_tree, key_tag):
        for tree in xml_tree:
            if key_tag in tree.tag:
                for i in tree:
                    hpl_properties.entity_baseclass_list.append(i.attrib['Name'])

    def get_entity_vars(ent):

        root = bpy.context.scene.hpl_parser.hpl_game_root_path

        entity_type = 'Prop_Grab' #TODO: get *.ent file class of selected object.
        def_file_path = root + hpl_config.hpl_properties['entities']

        def_file = ""
        with open(def_file_path, 'rt', encoding='ascii') as fobj:
            def_file = fobj.read()

        #TODO: build xml handler that ignores quotation segments
        def_file = def_file.replace('&', '')
        def_file = def_file.replace(' < ', '')
        def_file = def_file.replace(' > ', '')

        parser = xtree.XMLParser(encoding="ascii")
        tree = xtree.fromstring(def_file, parser=parser)

        derived_class = {}
        base_class = {}

        for category in tree.iter():
            if entity_type in category.attrib.values():
                if hpl_config.hpl_xml_inherit_attribute in category.attrib:
                    derived_class = category.attrib
                for e in iter(category):
                    if hpl_config.hpl_xml_typevars in e.tag:
                        e=e[0]
                        for i in e:
                            pass
        derived_class.update(derived_class)
        return derived_class
    
    def get_material_vars(mat_file):
        if mat_file:
            tree = xtree.parse(mat_file).getroot()
            mat_data = {}

            for c in hpl_config.hpl_mat_containers:
                data_tree = tree.find(f'{c}')
                for data in data_tree.iter():
                    if data.attrib:
                        mat_data[data.tag] = data.attrib
            return mat_data
        else:
            return None
        
    def get_material_file_from_dae(dae_file):

        root = bpy.context.scene.hpl_parser.hpl_game_root_path
        def check_for_mat_tags(dae_file):    
            with open(dae_file, 'r', encoding='ascii') as fobj:
                fl = False
                #TODO: proper xml parser ?
                #io reading the file for a few lines is somehow more reliable than ElementTree. Or I suck at ElementTree
                for i in range(0,49):
                    xml_line = fobj.readline()
                    if '<image id=' in xml_line:
                        fl = True
                    if fl:
                        if '<init_from>' in xml_line:
                            return xml_line
                        else:
                            fl = False
            return None
        
        #alternative heuristic to determine mesh:mat pairs
        def step_through_chars(xml_line, mat):
            skip_x = False
            score = 0
            fscore = 0
            for x in xml_line:
                if score > fscore:
                    fscore = score
                if skip_x:
                    skip_x = False
                    continue
                for m in mat:
                    if x == m:
                        score = score + 1
                        skip_x = True
                        continue
                    else:
                        score = 0
            return fscore
        
        if dae_file:
            xml_line = check_for_mat_tags(dae_file)
            if xml_line:

                if '.' in xml_line:
                    xml_line = xml_line.rsplit('.')[0]
                xml_line = xml_line.rsplit('\\')[-1]
                xml_line = xml_line.rsplit('/')[-1]
                
                #check if *.mat is in *.daes subfolder beforehand
                path_length = len(dae_file.rsplit('\\')[-1])
                mat_path = dae_file[:-path_length] + xml_line + '.mat'
                if mat_path:
                    if not os.path.isfile(mat_path):
                        return mat_path
                
                #heuristic to check for across-subfolder *.dae - *.mat references
                score = 0
                final_score = 0
                mat_name = None
                for mat in hpl_config.hpl_asset_material_files:
                    if mat in xml_line:
                        score = abs(len(set(mat) - set(xml_line))-len(xml_line))
                        if score > final_score:
                            final_score = score
                            mat_name = hpl_config.hpl_asset_material_files[mat]
                return mat_name
            
    def load_def_file(file_path):
        root = bpy.context.scene.hpl_parser.hpl_game_root_path
        def_file_path = root + file_path

        if os.path.isfile(def_file_path):
            def_file = ""
            with open(def_file_path, 'r') as def_f:
                def_file = def_f.read()

            #TODO: build xml handler that ignores quotation segments
            def_file = def_file.replace('&', '')
            def_file = def_file.replace(' < ', '')
            def_file = def_file.replace(' > ', '')
            return def_file
        return ''

    entity_baseclass_list = []
    entity_prop_dict = {}
    def get_leveleditor_properties_from_entity_classes(id, group_type):
        
        entity_class_tree = xtree.fromstring(hpl_properties.load_def_file(hpl_config.hpl_entity_classes_file_sub_path))
        globals_tree = xtree.fromstring(hpl_properties.load_def_file(hpl_config.hpl_entity_classes_file_sub_path))

        sub_prop = 'Prop_PlayerBody'
        variable_type = 'TypeVars'
        inherits = ''

        def get_vars(classes, variable_type):
            var_dict = {}
            for sub_classes in classes:
                if sub_classes.tag == variable_type:
                    for groups in sub_classes:
                        var_dict[groups.get('Name')] = list(v.attrib for v in groups.iter("Var"))
                    return var_dict

        classes = [var for var in entity_class_tree.findall(f'.//Class') if var.get('Name') == sub_prop]
        base_classes = [var for var in entity_class_tree.findall(f'.//BaseClass')]
        var_dict = get_vars(classes[0], variable_type)

        inherits = [classes[0].attrib[var] for var in classes[0].attrib if var == 'InheritsFrom']
        components = [classes[0].attrib[var].replace(' ', '').rsplit(',') for var in classes[0].attrib if var == 'UsesComponents'][0]

        #Adding Inherits
        for i in inherits:
            base_classes = [var for var in entity_class_tree.findall(f'.//BaseClass') if var.get('Name') == i]
            var_dict.update(get_vars(base_classes[0], variable_type))

        #Adding components
        var_hidden_dict = []
        for c in components:
            base_classes = [var for var in globals_tree.findall(f'.//Components') if var.get('Name') == c]
            print(base_classes)
            var_hidden_dict = get_vars(base_classes, variable_type)
        
        print(var_dict)
        print(var_hidden_dict)
        #hpl_properties.entity_prop_dict['Inherits']    

        #print(var_dict)
        #hpl_properties.entity_prop_dict['Data'].update(var_dict)

    def get_base_classes_from_entity_classes():
        def_file = hpl_properties.load_def_file(hpl_config.hpl_entity_classes_file_sub_path)

        if def_file:
            xml_root = xtree.fromstring(def_file)
            hpl_properties.traverse_tree_headers(xml_root, 'Class')
            return hpl_properties.entity_baseclass_list
        else:
            return None
        
    def initialize_editor_vars(ent):

        delete_vars = []
        for var in ent.items():
            if 'hpl_' in var[0]:
                delete_vars.append(var[0])

        for var in delete_vars:
            del ent[var]

        if hpl_properties.entity_prop_dict:
            for var in hpl_properties.entity_prop_dict['Data']:
                var_value = var['DefaultValue']
                var_type = var['Type'].lower()

                if var_type == 'vec3':
                    var_type = 'tuple'
                    var_value = (0.0,0.0,0.0)

                if var_type == 'bool':
                    if var_value == 'false':
                        var_value = None

                variable = 'hpl_'+var['Name']

                
                if var_type == 'string':
                    ent[variable] = ''
                else:
                    ent[variable] = eval(var_type)(var_value)
                
                id_props = ent.id_properties_ui(variable)
                if 'Max' in var:
                    id_props.update(min=var['Min'],max=var['Max'])
                if 'Description' in var:
                    id_props.update(description=var['Description'])

                ent.property_overridable_library_set(f'["{variable}"]', True)
                '''
                #location = getattr(object, "location")
                if var_type == 'string':
                    setattr(ent, variable, '')
                else:
                    setattr(ent, variable, eval(var_type)(var_value))
                '''




                {'InteractConnection': [{'Name': 'Animation', 'Type': 'String', 'DefaultValue': '', 'Description': 'Name of the animation to be influenced by the interact connection.'}, {'Name': 'AnimationDirection', 'Type': 'Enum', 'DefaultValue': 'Both', 'Description': 'The direction the animation is allowed to move when influenced by the interact connection.'}, {'Name': 'AnimationStuckState', 'Type': 'Int', 'DefaultValue': '-1', 'Description': "Locks the animation when it reaches the specified state. -1 = can't get stuck."}], 'Base': [{'Name': 'Health', 'Type': 'Float', 'DefaultValue': '1.0', 'Description': 'The amount of damamge an entity can take.'}, {'Name': 'Toughness', 'Type': 'Int', 'DefaultValue': '0', 'Description': 'If strength of attack is 1 lower than damage is halfed. 2 or more lower damage is 0. If equal or higher, damage stays the same.'}, {'Name': 'MaxInteractDistance', 'Type': 'Int', 'DefaultValue': '0', 'Description': 'The max distance that interaction can take place. If within player height, then made in 2D (xz). If 0, default is used!'}, {'Name': 'EventTag', 'Type': 'String', 'DefaultValue': '', 'Description': 'A tag string used that is mainly used by the event system to group certain type of objects.'}, {'Name': 'ShowHints', 'Type': 'Bool', 'DefaultValue': 'true', 'Description': 'If it is allowed to show hints upon interaction with entity.'}, {'Name': 'LifeLength', 'Type': 'Float', 'DefaultValue': '0', 'Description': 'A time after which the entity automatically breaks. 0=lasts forever.'}, {'Name': 'DissolveDuringLifeDecrease', 'Type': 'Bool', 'DefaultValue': 'true', 'Description': 'If the entity should dissolve when the life count decreases.'}, {'Name': 'QuickSave', 'Type': 'Bool', 'DefaultValue': 'false', 'Description': 'Skips saving variables and only saves the transform of this prop type and its sub entities'}, {'Name': 'FullGameSave', 'Type': 'Bool', 'DefaultValue': 'false', 'Description': 'If the all things in the entity should be saved when exiting the level. Only use on few entities!'}, {'Name': 'AllowMapTransfer', 'Type': 'Bool', 'DefaultValue': 'false', 'Description': 'If the prop can be moved between maps'}, {'Name': 'VoiceSourceBone', 'Type': 'String', 'DefaultValue': '', 'Description': "The bone where a voice will be played in the Prop. If '' then props position is used."}], 'Physics': [{'Name': 'BlocksLineOfSight', 'Type': 'Enum', 'DefaultValue': 'MaterialBased', 'Description': 'If this object should block line of sight tests. If Material Based is selected only solid SubMeshes will be checked'}, {'Name': 'MainPhysicsBody', 'Type': 'String', 'DefaultValue': '', 'Description': 'This is the name of the most imporant physics body. The body that sounds are played from and objects attached to (attached as results from script!).'}, {'Name': 'NoGravityWhenUnderwater', 'Type': 'Bool', 'DefaultValue': 'false', 'Description': 'When this object is in an liquid area and fully submerged it has no gravity.'}, {'Name': 'DisableFreezeAtStart', 'Type': 'Bool', 'DefaultValue': 'false', 'Description': 'By default (unless skeletalphysics) bodies are frozen at start of a map. This disables that for this entity.'}], 'Script': [{'Name': 'CustomScriptFile', 'Type': 'String', 'DefaultValue': '', 'Description': 'The file of the custom script.'}, {'Name': 'CustomScriptClass', 'Type': 'String', 'DefaultValue': '', 'Description': 'The class name of the custom script. '}], 'Appearance': [{'Name': 'ShowMesh', 'Type': 'Bool', 'DefaultValue': 'true', 'Description': 'If the mesh should be visible. Having this false might useful for blocker objects.'}, {'Name': 'DissolveOnDestruction', 'Type': 'Bool', 'DefaultValue': 'false', 'Description': 'If the dissolve effect should used when entity is destroyed.'}, {'Name': 'DissolveTime', 'Type': 'Float', 'DefaultValue': '1.0', 'Description': 'The time it takes for the dissolve effect to be over.'}, {'Name': 'RandomizeAnimationStart', 'Type': 'Bool', 'DefaultValue': 'true', 'Description': 'Should the animation start time be randomized at start. If false all animations of entity are synchronized.'}, {'Name': 'RootMotionBone', 'Type': 'String', 'DefaultValue': '', 'Description': 'Bone to use when setting up root motion. The entity will follow the movement of this bone'}], 'Effects': [{'Name': 'EffectsOnSound', 'Type': 'File', 'ResType': 'Sound', 'DefaultValue': '', 'Description': 'Sound made when turned on. (used for lamps lit/unlit, but also other entity types).'}, {'Name': 'EffectsOffSound', 'Type': 'File', 'ResType': 'Sound', 'DefaultValue': '', 'Description': 'Sound made when turned off. (used for lamps lit/unlit, but also other entity types).'}, {'Name': 'EffectsOnTime', 'Type': 'Float', 'DefaultValue': '0.2', 'Description': 'Time it takes for on effect to be done. (used for lamps lit/unlit, but also other entity types).'}, {'Name': 'EffectsOffTime', 'Type': 'Float', 'DefaultValue': '0.2', 'Description': 'Time it takes for off effect to be done. (used for lamps lit/unlit, but also other entity types).'}], 'StaticMove': [{'Name': 'StaticMoveCheckCollision', 'Type': 'Bool', 'DefaultValue': 'false', 'Description': 'If a static move should check for collision. (used when static bodies are moved through script of type specific effect.)'}, {'Name': 'StaticMoveStartSound', 'Type': 'File', 'ResType': 'Sound', 'DefaultValue': '', 'Description': 'Sound made at the start of a static move. (used when static bodies are moved through script of type specific effect.)'}, {'Name': 'StaticMoveStopSound', 'Type': 'File', 'ResType': 'Sound', 'DefaultValue': '', 'Description': 'Sound made at the end of a static move. (used when static bodies are moved through script of type specific effect.)'}, {'Name': 'StaticMoveLoopSound', 'Type': 'File', 'ResType': 'Sound', 'DefaultValue': '', 'Description': 'Sound made during a static move. (used when static bodies are moved through script of type specific effect.)'}, {'Name': 'StaticMoveLoopSoundFade', 'Type': 'Bool', 'DefaultValue': 'true', 'Description': 'If the static move sound should fade in and out or be instant. (used when static bodies are moved through script of type specific effect.)'}], 'Break': [{'Name': 'BreakActive', 'Type': 'Bool', 'DefaultValue': 'false', 'Description': 'If entity is broken when hit hard enough or health is 0.'}, {'Name': 'CustomBreakBehaviour', 'Type': 'Bool', 'DefaultValue': 'false', 'Description': 'If true, void OnCustomBreak() will be called inside the prop script and override the normal break behaviour.'}, {'Name': 'BreakOnlyOnMainBody', 'Type': 'Bool', 'DefaultValue': 'false', 'Description': 'If the entity will only break from impact if the main body is hit.'}, {'Name': 'BreakDestroyJoints', 'Type': 'Bool', 'DefaultValue': 'false', 'Description': 'If all physics joints should be destroyed when broken.'}, {'Name': 'BreakMinEnergy', 'Type': 'Float', 'DefaultValue': '100', 'Description': 'The minimum energy needed for breakage. Energy = Object1Speed * Object1Mass + Object2Speed * Object2Mass. Speed = m/s. If Object 2 is floor or something static, its speed is always 0 and does not contribute to total energy!'}, {'Name': 'BreakEntity', 'Type': 'File', 'Extensions': 'ent', 'DefaultValue': '', 'Description': 'The entity this entity turns into when broken.'}, {'Name': 'BreakEntityAlignBody', 'Type': 'String', 'DefaultValue': '', 'Description': "The body BreakEntity uses to align itself when created. ''=no entity is created."}, {'Name': 'BreakSound', 'Type': 'File', 'ResType': 'Sound', 'DefaultValue': '', 'Description': 'The sound made when broken.'}, {'Name': 'BreakAIEventSoundRadius', 'Type': 'Float', 'DefaultValue': '18', 'Description': 'The radius of the sound AI event.'}, {'Name': 'BreakAIEventSoundPrio', 'Type': 'Int', 'DefaultValue': '4', 'Description': 'The prio of the sound AI event.'}, {'Name': 'BreakParticleSystem', 'Type': 'File', 'ResType': 'ParticleSystem', 'DefaultValue': '', 'Description': 'Particle system shown when broken.'}, {'Name': 'BreakImpulse', 'Type': 'Float', 'DefaultValue': '4', 'Description': 'Impulse (speed in m/s really) added to all bodies in BreakENtity when created. The direction of impulse is outwards from center of entity.'}]}
