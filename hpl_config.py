#---HPM PARSER CONFIG
import dataclasses
from typing import Dict
from enum import Enum

hpl_invoke_mod_dialogue = 1
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
hpl_mat_ui_var_dict = {}
hpl_var_dict = {}
hpl_enum_iterator = 0
hpl_ui_enum_dict = {}
hpl_joint_set_current_dict = {}
hpl_joint_set_warning = False

hpl_previous_project_col = None
hpl_previous_scene_collection = []
hpl_shape_types = ['box','cylinder','capsule','sphere']

hpl_mod_init_files = {'main_init.cfg' : {'Directories' : '','Variables' : '', 'StartMap' : ''}, 'main_settings' : 'main_settings.cfg', 'main_menu' : 'main_menu.cfg'}
'''
class HPLConfig:
    def __init__(self):
        self._hpl_outliner_selection = None

    @property
    def hpl_outliner_selection(self):
        return self._hpl_outliner_selection

    @hpl_outliner_selection.setter
    def hpl_outliner_selection(self, value):
        self._hpl_outliner_selection = value
        # You can add additional code here to be executed when the value is set
'''
hpl_outliner_selection = None
hpl_previous_outliner_selection = None
hpl_viewport_selection = None
hpl_active_material = None
hpl_skip_scene_listener = False

#   UI variables
hpl_ui_outliner_selection_name = ''
hpl_ui_viewport_selection_name = ''
hpl_ui_active_material_name = ''

hpl_ui_outliner_selection_color_tag = ''
hpl_ui_outliner_selection_instancer_name = ''
hpl_ui_outliner_selection_prop_type = ''


class hpl_selection(Enum):
    NONE = 0
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
    BLANK_SUBMESH = 17
    ACTIVE_SUBMESH = 18
    INACTIVE_SUBMESH = 19

hpl_selection_type = None

@dataclasses.dataclass
class EntityTypeData:
    id: int
    active: bool

class hpl_entity_type(Enum):
    MAP = EntityTypeData(1, True)
    ENTITY = EntityTypeData(2, True)
    ENTITY_INSTANCE = EntityTypeData(3, True)
    BODY = EntityTypeData(4, True)
    SHAPE = EntityTypeData(5, True)
    SUBMESH = EntityTypeData(6, True)
    LIGHT = EntityTypeData(7, True)
    MATERIAL = EntityTypeData(8, True)
    JOINT = EntityTypeData(9, True)
    STATIC_OBJECT = EntityTypeData(10, True)

    def init(self):
        return self.value.id
'''
class hpl_entity_type(Enum):
    MAP = 1
    ENTITY = 2
    ENTITY_INSTANCE = 3
    BODY = 4
    SHAPE = 5
    SUBMESH = 6
    LIGHT = 7
    MATERIAL = 8
    JOINT = 9
'''
hpl_selection_entity_type = None

class hpl_shape_type(Enum):
    BOX = 1
    SPHERE = 2
    CYLINDER = 3
    CAPSULE = 4

    def init(self):
        return self.value

class hpl_joint_type(Enum):
    HINGE = 1
    SCREW = 2
    BALL = 3
    SLIDER = 4

    def init(self):
        return self.value

hpl_entity_baseclass_list = []

hpl_static_object_class_list = ['Static_Object']

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
hpl_int_array_type_identifier_list = ['vector2', 'vector3', 'vector4', 'vec2', 'vec3', 'vec4', 'color', 'color3', 'color4'] 

#   Only Dict in which the default values are not stored as strings
hpl_instance_general_vars_dict = {'General' :
    {
        'Active'            : {'Type' : "Bool",   'DefaultValue' : True,  'Description' : "Activate or Deactivate the Object"},
        'Important'         : {'Type' : "Bool",   'DefaultValue' : False, 'Description' : ""},
        'Static'            : {'Type' : "Bool",   'DefaultValue' : False, 'Description' : "Enable if this entity should stationary."},
        'CulledByDistance'  : {'Type' : "Bool",   'DefaultValue' : True,  'Description' : "Disable if the entity should be always rendered, no matter the distance."},
        'CulledByFog'       : {'Type' : "Bool",   'DefaultValue' : True,  'Description' : "Disable if the entity should be always rendered, even if fog occludes it."},
    }
}

