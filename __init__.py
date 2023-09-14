# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
import bpy.props
from bpy.app.handlers import persistent
import bpy.utils.previews
from glob import glob
import os
import re
import random
from mathutils import Vector, Matrix

from . import hpl_config
from . import hpm_config
from . import hpm_class_extractor
from . import hpl_property_io
from . import hpl_importer
from .hpm_exporter import (HPM_OT_EXPORTER)
from .hpl_exporter import (HPL_OT_DAEEXPORTER)
from .hpl_importer import (HPL_OT_ASSETIMPORTER)
from .hpl_property_io import (HPL_OT_RESETPROPERTIES)

bl_info = {
    "name" : "hpl_parser",
    "author" : "Christian Friedrich",
    "description" : "",
    "blender" : (3, 60, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
	"location": "View3D > Properties Panel",
	"category": "Object"
}

def get_hpl_selected_collection(self): 
    return self['hpl_selected_collection']

def set_hpl_selected_collection(self, value):
    self['hpl_selected_collection'] = value


def get_hpl_game_root_path(self): 
    return self['hpl_game_root_path']
    
def set_hpl_game_root_path(self, value):
    if '.exe' in value:
        value = os.path.dirname(value)+"\\"
    self['hpl_game_root_path'] = value

    if value:
        if check_for_game_exe(value):
            bpy.context.scene.hpl_parser.dae_file_count = ' '+str(len(hpl_importer.pre_scan_for_dae_files(value)))
            bpy.context.scene.hpl_parser.hpl_is_game_root_valid = True
            hpm_class_extractor.hpm_properties.get_properties_from_hpm_file()
        else:
            bpy.context.scene.hpl_parser.hpl_is_game_root_valid = False

def get_hpl_base_classes_enum(self): 
    return self['hpl_base_classes_enum']

def set_hpl_base_classes_enum(self, value):
    self['hpl_base_classes_enum'] = value
    hpl_property_io.hpl_properties.set_entity_type_on_collection()

def get_hpl_project_root_col(self):
    return self['hpl_project_root_col']

def set_hpl_project_root_col(self, value):
    self['hpl_project_root_col'] = value    
    if not any([col for col in bpy.data.collections[bpy.context.scene.hpl_parser.hpl_project_root_col].children if col.name == 'Maps']):
        bpy.ops.collection.create(name='Maps')
        bpy.data.collections[bpy.context.scene.hpl_parser.hpl_project_root_col].children.link(bpy.data.collections['Maps'])


'''    
def getBackgroundBlur(self):
    try:
        value = self['backgroundBlur']
    except:
        value = 0.025
    return value

def setBackgroundBlur(self, value):
    self['backgroundBlur'] = value
    bpy.data.objects['Background'].material_slots[0].material.node_tree.nodes['Blur'].inputs[0].default_value = value
    return

def getBadgeColorAL(self):
    try:
        value = self['badgeColorAL']
    except:
        value = (0.5,0.5,0.5,1)
    return value

def setBadgeColorAL(self, value):
    self['badgeColorAL'] = value
    bpy.data.materials["Badge"].node_tree.nodes["ColorAL"].inputs[2].default_value = value
    return
'''

# Custom properties for GlobalSettings
class HPLLevelSettingsProperties(bpy.types.PropertyGroup):
    # Fog settings
    def get_fog_active(self):
        return self["FogActive"]

    def set_fog_active(self, value):
        self["FogActive"] = value
    
    FogActive: bpy.props.BoolProperty(
        name="Fog Active",
        description="Toggle fog on/off",
        default=True,
        get=get_fog_active,
        set=set_fog_active,
    )
    
    def get_fog_culling(self):
        return self["FogCulling"]

    def set_fog_culling(self, value):
        self["FogCulling"] = value

    FogCulling: bpy.props.BoolProperty(
        name="Fog Culling",
        description="Toggle fog culling on/off",
        default=True,
        get=get_fog_culling,
        set=set_fog_culling,
    )

    fog_color_default = '1 1 1 1'

    def get_fog_color(self):
        return self.get("FogColor")

    def set_fog_color(self, value):
        self["FogColor"] = value

    fog_color: bpy.props.StringProperty(
        name="Fog Color",
        description="Fog color (RGBA)",
        default="1 1 1 1",
        get=get_fog_color,
        set=set_fog_color,
    )

    fog_brightness_default=1.0

    def get_fog_brightness(self):
        #return self["FogBrightness"]
        return self.get("FogBrightness", self.fog_brightness_default)

    def set_fog_brightness(self, value):
        self["FogBrightness"] = value

    FogBrightness: bpy.props.FloatProperty(
        name="Fog Brightness",
        description="Fog brightness",
        default=fog_brightness_default,
        min=0.0,
        get=get_fog_brightness,
        set=set_fog_brightness,
    )

    fog_fade_start_default=0.0

    def get_fog_fade_start(self):
        #return self["FogFadeStart"]
        return self.get("FogFadeStart", self.fog_fade_start_default)

    def set_fog_fade_start(self, value):
        self["FogFadeStart"] = value

    FogFadeStart: bpy.props.FloatProperty(
        name="Fog Fade Start",
        description="Fog fade start distance",
        default=fog_fade_start_default,
        min=0.0,
        get=get_fog_fade_start,
        set=set_fog_fade_start,
    )
'''
    def get_fog_fade_end(self):
        return self["FogFadeEnd"]

    def set_fog_fade_end(self, value):
        self["FogFadeEnd"] = value

    FogFadeEnd: bpy.props.FloatProperty(
        name="Fog Fade End",
        description="Fog fade end distance",
        default=20.0,
        min=0.0,
        get=get_fog_fade_end,
        set=set_fog_fade_end,
    )

    def get_fog_falloff_exp(self):
        return self["FogFalloffExp"]

    def set_fog_falloff_exp(self, value):
        self["FogFalloffExp"] = value

    FogFalloffExp: bpy.props.FloatProperty(
        name="Fog Falloff Exp",
        description="Fog falloff exponent",
        default=1.0,
        min=0.0,
        get=get_fog_falloff_exp,
        set=set_fog_falloff_exp,
    )

    def get_fog_underwater(self):
        return self["FogUnderwater"]

    def set_fog_underwater(self, value):
        self["FogUnderwater"] = value

    FogUnderwater: bpy.props.BoolProperty(
        name="Fog Underwater",
        description="Toggle fog underwater on/off",
        default=False,
        get=get_fog_underwater,
        set=set_fog_underwater,
    )

    def get_fog_lighten(self):
        return self["FogLighten"]

    def set_fog_lighten(self, value):
        self["FogLighten"] = value

    FogLighten: bpy.props.BoolProperty(
        name="Fog Lighten",
        description="Toggle fog lighten on/off",
        default=True,
        get=get_fog_lighten,
        set=set_fog_lighten,
    )

    def get_fog_use_skybox(self):
        return self["FogUseSkybox"]

    def set_fog_use_skybox(self, value):
        self["FogUseSkybox"] = value

    FogUseSkybox: bpy.props.BoolProperty(
        name="Fog Use Skybox",
        description="Toggle fog use skybox on/off",
        default=True,
        get=get_fog_use_skybox,
        set=set_fog_use_skybox,
    )

    def get_fog_noise_strength(self):
        return self["FogNoiseStrength"]

    def set_fog_noise_strength(self, value):
        self["FogNoiseStrength"] = value

    FogNoiseStrength: bpy.props.FloatProperty(
        name="Fog Noise Strength",
        description="Fog noise strength",
        default=0.0,
        min=0.0,
        get=get_fog_noise_strength,
        set=set_fog_noise_strength,
    )

    def get_fog_noise_size(self):
        return self["FogNoiseSize"]

    def set_fog_noise_size(self, value):
        self["FogNoiseSize"] = value

    FogNoiseSize: bpy.props.FloatProperty(
        name="Fog Noise Size",
        description="Fog noise size",
        default=8.0,
        min=0.0,
        get=get_fog_noise_size,
        set=set_fog_noise_size,
    )

    def get_fog_noise_turbulence(self):
        return self["FogNoiseTurbulence"]

    def set_fog_noise_turbulence(self, value):
        self["FogNoiseTurbulence"] = value

    FogNoiseTurbulence: bpy.props.StringProperty(
        name="Fog Noise Turbulence",
        description="Fog noise turbulence (X Y Z)",
        default="0.5 0.5 0.5",
        get=get_fog_noise_turbulence,
        set=set_fog_noise_turbulence,
    )

    def get_fog_apply_after_fog_areas(self):
        return self["FogApplyAfterFogAreas"]

    def set_fog_apply_after_fog_areas(self, value):
        self["FogApplyAfterFogAreas"] = value

    FogApplyAfterFogAreas: bpy.props.BoolProperty(
        name="Fog Apply After Fog Areas",
        description="Toggle fog apply after fog areas on/off",
        default=True,
        get=get_fog_apply_after_fog_areas,
        set=set_fog_apply_after_fog_areas,
    )

    def get_fog_height_based(self):
        return self["FogHeightBased"]

    def set_fog_height_based(self, value):
        self["FogHeightBased"] = value

    FogHeightBased: bpy.props.BoolProperty(
        name="Fog Height Based",
        description="Toggle height-based fog on/off",
        default=False,
        get=get_fog_height_based,
        set=set_fog_height_based,
    )

    def get_fog_exponential(self):
        return self["FogExponential"]

    def set_fog_exponential(self, value):
        self["FogExponential"] = value

    FogExponential: bpy.props.BoolProperty(
        name="Fog Exponential",
        description="Toggle exponential fog on/off",
        default=True,
        get=get_fog_exponential,
        set=set_fog_exponential,
    )

    def get_fog_density(self):
        return self["FogDensity"]

    def set_fog_density(self, value):
        self["FogDensity"] = value

    FogDensity: bpy.props.FloatProperty(
        name="Fog Density",
        description="Fog density",
        default=0.06,
        min=0.0,
        get=get_fog_density,
        set=set_fog_density,
    )

    def get_fog_height_density(self):
        return self["FogHeightDensity"]

    def set_fog_height_density(self, value):
        self["FogHeightDensity"] = value

    FogHeightDensity: bpy.props.FloatProperty(
        name="Fog Height Density",
        description="Height-based fog density",
        default=0.01,
        min=0.0,
        get=get_fog_height_density,
        set=set_fog_height_density,
    )

    def get_fog_height_horizon(self):
        return self["FogHeightHorizon"]

    def set_fog_height_horizon(self, value):
        self["FogHeightHorizon"] = value

    FogHeightHorizon: bpy.props.FloatProperty(
        name="Fog Height Horizon",
        description="Height-based fog horizon",
        default=5.0,
        min=0.0,
        get=get_fog_height_horizon,
        set=set_fog_height_horizon,
    )

    def get_fog_secondary_active(self):
        return self["FogSecondaryActive"]

    def set_fog_secondary_active(self, value):
        self["FogSecondaryActive"] = value

    FogSecondaryActive: bpy.props.BoolProperty(
        name="Fog Secondary Active",
        description="Toggle secondary fog on/off",
        default=True,
        get=get_fog_secondary_active,
        set=set_fog_secondary_active,
    )

    def get_fog_secondary_color(self):
        return self["FogSecondaryColor"]

    def set_fog_secondary_color(self, value):
        self["FogSecondaryColor"] = value

    FogSecondaryColor: bpy.props.StringProperty(
        name="Fog Secondary Color",
        description="Secondary fog color (RGBA)",
        default="1 1 1 1",
        get=get_fog_secondary_color,
        set=set_fog_secondary_color,
    )

    def get_fog_secondary_fade_start(self):
        return self["FogSecondaryFadeStart"]

    def set_fog_secondary_fade_start(self, value):
        self["FogSecondaryFadeStart"] = value

    FogSecondaryFadeStart: bpy.props.FloatProperty(
        name="Fog Secondary Fade Start",
        description="Secondary fog fade start distance",
        default=0.0,
        min=0.0,
        get=get_fog_secondary_fade_start,
        set=set_fog_secondary_fade_start,
    )

    def get_fog_secondary_fade_end(self):
        return self["FogSecondaryFadeEnd"]

    def set_fog_secondary_fade_end(self, value):
        self["FogSecondaryFadeEnd"] = value

    FogSecondaryFadeEnd: bpy.props.FloatProperty(
        name="Fog Secondary Fade End",
        description="Secondary fog fade end distance",
        default=20.0,
        min=0.0,
        get=get_fog_secondary_fade_end,
        set=set_fog_secondary_fade_end,
    )

    def get_fog_secondary_falloff_exp(self):
        return self["FogSecondaryFalloffExp"]

    def set_fog_secondary_falloff_exp(self, value):
        self["FogSecondaryFalloffExp"] = value

    FogSecondaryFalloffExp: bpy.props.FloatProperty(
        name="Fog Secondary Falloff Exp",
        description="Secondary fog falloff exponent",
        default=1.0,
        min=0.0,
        get=get_fog_secondary_falloff_exp,
        set=set_fog_secondary_falloff_exp,
    )

    def get_fog_secondary_density(self):
        return self["FogSecondaryDensity"]

    def set_fog_secondary_density(self, value):
        self["FogSecondaryDensity"] = value

    FogSecondaryDensity: bpy.props.FloatProperty(
        name="Fog Secondary Density",
        description="Secondary fog density",
        default=0.01,
        min=0.0,
        get=get_fog_secondary_density,
        set=set_fog_secondary_density,
    )

    def get_fog_secondary_height_density(self):
        return self["FogSecondaryHeightDensity"]

    def set_fog_secondary_height_density(self, value):
        self["FogSecondaryHeightDensity"] = value

    FogSecondaryHeightDensity: bpy.props.FloatProperty(
        name="Fog Secondary Height Density",
        description="Secondary height-based fog density",
        default=0.25,
        min=0.0,
        get=get_fog_secondary_height_density,
        set=set_fog_secondary_height_density,
    )

    def get_fog_secondary_height_horizon(self):
        return self["FogSecondaryHeightHorizon"]

    def set_fog_secondary_height_horizon(self, value):
        self["FogSecondaryHeightHorizon"] = value

    FogSecondaryHeightHorizon: bpy.props.FloatProperty(
        name="Fog Secondary Height Horizon",
        description="Secondary height-based fog horizon",
        default=5.0,
        min=0.0,
        get=get_fog_secondary_height_horizon,
        set=set_fog_secondary_height_horizon,
    )

    # SkyBox settings
    def get_sky_box_active(self):
        return self["SkyBoxActive"]

    def set_sky_box_active(self, value):
        self["SkyBoxActive"] = value

    SkyBoxActive: bpy.props.BoolProperty(
        name="SkyBox Active",
        description="Toggle skybox on/off",
        default=True,
        get=get_sky_box_active,
        set=set_sky_box_active,
    )

    def get_sky_box_color(self):
        return self["SkyBoxColor"]

    def set_sky_box_color(self, value):
        self["SkyBoxColor"] = value

    SkyBoxColor: bpy.props.StringProperty(
        name="SkyBox Color",
        description="Skybox color (RGBA)",
        default="1 1 1 1",
        get=get_sky_box_color,
        set=set_sky_box_color,
    )

    def get_sky_box_texture(self):
        return self["SkyBoxTexture"]

    def set_sky_box_texture(self, value):
        self["SkyBoxTexture"] = value

    SkyBoxTexture: bpy.props.StringProperty(
        name="SkyBox Texture",
        description="Skybox texture",
        default="",
        get=get_sky_box_texture,
        set=set_sky_box_texture,
    )

    def get_sky_box_brightness(self):
        return self["SkyBoxBrightness"]

    def set_sky_box_brightness(self, value):
        self["SkyBoxBrightness"] = value

    SkyBoxBrightness: bpy.props.FloatProperty(
        name="SkyBox Brightness",
        description="Skybox brightness",
        default=1.0,
        min=0.0,
        get=get_sky_box_brightness,
        set=set_sky_box_brightness,
    )

    # DirLight settings
    def get_dir_light_active(self):
        return self["DirLightActive"]

    def set_dir_light_active(self, value):
        self["DirLightActive"] = value

    DirLightActive: bpy.props.BoolProperty(
        name="Directional Light Active",
        description="Toggle directional light on/off",
        default=True,
        get=get_dir_light_active,
        set=set_dir_light_active,
    )

    def get_dir_light_shadow_caster_dist(self):
        return self["DirLightShadowCasterDist"]

    def set_dir_light_shadow_caster_dist(self, value):
        self["DirLightShadowCasterDist"] = value

    DirLightShadowCasterDist: bpy.props.FloatProperty(
        name="Shadow Caster Distance",
        description="Shadow caster distance",
        default=35.0,
        min=0.0,
        get=get_dir_light_shadow_caster_dist,
        set=set_dir_light_shadow_caster_dist,
    )

    def get_dir_light_shadow_distance(self):
        return self["DirLightShadowDistance"]

    def set_dir_light_shadow_distance(self, value):
        self["DirLightShadowDistance"] = value

    DirLightShadowDistance: bpy.props.FloatProperty(
        name="Shadow Distance",
        description="Shadow distance",
        default=-1.0,
        min=-1.0,
        get=get_dir_light_shadow_distance,
        set=set_dir_light_shadow_distance,
    )

    def get_dir_light_diffuse_color(self):
        return self["DirLightDiffuseColor"]

    def set_dir_light_diffuse_color(self, value):
        self["DirLightDiffuseColor"] = value

    DirLightDiffuseColor: bpy.props.StringProperty(
        name="Diffuse Color",
        description="Diffuse color (RGBA)",
        default="1 1 1 1",
        get=get_dir_light_diffuse_color,
        set=set_dir_light_diffuse_color,
    )

    def get_dir_light_brightness(self):
        return self["DirLightBrightness"]

    def set_dir_light_brightness(self, value):
        self["DirLightBrightness"] = value

    DirLightBrightness: bpy.props.StringProperty(
        name="Brightness",
        description="Brightness (RGBA)",
        default="1 1 1 1",
        get=get_dir_light_brightness,
        set=set_dir_light_brightness,
    )

    def get_dir_light_gobo(self):
        return self["DirLightGobo"]

    def set_dir_light_gobo(self, value):
        self["DirLightGobo"] = value

    DirLightGobo: bpy.props.StringProperty(
        name="Gobo",
        description="Gobo texture",
        default="",
        get=get_dir_light_gobo,
        set=set_dir_light_gobo,
    )

    def get_dir_light_gobo_anim_mode(self):
        return self["DirLightGoboAnimMode"]

    def set_dir_light_gobo_anim_mode(self, value):
        self["DirLightGoboAnimMode"] = value

    DirLightGoboAnimMode: bpy.props.EnumProperty(
        name="Gobo Animation Mode",
        description="Gobo animation mode",
        items=[
            ("None", "None", "No animation"),
            ("Loop", "Loop", "Loop animation"),
            ("PingPong", "PingPong", "PingPong animation"),
        ],
        default="None",
        get=get_dir_light_gobo_anim_mode,
        set=set_dir_light_gobo_anim_mode,
    )

    def get_dir_light_gobo_anim_start_time(self):
        return self["DirLightGoboAnimStartTime"]

    def set_dir_light_gobo_anim_start_time(self, value):
        self["DirLightGoboAnimStartTime"] = value

    DirLightGoboAnimStartTime: bpy.props.FloatProperty(
        name="Gobo Anim Start Time",
        description="Gobo animation start time",
        default=0.0,
        min=0.0,
        get=get_dir_light_gobo_anim_start_time,
        set=set_dir_light_gobo_anim_start_time,
    )

    def get_dir_light_gobo_anim_frame_time(self):
        return self["DirLightGoboAnimFrameTime"]

    def set_dir_light_gobo_anim_frame_time(self, value):
        self["DirLightGoboAnimFrameTime"] = value

    DirLightGoboAnimFrameTime: bpy.props.FloatProperty(
        name="Gobo Anim Frame Time",
        description="Gobo animation frame time",
        default=0.0,
        min=0.0,
        get=get_dir_light_gobo_anim_frame_time,
        set=set_dir_light_gobo_anim_frame_time,
    )

    def get_dir_light_gobo_scale(self):
        return self["DirLightGoboScale"]

    def set_dir_light_gobo_scale(self, value):
        self["DirLightGoboScale"] = value

    DirLightGoboScale: bpy.props.StringProperty(
        name="Gobo Scale",
        description="Gobo scale (X Y)",
        default="1 1",
        get=get_dir_light_gobo_scale,
        set=set_dir_light_gobo_scale,
    )

    def get_dir_light_direction(self):
        return self["DirLightDirection"]

    def set_dir_light_direction(self, value):
        self["DirLightDirection"] = value

    DirLightDirection: bpy.props.StringProperty(
        name="Direction",
        description="Light direction (X Y Z)",
        default="0.57735 -0.57735 0.57735",
        get=get_dir_light_direction,
        set=set_dir_light_direction,
    )

    def get_dir_light_cast_shadows(self):
        return self["DirLightCastShadows"]

    def set_dir_light_cast_shadows(self, value):
        self["DirLightCastShadows"] = value

    DirLightCastShadows: bpy.props.BoolProperty(
        name="Cast Shadows",
        description="Toggle shadow casting on/off",
        default=False,
        get=get_dir_light_cast_shadows,
        set=set_dir_light_cast_shadows,
    )

    def get_dir_light_sky_col(self):
        return self["DirLightSkyCol"]

    def set_dir_light_sky_col(self, value):
        self["DirLightSkyCol"] = value

    DirLightSkyCol: bpy.props.StringProperty(
        name="Sky Color",
        description="Sky color (RGBA)",
        default="1 1 1 1",
        get=get_dir_light_sky_col,
        set=set_dir_light_sky_col,
    )

    def get_dir_light_ground_col(self):
        return self["DirLightGroundCol"]

    def set_dir_light_ground_col(self, value):
        self["DirLightGroundCol"] = value

    DirLightGroundCol: bpy.props.StringProperty(
        name="Ground Color",
        description="Ground color (RGBA)",
        default="1 1 1 1",
        get=get_dir_light_ground_col,
        set=set_dir_light_ground_col,
    )

    def get_dir_light_shadow_map_bias_mul(self):
        return self["DirLightShadowMapBiasMul"]

    def set_dir_light_shadow_map_bias_mul(self, value):
        self["DirLightShadowMapBiasMul"] = value

    DirLightShadowMapBiasMul: bpy.props.FloatProperty(
        name="Shadow Map Bias Multiplier",
        description="Shadow map bias multiplier",
        default=3.0,
        min=0.0,
        get=get_dir_light_shadow_map_bias_mul,
        set=set_dir_light_shadow_map_bias_mul,
    )

    def get_dir_light_shadow_map_slope_scale_bias_mul(self):
        return self["DirLightShadowMapSlopeScaleBiasMul"]

    def set_dir_light_shadow_map_slope_scale_bias_mul(self, value):
        self["DirLightShadowMapSlopeScaleBiasMul"] = value

    DirLightShadowMapSlopeScaleBiasMul: bpy.props.FloatProperty(
        name="Shadow Map Slope Scale Bias Multiplier",
        description="Shadow map slope scale bias multiplier",
        default=2.5,
        min=0.0,
        get=get_dir_light_shadow_map_slope_scale_bias_mul,
        set=set_dir_light_shadow_map_slope_scale_bias_mul,
    )

    def get_dir_light_auto_shadow_slice_settings(self):
        return self["DirLightAutoShadowSliceSettings"]

    def set_dir_light_auto_shadow_slice_settings(self, value):
        self["DirLightAutoShadowSliceSettings"] = value

    DirLightAutoShadowSliceSettings: bpy.props.BoolProperty(
        name="Auto Shadow Slice Settings",
        description="Toggle auto shadow slice settings on/off",
        default=True,
        get=get_dir_light_auto_shadow_slice_settings,
        set=set_dir_light_auto_shadow_slice_settings,
    )

    def get_dir_light_auto_shadow_slice_log_term(self):
        return self["DirLightAutoShadowSliceLogTerm"]

    def set_dir_light_auto_shadow_slice_log_term(self, value):
        self["DirLightAutoShadowSliceLogTerm"] = value

    DirLightAutoShadowSliceLogTerm: bpy.props.FloatProperty(
        name="Auto Shadow Slice Log Term",
        description="Auto shadow slice log term",
        default=0.9,
        min=0.0,
        get=get_dir_light_auto_shadow_slice_log_term,
        set=set_dir_light_auto_shadow_slice_log_term,
    )

    # SSAO settings
    def get_ssaon_normal_map(self):
        return self["SSAONormalMap"]

    def set_ssaon_normal_map(self, value):
        self["SSAONormalMap"] = value

    SSAONormalMap: bpy.props.BoolProperty(
        name="Normal Map",
        description="Toggle SSAO normal map on/off",
        default=False,
        get=get_ssaon_normal_map,
        set=set_ssaon_normal_map,
    )

    def get_ssaon_num_of_directions(self):
        return self["SSAONumOfDirections"]

    def set_ssaon_num_of_directions(self, value):
        self["SSAONumOfDirections"] = value

    SSAONumOfDirections: bpy.props.IntProperty(
        name="Number of Directions",
        description="Number of SSAO directions",
        default=0,
        min=0,
        get=get_ssaon_num_of_directions,
        set=set_ssaon_num_of_directions,
    )

    def get_ssaon_num_of_steps(self):
        return self["SSAONumOfSteps"]

    def set_ssaon_num_of_steps(self, value):
        self["SSAONumOfSteps"] = value

    SSAONumOfSteps: bpy.props.IntProperty(
        name="Number of Steps",
        description="Number of SSAO steps",
        default=0,
        min=0,
        get=get_ssaon_num_of_steps,
        set=set_ssaon_num_of_steps,
    )

    def get_ssaon_angle_bias(self):
        return self["SSAOAngleBias"]

    def set_ssaon_angle_bias(self, value):
        self["SSAOAngleBias"] = value

    SSAOAngleBias: bpy.props.FloatProperty(
        name="Angle Bias",
        description="SSAO angle bias",
        default=0.0,
        min=0.0,
        get=get_ssaon_angle_bias,
        set=set_ssaon_angle_bias,
    )

    def get_ssaon_power(self):
        return self["SSAOPower"]

    def set_ssaon_power(self, value):
        self["SSAOPower"] = value

    SSAOPower: bpy.props.FloatProperty(
        name="Power",
        description="SSAO power",
        default=4.4,
        min=0.0,
        get=get_ssaon_power,
        set=set_ssaon_power,
    )

    def get_ssaon_radius(self):
        return self["SSAORadius"]

    def set_ssaon_radius(self, value):
        self["SSAORadius"] = value

    SSAORadius: bpy.props.FloatProperty(
        name="Radius",
        description="SSAO radius",
        default=2.0,
        min=0.0,
        get=get_ssaon_radius,
        set=set_ssaon_radius,
    )

    def get_ssaon_buffer_size_div(self):
        return self["SSAOBufferSizeDiv"]

    def set_ssaon_buffer_size_div(self, value):
        self["SSAOBufferSizeDiv"] = value

    SSAOBufferSizeDiv: bpy.props.IntProperty(
        name="Buffer Size Divisor",
        description="SSAO buffer size divisor",
        default=2,
        min=1,
        get=get_ssaon_buffer_size_div,
        set=set_ssaon_buffer_size_div,
    )

    # EnvParticles settings
    def get_env_particles_active(self):
        return self["EnvParticlesActive"]

    def set_env_particles_active(self, value):
        self["EnvParticlesActive"] = value

    EnvParticlesActive: bpy.props.BoolProperty(
        name="EnvParticles Active",
        description="Toggle environment particles on/off",
        default=True,
        get=get_env_particles_active,
        set=set_env_particles_active,
    )

    def get_env_particle_name(self):
        return self["EnvParticleName"]

    def set_env_particle_name(self, value):
        self["EnvParticleName"] = value

    EnvParticleName: bpy.props.StringProperty(
        name="Particle Name",
        description="Environment particle name",
        default="",
        get=get_env_particle_name,
        set=set_env_particle_name,
    )

    def get_env_particle_color(self):
        return self["EnvParticleColor"]

    def set_env_particle_color(self, value):
        self["EnvParticleColor"] = value

    EnvParticleColor: bpy.props.StringProperty(
        name="Particle Color",
        description="Particle color (RGBA)",
        default="1 1 1 1",
        get=get_env_particle_color,
        set=set_env_particle_color,
    )

    def get_env_particle_brightness(self):
        return self["EnvParticleBrightness"]

    def set_env_particle_brightness(self, value):
        self["EnvParticleBrightness"] = value

    EnvParticleBrightness: bpy.props.FloatProperty(
        name="Brightness",
        description="Particle brightness",
        default=1.0,
        min=0.0,
        get=get_env_particle_brightness,
        set=set_env_particle_brightness,
    )

    def get_env_particle_box_distance(self):
        return self["EnvParticleBoxDistance"]

    def set_env_particle_box_distance(self, value):
        self["EnvParticleBoxDistance"] = value

    EnvParticleBoxDistance: bpy.props.FloatProperty(
        name="Box Distance",
        description="Particle box distance",
        default=2.0,
        min=0.0,
        get=get_env_particle_box_distance,
        set=set_env_particle_box_distance,
    )

    def get_env_particle_gravity_velocity(self):
        return self["EnvParticleGravityVelocity"]

    def set_env_particle_gravity_velocity(self, value):
        self["EnvParticleGravityVelocity"] = value

    EnvParticleGravityVelocity: bpy.props.StringProperty(
        name="Gravity Velocity",
        description="Particle gravity velocity (X Y Z)",
        default="0 0 0",
        get=get_env_particle_gravity_velocity,
        set=set_env_particle_gravity_velocity,
    )

    def get_env_particle_gravity_speed_random_amount(self):
        return self["EnvParticleGravitySpeedRandomAmount"]

    def set_env_particle_gravity_speed_random_amount(self, value):
        self["EnvParticleGravitySpeedRandomAmount"] = value

    EnvParticleGravitySpeedRandomAmount: bpy.props.FloatProperty(
        name="Gravity Speed Random Amount",
        description="Particle gravity speed random amount",
        default=0.0,
        min=0.0,
        get=get_env_particle_gravity_speed_random_amount,
        set=set_env_particle_gravity_speed_random_amount,
    )

    def get_env_particle_wind_velocity(self):
        return self["EnvParticleWindVelocity"]

    def set_env_particle_wind_velocity(self, value):
        self["EnvParticleWindVelocity"] = value

    EnvParticleWindVelocity: bpy.props.StringProperty(
        name="Wind Velocity",
        description="Particle wind velocity (X Y Z)",
        default="0 0 0",
        get=get_env_particle_wind_velocity,
        set=set_env_particle_wind_velocity,
    )

    def get_env_particle_wind_speed_random_amount(self):
        return self["EnvParticleWindSpeedRandomAmount"]

    def set_env_particle_wind_speed_random_amount(self, value):
        self["EnvParticleWindSpeedRandomAmount"] = value

    EnvParticleWindSpeedRandomAmount: bpy.props.FloatProperty(
        name="Wind Speed Random Amount",
        description="Particle wind speed random amount",
        default=0.0,
        min=0.0,
        get=get_env_particle_wind_speed_random_amount,
        set=set_env_particle_wind_speed_random_amount,
    )

    def get_env_particle_wind_dir_random_amount(self):
        return self["EnvParticleWindDirRandomAmount"]

    def set_env_particle_wind_dir_random_amount(self, value):
        self["EnvParticleWindDirRandomAmount"] = value

    EnvParticleWindDirRandomAmount: bpy.props.FloatProperty(
        name="Wind Direction Random Amount",
        description="Particle wind direction random amount",
        default=0.0,
        min=0.0,
        get=get_env_particle_wind_dir_random_amount,
        set=set_env_particle_wind_dir_random_amount,
    )

    def get_env_particle_rotate_velocity(self):
        return self["EnvParticleRotateVelocity"]

    def set_env_particle_rotate_velocity(self, value):
        self["EnvParticleRotateVelocity"] = value

    EnvParticleRotateVelocity: bpy.props.StringProperty(
        name="Rotate Velocity",
        description="Particle rotation velocity (X Y Z)",
        default="0 0 0",
        get=get_env_particle_rotate_velocity,
        set=set_env_particle_rotate_velocity,
    )

    def get_env_particle_rotate_speed_random_amount(self):
        return self["EnvParticleRotateSpeedRandomAmount"]

    def set_env_particle_rotate_speed_random_amount(self, value):
        self["EnvParticleRotateSpeedRandomAmount"] = value

    EnvParticleRotateSpeedRandomAmount: bpy.props.FloatProperty(
        name="Rotate Speed Random Amount",
        description="Particle rotation speed random amount",
        default=0.0,
        min=0.0,
        get=get_env_particle_rotate_speed_random_amount,
        set=set_env_particle_rotate_speed_random_amount,
    )

    def get_env_particle_rotate_both_dirs(self):
        return self["EnvParticleRotateBothDirs"]

    def set_env_particle_rotate_both_dirs(self, value):
        self["EnvParticleRotateBothDirs"] = value

    EnvParticleRotateBothDirs: bpy.props.BoolProperty(
        name="Rotate Both Directions",
        description="Toggle rotating in both directions on/off",
        default=False,
        get=get_env_particle_rotate_both_dirs,
        set=set_env_particle_rotate_both_dirs,
    )

    def get_env_particle_num_iterations(self):
        return self["EnvParticleNumIterations"]

    def set_env_particle_num_iterations(self, value):
        self["EnvParticleNumIterations"] = value

    EnvParticleNumIterations: bpy.props.IntProperty(
        name="Number of Iterations",
        description="Number of iterations for particle simulation",
        default=5,
        min=1,
        get=get_env_particle_num_iterations,
        set=set_env_particle_num_iterations,
    )

    def get_env_particle_sim_type(self):
        return self["EnvParticleSimType"]

    def set_env_particle_sim_type(self, value):
        self["EnvParticleSimType"] = value

    EnvParticleSimType: bpy.props.EnumProperty(
        name="Simulation Type",
        description="Environment particle simulation type",
        items=[
            ("Static", "Static", "Static simulation"),
            ("Dynamic", "Dynamic", "Dynamic simulation"),
        ],
        default="Static",
        get=get_env_particle_sim_type,
        set=set_env_particle_sim_type,
    )

    def get_env_particle_outside_bounds(self):
        return self["EnvParticleOutsideBounds"]

    def set_env_particle_outside_bounds(self, value):
        self["EnvParticleOutsideBounds"] = value

    EnvParticleOutsideBounds: bpy.props.BoolProperty(
        name="Outside Bounds",
        description="Toggle rendering particles outside bounds on/off",
        default=True,
        get=get_env_particle_outside_bounds,
        set=set_env_particle_outside_bounds,
    )
'''
# Register the custom properties on add-ons enable
#if __name__ == "__main__":
#    register()


class HPLSettingsPropertyGroup(bpy.types.PropertyGroup):

    ###LEVEL SETTINGS###

    def get_hpl_map_root_col(self):
        try:
            value = self['get_hpl_map_root_col']
        except:
            value = 0
        return value

    def set_hpl_map_root_col(self, value):
        self['set_hpl_map_root_col'] = value
        return


    hpl_is_game_root_valid : bpy.props.BoolProperty(default=False)

    dae_file_count: bpy.props.StringProperty(default='', name = 'dae file count')
    vmf_scale: bpy.props.IntProperty(default=45, name = '', min = 1, max = 256)
    
    settings : bpy.props.BoolProperty(default=True)
    hpl_is_game_root_valid : bpy.props.BoolProperty(default=False)

    hpl_selected_collection: bpy.props.StringProperty(name="selected object",                               
                                        get=get_hpl_selected_collection, 
                                        set=set_hpl_selected_collection)
    
    def update_hpl_game_root_path(self, context):
        filename = glob(self['hpl_game_root_path']+'*.exe')
        bpy.context.scene.hpl_parser.hpl_is_game_root_valid = any(filename)
    
    hpl_game_root_path: bpy.props.StringProperty(name="game path",
                                        description='Select the game path were the games *.exe is located',
                                        #default="*.exe;",
                                        #options={'HIDDEN'},
                                        subtype="FILE_PATH",                                 
                                        get=get_hpl_game_root_path, 
                                        set=set_hpl_game_root_path,
                                        update=update_hpl_game_root_path)
    
    hpl_create_preview: bpy.props.BoolProperty(name="Create Asset Thumbnails",
                                        description="Renders preview Images for every asset, very slow. Can take up to two hours",
                                        default=False)
    
    hpl_export_textures : bpy.props.BoolProperty(default=True, name="Textures",
                                        description="Convert and export all referenced textures to HPL")
    hpl_export_meshes : bpy.props.BoolProperty(default=True, name="Meshes",
                                        description="Export all meshes")
    hpl_export_maps : bpy.props.BoolProperty(default=True, name="Maps",
                                        description="write out *.hpm files")
    
    def update_hpl_project_root_col(self, context):
        data = []
        for collection in bpy.context.scene.collection.children:
            fdata = (collection.name,collection.name,'')
            data.append(fdata)
        return data
    
    hpl_project_root_col: bpy.props.EnumProperty(
        name='Project Name',
        options={'LIBRARY_EDITABLE'},
        description='Should be the name of your Amnesia mod. All map collections go in here',
        items=update_hpl_project_root_col,
        get=get_hpl_project_root_col, 
        set=set_hpl_project_root_col,
    )
        
    def update_hpl_map_root_col(self, context):
        data = []
        if bpy.context.scene.hpl_parser.hpl_project_root_col:
            for collection in bpy.data.collections[bpy.context.scene.hpl_parser.hpl_project_root_col].children:
                fdata = (collection.name,collection.name,'')
                data.append(fdata)
        return data
        
    hpl_map_root_col: bpy.props.EnumProperty(
        name='Project Name',
        options={'LIBRARY_EDITABLE'},
        description='Should be the name of your Amnesia mod. All map collections go in here',
        items=update_hpl_map_root_col,
        get=get_hpl_map_root_col, 
        set=set_hpl_map_root_col,
    )
    
    def update_hpl_base_classes_enum(self, context):
        if not hpl_property_io.hpl_properties.entity_baseclass_list:
            hpl_property_io.hpl_properties.get_base_classes_from_entity_classes()
        data = [('None','None','')]
        for name in hpl_property_io.hpl_properties.entity_baseclass_list:
            fdata = (name,name,'')
            data.append(fdata)
        return data

    hpl_base_classes_enum: bpy.props.EnumProperty(
        name='Entity Types',
        options={'LIBRARY_EDITABLE'},
        description='Prop types for hpl entities',
        items=update_hpl_base_classes_enum,
        get=get_hpl_base_classes_enum, 
        set=set_hpl_base_classes_enum,
    )
    
    '''
    backgroundBlur: bpy.props.FloatProperty(name="Background blur", description='',
                                            default=0.025, min=0, max=1, step=0.0, precision=3, subtype = 'FACTOR',     
                                            get=getBackgroundBlur,
                                            set=setBackgroundBlur)

    badgeColorAL: bpy.props.FloatVectorProperty(
                                            name = "Zoff Badge Color",
                                            subtype = "COLOR",
                                            size = 4,
                                            min = 0.0,
                                            max = 1.0,
                                            default = (0.75,0.75,0.75,0.2),
                                            get=getBadgeColorAL,
                                            set=setBadgeColorAL)
    '''
    def update_presets(self, context):
        enum_name = bpy.context.scene.hpl_parser.hpl_parser_preset_enu
        bpy.context.scene.hpl_parser.hpl_parser_preset_nam = enum_name[:-4].title().replace('_',' ')

def check_for_game_exe(root):

    if os.path.exists(root):
        game_name = root.split("\\")[-2].replace(' ','')
        return os.path.isfile(root+game_name+'.exe')
    return False

def draw_level_settings_ui(scene, layout):
        
        #props = scene.hpl_parser
        level_settings = scene.level_settings

        # Fog Settings
        layout.label(text="Fog Settings")
        layout.prop(level_settings, "FogActive")
        layout.prop(level_settings, "FogCulling")
        
        layout.prop(level_settings, "FogColor")
        
        layout.prop(level_settings, "FogBrightness")
        
        layout.prop(level_settings, "FogFadeStart")
        '''
        layout.prop(level_settings, "FogFadeEnd")
        layout.prop(level_settings, "FogFalloffExp")
        layout.prop(level_settings, "FogUnderwater")
        layout.prop(level_settings, "FogLighten")
        layout.prop(level_settings, "FogUseSkybox")
        layout.prop(level_settings, "FogNoiseStrength")
        layout.prop(level_settings, "FogNoiseSize")
        layout.prop(level_settings, "FogNoiseTurbulence")
        layout.prop(level_settings, "FogApplyAfterFogAreas")
        layout.prop(level_settings, "FogHeightBased")
        layout.prop(level_settings, "FogExponential")
        layout.prop(level_settings, "FogDensity")
        layout.prop(level_settings, "FogHeightDensity")
        layout.prop(level_settings, "FogHeightHorizon")
        layout.prop(level_settings, "FogSecondaryActive")
        layout.prop(level_settings, "FogSecondaryColor")
        layout.prop(level_settings, "FogSecondaryFadeStart")
        layout.prop(level_settings, "FogSecondaryFadeEnd")
        layout.prop(level_settings, "FogSecondaryFalloffExp")
        layout.prop(level_settings, "FogSecondaryDensity")
        layout.prop(level_settings, "FogSecondaryHeightDensity")
        layout.prop(level_settings, "FogSecondaryHeightHorizon")

        # SkyBox Settings
        layout.label(text="SkyBox Settings")
        layout.prop(level_settings, "SkyBoxActive")
        layout.prop(level_settings, "SkyBoxColor")
        layout.prop(level_settings, "SkyBoxTexture")
        layout.prop(level_settings, "SkyBoxBrightness")

        # DirLight Settings
        layout.label(text="Directional Light Settings")
        layout.prop(level_settings, "DirLightActive")
        layout.prop(level_settings, "DirLightShadowCasterDist")
        layout.prop(level_settings, "DirLightShadowDistance")
        layout.prop(level_settings, "DirLightDiffuseColor")
        layout.prop(level_settings, "DirLightBrightness")
        layout.prop(level_settings, "DirLightGobo")
        layout.prop(level_settings, "DirLightGoboAnimMode")
        layout.prop(level_settings, "DirLightGoboAnimStartTime")
        layout.prop(level_settings, "DirLightGoboAnimFrameTime")
        layout.prop(level_settings, "DirLightGoboScale")
        layout.prop(level_settings, "DirLightDirection")
        layout.prop(level_settings, "DirLightCastShadows")
        layout.prop(level_settings, "DirLightSkyCol")
        layout.prop(level_settings, "DirLightGroundCol")
        layout.prop(level_settings, "DirLightShadowMapBiasMul")
        layout.prop(level_settings, "DirLightShadowMapSlopeScaleBiasMul")
        layout.prop(level_settings, "DirLightAutoShadowSliceSettings")
        layout.prop(level_settings, "DirLightAutoShadowSliceLogTerm")

        # SSAO Settings
        layout.label(text="SSAO Settings")
        layout.prop(level_settings, "SSAONormalMap")
        layout.prop(level_settings, "SSAONumOfDirections")
        layout.prop(level_settings, "SSAONumOfSteps")
        layout.prop(level_settings, "SSAOAngleBias")
        layout.prop(level_settings, "SSAOPower")
        layout.prop(level_settings, "SSAORadius")
        layout.prop(level_settings, "SSAOBufferSizeDiv")

        # EnvParticles Settings
        layout.label(text="Environment Particles Settings")
        layout.prop(level_settings, "EnvParticlesActive")
        layout.prop(level_settings, "EnvParticleName")
        layout.prop(level_settings, "EnvParticleColor")
        layout.prop(level_settings, "EnvParticleBrightness")
        layout.prop(level_settings, "EnvParticleBoxDistance")
        layout.prop(level_settings, "EnvParticleGravityVelocity")
        layout.prop(level_settings, "EnvParticleGravitySpeedRandomAmount")
        layout.prop(level_settings, "EnvParticleWindVelocity")
        layout.prop(level_settings, "EnvParticleWindSpeedRandomAmount")
        layout.prop(level_settings, "EnvParticleWindDirRandomAmount")
        layout.prop(level_settings, "EnvParticleRotateVelocity")
        layout.prop(level_settings, "EnvParticleRotateSpeedRandomAmount")
        layout.prop(level_settings, "EnvParticleRotateBothDirs")
        layout.prop(level_settings, "EnvParticleNumIterations")
        layout.prop(level_settings, "EnvParticleSimType")
        layout.prop(level_settings, "EnvParticleOutsideBounds")
        '''
def draw_panel_content(context, layout):	

    scene = context.scene
    props = context.scene.hpl_parser
    wm = context.window_manager
    layout.use_property_split = True
    layout.use_property_decorate = False
    
    row = layout.row()
    col = layout.column(align=True)
    box = col.box()
    box.label(text='Game Settings')
    box.prop(props, 'hpl_game_root_path', text='Game Path', icon_only = True)

    if bpy.context.scene.hpl_parser.hpl_is_game_root_valid:
        row = layout.row()
        #row.scale_y = 2
        col = layout.column(align=True)
        box = col.box()
        #box.enabled = is_valid_game_root
        box.label(text='Project Resources')
        op = box.operator(HPL_OT_ASSETIMPORTER.bl_idname, icon = "IMPORT", text='Import'+bpy.context.scene.hpl_parser.dae_file_count+' Game Assets') #'CONSOLE'
        #op.dae_file_counter = bpy.context.scene.hpl_parser.dae_file_count
        box.prop(props, 'hpl_create_preview')
        col = layout.column(align=True)
        box = col.box()
        #pbox.enabled = is_valid_game_root
        box.label(text='Project Settings')

        singleRow = box.row(align=True)
        singleRow.prop(props, "hpl_project_root_col", text='Project Root Collection', expand=False)
        if not any([col for col in bpy.data.collections if col.name == 'Maps']):
            box.label(text=f'Create a collection called \'Maps\' under \'{bpy.context.scene.hpl_parser.hpl_project_root_col}\'', icon= 'ERROR')
        
        singleRow = box.row(align=True)
        singleRow.enabled = bpy.context.scene.hpl_parser.hpl_project_root_col != None and any([col for col in bpy.data.collections[bpy.context.scene.hpl_parser.hpl_project_root_col].children if col.name == 'Maps'])
        singleRow.scale_y = 2
        singleRow.operator(HPL_OT_DAEEXPORTER.bl_idname, icon = "EXPORT") #'CONSOLE'

        layout.use_property_split = False
        col = layout.column(align=False)
        singleRow = box.row(align=True)
        singleRow.use_property_split = False
        singleRow.prop(props, 'hpl_export_textures', expand=False)
        singleRow.prop(props, 'hpl_export_meshes', expand=False)
        singleRow.prop(props, 'hpl_export_maps', expand=False)
        
        code, ent = hpl_property_io.hpl_properties.get_valid_selection()

        layout.use_property_split = True
        col = layout.column(align=True)
        if code == 7:
            box = col.box()
            box.label(text=f'\"{ent.name}\" must be stored inside \"{bpy.context.scene.hpl_parser.hpl_project_root_col}\".', icon='ERROR')    
        elif code == 6:
            box = col.box()
            box.label(text=f'\"{ent.name}\" is a level collection.', icon='HOME')
            draw_level_settings_ui(scene, layout)
        elif code == 5:
            box = col.box()
            box.label(text=f'\"{ent.name}\" is not stored in a level collection, therefore ignored for export.', icon='INFO')
        elif code == 4:
            box = col.box()
            box.label(text=f'\"{ent.name}\" is the root level collection. All levels go in here.', icon='HOME')
        elif code == 3:
            box = col.box()
            box.label(text=f'\"{ent.name}\" is the root collection.', icon='WORLD')
        elif code == 2:
            box = col.box()
            box.label(text=f'\"{ent.name}\" is not stored in \"{bpy.context.scene.hpl_parser.hpl_project_root_col}\", therefore ignored for export.', icon='INFO') 
        elif code == 1:
            box = col.box()
            if ent.bl_rna.identifier == 'Object':
                if any([var for var in ent.items() if 'hpl_parserinstance_of' in var[0]]):
                    instance_of = ent['hpl_parserinstance_of']
                    box.label(text=f'\"{ent.name}\" is an entity instance of \"{instance_of}\".', icon='GHOST_ENABLED') #OBJECT_DATA GHOST_ENABLED OUTLINER_COLLECTION FILE_3D
            else:
                box.label(text=f'\"{ent.name}\" is an entity.', icon='OUTLINER_COLLECTION') #OBJECT_DATA GHOST_ENABLED OUTLINER_COLLECTION FILE_3D
                col = layout.column(align=True)
                box.prop(props, "hpl_base_classes_enum", text='Entity Type', expand=False)
                singleRowbtn = box.row(align=True)
                singleRowbtn.operator(HPL_OT_RESETPROPERTIES.bl_idname, icon = "FILE_REFRESH")
                singleRowbtn.enabled = False if bpy.context.scene.hpl_parser.hpl_base_classes_enum == 'None' else True

            for group in hpl_config.hpl_ui_var_dict:
                row = layout.row()
                row.prop(ent, f'["{group}"]',
                    icon = "TRIA_DOWN" if ent[group] else "TRIA_RIGHT",
                    icon_only = True, emboss = False
                )

                row.label(text=group.rsplit('_')[-1])
                if ent[group]:
                    row = layout.row()      
                    col = layout.column(align=True)
                    box = col.box()
                    for var in hpl_config.hpl_ui_var_dict[group]:
                        var_ui_name = re.sub(r"(\w)([A-Z])", r"\1 \2", var[11:].replace('_',' '))
                        singleRow = box.row(align=False)
                        singleRow.prop(ent, f'["{var}"]', icon_only=True, text=var_ui_name, expand=False)

class HPL_PT_CREATE(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HPL'
    bl_label = "HPL Parser"
    bl_idname = "HPL_PT_CREATE"

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context, event):
        pass
    
    def invoke(self, context, event):
        pass

    def draw(self, context):
        draw_panel_content(context, self.layout)

    #persistent handler for later asset import
    
    #@persistent

def get_dict_from_entity_vars(ent):
    _temp_ui_var_dict = {}
    group = None
    for var in ent.items():
        if 'hpl_parserdropdown_' in var[0]:
            group = var[0]
            _temp_ui_var_dict[group] = []
        if group:
            if 'hpl_parser_' in var[0]:
                _temp_ui_var_dict[group].append(var[0])
    return _temp_ui_var_dict

def scene_selection_listener(self, context):
    ent = hpl_property_io.hpl_properties.get_outliner_selection()
    if ent:
        #Catch newly created instances (Alt+G)
        if ent.bl_rna.identifier == 'Object' and ent.is_instancer:
            if not any([var for var in ent.items() if 'hpl_parser_' in var[0]]):
                hpl_property_io.hpl_properties.set_collection_properties_on_instance(ent)
        hpl_config.hpl_ui_var_dict = get_dict_from_entity_vars(ent)
    else:
        hpl_config.hpl_ui_var_dict = {}

def register():
    bpy.utils.register_class(HPL_PT_CREATE)
    bpy.utils.register_class(HPM_OT_EXPORTER)
    bpy.utils.register_class(HPL_OT_DAEEXPORTER)
    bpy.utils.register_class(HPL_OT_ASSETIMPORTER)
    bpy.utils.register_class(HPL_OT_RESETPROPERTIES)
    bpy.utils.register_class(HPLSettingsPropertyGroup)
    bpy.utils.register_class(HPLLevelSettingsProperties)
    bpy.types.Scene.level_settings = bpy.props.PointerProperty(type=HPLLevelSettingsProperties)
    bpy.types.Scene.hpl_parser = bpy.props.PointerProperty(type=HPLSettingsPropertyGroup)
    bpy.app.handlers.depsgraph_update_post.append(scene_selection_listener)

def unregister():
    bpy.utils.unregister_class(HPL_PT_CREATE)
    bpy.utils.unregister_class(HPM_OT_EXPORTER)
    bpy.utils.unregister_class(HPL_OT_DAEEXPORTER)
    bpy.utils.unregister_class(HPL_OT_ASSETIMPORTER)
    bpy.utils.unregister_class(HPL_OT_RESETPROPERTIES)
    bpy.utils.unregister_class(HPLSettingsPropertyGroup)
    bpy.utils.unregister_class(HPLLevelSettingsProperties)
    del bpy.types.Scene.level_settings
    del bpy.types.Scene.hpl_parser
    bpy.app.handlers.depsgraph_update_post.clear()