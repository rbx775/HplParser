import bpy, os, json, pickle, pathlib, bmesh
from . import hpl_config

HPMString = ""

class HPM_OT_EXPORTER(bpy.types.Operator):
    
    bl_idname = "hpl.hpmexporter"
    bl_label = "Write HPM File"
    bl_description = "This will write the HPM file to disk, to be opened with HPL LE then"
    bl_options = {'REGISTER', 'UNDO'}

def write_file():

    HPM = read_template()
    for v in vd.hpl_variables.keys():
        vd.hpl_variables[v] = []
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
    file = f'{desktop}\\parser.hpm'

    #me = bpy.context.object.data
    me = bpy.context.view_layer.objects.active.data

    bm = bmesh.new()
    bm.from_mesh(me)
    uv_lay = bm.loops.layers.uv.active


    mx_inv = bpy.context.object.matrix_world.inverted()
    mx_norm = mx_inv.transposed().to_3x3()

    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table() #not necessary?
    bm.faces.ensure_lookup_table()
    
    print('VCO')
    
    #vco = datamodel.make_array((v.co for v in bm.verts),datamodel.Vector3)
    #print(str(len(vco)) + " " + str(vco))
    print('LOOPS')
    #loops = datamodel.make_array((l.vert.index for f in bm.faces for l in f.loops),int)
    #print(str(len(loops))+" "+str(loops))

    #vertex_data[keywords['pos']] = datamodel.make_array((v.co for v in bm.verts),datamodel.Vector3)
    #vertex_data[keywords['pos'] + "Indices"] = datamodel.make_array((l.vert.index for f in bm.faces for l in f.loops),int)
    #edges = [bm.edges[i] for i in edge_indices]

    for e in bm.edges:
        for v in e.verts:
            vd.hpl_variables['HPMedgeVertexIndices'].append(v.index)

    for i in range(len(vd.hpl_variables['HPMedgeVertexIndices'])):
        if (i % 2) == 0:
            vd.hpl_variables['HPMedgeOppositeIndices'].append(i+1)
        else:
            vd.hpl_variables['HPMedgeOppositeIndices'].append(i-1)

    for face in bm.faces:
        for loop in face.loops:
            vd.hpl_variables['HPMtexcoord'].append(format_vector(loop[uv_lay].uv))
            #HPMtexcoord = loop[uv_lay].uv
            #print("Loop UV: %f, %f" % HPMtexcoord[:])
            vd.hpl_variables['HPMposition'].append(format_vector(loop.vert.co * vd.hpl_vmf_factor))
            #HPMposition.append(loop.vert.co)
            #print("Loop Vert: (%f,%f,%f)" % vert.co[:])
            #world_normal = mx_norm @ vert.normal
            #print("Loop Normal: (%f,%f,%f)" % world_normal[:])
            #print("Loop UV: (%f,%f,%f)" % uv_lay)
            
    for face in me.polygons:
        vd.hpl_variables['HPMfaceDataIndices'].append(face.index)
        #HPMfaceDataIndices.append(face.index)
        for vert in [me.loops[i] for i in face.loop_indices]:
            #HPMposition.append(mx_norm @ vert.co)
            vd.hpl_variables['HPMnormal'].append(format_vector(mx_norm @ vert.normal))
            #print("Loop Normal: (%f,%f,%f)" % world_normal[:])
            #HPMnormal.append(mx_norm @ vert.normal)
            vd.hpl_variables['HPMtangent'].append(format_vector(mx_norm @ vert.tangent))
            #HPMtangent.append(mx_norm @ vert.tangent)

            #print("Loop Tangent: (%f,%f,%f)" % world_tangent[:])
            #world_bitangent.append(vert.bitangent_sign * world_normal.cross(world_tangent))
            #print("Loop Bi-Tangent: (%f,%f,%f)" % world_bitangent[:])
            vd.hpl_variables['HPMvertexEdgeIndices'].append(vert.edge_index)
            #HPMvertexEdgeIndices.append(vert.edge_index)
            vd.hpl_variables['HPMvertexDataIndices'].append(vert.index)
            #HPMvertexDataIndices.append(vert.index)
            
    fc_count = 0
    for face in bm.faces:
        for loop in face.loops:
            fc_count = fc_count + 1

    vd.hpl_datacounter['HPMTOTALVERTCOUNT'] = len(bm.verts)
    vd.hpl_datacounter['HPMTOTALFACECORNERCOUNT'] = fc_count
    vd.hpl_datacounter['HPMTOTALEDGECOUNT'] = len(bm.edges)
    vd.hpl_datacounter['HPMTOTALFACECOUNT'] = len(me.polygons)

    variable = False
    with open(file, "w") as f:
        for l in HPM:
            for v in vd.hpl_variables.keys():
                if v in l:
                    i = 0
                    for s in vd.hpl_variables[v]:
                        if i < len(vd.hpl_variables[v])-1:
                            f.write(f'\"{str(s)}\",\n')
                        else:
                            f.write(f'\"{str(s)}\"')
                        i=i+1
                        #f.write("\"" + str(s) + "\"" + "," + '\n')
                    #f.writelines([string + '\n' for string in str(vd.hpl_variables[v])])
                    #[string + '\n' for string in vd.hpl_variables[v]]
                    variable = True
                    #f.write(str(vd.hpl_variables[v]))
            for v in vd.hpl_datacounter.keys():
                if v in l:
                    f.write('\"size\" \"int\" {mesh_data}'.format(mesh_data=vd.hpl_datacounter[v]))
                    variable = True
                    
            if (not variable):
                f.write(l)
            variable = False
            f.write("\n")
        #f.writelines([string + '\n' for string in HPM])
        #f.write(f'{len(HPM)}')
    