###BODY
hpl_body_properties_vars_dict = {'Body' : 
    {
        'Material'                  : {'Type' : "String", 'DefaultValue' : "Default", 'Description' : ""},
        'Mass'                      : {'Type' : "Float",  'DefaultValue' : "0",       'Description' : ""}, 
        'LinearDamping'             : {'Type' : "Float",  'DefaultValue' : "0.1",     'Description' : ""},
        'AngularDamping'            : {'Type' : "Float",  'DefaultValue' : "0.1",     'Description' : ""},
        'MaxAngularSpeed'           : {'Type' : "Int",    'DefaultValue' : "20",      'Description' : ""},
        'MaxLinearSpeed'            : {'Type' : "Int",    'DefaultValue' : "20",      'Description' : ""},
        'BuoyancyDensityMul'        : {'Type' : "Int",    'DefaultValue' : "1",       'Description' : ""},
        'BlocksLight'               : {'Type' : "Bool",   'DefaultValue' : "true",    'Description' : ""},
        'BlocksSound'               : {'Type' : "Bool",   'DefaultValue' : "false",   'Description' : ""},
        'ContinuousCollision'       : {'Type' : "Bool",   'DefaultValue' : "true",    'Description' : ""},
        'CanAttachCharacter'        : {'Type' : "Bool",   'DefaultValue' : "false",   'Description' : ""},
        'PushedByCharacterGravity'  : {'Type' : "Bool",   'DefaultValue' : "false",   'Description' : ""},
        'CollideCharacter'          : {'Type' : "Bool",   'DefaultValue' : "true",    'Description' : ""},
        'CollideNonCharacter'       : {'Type' : "Bool",   'DefaultValue' : "true",    'Description' : ""},
        'Volatile'                  : {'Type' : "Bool",   'DefaultValue' : "false",   'Description' : ""},
        'UseSurfaceEffects'         : {'Type' : "Bool",   'DefaultValue' : "true",    'Description' : ""},
        'HasGravity'                : {'Type' : "Bool",   'DefaultValue' : "false",   'Description' : ""},
    }
}

###BASE
hpl_joint_base_properties_vars_dict = {'JointBase' :
    {
        'LimitStepCount'     : {'Type' : "Int",   'DefaultValue' : "0",      'Description' : ""},
        'Stiffness'          : {'Type' : "Int",   'DefaultValue' : "0",      'Description' : ""},
        'StickyMinLimit'     : {'Type' : "Bool",  'DefaultValue' : "false",  'Description' : ""},
        'StickyMaxLimit'     : {'Type' : "Bool",  'DefaultValue' : "false",  'Description' : ""},
        'CollideBodies'      : {'Type' : "Bool",  'DefaultValue' : "true",   'Description' : ""},
        'Breakable'          : {'Type' : "Bool",  'DefaultValue' : "false",  'Description' : ""},
        'BreakForce'         : {'Type' : "Int",   'DefaultValue' : "0",      'Description' : ""},
    }
}

###BALL
hpl_joint_ball_properties_vars_dict = {'BallParams' :
    {
        'MaxConeAngle'   : {'Type' : "Int",   'DefaultValue' : "0",  'Description' : ""},
        'MaxTwistAngle'  : {'Type' : "Int",   'DefaultValue' : "0",  'Description' : ""},
    }
}

###HINGE
hpl_joint_hinge_properties_vars_dict = {'HingeParams' :
    {
        'MinAngle' : {'Type' : "Int", 'DefaultValue' : "0", 'Description' : ""},
        'MaxAngle' : {'Type' : "Int", 'DefaultValue' : "0", 'Description' : ""},
    }
}

