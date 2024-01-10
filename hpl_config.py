#---HPM PARSER CONFIG
import dataclasses
from typing import Dict
from enum import Enum
import math

hpl_invoke_mod_dialogue = 1
hpl_icon_value = 0
hpl_xml_typevars = 'TypeVars'
hpl_xml_inherit_attribute = 'InheritsFrom'

hpl_sub_folders = {'config' : 'config', 'entities' : 'entities', 'particles' : 'particles', \
                    'script' : 'script'}

hpl_asset_filetypes = {'geometry' : '.dae', 'material' : '.mat', 'entity' : '.ent'}

hpl_previous_scene_object_count = math.inf
hpl_previous_scene_collection_count = math.inf

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

hpl_outliner_selection = None
hpl_previous_outliner_selection = None
hpl_viewport_selection = None
hpl_active_material = None
hpl_previous_active_material = None
hpl_skip_scene_listener = False

#   UI variables
hpl_ui_outliner_selection_name = ''
hpl_ui_viewport_selection_name = ''
hpl_ui_active_material_name = ''

hpl_ui_outliner_selection_color_tag = ''
hpl_ui_outliner_selection_instancer_name = ''
hpl_ui_outliner_selection_prop_type = ''
hpl_ui_folder_entities_col = ''
hpl_ui_folder_maps_col = ''
hpl_ui_folder_static_objects_col = ''
hpl_ui_folder_project_root_col = ''

hpl_valid_operational_folders = True

@dataclasses.dataclass
class EntityTypeData:
    EntityType: int
    InstancerName: str
    state: bool

class hpl_entity_type(Enum):
    NONE = 0
    SUBMESH = 1
    ENTITY = 2
    ENTITY_INSTANCE = 3
    MOD = 4
    MAP_FOLDER = 5
    ENTITY_FOLDER = 6
    STATIC_OBJECT_FOLDER = 7
    FOLDER = 8
    MAP = 9
    BODY = 10
    AREA = 11
    STATIC_OBJECT = 12
    STATIC_OBJECT_INSTANCE = 13
    MATERIAL = 14

    SPHERE_SHAPE = 20
    BOX_SHAPE = 21
    CYLINDER_SHAPE = 22
    CAPSULE_SHAPE = 23

    HINGE_JOINT = 30
    BALL_JOINT = 31
    SLIDER_JOINT = 32
    SCREW_JOINT = 33

    POINT_LIGHT = 40
    SPOT_LIGHT = 41
    BOX_LIGHT = 42

    def init(self):
        return self.value

hpl_selection_type = ''
hpl_selection_state = False
hpl_selection_inactive_reason = ''
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
    
class hpl_light_type(Enum):
    POINT = 1
    SPOT = 2
    BOX = 3

    def init(self):
        return self.value

hpl_entity_baseclass_list = []
hpl_area_baseclass_list = []

hpl_static_object_class_list = ['Static_Object']

hpl_custom_properties_prefixes_dict = {'Var' : 'hpl_parser_var_'}

hpl_properties = {'entities' : 'editor\\userclasses\\EntityClasses.def'}

hpl_datacounter = {'HPMTOTALVERTCOUNT' : 0, 'HPMTOTALFACECORNERCOUNT' : 0, \
                    'HPMTOTALEDGECOUNT' : 0, 'HPMTOTALFACECOUNT' : 0}

hpl_exclude_import_subfolders = {'mods' : 'mods', 'editor' : 'editor', 'viewer' : 'viewer'}

hpl_texture_types = {'Diffuse':'Diffuse','NMap':'Normal Map','Specular':'Specular','Height':'Height'}

hpl_mat_containers = {'Main':'Shader','TextureUnits':'Textures','SpecificVariables':'ShaderValues'}

hpl_dae_containers = {'library_images':'library_images','image':'image','init_from':'init_from'}

hpl_joint_identifier_dict = {'BALL_JOINT' : 'JointBall', 'HINGE_JOINT' : 'JointHinge', 'SLIDER_JOINT' : 'JointSlider', 'SCREW_JOINT' : 'JointScrew'}
hpl_light_identifier_dict = {'POINT_LIGHT' : 'PointLight', 'SPOT_LIGHT' : 'SpotLight', 'BOX_LIGHT' : 'BoxLight'}


