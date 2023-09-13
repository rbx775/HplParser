
hpm_file_containers = ['', '_Area', '_Billboard', '_Compound', '_Decal', '_DetailMeshes', '_Entity', '_ExposureArea', '_FogArea', '_LensFlare', '_Light',
                        '_LightMask', '_ParticleSystem', '_Primitive', '_Sound', '_StaticComboArea', '_StaticObject', '_StaticObjectBatches', '_Terrain']


hpm_area = {'HPLMapTrack' : ['ID', 'MajorVersion', 'MinorVersion']}

hpm_billboard = {'HPLMapTrack' : ['ID', 'MajorVersion', 'MinorVersion']}

hpm_maintags = {'HPLMapTrack' : ['ID', 'MajorVersion', 'MinorVersion']}

hpm_staticobjects_file_count = {'FileIndex_StaticObjects' : ['NumOfFiles']}
hpm_staticobjects_file_id = {'File' : ['Id', 'Path']}
hpm_staticobjects_properties = {'StaticObject' : ['ID', 'Name', 'CreStamp', 'ModStamp', 'WorldPos', 'Rotation', 
                                                    'Scale', 'FileIndex', 'Collides', 'CastShadows', 'IsOccluder', 
                                                    'ColorMul', 'CulledByDistance' 'CulledByFog', 'IllumColor', 'IllumBrightness', 'UID']}
'''
__hpm_entities_file_index_tag = {'Objects': None}
__hpm_entities_file_index_attributes = {'NumOfFiles' : 0, 'NumOfFiles2' : 1}
__hpm_entities_file_index_element = {__hpm_entities_file_index_tag, __hpm_entities_file_index_attributes}
__hpm_entities_file_index_dict = {__hpm_entities_file_index_element, None}

__hpm_entities_file_index_tag = {'FileIndex_Entities': None}
__hpm_entities_file_index_attributes = {'NumOfFiles' : 0, 'NumOfFiles2' : 1}
__hpm_entities_file_index_element = {__hpm_entities_file_index_tag, __hpm_entities_file_index_attributes}
__hpm_entities_file_index_dict = {__hpm_entities_file_index_element, None}

__hpm_entities_section_tag = {'Section' : __hpm_entities_file_index_tag}
__hpm_entities_section_attributes = {'Name' : 0}
__hpm_entities_section_element = {__hpm_entities_section_tag : __hpm_entities_section_attributes}
__hpm_entities_section_dict = {__hpm_entities_section_element : __hpm_entities_file_index_dict}

__hpm_entities_hpl_map_track_tag = {'HPLMapTrack_Entity' : __hpm_entities_section_tag}
__hpm_entities_hpl_map_track_attributes = {'ID' : 0, 'MajorVersion' : 1, 'MinorVersion' : 1}
__hpm_entities_hpl_map_track_element = {__hpm_entities_hpl_map_track_tag : __hpm_entities_hpl_map_track_attributes}
hpm_entities_dict = {__hpm_entities_hpl_map_track_element : __hpm_entities_section_dict}
'''

#ent_list = [{'HPLMapTrack_Entity' : __hpm_entities_hpl_map_track_attributes} ,{'Section' : __hpm_entities_section_attributes}, {'FileIndex_Entities': __hpm_entities_file_index_attributes, }]
#for ent in ent_list:




hpm_entities_file_count = {'FileIndex_Entities' : ['NumOfFiles']}
hpm_entities_file_id = {'File' : ['Id', 'Path']}
hpm_entities_properties_objects = 'Objects'
hpm_entities_properties = {'Entity' : ['ID', 'Name', 'CreStamp', 'ModStamp', 'WorldPos', 'Rotation', 
                                                    'Scale', 'FileIndex', 'Active', 'Important', 'Static', 
                                                    'CulledByDistance', 'CulledByFog', 'UID']}
hpm_entities_vars = {'Var' : ['ObjectId', 'Name']}


hpm_sampler_file_identifier = 'arsenal'
hpm_sampler_file_path = 'maps\\'+hpm_sampler_file_identifier+'\\'

#[('hpl_parser_instance_of', 'Suzi'), ('hpl_parser_Active', True), ('hpl_parser_Important', False), ('hpl_parser_Static', False), ('hpl_parser_Distance Culling', True), ('hpl_parser_Culles by Fog', True), ('hpl_parser_Note', ''), ('hpl_parser_EventInstanceTag', ''), ('hpl_parser_CollideGroup', ''), ('hpl_parser_UserVar', ''), ('hpl_parser_DisableBreakable', False), ('hpl_parser_FullGameSave', False), ('hpl_parser_StaticPhysics', False), ('hpl_parser_QuickSave', False), ('hpl_parser_AllowMapTransfer', False), ('hpl_parser_EffectsActive', True), ('hpl_parser_InteractionDisabled', False), ('hpl_parser_CastShadows', True), ('hpl_parser_ColorMul', <bpy id property array [4]>), ('hpl_parser_EffectColorMul', <bpy id property array [4]>), ('hpl_parser_EffectBrightnessMul', 1.0), ('hpl_parser_IllumColor', <bpy id property array [4]>), ('hpl_parser_IllumBrightness', 1.0), ('hpl_parser_IsAffectedByDecal', False), ('hpl_parser_IsOccluder', False), ('hpl_parser_UpdateBonesWhenCulled', False), ('hpl_parser_OnBreakCallbackFunc', 'hpl_function'), ('hpl_parser_ConnectionStateChangeCallback', 'hpl_function'), ('hpl_parser_PlayerLookAtCallback', 'hpl_function'), ('hpl_parser_PlayerLookAtCallbackAutoRemove', False), ('hpl_parser_PlayerLookAtCheckCenterOfScreen', True), ('hpl_parser_PlayerLookAtCheckRayIntersection', True), ('hpl_parser_PlayerLookAtMaxDistance', -1.0), ('hpl_parser_PlayerLookAtCallbackDelay', 0.0), ('hpl_parser_PlayerInteractCallback', 'hpl_function'), ('hpl_parser_PlayerInteractCallbackAutoRemove', False), ('hpl_parser_PlayerInteractLeaveCallback', 'hpl_function'), ('hpl_parser_PlayerInteractLeaveCallbackAutoRemove', False), ('hpl_parser_RecieveMessageCallback', 'hpl_function'), ('hpl_parser_CC_Entities', ''), ('hpl_parser_CC_Funcs', 'hpl_function'), ('hpl_parser_ConnectedEntity', ''), ('hpl_parser_ConnectedEntityInvertState', False), ('hpl_parser_ConnectedEntityStatesUsed', 0), ('hpl_parser_ParentAttachEntity', ''), ('hpl_parser_ParentAttachUseRotation', True), ('hpl_parser_ParentAttachBody', ''), ('hpl_parser_ParentAttachSocket', ''), ('hpl_parser_ParentAttachSnap', False), ('hpl_parser_ParentAttachLocked', False), ('hpl_parser_ConnectedLight', ''), ('hpl_parser_ConnectionLightAmount', 1.0), ('hpl_parser_ConnectionLightUseOnColor', True), ('hpl_parser_ConnectionLightUseSpec', False), ('hpl_parser_ConnectionLightType', 'hpl_enum'), ('hpl_parser_ExtraConnectedLight', ''), ('hpl_parser_ExtraConnectionLightAmount', 1.0), ('hpl_parser_ExtraConnectionLightUseOnColor', True), ('hpl_parser_ExtraConnectionLightUseSpec', False), ('hpl_parser_ExtraConnectionLightType', 'hpl_enum'), ('hpl_parser_InteractDisablesStaticPhysics', False)]