import bpy
import xml.etree.ElementTree as xtree
from . import hpl_config

class hpl_porperties():

    def get_entity_vars(ent):

        entity_type = 'Prop_Grab' #TODO: get *.ent file class of selected object.
        def_file_path = bpy.context.scene.hpl_parser.hpl_game_root_path + 'editor\\userclasses\\' + hpl_config.hpl_properties['entities']
        #def_file_path = 'F:\\SteamLibrary\\steamapps\\common\\Amnesia The Bunker\\editor\\userclasses\\EntityClasses.def'
        def_file = ""

        with open(def_file_path, 'rt', encoding='ascii') as fobj:
            def_file = fobj.read()

        #TODO: build xml handler that ignores quotation segments
        def_file = def_file.replace('&', '')
        def_file = def_file.replace(' < ', '')
        def_file = def_file.replace(' > ', '')

        parser = xtree.XMLParser(encoding="ascii")
        tree = xtree.fromstring(def_file, parser=parser)

        derived_class = {}
        base_class = {}

        for category in tree.iter():
            if entity_type in category.attrib.values():
                if hpl_config.hpl_xml_inherit_attribute in category.attrib:
                    derived_class = category.attrib
                for e in iter(category):
                    if hpl_config.hpl_xml_typevars in e.tag:
                        e=e[0]
                        for i in e:
                            print(i.tag, i.attrib)
                            #base_class(i.tag, i.attrib)
        derived_class.update(derived_class)
        return derived_class