hpl_entity_classes_file_sub_path = 'editor\\userclasses\\EntityClasses.def'
hpl_area_classes_file_sub_path = 'editor\\userclasses\\AreaClasses.def'
hpl_globals_file_sub_path = 'editor\\userclasses\\Globals.def'
hpl_hpm_sub_path = 'mods\\maps\\'
hpl_common_variable_types = [bool, int, float, str, list]
hpl_int_array_type_identifier_list = ['vector2', 'vector3', 'vector4', 'vec2', 'vec3', 'vec4', 'color', 'color3', 'color4'] 

hpl_static_object_map_vars_dict = {'General' :
    {
        'CulledByDistance'      : {'Type' : "Bool",       'DefaultValue' : True,  'Description' : "Disable if the entity should be always rendered, no matter the distance."},
        'CulledByFog'           : {'Type' : "Bool",       'DefaultValue' : True,  'Description' : "Disable if the entity should be always rendered, even if fog occludes it."},
    },
    'Static Object' : {
        'Collides'              : {'Type' : "Bool",   'DefaultValue' : True,                  'Description' : ""},
        'CastShadows'           : {'Type' : "Bool",   'DefaultValue' : True,                  'Description' : ""},
        'IsOccluder'            : {'Type' : "Bool",   'DefaultValue' : True,                  'Description' : ""},
        'ColorMul'              : {'Type' : "Color",  'DefaultValue' : (1.0, 1.0, 1.0, 1.0),  'Description' : ""},
        'IllumColor'            : {'Type' : "Color",  'DefaultValue' : (1.0, 1.0, 1.0, 1.0),  'Description' : ""},
        'IllumBrightness'       : {'Type' : "Float",  'DefaultValue' : 1.0,                   'Description' : ""},
    }
}

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
        'Mass'                      : {'Type' : "Float",  'DefaultValue' : 0.0,       'Description' : ""}, 
        'LinearDamping'             : {'Type' : "Float",  'DefaultValue' : 0.1,     'Description' : ""},
        'AngularDamping'            : {'Type' : "Float",  'DefaultValue' : 0.1,     'Description' : ""},
        'MaxAngularSpeed'           : {'Type' : "Int",    'DefaultValue' : 20,      'Description' : ""},
        'MaxLinearSpeed'            : {'Type' : "Int",    'DefaultValue' : 20,      'Description' : ""},
        'BuoyancyDensityMul'        : {'Type' : "Int",    'DefaultValue' : 1,       'Description' : ""},
        'BlocksLight'               : {'Type' : "Bool",   'DefaultValue' : True,    'Description' : ""},
        'BlocksSound'               : {'Type' : "Bool",   'DefaultValue' : False,   'Description' : ""},
        'ContinuousCollision'       : {'Type' : "Bool",   'DefaultValue' : True,    'Description' : ""},
        'CanAttachCharacter'        : {'Type' : "Bool",   'DefaultValue' : False,   'Description' : ""},
        'PushedByCharacterGravity'  : {'Type' : "Bool",   'DefaultValue' : False,   'Description' : ""},
        'CollideCharacter'          : {'Type' : "Bool",   'DefaultValue' : True,    'Description' : ""},
        'CollideNonCharacter'       : {'Type' : "Bool",   'DefaultValue' : True,    'Description' : ""},
        'Volatile'                  : {'Type' : "Bool",   'DefaultValue' : False,   'Description' : ""},
        'UseSurfaceEffects'         : {'Type' : "Bool",   'DefaultValue' : True,    'Description' : ""},
        'HasGravity'                : {'Type' : "Bool",   'DefaultValue' : False,   'Description' : ""},
    }
}

###BASE
hpl_joint_base_properties_vars_dict = {'JointBase' :
    {
        'LimitStepCount'     : {'Type' : "Int",   'DefaultValue' : 0,      'Description' : ""},
        'Stiffness'          : {'Type' : "Int",   'DefaultValue' : 0,      'Description' : ""},
        'StickyMinLimit'     : {'Type' : "Bool",  'DefaultValue' : False,  'Description' : ""},
        'StickyMaxLimit'     : {'Type' : "Bool",  'DefaultValue' : False,  'Description' : ""},
        'CollideBodies'      : {'Type' : "Bool",  'DefaultValue' : True,   'Description' : ""},
        'Breakable'          : {'Type' : "Bool",  'DefaultValue' : False,  'Description' : ""},
        'BreakForce'         : {'Type' : "Int",   'DefaultValue' : 0,      'Description' : ""},
    }
}

