import bpy
from threading import Thread
from . import hpl_config

class MatCreator (Thread):

    def connectMasterDecay():

        links = bpy.data.node_groups['_Master_Decay'].links
        decayMixer = bpy.data.node_groups['_Master_Decay'].nodes['DecayMixer']
        groupOut = bpy.data.node_groups['_Master_Decay'].nodes['Group Output']
        normalMap = bpy.data.node_groups['_Master_Decay'].nodes['Normal Map']

        links.new(decayMixer.outputs[0], groupOut.inputs[0])
        links.new(decayMixer.outputs[1], groupOut.inputs[1])
        links.new(decayMixer.outputs[2], groupOut.inputs[2])
        links.new(decayMixer.outputs[3], groupOut.inputs[3])
        links.new(normalMap.outputs[0], groupOut.inputs[4])


    def newMaterial(id):

        mat = bpy.data.materials.get(id) 

        if mat is None:
            mat = bpy.data.materials.new(name=id)

        mat.use_nodes = True

        if mat.node_tree:
            mat.node_tree.links.clear()
            mat.node_tree.nodes.clear()

        return mat

    def loadInTexture(s):
        for imgs in bpy.data.images:
            if s == imgs.name:
                return s
        return 'errorTex'

    def createShader(id, tex):
        
        dist = 400
        mat = MatCreator.newMaterial(id)

        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location.x = dist * 3

        shader = nodes.new(type='ShaderNodeBsdfPrincipled')
        shader.location.x = dist * 2
        shader.inputs[5].default_value = 0.8
        shader.subsurface_method = 'RANDOM_WALK_FIXED_RADIUS' 

        links.new(shader.outputs[0], output.inputs[0])

        mixNode = nodes.new(type='ShaderNodeMixRGB')
        mixNode.name = 'MixNode'
        mixNode.location.x -= dist
        links.new(mixNode.outputs[0], shader.inputs[0])
        links.new(mixNode.outputs[0], shader.inputs[3])

        mixCONode = nodes.new(type='ShaderNodeMixRGB')
        mixCONode.name = 'MixCONode'
        mixCONode.location.x -= dist*3
        mixCONode.location.y = dist
        links.new(mixCONode.outputs[0], mixNode.inputs[2])

        clrRNode = nodes.new(type='ShaderNodeValToRGB')
        clrRNode.name = 'clrRNode'
        clrRNode.name = 'ColorRampNFT'
        clrRNode.location.x -= dist*4
        clrRNode.location.y = dist*2
        links.new(clrRNode.outputs[0], mixCONode.inputs[1])
        
        decayMasterNode = nodes.new(type="ShaderNodeGroup")
        decayMasterNode.node_tree = bpy.data.node_groups['_Master_Decay']
        decayMasterNode.location.x -= dist*2
        links.new(decayMasterNode.outputs[0], mixNode.inputs[1])
        links.new(decayMasterNode.outputs[1], shader.inputs[9])
        links.new(decayMasterNode.outputs[2], shader.inputs[6])
        links.new(decayMasterNode.outputs[3], mixNode.inputs[0])
        links.new(decayMasterNode.outputs[4], shader.inputs[22])

        if 'Apparel' in id:
            decayMasterNode.inputs[6].default_value = 1.0
        else:
            decayMasterNode.inputs[6].default_value = 0.0

        
        valueDecayNode = nodes.new(type="ShaderNodeGroup")
        valueDecayNode.node_tree = bpy.data.node_groups['DecayValueOverride']
        valueDecayNode.location.x -= dist*4
        valueDecayNode.location.y -= dist*2

        if 'Body' in id:
            shader.inputs[2].default_value = [0.2, 0.04, 0.02]
            #shader.inputs[1].default_value = 0.07                  #SSS OFF
            skinMixAsian = nodes.new(type='ShaderNodeMixRGB')
            skinMixAsian.name = 'SkinMixAsian'
            skinMixAsian.blend_type = 'MULTIPLY'
            skinMixAsian.location.x -= dist * 4
            skinMixAsian.inputs[0].default_value = 1.0 
            skinMixAsian.inputs[2].default_value = env.ethnicityColor['Asian']

            skinMixAfrican = nodes.new(type='ShaderNodeMixRGB')
            skinMixAfrican.name = 'SkinMixAfrican'
            skinMixAfrican.blend_type = 'MULTIPLY'
            skinMixAfrican.location.x -= dist * 5
            skinMixAfrican.inputs[0].default_value = 1.0
            skinMixAfrican.inputs[2].default_value = env.ethnicityColor['African']
            links.new(skinMixAfrican.outputs[0], skinMixAsian.inputs[1])
            links.new(skinMixAsian.outputs[0], decayMasterNode.inputs[0])
        else:
            links.new(valueDecayNode.outputs[0], decayMasterNode.inputs[4])

        diffNode = nodes.new(type='ShaderNodeTexImage')
        diffNode.location.x -= dist*6
        diffNode.image = bpy.data.images.get(MatCreator.loadInTexture(tex+'_D'+'.png'))
        if 'Body' in id:
            links.new(diffNode.outputs[0], skinMixAfrican.inputs[1])
        else:
            links.new(diffNode.outputs[0], decayMasterNode.inputs[0])
        MatCreator.createMappingNodes(diffNode, nodes, links)

        compNode = nodes.new(type='ShaderNodeTexImage')
        compNode.location.x -= dist*6
        compNode.location.y -= dist
        compTex = bpy.data.images.get(MatCreator.loadInTexture(tex+'_S'+'.png'))
        
        compTex.colorspace_settings.name = 'Non-Color'
        compNode.image = compTex
        links.new(compNode.outputs[0], decayMasterNode.inputs[1])
        if 'Body' not in id:
            links.new(compNode.outputs[1], decayMasterNode.inputs[2])
        MatCreator.createMappingNodes(compNode, nodes, links)

        separateNodeS = nodes.new(type='ShaderNodeSeparateRGB')
        separateNodeS.location.x -= dist*5
        separateNodeS.location.y -= dist
        links.new(compNode.outputs[0], separateNodeS.inputs[0])

        metalColorRoughnessGroup = nodes.new(type="ShaderNodeGroup")
        metalColorRoughnessGroup.node_tree = bpy.data.node_groups['metalColorRoughnessGroup']
        metalColorRoughnessGroup.name = 'metalColorRoughnessGroup'
        #metalColorRoughnessGroup.inputs[2].default_value = (0.06, 0.06, 0.06, 1.0)
        metalColorRoughnessGroup.location.x -= dist*3.5
        #metalColorMixNodeGroup.location.y -= dist #* 2
        links.new(separateNodeS.outputs[0], metalColorRoughnessGroup.inputs[0])
        
        metalColorMetalnessGroup = nodes.new(type="ShaderNodeGroup")
        metalColorMetalnessGroup.node_tree = bpy.data.node_groups['metalColorMetalnessGroup']
        metalColorMetalnessGroup.name = 'metalColorMetalnessGroup'
        #metalColorMetalnessGroup.inputs[2].default_value = (0.06, 0.06, 0.06, 1.0)
        metalColorMetalnessGroup.location.x -= dist*3.5
        metalColorMetalnessGroup.location.y -= dist * 1.5
        links.new(separateNodeS.outputs[1], metalColorMetalnessGroup.inputs[0])

        combineNodeS = nodes.new(type='ShaderNodeCombineRGB')
        combineNodeS.location.x -= dist*3
        combineNodeS.location.y -= dist*0.5
        links.new(metalColorRoughnessGroup.outputs[0], combineNodeS.inputs[0])
        links.new(metalColorMetalnessGroup.outputs[0], combineNodeS.inputs[1])
        links.new(separateNodeS.outputs[2], combineNodeS.inputs[2])
        #links.new(combineNodeS.outputs[0], decayMasterNode.inputs[1])

        if 'Exosuit' in id:
            separateNodeD = nodes.new(type='ShaderNodeSeparateRGB')
            separateNodeD.location.x -= dist*4
            separateNodeD.location.y = dist
            links.new(diffNode.outputs[0], separateNodeD.inputs[0])
            ''' 
            clothMathPowerNode = nodes.new(type='ShaderNodeMath')
            clothMathPowerNode.name = 'ClothMathPowerNode'
            clothMathPowerNode.operation = 'POWER'
            clothMathPowerNode.use_clamp = True
            clothMathPowerNode.location.x -= dist
            clothMathPowerNode.location.y -= dist * 0.5
            clothMathPowerNode.inputs[1].default_value = 0.7
            links.new(separateNodeD.outputs[0], clothMathPowerNode.inputs[0])
            
            clothMathSubtractNode = nodes.new(type='ShaderNodeMath')
            clothMathSubtractNode.name = 'ClothMathSubtractNode'
            clothMathSubtractNode.operation = 'SUBTRACT'
            clothMathSubtractNode.use_clamp = True
            clothMathSubtractNode.location.y -= dist * 0.5
            clothMathSubtractNode.inputs[1].default_value = 0.1
            links.new(clothMathPowerNode.outputs[0], clothMathSubtractNode.inputs[0])
                    
            clothMathMultiplyNode = nodes.new(type='ShaderNodeMath')
            clothMathMultiplyNode.name = 'ClothMathMultiplyNode'
            clothMathMultiplyNode.operation = 'MULTIPLY'
            clothMathMultiplyNode.use_clamp = True
            clothMathMultiplyNode.location.x = dist
            clothMathMultiplyNode.location.y -= dist * 0.5
            clothMathMultiplyNode.inputs[1].default_value = 5.0
            links.new(clothMathSubtractNode.outputs[0], clothMathMultiplyNode.inputs[0])

            invertNodeClothColor = nodes.new(type='ShaderNodeInvert')
            invertNodeClothColor.location.x = dist * 2
            invertNodeClothColor.location.y -= dist
            invertNodeClothColor.inputs[0].default_value = 100.0
            links.new(clothMathMultiplyNode.outputs[0], invertNodeClothColor.inputs[1])
        
            mixMetalClothMathNode = nodes.new(type='ShaderNodeMath')
            mixMetalClothMathNode.name = 'MixMetalClothMathNode'
            mixMetalClothMathNode.location.x = dist * 3
            mixMetalClothMathNode.location.y -= dist * 0.5
            links.new(invertNodeClothColor.outputs[0], mixMetalClothMathNode.inputs[0])
            links.new(clothMathMultiplyNode.outputs[0], mixMetalClothMathNode.inputs[1])

            metalColorMixNodeGroup = nodes.new(type="ShaderNodeGroup")
            metalColorMixNodeGroup.node_tree = bpy.data.node_groups['MetalColorMixGroup']
            metalColorMixNodeGroup.name = 'MetalColorMixGroup'
            metalColorMixNodeGroup.inputs[2].default_value = (0.06, 0.06, 0.06, 1.0)
            metalColorMixNodeGroup.location.x = dist
            metalColorMixNodeGroup.location.y -= dist #* 2

            links.new(mixMetalClothMathNode.outputs[0], metalColorMixNodeGroup.inputs[0])
            links.new(mixNode.outputs[0], metalColorMixNodeGroup.inputs[1])
            links.new(metalColorMixNodeGroup.outputs[0], shader.inputs[0]) 
            '''

        #else:
        invertNodeS = nodes.new(type='ShaderNodeInvert')
        invertNodeS.location.x -= dist*4.5
        invertNodeS.location.y -= dist
        links.new(separateNodeS.outputs[2], invertNodeS.inputs[1])

        metalMathMixNode = nodes.new(type='ShaderNodeMath')
        metalMathMixNode.name = 'MetalMathMix'
        metalMathMixNode.operation = 'MULTIPLY'
        metalMathMixNode.location.x -= dist * 4
        metalMathMixNode.location.y -= dist
        metalMathMixNode.inputs[0].default_value = 1.0
        links.new(separateNodeS.outputs[1], metalMathMixNode.inputs[0])
        links.new(invertNodeS.outputs[0], metalMathMixNode.inputs[1])
        links.new(metalMathMixNode.outputs[0], metalColorRoughnessGroup.inputs[1])
        links.new(metalMathMixNode.outputs[0], metalColorMetalnessGroup.inputs[1])

        metalColorMixNodeGroup = nodes.new(type="ShaderNodeGroup")
        metalColorMixNodeGroup.node_tree = bpy.data.node_groups['MetalColorMixGroup']
        metalColorMixNodeGroup.name = 'MetalColorMixGroup'
        metalColorMixNodeGroup.inputs[2].default_value = (0.06, 0.06, 0.06, 1.0)
        metalColorMixNodeGroup.location.x = dist*1.5
        metalColorMixNodeGroup.location.y -= dist #* 2

        invertNodeMetalColor = nodes.new(type='ShaderNodeInvert')
        invertNodeMetalColor.location.x -= dist*0.5
        invertNodeMetalColor.location.y -= dist
        if 'Exosuit' in id:
            links.new(separateNodeD.outputs[0], invertNodeMetalColor.inputs[1])
        else:
            links.new(mixNode.outputs[0], invertNodeMetalColor.inputs[1])

        
        metalMathPowerNode = nodes.new(type='ShaderNodeMath')
        metalMathPowerNode.name = 'MetalMathPowerNode'
        metalMathPowerNode.operation = 'POWER'
        metalMathPowerNode.location.x -= 0.5
        metalMathPowerNode.location.y -= dist * 0.5
        if 'Exosuit' in id:
            metalMathPowerNode.inputs[1].default_value = 1.0
        else:
            metalMathPowerNode.inputs[1].default_value = 5.0
        links.new(invertNodeMetalColor.outputs[0], metalMathPowerNode.inputs[0])

        metalMathMultiplyNode = nodes.new(type='ShaderNodeMath')
        metalMathMultiplyNode.name = 'MetalMathMultiplyNode'
        metalMathMultiplyNode.operation = 'MULTIPLY'
        metalMathMultiplyNode.location.x = dist*0.5
        metalMathMultiplyNode.location.y -= dist
        metalMathMultiplyNode.inputs[1].default_value = 1.0
        links.new(metalMathPowerNode.outputs[0], metalMathMultiplyNode.inputs[0])
        if 'Exosuit' in id:
            if '_RB_' in id:
                links.new(metalMathMixNode.outputs[0], metalMathMultiplyNode.inputs[1])
            else:
                invertZoffExo = nodes.new(type='ShaderNodeInvert')
                invertZoffExo.name = 'invertZoffExo'
                invertZoffExo.location.x = dist
                invertZoffExo.location.y = dist

                links.new(separateNodeS.outputs[2], invertZoffExo.inputs[1])
                links.new(invertZoffExo.outputs[0], metalMathMultiplyNode.inputs[1])
        else:
            links.new(metalMathMixNode.outputs[0], metalMathMultiplyNode.inputs[1])

        links.new(metalMathMultiplyNode.outputs[0], metalColorMixNodeGroup.inputs[0])
        links.new(mixNode.outputs[0], metalColorMixNodeGroup.inputs[1])
        links.new(metalColorMixNodeGroup.outputs[0], shader.inputs[0])
        ###
        normalNode = nodes.new(type='ShaderNodeTexImage')
        normalNode.location.x -= dist*6
        normalNode.location.y -= dist*2
        normalTex = bpy.data.images.get(MatCreator.loadInTexture(tex+'_N'+'.png'))
        normalTex.colorspace_settings.name = 'Non-Color'
        normalNode.image = normalTex
        links.new(normalNode.outputs[0], decayMasterNode.inputs[3])
        MatCreator.createMappingNodes(normalNode, nodes, links)

        curvatureNode = nodes.new(type='ShaderNodeTexImage')
        curvatureNode.name = 'CurvatureMap'
        curvatureNode.location.x -= dist*6
        curvatureNode.location.y -= dist*3
        curvTex = bpy.data.images.get(MatCreator.loadInTexture(tex+'_C'+'.png'))
        curvTex.colorspace_settings.name = 'Non-Color'
        curvatureNode.image = curvTex
        links.new(curvatureNode.outputs[0], decayMasterNode.inputs[5])
        MatCreator.createMappingNodes(curvatureNode, nodes, links)
        
        camoGrp = nodes.new(type="ShaderNodeGroup")
        camoGrp.node_tree = bpy.data.node_groups['Camouflage']
        camoGrp.name = 'Camouflage'
        camoGrp.location.x = clrRNode.location.x -dist
        camoGrp.location.y = clrRNode.location.y
        camoGrp.inputs[0].default_value = -1.0 
        links.new(combineNodeS.outputs[0], decayMasterNode.inputs[1])

        mapNode = nodes.new(type='ShaderNodeMapping')
        mapNode.name = 'CamouflageMapping'
        mapNode.location.x = camoGrp.location.x - 250
        mapNode.location.y = camoGrp.location.y
        
        links.new(mapNode.outputs[0], camoGrp.inputs[1])
        
        coordNode = nodes.new(type='ShaderNodeTexCoord')
        coordNode.location.x = mapNode.location.x - 250
        coordNode.location.y = mapNode.location.y
        
        links.new(coordNode.outputs[4], mapNode.inputs[0])
        links.new(coordNode.outputs[4], mapNode.inputs[2])
        
        links.new(camoGrp.outputs[0], clrRNode.inputs[0])
        links.new(camoGrp.outputs[0], mixCONode.inputs[2])
        links.new(camoGrp.outputs[1], mixCONode.inputs[0])

        for n in nodes:
            n.select = False

        nodes.active = diffNode
        diffNode.select = True
        
        return mat

    def createMappingNodes(node, nodes, links, input=0):
        
        mapNode = nodes.new(type='ShaderNodeMapping')
        mapNode.location.x = node.location.x - 250
        mapNode.location.y = node.location.y
        
        links.new(mapNode.outputs[0], node.inputs[input])
        
        coordNode = nodes.new(type='ShaderNodeTexCoord')
        coordNode.location.x = mapNode.location.x - 250
        coordNode.location.y = mapNode.location.y
        
        links.new(coordNode.outputs[2], mapNode.inputs[0])

    def createMappingNodesProjector(node, nodes, links):
            
        mapNode = nodes.new(type='ShaderNodeMapping')
        mapNode.location.x = node.location.x - 250
        mapNode.location.y = node.location.y
        mapNode.inputs[1].default_value = [0.5, 0.5, 0.5]
        mapNode.inputs[3].default_value = [2, 2, 2]
        links.new(mapNode.outputs[0], node.inputs[0])
        
        coordNode = nodes.new(type='ShaderNodeTexCoord')
        coordNode.location.x = mapNode.location.x - 250
        coordNode.location.y = mapNode.location.y
        
        links.new(coordNode.outputs[1], mapNode.inputs[0])
        
    def camoTexSetup(node, nodes, links):
        
        camoNodes = []
        mixNodes = []
        mathNodes = []
        img_camo_png = env.img_camo_png.copy()
        for c in range(0, len(img_camo_png)):

            camoNodes.append(nodes.new(type='ShaderNodeTexImage'))          
            camoNodes[c].location = (-350*(c+1) + node.location.x - 350, 350*(c+1) + node.location.y)
            camoNodes[c].image = bpy.data.images.get(MatCreator.loadInTexture(img_camo_png[len(img_camo_png)-1-c]))
            
            mixNodes.append(nodes.new(type='ShaderNodeMixRGB'))
            mixNodes[c].location = (camoNodes[c].location.x + 350, camoNodes[c].location.y + 250 + node.location.y)
            
            mathNodes.append(nodes.new(type='ShaderNodeMath'))             
            mathNodes[c].location = (camoNodes[c].location.x, camoNodes[c].location.y + 250 + node.location.y)
            mathNodes[c].operation = 'GREATER_THAN'
            mathNodes[c].inputs[1].default_value = len(img_camo_png)-2-c
            
            if c > 0:
                links.new(mixNodes[c].outputs[0], mixNodes[c-1].inputs[1])
            links.new(camoNodes[c].outputs[0], mixNodes[c].inputs[2])
            links.new(mathNodes[c].outputs[0], mixNodes[c].inputs[0])
        '''     
        signNode = nodes.new(type='ShaderNodeMath')         
        signNode.location = (mixNodes[-1].location.x - 800 + node.location.x, mixNodes[-1].location.y - 200 + node.location.y)
        signNode.operation = 'SIGN'
        '''
        overrideMixNode = nodes.new(type='ShaderNodeMixRGB')    
        overrideMixNode.name = 'Override1'
        overrideMixNode.location = (mixNodes[-1].location.x - 700 + node.location.x, mixNodes[-1].location.y - 200 + node.location.y)
        #links.new(signNode.outputs[0], overrideMixNode.inputs[0])
        ''' 
        signCPNode = nodes.new(type='ShaderNodeMath')         
        signCPNode.location = (mixNodes[-1].location.x - 800 + node.location.x, mixNodes[-1].location.y - 200 + node.location.y)
        signCPNode.operation = 'SIGN'
        '''
        overrideCPMixNode = nodes.new(type='ShaderNodeMixRGB')
        overrideCPMixNode.name = 'Override2'
        overrideCPMixNode.location = (mixNodes[-1].location.x - 700 + node.location.x, mixNodes[-1].location.y - 200 + node.location.y)
        #links.new(signCPNode.outputs[0], overrideCPMixNode.inputs[0])
        links.new(overrideCPMixNode.outputs[0], overrideMixNode.inputs[1])

        GroupInputNode = nodes.new(type='NodeGroupInput')
        GroupInputNode.location = (mixNodes[-1].location.x - 1200 + node.location.x, mixNodes[-1].location.y - 200 + node.location.y)
        #links.new(GroupInputNode.outputs[0], signNode.inputs[0])
        #links.new(GroupInputNode.outputs[0], signNode.inputs[0])
        links.new(GroupInputNode.outputs[0], overrideMixNode.inputs[2])

        for math in mathNodes:
            links.new(overrideMixNode.outputs[0], math.inputs[0])
        
        mapNode = nodes.new(type='ShaderNodeMapping')
        mapNode.name = 'PatternSkinOV'
        mapNode.inputs[3].default_value = (2.5,2.5,2.5)
        mapNode.location = (mixNodes[-1].location.x - 900 + node.location.x, mixNodes[-1].location.y - 450 + node.location.y)
        
        mapNodeOV = nodes.new(type='ShaderNodeMapping')
        mapNodeOV.name = 'PatternEditOV'
        mapNodeOV.inputs[3].default_value = (2.5,2.5,2.5)
        mapNodeOV.location = (mixNodes[-1].location.x - 900 + node.location.x, mixNodes[-1].location.y - 900 + node.location.y)

        overrideMapMixNode = nodes.new(type='ShaderNodeMixRGB')
        overrideMapMixNode.name = 'ColorEditOV'
        overrideMapMixNode.inputs[0].default_value = 0.0
        overrideMapMixNode.location = (mixNodes[-1].location.x - 450 + node.location.x, mixNodes[-1].location.y - 900 + node.location.y)
        #links.new(signMapNode.outputs[0], overrideMapMixNode.inputs[0])
        links.new(GroupInputNode.outputs[1], overrideMapMixNode.inputs[1])
            
        overrideMapMixNode2 = nodes.new(type='ShaderNodeMixRGB')
        overrideMapMixNode2.name = 'ColorEditOV2'
        overrideMapMixNode2.location = (mixNodes[-1].location.x - 600 + node.location.x, mixNodes[-1].location.y - 900 + node.location.y)
        overrideMapMixNode2.inputs[0].default_value = 0.0
        #links.new(signMapNode.outputs[0], overrideMapMixNode.inputs[0])
        links.new(GroupInputNode.outputs[1], overrideMapMixNode.inputs[1])
        links.new(mapNodeOV.outputs[0], overrideMapMixNode2.inputs[2])
        links.new(overrideMapMixNode2.outputs[0], overrideMapMixNode.inputs[2])
        links.new(mapNode.outputs[0], overrideMapMixNode2.inputs[1])

        for camo in camoNodes:
            links.new(overrideMapMixNode.outputs[0], camo.inputs[0])
        
        coordNode = nodes.new(type='ShaderNodeTexCoord')
        coordNode.location = (mapNode.location.x -250, mapNode.location.y)
        
        links.new(coordNode.outputs[4], mapNode.inputs[0])
        links.new(coordNode.outputs[4], mapNode.inputs[2])
        links.new(coordNode.outputs[4], mapNodeOV.inputs[0])
        links.new(coordNode.outputs[4], mapNodeOV.inputs[2])

        camocrNode =  nodes.new(type='ShaderNodeValToRGB')
        camocrNode.name = 'ColorRampOverrideEdit'
        camocrNode.location = (-250, 0)

        camocrovNode =  nodes.new(type='ShaderNodeValToRGB')
        camocrovNode.name = 'ColorRampOverrideSkin'
        camocrovNode.location = (-350, 250)
        links.new(mixNodes[0].outputs[0], camocrNode.inputs[0])
        links.new(camocrNode.outputs[0], camocrovNode.inputs[0])

        return camocrovNode.outputs[0]

    def createCamoGroup():
        
        x = bpy.data.node_groups.new("Camouflage","ShaderNodeTree")
        x.inputs.new("NodeSocketFloat", "Float")
        x.inputs.new("NodeSocketVector", "Vector")
        x.name = 'Camouflage'
        ngo = x.nodes.new(type="NodeGroupOutput")
        x.links.new(MatCreator.camoTexSetup(ngo, x.nodes, x.links),ngo.inputs[0])
        #x.links.new(camoTexSetup(ngo, x.nodes, x.links),ngo.inputs[1])

        camoOVerrideNode =  x.nodes.new(type='ShaderNodeValue')
        camoOVerrideNode.location = (-250, -200)
        x.links.new(camoOVerrideNode.outputs[0], ngo.inputs[1])
        #x.links.new(camoOVerrideNode.outputs[0], ngo.inputs[1])

    def createProjectorMaterial(projector, isAlpha):
        dist = 400
        
        nodes = projector.node_tree.nodes
        links = projector.node_tree.links
        emission = nodes[0]
        output = nodes[1]
        links.new(emission.outputs[0], output.inputs[0])

        diffNode = nodes.new(type='ShaderNodeTexImage')
        diffNode.location.x -= dist
        diffNode.location.y += dist
        diffNode.image = bpy.data.images.get(MatCreator.loadInTexture(bpy.context.scene.nftcreator.memeTextures))
        diffNode.extension = 'EXTEND'
        links.new(diffNode.outputs[int(isAlpha)], emission.inputs[0])
        MatCreator.createMappingNodesProjector(diffNode, nodes, links)
        
        fallOffNode = nodes.new(type="ShaderNodeLightFalloff")
        fallOffNode.location.x -= dist
        links.new(fallOffNode.outputs[2], emission.inputs[1])