###SLIDE
hpl_joint_slider_properties_vars_dict = {'SlideParams' : 
    {
        'MinDistance' : {'Type' : "Int", 'DefaultValue' : "0", 'Description' : ""},
        'MaxDistance' : {'Type' : "Int", 'DefaultValue' : "0", 'Description' : ""},
    }
}

###SCREW
hpl_joint_screw_properties_vars_dict = {'ScrewParams' :
    {
        'MinAngle' : {'Type' : "Int", 'DefaultValue' : "0", 'Description' : ""},
        'MaxAngle' : {'Type' : "Int", 'DefaultValue' : "0", 'Description' : ""},
    }
}

###SOUND
hpl_joint_sound_properties_vars_dict = {'JointSounds' :
    {
        'MoveType'           : {'Type' : "bb",    'DefaultValue' : "Linear", 'Description' : ""},
        'MoveSound'          : {'Type' : "File",  'DefaultValue' : "",       'Description' : ""},
        'MinMoveSpeed'       : {'Type' : "Float", 'DefaultValue' : "0.1",    'Description' : ""},
        'MinMoveFreq'        : {'Type' : "Float", 'DefaultValue' : "0.95",   'Description' : ""},
        'MinMoveFreqSpeed'   : {'Type' : "Float", 'DefaultValue' : "0.2",    'Description' : ""},
        'MinMoveVolume'      : {'Type' : "Float", 'DefaultValue' : "0.01",   'Description' : ""},
        'MaxMoveSpeed'       : {'Type' : "Float", 'DefaultValue' : "2",      'Description' : ""},
        'MaxMoveFreq'        : {'Type' : "Float", 'DefaultValue' : "1.1",    'Description' : ""},
        'MaxMoveFreqSpeed'   : {'Type' : "Float", 'DefaultValue' : "0.7",    'Description' : ""},
        'MaxMoveVolume'      : {'Type' : "Float", 'DefaultValue' : "0.8",    'Description' : ""},
        'MiddleMoveSpeed'    : {'Type' : "Float", 'DefaultValue' : "0.5",    'Description' : ""},
        'MiddleMoveVolume'   : {'Type' : "Float", 'DefaultValue' : "0.5",    'Description' : ""},
        'BreakSound'         : {'Type' : "File",  'DefaultValue' : "",       'Description' : ""},
        'MinLimitSound'      : {'Type' : "File",  'DefaultValue' : "",       'Description' : ""},
        'MinLimitMinSpeed'   : {'Type' : "Float", 'DefaultValue' : "0",      'Description' : ""},
        'MinLimitMaxSpeed'   : {'Type' : "Float", 'DefaultValue' : "0",      'Description' : ""},
        'MaxLimitSound'      : {'Type' : "File",  'DefaultValue' : "",       'Description' : ""},
        'MaxLimitMinSpeed'   : {'Type' : "Float", 'DefaultValue' : "0",      'Description' : ""},
        'MaxLimitMaxSpeed'   : {'Type' : "Float", 'DefaultValue' : "0",      'Description' : ""},
    }
}

###SUBMESH
hpl_submesh_properties_vars_dict = {'General' :
    {
        'Static'            : {'Type':"Bool",      'DefaultValue':"True",      'Description':""},
    }
}

###COLLIDER
hpl_collider_properties_vars_dict = {'General' :
    {
        'ConnectedParentBodyID' : {'Type' : "String", 'DefaultValue' : "", 'Description' : ""},
        'ConnectedChildBodyID'  : {'Type' : "String", 'DefaultValue' : "", 'Description' : ""},
    }
}