###BALL
hpl_joint_ball_properties_vars_dict = {'BallParams' :
    {
        'MaxConeAngle'   : {'Type' : "Int",   'DefaultValue' : 0,  'Description' : ""},
        'MaxTwistAngle'  : {'Type' : "Int",   'DefaultValue' : 0,  'Description' : ""},
    }
}

###HINGE
hpl_joint_hinge_properties_vars_dict = {'HingeParams' :
    {
        'MinAngle' : {'Type' : "Int", 'DefaultValue' : 0, 'Description' : ""},
        'MaxAngle' : {'Type' : "Int", 'DefaultValue' : 0, 'Description' : ""},
    }
}

###SLIDE
hpl_joint_slider_properties_vars_dict = {'SlideParams' : 
    {
        'MinDistance' : {'Type' : "Int", 'DefaultValue' : 0, 'Description' : ""},
        'MaxDistance' : {'Type' : "Int", 'DefaultValue' : 0, 'Description' : ""},
    }
}

###SCREW
hpl_joint_screw_properties_vars_dict = {'ScrewParams' :
    {
        'MinAngle' : {'Type' : "Int", 'DefaultValue' : 0, 'Description' : ""},
        'MaxAngle' : {'Type' : "Int", 'DefaultValue' : 0, 'Description' : ""},
    }
}

###SOUND
hpl_joint_sound_properties_vars_dict = {'JointSounds' :
    {
        'MoveType'           : {'Type' : "Enum",  'DefaultValue' : "Linear", 'EnumValues' : [['Linear', 'Angular'], 'Linear'], 'Description' : ""},
        'MoveSound'          : {'Type' : "File",  'DefaultValue' : "",       'Description' : ""},
        'MinMoveSpeed'       : {'Type' : "Float", 'DefaultValue' : 0.1,      'Description' : ""},
        'MinMoveFreq'        : {'Type' : "Float", 'DefaultValue' : 0.95,     'Description' : ""},
        'MinMoveFreqSpeed'   : {'Type' : "Float", 'DefaultValue' : 0.2,      'Description' : ""},
        'MinMoveVolume'      : {'Type' : "Float", 'DefaultValue' : 0.01,     'Description' : ""},
        'MaxMoveSpeed'       : {'Type' : "Float", 'DefaultValue' : 2.0,      'Description' : ""},
        'MaxMoveFreq'        : {'Type' : "Float", 'DefaultValue' : 1.1,      'Description' : ""},
        'MaxMoveFreqSpeed'   : {'Type' : "Float", 'DefaultValue' : 0.7,      'Description' : ""},
        'MaxMoveVolume'      : {'Type' : "Float", 'DefaultValue' : 0.8,      'Description' : ""},
        'MiddleMoveSpeed'    : {'Type' : "Float", 'DefaultValue' : 0.5,      'Description' : ""},
        'MiddleMoveVolume'   : {'Type' : "Float", 'DefaultValue' : 0.5,      'Description' : ""},
        'BreakSound'         : {'Type' : "File",  'DefaultValue' : "",       'Description' : ""},
        'MinLimitSound'      : {'Type' : "File",  'DefaultValue' : "",       'Description' : ""},
        'MinLimitMinSpeed'   : {'Type' : "Float", 'DefaultValue' : 0.0,      'Description' : ""},
        'MinLimitMaxSpeed'   : {'Type' : "Float", 'DefaultValue' : 0.0,      'Description' : ""},
        'MaxLimitSound'      : {'Type' : "File",  'DefaultValue' : "",       'Description' : ""},
        'MaxLimitMinSpeed'   : {'Type' : "Float", 'DefaultValue' : 0.0,      'Description' : ""},
        'MaxLimitMaxSpeed'   : {'Type' : "Float", 'DefaultValue' : 0.0,      'Description' : ""},
    }
}

###SUBMESH
hpl_submesh_properties_vars_dict = {'General' :
    {
        'Static'            : {'Type':"Bool",      'DefaultValue': True,      'Description':""},
    }
}

