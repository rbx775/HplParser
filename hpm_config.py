
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