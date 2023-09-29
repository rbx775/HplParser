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

hpl_current_scene_collection = []
hpl_shape_types = ['box','cylinder','capsule','sphere']

class hpl_selection(Enum):
    ACTIVE_ENTITY_INSTANCE = 1
    INACTIVE_ENTITY_INSTANCE = 2
    MOD = 3
    MAPROOT = 4
    MAP = 5
    INACTIVE_ENTITY = 6
    ACTIVE_ENTITY = 7
    ACTIVE_BODY = 8
    INACTIVE_BODY = 9
    INACTIVE_JOINT = 10
    ACTIVE_SHAPE = 11
    INACTIVE_SHAPE = 12
    ACTIVE_HINGE_JOINT = 13
    ACTIVE_BALL_JOINT = 14
    ACTIVE_SLIDER_JOINT = 15
    ACTIVE_SCREW_JOINT = 16

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

hpl_level_editor_general_vars_list =    [
    {'Name':"Active", 'Type':"Bool", 'DefaultValue':"true", 'Description':"Activate or Deactivate the Object"},
    {'Name':"Important", 'Type':"Bool", 'DefaultValue':"false", 'Description':""},
    {'Name':"Static", 'Type':"Bool", 'DefaultValue':"false", 'Description':"Enable if this entity should stationary."},
    {'Name':"CulledByDistance", 'Type':"Bool", 'DefaultValue':"true", 'Description':"Disable if the entity should be always rendered, no matter the distance."},
    {'Name':"CulledByFog", 'Type':"Bool", 'DefaultValue':"true", 'Description':"Disable if the entity should be always rendered, even if fog occludes it."}]

hpl_level_editor_general_vars_dict = {'General' : hpl_level_editor_general_vars_list}

###BODY
hpl_body_properties_vars_list = [
    {'Name':'Material',                     'Type':"String",    'DefaultValue':"Default",       'Description':""},
    {'Name':'Mass',                         'Type':"Int",       'DefaultValue':"0",             'Description':""}, 
    {'Name':'LinearDamping',                'Type':"Float",     'DefaultValue':"0.1",           'Description':""}, 
    {'Name':'AngularDamping',               'Type':"Float",     'DefaultValue':"0.1",           'Description':""}, 
    {'Name':'MaxAngularSpeed',              'Type':"Int",       'DefaultValue':"20",            'Description':""}, 
    {'Name':'MaxLinearSpeed',               'Type':"Int",       'DefaultValue':"20",            'Description':""}, 
    {'Name':'BuoyancyDensityMul',           'Type':"Int",       'DefaultValue':"1",             'Description':""}, 
    {'Name':'BlocksSound',                  'Type':"Bool",      'DefaultValue':"false",         'Description':""}, 
    {'Name':'ContinuousCollision',          'Type':"Bool",      'DefaultValue':"true",          'Description':""}, 
    {'Name':'CanAttachCharacter',           'Type':"Bool",      'DefaultValue':"false",         'Description':""}, 
    {'Name':'PushedByCharacterGravity',     'Type':"Bool",      'DefaultValue':"false",         'Description':""}, 
    {'Name':'CollideCharacter',             'Type':"Bool",      'DefaultValue':"true",          'Description':""}, 
    {'Name':'CollideNonCharacter',          'Type':"Bool",      'DefaultValue':"true",          'Description':""}, 
    {'Name':'Volatile',                     'Type':"Bool",      'DefaultValue':"false",         'Description':""}, 
    {'Name':'UseSurfaceEffects',            'Type':"Bool",      'DefaultValue':"true",          'Description':""}, 
    {'Name':'HasGravity',                   'Type':"Bool",      'DefaultValue':"false",         'Description':""}, 
    {'Name':'BlocksLight',                  'Type':"Bool",      'DefaultValue':"true",          'Description':""}
    ]
hpl_body_properties_vars_dict = {'Body' : hpl_body_properties_vars_list}

###BASE
hpl_joint_base_properties_vars_list = [
    {'Name':'LimitStepCount',               'Type':"Int",       'DefaultValue':"0",             'Description':""}, 
    {'Name':'Stiffness',                    'Type':"Int",       'DefaultValue':"0",             'Description':""}, 
    {'Name':'StickyMinLimit',               'Type':"Bool",      'DefaultValue':"false",         'Description':""}, 
    {'Name':'StickyMaxLimit',               'Type':"Bool",      'DefaultValue':"false",         'Description':""}, 
    {'Name':'CollideBodies',                'Type':"Bool",      'DefaultValue':"true",          'Description':""}, 
    {'Name':'Breakable',                    'Type':"Bool",      'DefaultValue':"false",         'Description':""}, 
    {'Name':'BreakForce',                   'Type':"Int",       'DefaultValue':"0",             'Description':""}, 
    ]