###COLLIDER
hpl_collider_properties_vars_dict = {'General' :
    {
        'ConnectedParentBodyID' : {'Type' : "Enum",   'DefaultValue' : "High",   'EnumValues' : [['Low', 'Medium', 'High', 'VeryHigh'], "High"], 'Description' : ""},
        'ConnectedChildBodyID'  : {'Type' : "Enum",   'DefaultValue' : "High",   'EnumValues' : [['Low', 'Medium', 'High', 'VeryHigh'], "High"], 'Description' : ""},
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
        'SwayOctaveMuls'            : {'Type' : "Vector3",  'DefaultValue' : (0.125, 0.25, 1.0), 'Description' : ""},
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

hpl_light_general_vars_dict = {'General' :
    {
        'Static'            : {'Type' : "Bool",   'DefaultValue' : False, 'Description' : "Enable if this entity should stationary."},
        'CulledByDistance'  : {'Type' : "Bool",   'DefaultValue' : True,  'Description' : "Disable if the entity should be always rendered, no matter the distance."},
        'CulledByFog'       : {'Type' : "Bool",   'DefaultValue' : True,  'Description' : "Disable if the entity should be always rendered, even if fog occludes it."},
    }
}

hpl_light_flicker_properties_vars_dict = {'Flicker' :
    {
        'FlickerActive'             : {'Type' : "Bool",   'DefaultValue' : False,    'Description' : ""},
        'FlickerOnMinLength'        : {'Type' : "Int",    'DefaultValue' : 0,        'Description' : ""},
        'FlickerOnMaxLength'        : {'Type' : "Int",    'DefaultValue' : 0,        'Description' : ""},
        'FlickerOnPS'               : {'Type' : "String", 'DefaultValue' : "",       'Description' : ""},
        'FlickerOnSound'            : {'Type' : "String", 'DefaultValue' : "",       'Description' : ""},
        'FlickerOffMinLength'       : {'Type' : "Int",    'DefaultValue' : 0,        'Description' : ""},
        'FlickerOffMaxLength'       : {'Type' : "Int",    'DefaultValue' : 0,        'Description' : ""},
        'FlickerOffPS'              : {'Type' : "String", 'DefaultValue' : "",       'Description' : ""},
        'FlickerOffSound'           : {'Type' : "String", 'DefaultValue' : "",       'Description' : ""},
        'FlickerOffColor'           : {'Type' : "Color",  'DefaultValue' : (0.0, 0.0, 0.0, 1.0), 'Description' : ""},
        'FlickerOffRadius'          : {'Type' : "Float",  'DefaultValue' : 0.0,        'Description' : ""},
        'FlickerFade'               : {'Type' : "Bool",   'DefaultValue' : False,    'Description' : ""},
        'FlickerOnFadeMinLength'    : {'Type' : "Int",    'DefaultValue' : 0,        'Description' : ""},
        'FlickerOnFadeMaxLength'    : {'Type' : "Int",    'DefaultValue' : 0,        'Description' : ""},
        'FlickerOffFadeMinLength'   : {'Type' : "Int",    'DefaultValue' : 0,        'Description' : ""},
        'FlickerOffFadeMaxLength'   : {'Type' : "Int",    'DefaultValue' : 0,        'Description' : ""},
    }
}

hpl_point_light_properties_vars_dict = {'PointLight' :
    {
        'DiffuseColor'              : {'Type' : "Color",  'DefaultValue' : (1.0, 1.0, 1.0, 1.0), 'Description' : ""},
        'Brightness'                : {'Type' : "Float",  'DefaultValue' : 1.0,'Min' : 0.0, 'Max' : 100.0, 'Description' : ""},
        'CastDiffuseLight'          : {'Type' : "Bool",   'DefaultValue' : True,     'Description' : ""},
        'CastSpecularLight'         : {'Type' : "Bool",   'DefaultValue' : True,     'Description' : ""},
        'CastShadows'               : {'Type' : "Bool",   'DefaultValue' : True,     'Description' : ""},
        'ShadowResolution'          : {'Type' : "Enum",   'DefaultValue' : "High",   'EnumValues' : ['Low', 'Medium', 'High', 'VeryHigh'], 'Description' : ""},
        'ShadowsAffectStatic'       : {'Type' : "Bool",   'DefaultValue' : True,     'Description' : ""},
        'ShadowsAffectDynamic'      : {'Type' : "Bool",   'DefaultValue' : True,     'Description' : ""},
        'Radius'                    : {'Type' : "Float",  'DefaultValue' : 1.0,        'Description' : ""},
        'FalloffPow'                : {'Type' : "Float",  'DefaultValue' : 1.0,        'Description' : ""},
        'Gobo'                      : {'Type' : "String", 'DefaultValue' : "",       'Description' : ""},
        'GoboType'                  : {'Type' : "Enum",   'DefaultValue' : "Diffuse",'EnumValues' : [['Diffuse', 'Specular', 'DiffuseSpecular'], "Diffuse"], 'Description' : ""},
        'GoboAnimMode'              : {'Type' : "String", 'DefaultValue' : "None",   'Description' : ""},
        'GoboAnimFrameTime'         : {'Type' : "Int",    'DefaultValue' : 1,        'Description' : ""},
        'GoboAnimStartTime'         : {'Type' : "Int",    'DefaultValue' : 0,        'Description' : ""},
        'ConnectedLightMaskID'      : {'Type' : "Int",    'DefaultValue' : 0,        'Description' : ""},
    }
}
hpl_point_light_entity_properties_vars_dict = {**hpl_light_general_vars_dict, **hpl_point_light_properties_vars_dict, **hpl_light_flicker_properties_vars_dict}

# TODO: 'Hidden' boolean override property. Some properties are hidden in the editor, but seem to get set elsewhere.
# TODO: 'UIName' override property. i.e. 'Ground Color' -> 'AmbientGroundColor' or 'BlendFunc' -> 'BlendFunction'
# TODO: Convert in hpm_exporter -> hpl_radius = Radius * (math.pi / 180)
# TODO: rework box light
hpl_box_light_properties_vars_dict = {'BoxLight' :
    {
        'DiffuseColor'              : {'Type' : "Color",  'DefaultValue' : (1.0, 1.0, 1.0, 1.0), 'Description' : ""},
        'Brightness'                : {'Type' : "Float",  'DefaultValue' : 1.0, 'Min' : 0.0, 'Max' : 100.0,  'Description' : ""},
        'Size'                      : {'Type' : "Vector3",'DefaultValue' : (1.0, 1.0, 1.0), 'Description' : ""},
        'CastDiffuseLight'          : {'Type' : "Bool",   'DefaultValue' : True,     'Description' : ""},
        'CastSpecularLight'         : {'Type' : "Bool",   'DefaultValue' : True,     'Description' : ""},
        'CastShadows'               : {'Type' : "Bool",   'DefaultValue' : True,     'Description' : ""},
        'ShadowResolution'          : {'Type' : "Enum",   'DefaultValue' : "High",   'EnumValues' : [['Low', 'Medium', 'High', 'VeryHigh'], "High"], 'Description' : ""},
        'ShadowsAffectStatic'       : {'Type' : "Bool",   'DefaultValue' : True,     'Description' : ""},
        'ShadowsAffectDynamic'      : {'Type' : "Bool",   'DefaultValue' : True,     'Description' : ""},
        'Radius'                    : {'Type' : "Float",  'DefaultValue' : 1.0,        'Description' : ""},
        'BlendFunc'                 : {'Type' : "Enum",   'DefaultValue' : "Replace", 'EnumValues' : [['Replace', 'Add', 'Average'], "Replace"], 'Description' : ""},
        'GroundColor'               : {'Type' : "Color",  'DefaultValue' : (1.0, 1.0, 1.0, 1.0), 'Description' : ""},
        'SkyColor'                  : {'Type' : "Color",  'DefaultValue' : (1.0, 1.0, 1.0, 1.0), 'Description' : ""},
        'Weight'                    : {'Type' : "Float",  'DefaultValue' : 1.0,        'Description' : ""},
        'Bevel'                     : {'Type' : "Float",  'DefaultValue' : 0.0,        'Description' : ""},
        'FalloffPow'                : {'Type' : "Float",  'DefaultValue' : 0.0,        'Description' : ""},
        'UseSphericalHarmonics'     : {'Type' : "Bool",   'DefaultValue' : False,    'Description' : ""},
        'ProbeOffset'               : {'Type' : "Vector3",'DefaultValue' : (0.0, 0.0, 0.0), 'Description' : ""},
        'IrrSet'                    : {'Type' : "String", 'DefaultValue' : "Default",       'Description' : ""},
        'Gobo'                      : {'Type' : "String", 'DefaultValue' : "",       'Description' : ""},
        'GoboType'                  : {'Type' : "Enum",   'DefaultValue' : "Diffuse",'EnumValues' : [['Diffuse', 'Specular', 'DiffuseSpecular'], "Diffuse"], 'Description' : ""},
        'GoboAnimMode'              : {'Type' : "String", 'DefaultValue' : "None",   'Description' : ""},
        'GoboAnimFrameTime'         : {'Type' : "Int",    'DefaultValue' : 1,        'Description' : ""},
        'GoboAnimStartTime'         : {'Type' : "Int",    'DefaultValue' : 0,        'Description' : ""},
        'ConnectedLightMaskID'      : {'Type' : "Int",    'DefaultValue' : 0,        'Description' : ""},
    }
}

hpl_box_light_entity_properties_vars_dict = {**hpl_light_general_vars_dict, **hpl_box_light_properties_vars_dict, **hpl_light_flicker_properties_vars_dict}

# TODO: rework spot light
# TODO: fov_radians = Radius * (math.pi / 180)
hpl_spot_light_properties_vars_dict = {'SpotLight' :
    {
        'DiffuseColor'              : {'Type' : "Color",  'DefaultValue' : (1.0, 1.0, 1.0, 1.0), 'Description' : ""},
        'Brightness'                : {'Type' : "Float",  'DefaultValue' : 1.0, 'Min' : 0.0, 'Max' : 100.0,          'Description' : ""},
        'CastDiffuseLight'          : {'Type' : "Bool",   'DefaultValue' : True,     'Description' : ""},
        'CastSpecularLight'         : {'Type' : "Bool",   'DefaultValue' : True,     'Description' : ""},
        'CastShadows'               : {'Type' : "Bool",   'DefaultValue' : True,     'Description' : ""},
        'ShadowResolution'          : {'Type' : "Enum",   'DefaultValue' : "High",   'EnumValues' : [['Low', 'Medium', 'High', 'VeryHigh'], "High"], 'Description' : ""},
        'ShadowsAffectStatic'       : {'Type' : "Bool",   'DefaultValue' : True,     'Description' : ""},
        'ShadowsAffectDynamic'      : {'Type' : "Bool",   'DefaultValue' : True,     'Description' : ""},
        'Radius'                    : {'Type' : "Float",  'DefaultValue' : 1.0,        'Description' : ""},
        'NearClipPlane'             : {'Type' : "Float",  'DefaultValue' : 0.1,      'Description' : ""},
        'FalloffPow'                : {'Type' : "Float",  'DefaultValue' : 0.0,        'Description' : ""},
        'FOV'                       : {'Type' : "Float",  'DefaultValue' : 60.0,       'Description' : ""},
        'Aspect'                    : {'Type' : "Float",  'DefaultValue' : 1.0,        'Description' : ""},
        'SpotFalloffPow'            : {'Type' : "Float",  'DefaultValue' : 1.0,        'Description' : ""},
        'ShadowFadeRangeActive'     : {'Type' : "Bool",   'DefaultValue' : False,    'Description' : ""},
        'ShadowFadeRange'           : {'Type' : "Float",  'DefaultValue' : 0.0,       'Description' : ""},
        'ShadowCasterDistanceActive': {'Type' : "Bool",   'DefaultValue' : False,    'Description' : ""},
        'ShadowCasterDistance'      : {'Type' : "Float",  'DefaultValue' : 0.0,       'Description' : ""},
        'ShadowUpdatePriority'      : {'Type' : "Int",    'DefaultValue' : 10,       'Description' : ""},
        'Gobo'                      : {'Type' : "String", 'DefaultValue' : "",       'Description' : ""},
        'GoboType'                  : {'Type' : "Enum", 'DefaultValue' : "Diffuse", 'EnumValues' : [['Diffuse', 'Specular', 'DiffuseSpecular'], "Diffuse"], 'Description' : ""},
        'GoboAnimMode'              : {'Type' : "String", 'DefaultValue' : "None",   'Description' : ""},
        'GoboAnimFrameTime'         : {'Type' : "Int",    'DefaultValue' : 1,        'Description' : ""},
        'GoboAnimStartTime'         : {'Type' : "Int",    'DefaultValue' : 0,        'Description' : ""},
        'ConnectedLightMaskID'      : {'Type' : "Int",    'DefaultValue' : 0,        'Description' : ""},
    }
}
hpl_spot_light_entity_properties_vars_dict = {**hpl_light_general_vars_dict, **hpl_spot_light_properties_vars_dict, **hpl_light_flicker_properties_vars_dict}

hpl_hierarchy_enums_list = ['hplp_e_ConnectedChildBodyID', 'hplp_e_ConnectedParentBodyID', 'hplp_v_ConnectedChildBodyID', 'hplp_v_ConnectedParentBodyID']

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
hpl_export_queue = {}
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
                                    'Path' : 'bpy.context.scene.hpl_parser.hpl_game_root_path + \'mods\\\\\' + bpy.context.scene.hpl_parser.hpl_project_root_col + \'\\\\entry.hpc\'',
                                    },
                }