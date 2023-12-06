
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

hpm_attribute_identifiers_dict = {'Fog':'Fog', 'SecondaryFog':'Fog', 'SkyBox':'SkyBox', 'DirectionalLight':'DirLight', 'SSAO':'PostEffects', 
                                    'EnvironmentParticles':'EnvParticles', 'EnvironmentParticle':'EnvParticle', 'Decal': 'Decal',
                                    'PostEffects':'PostEffects', 'DistanceCulling':'DistanceCulling', 'Decal':'Decal', 'DetailMeshes':'DetailMeshes'}

hpm_entities_file_count = {'FileIndex_Entities' : ['NumOfFiles']}
hpm_entities_file_id = {'File' : ['Id', 'Path']}
hpm_entities_properties_objects = 'Objects'
hpm_entities_properties = {'Entity' : ['ID', 'Name', 'CreStamp', 'ModStamp', 'WorldPos', 'Rotation', 
                                                    'Scale', 'FileIndex', 'Active', 'Important', 'Static', 
                                                    'CulledByDistance', 'CulledByFog', 'UID']}
hpm_entities_vars = {'Var' : ['ObjectId', 'Name']}


hpm_sampler_file_identifier = 'arsenal'
hpm_sampler_file_path = 'maps\\'+hpm_sampler_file_identifier+'\\'