hpl_material_properties_sd_vars_dict = {'SolidDiffuse' :
    {
        'HeightMapScale'            : {'Type' : "Float",    'DefaultValue' : 0.05, 'Description' : ""},
        'HeightMapBias'             : {'Type' : "Float",    'DefaultValue' : 0.0,    'Description' : ""},
        'IlluminationBrightness'    : {'Type' : "Float",    'DefaultValue' : 1.0,    'Description' : ""},
        'FrenselBias'               : {'Type' : "Float",    'DefaultValue' : 0.2,  'Description' : ""},
        'FrenselPow'                : {'Type' : "Float",    'DefaultValue' : 8.0,    'Description' : ""},
        'AlphaDissolveFilter'       : {'Type' : "Bool",     'DefaultValue' : False,'Description' : ""},
        'DetailUvMul'               : {'Type' : "Vector2",  'DefaultValue' : (4.0, 4.0),  'Description' : ""},
        'DetailWeight_Diffuse'      : {'Type' : "Float",    'DefaultValue' : 1.0,    'Description' : ""},
        'DetailWeight_Specular'     : {'Type' : "Float",    'DefaultValue' : 1.0,    'Description' : ""},
        'DetailWeight_Normal'       : {'Type' : "Float",    'DefaultValue' : 1.0,    'Description' : ""},
        'DetailFadeStart'           : {'Type' : "Float",    'DefaultValue' : 5.0,    'Description' : ""},
        'DetailFadeEnd'             : {'Type' : "Float",    'DefaultValue' : 10.0,   'Description' : ""},
        'SwayActive'                : {'Type' : "Bool",     'DefaultValue' : False,'Description' : ""},
        'SwayForceFieldAffected'    : {'Type' : "Bool",     'DefaultValue' : True, 'Description' : ""},
        'SwayFreq'                  : {'Type' : "Float",    'DefaultValue' : 1.0,    'Description' : ""},
        'SwayAmplitude'             : {'Type' : "Float",    'DefaultValue' : 0.1,  'Description' : ""},
        'SwaySpeed'                 : {'Type' : "Float",    'DefaultValue' : 1.0,    'Description' : ""},
        'SwayOctaveMuls'            : {'Type' : "Vector3",  'DefaultValue' : (0.125, 0.25, 1), 'Description' : ""},
        'SwayForceFieldMul'         : {'Type' : "Float",    'DefaultValue' : 0.3,  'Description' : ""},
        'SwayForceFieldMax'         : {'Type' : "Float",    'DefaultValue' : 0.6,  'Description' : ""},
        'SwayYFreqMul'              : {'Type' : "Float",    'DefaultValue' : 0.0,    'Description' : ""},
        'SwaySingleDir'             : {'Type' : "Bool",     'DefaultValue' : False,'Description' : ""},
        'SwaySingleDirVector'       : {'Type' : "Vector3",  'DefaultValue' : (0.0, 0.0, 1.0), 'Description' : ""},
        'SwaySingleSampleVector'    : {'Type' : "Vector3", 'DefaultValue' : (1.0, 0.0, 0.0),   'Description' : ""},
        'LiquidTrickleColor'        : {'Type' : "Color",   'DefaultValue' : (0.0, 0.0, 0.0, 1.0), 'Description' : ""},
        'LiquidTrickleSpecular'     : {'Type' : "Color",   'DefaultValue' : (0.0, 0.0, 0.0, 0.0), 'Description' : ""},
        'LiquidTrickleLoopFade'     : {'Type' : "Bool",    'DefaultValue' : False,   'Description' : ""},
        'LiquidTrickleFadeSpeed'    : {'Type' : "Vector2", 'DefaultValue' : (0.5, 0.5), 'Description' : ""},
        'LiquidTrickleEdgeSize'     : {'Type' : "Float",   'DefaultValue' : 0.5,     'Description' : ""},
        'LiquidTrickleDryness'      : {'Type' : "Float",   'DefaultValue' : 0.5,     'Description' : ""},
        'LiquidTrickleBlendMode'    : {'Type' : "String",  'DefaultValue' : "Alpha",   'Description' : ""},
    }
}

