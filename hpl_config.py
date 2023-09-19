#---HPM PARSER CONFIG
from enum import Enum

hpl_map_collection_identifier = 'Maps'
hpl_xml_typevars = 'TypeVars'
hpl_xml_inherit_attribute = 'InheritsFrom'

hpl_sub_folders = {'config' : 'config', 'entities' : 'entities', 'particles' : 'particles', \
                    'script' : 'script'}

hpl_asset_filetypes = {'geometry' : '.dae', 'material' : '.mat', 'entity' : '.ent'}

#TODO: rename prefixes to cfg instead of hpl. Create new hpl_environments.py and use env as prefix for global variables.
hpl_asset_material_files = {}
hpl_asset_entity_files = {}
hpl_asset_categories_dict = {}
hpl_ui_var_dict = {}

class hpl_selection(Enum):
    ACTIVE_ENTITY_INSTANCE = 1
    UNACTIVE_ENTITY_INSTANCE = 2
    MOD = 3
    MAPROOT = 4
    MAP = 5
    UNACTIVE_ENTITY = 6
    ACTIVE_ENTITY = 7

hpl_custom_properties_prefixes_dict = {'Var' : 'hpl_parser_var_'}

hpl_properties = {'entities' : 'editor\\userclasses\\EntityClasses.def'}

hpl_datacounter = {'HPMTOTALVERTCOUNT' : 0, 'HPMTOTALFACECORNERCOUNT' : 0, \
                    'HPMTOTALEDGECOUNT' : 0, 'HPMTOTALFACECOUNT' : 0}

hpl_exclude_import_subfolders = {'mods' : 'mods', 'editor' : 'editor', 'viewer' : 'viewer'}

hpl_texture_types = {'Diffuse':'Diffuse','NMap':'Normal Map','Specular':'Specular','Height':'Height'}

hpl_mat_containers = {'Main':'Shader','TextureUnits':'Textures','SpecificVariables':'ShaderValues'}

hpl_dae_containers = {'library_images':'library_images','image':'image','init_from':'init_from'}

hpl_entity_classes_file_sub_path = 'editor\\userclasses\\EntityClasses.def'
hpl_globals_file_sub_path = 'editor\\userclasses\\Globals.def'
hpl_hpm_sub_path = 'mods\\maps\\'
hpl_common_variable_types = [bool, int, float, str]

hpl_level_editor_general_vars_list =    [{'Name':"Active", 'Type':"Bool", 'DefaultValue':"true", 'Description':"Activate or Deactivate the Object"},
                                        {'Name':"Important", 'Type':"Bool", 'DefaultValue':"false", 'Description':""},
                                        {'Name':"Static", 'Type':"Bool", 'DefaultValue':"false", 'Description':"Enable if this entity should stationary."},
                                        {'Name':"CulledByDistance", 'Type':"Bool", 'DefaultValue':"true", 'Description':"Disable if the entity should be always rendered, no matter the distance."},
                                        {'Name':"CulledByFog", 'Type':"Bool", 'DefaultValue':"true", 'Description':"Disable if the entity should be always rendered, even if fog occludes it."}]

hpl_level_editor_general_vars_dict = {'General' : hpl_level_editor_general_vars_list}

hpl_level_editor_entity_type = {'General':'TypeVars/Group', 'LevelEditor_Entity':'InstanceVars', 'Entity_File':'EditorSetupVars/Group'}

                                        #first stop                                                    #search inside container
hpl_entity_file_identifier =            {'Identifier':'Objects'             , 'File':hpl_entity_classes_file_sub_path, 'Tag':None,    'Attribute':None}         #*.hpm file
hpl_entity_class_file_identifier =      {'Identifier':'TypeVars'            , 'File':hpl_entity_classes_file_sub_path, 'Tag':'Group', 'Attribute':'Name'}       #Blender original collection
hpl_leveleditor_general_identifier =    {'Identifier':'UserDefinedVariables', 'File':hpl_hpm_sub_path, 'Tag':None   , 'Attribute':'EntityType'}                 #*.ent file
hpl_leveleditor_entity_identifier =     {'Identifier':'InstanceVars'        , 'File':hpl_entity_classes_file_sub_path, 'Tag':'Group', 'Attribute':'Name'}       #Blender instanced collection

hpl_ent_containers = {'Entity_File':hpl_entity_file_identifier, 'Entity_Class_File':hpl_entity_class_file_identifier, 'LevelEditor_General':hpl_leveleditor_general_identifier, 'LevelEditor_Entity':hpl_leveleditor_entity_identifier}

hpl_detail_mesh_identifier = '_detailmesh'
hpl_variable_identifier = 'hpl_parser_var'
hpl_dropdown_identifier = 'hpl_parser_dropdown'
hpl_entity_type_identifier = 'hpl_enum_entity_type'
hpl_entity_type_value = 'hpl_enum_entity_type_value'