def read_template():
    file = f'{os.path.dirname(__file__)}\\HPMTemplate.txt'
    with open(file) as f:
        return([line.rstrip('\n') for line in f])

def HPMfileexample(state):
    bpy.data.node_groups["metalColorRoughnessGroup"].nodes["metalColorRoughnessNFT"].mute = state
    bpy.data.node_groups["metalColorRoughnessGroup"].nodes["metalColorRoughnessOverride"].mute = not state
    bpy.data.node_groups["metalColorMetalnessGroup"].nodes["metalColorMetalnessNFT"].mute = state
    bpy.data.node_groups["metalColorMetalnessGroup"].nodes["metalColorMetalnessOverride"].mute = not state
    bpy.data.node_groups["MetalColorMixGroup"].nodes["MetalColorMixNFT"].mute = state
    bpy.data.node_groups["MetalColorMixGroup"].nodes["MetalColorMixOverride"].mute = not state

'''
def readJsonMetalColor():
    file = f'{env.assetPath}MetalColor.json'
    with open(file, 'r+') as outfile:
        return(json.load(outfile))

def purgeJsonMetalColor():
    file = f'{env.assetPath}MetalColor.json'
    with open(file, 'w') as outfile:
        json.dump({'MetalColor':{}}, outfile, indent=4)

def writeJsonMetalColor(ID, r,g,b, metalness, roughness, exclude):
    wt.addKey('MetalColor', ID)
    file = f'{env.assetPath}MetalColor.json'
    if not os.path.exists(file):
        with open(file, 'w') as outfile:
            json.dump({'MetalColor':{}}, outfile, indent=4)

    data = {'MetalColor':{}}
    with open(file, 'r+') as outfile:
        data = json.load(outfile)

    with open(file, 'w') as outfile:
        data['MetalColor'][ID] = {'color':(r,g,b)}
        data['MetalColor'][ID]['metalness'] = metalness
        data['MetalColor'][ID]['roughness'] = roughness
        data['MetalColor'][ID]['exclude'] = exclude
        json.dump(data, outfile, indent=4)
'''