hpl_material_shader_properties_vars_dict = {'Main' :
    {
        'DepthTest'        : {'Type' : "Bool",   'DefaultValue' : True,     'Description' : ""},
        'PhysicsMaterial'  : {'Type' : "String", 'DefaultValue' : "Default",  'Description' : ""},
        'SolidDiffuse'     : {'Type' : "String", 'DefaultValue' : "SolidDiffuse", 'Description' : ""},
    }
}
hpl_material_properties_vars_dict = {**hpl_material_shader_properties_vars_dict, **hpl_material_properties_sd_vars_dict}

hpl_level_editor_entity_type = {'General':'TypeVars/Group', 'LevelEditor_Entity':'InstanceVars', 'Entity_File':'EditorSetupVars/Group'}

                                        #first stop                                                    #search inside container
hpl_entity_file_identifier =            {'Identifier':'Objects'             , 'File':hpl_entity_classes_file_sub_path, 'Tag':None,    'Attribute':None}         #*.hpm file
hpl_entity_class_file_identifier =      {'Identifier':'TypeVars'            , 'File':hpl_entity_classes_file_sub_path, 'Tag':'Group', 'Attribute':'Name'}       #Blender original collection
hpl_leveleditor_general_identifier =    {'Identifier':'UserDefinedVariables', 'File':hpl_hpm_sub_path, 'Tag':None   , 'Attribute':'EntityType'}                 #*.ent file
hpl_leveleditor_entity_identifier =     {'Identifier':'InstanceVars'        , 'File':hpl_entity_classes_file_sub_path, 'Tag':'Group', 'Attribute':'Name'}       #Blender instanced collection

hpl_ent_containers = {'Entity_File':hpl_entity_file_identifier, 'Entity_Class_File':hpl_entity_class_file_identifier, 'LevelEditor_General':hpl_leveleditor_general_identifier, 'LevelEditor_Entity':hpl_leveleditor_entity_identifier}

hpl_detail_mesh_identifier = '_detailmesh'
hpl_variable_identifier = 'hpl_parser_var'
hpl_enum_variable_identifier = 'hpl_parser_var_enum'
hpl_file_variable_identifier = 'hpl_parser_var_file'
hpl_dropdown_identifier = 'hpl_parser_dropdown'
hpl_entity_type_identifier = 'hpl_enum_entity_type'
hpl_entity_type_value = 'hpl_enum_entity_type_value'
hpl_internal_type_identifier = 'hpl_internal_type'

hpl_submesh_identifier = 'SubMesh'
hpl_shape_identifier = 'Shape'
hpl_joint_identifier = 'Joint'
hpl_body_identifier = 'Body'

hpl_export_warnings = {}
main_window = None

texconv_subpath = "\\tools\\texconv.exe"
texconv_download_path = 'https://github.com/Microsoft/DirectXTex/releases/latest/download/texconv.exe'
is_texconv_available = False

texture_dict = {'Base Color': "", 'Specular': "", 'Normal': ""}
texture_default_dict = {'Base Color': "", 'Specular': "", 'Normal': ""}#{'Base Color': 'toy_football.dds', 'Specular': 'toy_football_spec.dds', 'Normal': 'toy_football_nrm.dds'}
texture_format_dict = {'Base Color': "BC1_UNORM", 'Specular': "BC3_UNORM", 'Normal': "BC5_UNORM"}

#   Values will be evaluated with eval() for mod creation.
hpl_mod_files = {   'main_init.cfg' : {
                                    'MainSaveFolder' : 'bpy.context.scene.hpl_parser.hpl_project_root_col+\'/save/\'',
                                    'File' : 'bpy.context.scene.hpl_parser.hpl_startup_map_col+\'.hpm\'',
                                    'GameName' : 'bpy.context.scene.hpl_parser.hpl_project_root_col',
                                    },
                    'entry.hpc' : {
                                    'Title' : 'bpy.context.scene.hpl_parser.hpl_project_root_col',
                                    },
                    'WIPMod.cfg' : {    
                                    'Path' : 'bpy.context.scene.hpl_parser.hpl_game_root_path + \'mods\\\' + bpy.context.scene.hpl_parser.hpl_project_root_col + \'\\entry.hpc\'',
                                    },
                  }