hpl_joint_base_properties_vars_dict = {'JointBase' : hpl_joint_base_properties_vars_list}

###BALL
hpl_joint_ball_properties_vars_list = [
    {'Name':'MaxConeAngle',                 'Type':"Int",       'DefaultValue':"0",             'Description':""},
    {'Name':'MaxTwistAngle',                'Type':"Int",       'DefaultValue':"0",             'Description':""}, 
    ]
hpl_joint_ball_properties_vars_dict = {'BallParams' : hpl_joint_ball_properties_vars_list}

###HINGE
hpl_joint_hinge_properties_vars_list = [
    {'Name':'MinAngle',                     'Type':"Int",       'DefaultValue':"0",             'Description':""},
    {'Name':'MaxAngle',                     'Type':"Int",       'DefaultValue':"0",             'Description':""}, 
    ]
hpl_joint_hinge_properties_vars_dict = {'HingeParams' : hpl_joint_hinge_properties_vars_list}

###SLIDE
hpl_joint_slider_properties_vars_list = [
    {'Name':'MinDistance',                  'Type':"Int",       'DefaultValue':"0",             'Description':""},
    {'Name':'MaxDistance',                  'Type':"Int",       'DefaultValue':"0",             'Description':""}, 
    ]
hpl_joint_slider_properties_vars_dict = {'SlideParams' : hpl_joint_slider_properties_vars_list}

###SCREW
hpl_joint_screw_properties_vars_list = [
    {'Name':'MinAngle',                     'Type':"Int",       'DefaultValue':"0",             'Description':""},
    {'Name':'MaxAngle',                     'Type':"Int",       'DefaultValue':"0",             'Description':""}, 
    ]
hpl_joint_screw_properties_vars_dict = {'ScrewParams' : hpl_joint_screw_properties_vars_list}

###SOUND
hpl_joint_sound_properties_vars_list = [
    {'Name':'MoveType',                 'Type':"Enum",      'DefaultValue':"Linear",    'Description':""},
    {'Name':'MoveSound',                'Type':"File",      'DefaultValue':"",          'Description':""}, 
    {'Name':'MinMoveSpeed',             'Type':"Float",     'DefaultValue':"0.1",       'Description':""}, 
    {'Name':'MinMoveFreq',              'Type':"Float",     'DefaultValue':"0.95",      'Description':""}, 
    {'Name':'MinMoveFreqSpeed',         'Type':"Float",     'DefaultValue':"0.2",       'Description':""}, 
    {'Name':'MinMoveVolume',            'Type':"Float",     'DefaultValue':"0.01",      'Description':""}, 
    {'Name':'MaxMoveSpeed',             'Type':"Float",     'DefaultValue':"2",         'Description':""}, 
    {'Name':'MaxMoveFreq',              'Type':"Float",     'DefaultValue':"1.1",       'Description':""}, 
    {'Name':'MaxMoveFreqSpeed',         'Type':"Float",     'DefaultValue':"0.7",       'Description':""}, 
    {'Name':'MaxMoveVolume',            'Type':"Float",     'DefaultValue':"0.8",       'Description':""}, 
    {'Name':'MiddleMoveSpeed',          'Type':"Float",     'DefaultValue':"0.5",       'Description':""}, 
    {'Name':'MiddleMoveVolume',         'Type':"Float",     'DefaultValue':"0.5",       'Description':""}, 
    {'Name':'BreakSound',               'Type':"File",      'DefaultValue':"",          'Description':""}, 
    {'Name':'MinLimitSound',            'Type':"File",      'DefaultValue':"",          'Description':""}, 
    {'Name':'MinLimitMinSpeed',         'Type':"Float",     'DefaultValue':"0",         'Description':""}, 
    {'Name':'MinLimitMaxSpeed',         'Type':"Float",     'DefaultValue':"0",         'Description':""}, 
    {'Name':'MaxLimitSound',            'Type':"File",      'DefaultValue':"",          'Description':""}, 
    {'Name':'MaxLimitMinSpeed',         'Type':"Float",     'DefaultValue':"0",         'Description':""}, 
    {'Name':'MaxLimitMaxSpeed',         'Type':"Float",     'DefaultValue':"0",         'Description':""}, 
    ]
hpl_joint_sound_properties_vars_dict = {'JointSounds' : hpl_joint_sound_properties_vars_list}

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
hpl_internal_type_identifier = 'hpl_internal_type'

hpl_shape_identifier = 'Shape'
hpl_joint_identifier = 'Joint'
hpl_body_identifier = 'Body'

