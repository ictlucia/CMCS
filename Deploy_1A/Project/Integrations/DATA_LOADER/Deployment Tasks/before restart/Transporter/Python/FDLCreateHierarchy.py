"""-------------------------------------------------------------------
MODULE
    FDLCreateHierarchy - Creates hierarchy in database

DESCRIPTION
    This module creates hierarchy in database based on user input

VERSION: 5.0.6
--------------------------------------------------------------------"""

import os
import xml.etree.ElementTree
import acm

import FDLFileOperations
import FDLConfigSingleton
import FLogger

logger = FLogger.FLogger('DLHierarchy')

class RestrictionKeys :
    """ Restrictions on Hierarchy Column Definitions """
    no_restrictions = 'None'
    group_level_only = 'Group Level Only'
    leaf_level_only = 'Leaf Level Only'

class ColumnDefs :
    """ Hierarchy Column Definitions """
    Def = [
           {'Name':                 'INSTRUMENT',
            'TypeGroup':            'RecordRef',
            'TypeString':           'Instrument',
            'TypeInfo':             '',
            'Restriction':           RestrictionKeys.leaf_level_only,
            'Description':          'Instrument in database'},
           {'Name':                 'PARTY',
            'TypeGroup':            'RecordRef',
            'TypeString':           'Party',
            'TypeInfo':             '',
            'Restriction':           RestrictionKeys.leaf_level_only,
            'Description':          'Party in database'},

          ]

class GICSHierarchy:
    """ GICS data """
    hierarchy_name = 'Global Industry Classification Standard'
    hierarchy_type = 'Global Industry Classification Standard'
    xml_file_name = 'bbg_global_industry_classification_standard'

class BICSHierarchy:
    """ BICS Data """
    hierarchy_name = 'Bloomberg Industry Classification Scheme'
    hierarchy_type = 'Bloomberg Industry Classification Scheme'
    xml_file_name = 'bbg_bloomberg_industry_classification_scheme'

class ICBHierarchy:
    """ ICB Data """
    hierarchy_name = 'Industry Classification Benchmark'
    hierarchy_type = 'Industry Classification Benchmark'
    xml_file_name = 'bbg_industry_classification_benchmark'


class CreateDataLoaderSectorsHierarchy(object):
    """ Creation of secutity classification hierarchy """
    def __init__(self, hierarchy_obj):
        self.hierarchy_obj = hierarchy_obj

    def get_data_type_integer( self, data_type_string, data_type_group ):
        """ ACM data type """
        enumeration = 0
        if data_type_group == 'Standard' :
            enumeration = acm.FEnumeration['enum(B92StandardType)']
        elif data_type_group == 'Enums' :
            enumeration = acm.FEnumeration['enum(B92EnumType)']
        elif data_type_group == 'RecordRef' :
            enumeration = acm.FEnumeration['enum(B92RecordType)']

        return enumeration.Enumeration(data_type_string) if enumeration else 0

    def create_column_definition(self, column_spec_name, hierarchy_type, data_type_group, data_type_string, data_type_info, restriction, description, previous_column_def_name):
        """ Create Column Definitions """
        try:
            logger.LOG("Creating Column Definition <%s>"%column_spec_name)
            columnDefinition = acm.FHierarchyColumnSpecification()
            columnDefinition.Name(column_spec_name)
            columnDefinition.HierarchyType(hierarchy_type)
            columnDefinition.DataTypeGroup(data_type_group)
            columnDefinition.DataTypeType(self.get_data_type_integer(data_type_string, data_type_group))
            columnDefinition.DataTypeInfo(data_type_info)
            columnDefinition.Restriction(restriction)
            columnDefinition.Description(description)
            columnDefinition.PreviousColumnSpecificationName(previous_column_def_name)

            columnDefinition.RegisterInStorage()
            return columnDefinition
        except Exception as e:
            logger.ELOG("Exception in create_column_definition : %s"%str(e))

    def create_hierarchy_type(self, hierarchy_type_name):
        """ Create HierarchyType """
        try:
            logger.LOG("Creating FHierarchyType <%s>"%hierarchy_type_name)
            hierarchy_type = acm.FHierarchyType[hierarchy_type_name]
            if hierarchy_type :
                hierarchy_type.Delete()

            hierarchy_type = acm.FHierarchyType()
            hierarchy_type.Name(hierarchy_type_name)
            hierarchy_type.RegisterInStorage()

            previous = ''
            for cd in ColumnDefs.Def :
                self.create_column_definition(cd['Name'], hierarchy_type, cd['TypeGroup'], cd['TypeString'], cd.get('TypeInfo', ''), cd.get('Restriction', RestrictionKeys.no_restrictions), cd.get('Description', ''), previous)
                previous = cd['Name']

            return hierarchy_type
        except Exception as e:
            logger.ELOG("Exception in create_hierarchy_type : %s"%str(e))

    def get_valid_hierarchy_data_value(self, data_val, columnSpecification) :
        """ Create Hierarchy Data Value """
        try:
            hierarchyDataValue = acm.FHierarchyDataValue()
            hierarchyDataValue.HierarchyColumnSpecification = columnSpecification

            if data_val :
                hierarchyDataValue.DataValueVA(data_val)
            dataValue = hierarchyDataValue.DataValue()

            return hierarchyDataValue, dataValue
        except Exception as e:
            logger.ELOG("Exception in get_valid_hierarchy_data_value : %s"%str(e))

    def create_hierarchy_data_value(self, node, columnSpecification, data_val):
        """ Create Hierarchy Data Value """
        try:
            hierarchyDataValue, dataValue = self.get_valid_hierarchy_data_value(data_val, columnSpecification)

            if hierarchyDataValue.DataValue() not in [None, '']:
                hierarchyDataValue.HierarchyNode = node
                hierarchyDataValue.RegisterInStorage()
        except Exception as e:
            logger.ELOG("Exception in create_hierarchy_data_value : %s"%str(e))

    def create_hierarchy_from_xml(self, parent_node, sector_tree, hierarchy_tree, column_spec_by_name):
        """ Create hierarchy from the input XML """
        add_node_flag = True
        if sector_tree != None:
            root = None
            if hasattr(sector_tree, 'getroot'):  # Parent root node
                root = sector_tree.getroot()
                if hierarchy_tree.RootNode() and hierarchy_tree.RootNode().DisplayName() == root.attrib.get('name', None):
                    add_node_flag = False
                    parent_node = hierarchy_tree.RootNode()
            else:
                root = sector_tree
                try:
                    child_node = hierarchy_tree.FindChildByName01(root.attrib.get('name', None), parent_node, 1)
                    if child_node:
                        parent_node = child_node
                        add_node_flag = False
                except Exception as e:
                    logger.ELOG("Exception : Cannot find child node : %s "%str(e))

            display_name = root.attrib.get('name', None)

            if display_name and add_node_flag:
                parent_node = hierarchy_tree.Add(display_name, parent_node)
                parent_node.RegisterInStorage()
                parent_node.IsLeaf('No')

            childrens = list(root)
            for chld in childrens:
                try:
                    self.create_hierarchy_from_xml(parent_node, chld, hierarchy_tree, column_spec_by_name)
                except Exception as e:
                    logger.ELOG("Exception in create_hierarchy_from_xml : %s"%str(e))

    def create_hierarchy(self, hierarchy_tree):
        """ Create Hierarchy """
        hierarchy = hierarchy_tree.Hierarchy()
        hierarchy_type = hierarchy.HierarchyType()

        column_spec_by_name = {}

        for columnSpec in hierarchy_type.HierarchyColumnSpecifications() :
            column_spec_by_name[str(columnSpec.Name())] = columnSpec

        self.create_hierarchy_from_xml(None, self.hierarchy_obj, hierarchy_tree, column_spec_by_name)

    def create(self, hierarchy_name, hierarchy_type_name):
        """ Create Hierarchy """
        try :
            hierarchy = acm.FHierarchy[hierarchy_name]

            if not hierarchy:
                hierarchy = acm.FHierarchy()
                hierarchy.Name(hierarchy_name)
                hierarchy.RegisterInStorage()
                hierarchy_type = self.create_hierarchy_type(hierarchy_type_name)
                hierarchy.HierarchyType(hierarchy_type)

                hierarchy_tree = acm.FHierarchyTree()
                hierarchy_tree.Hierarchy(hierarchy)
                self.create_hierarchy(hierarchy_tree)
                hierarchy_type.Commit()
                hierarchy.Commit()
                logger.LOG("Created Hierarchy <%s>"%hierarchy_name)
            else:
                logger.LOG('Hierarchy <%s> already present in database'%hierarchy_name)
                hierarchy.RegisterInStorage()
                hierarchy_tree = acm.FHierarchyTree()
                hierarchy_tree.Hierarchy(hierarchy)
                self.create_hierarchy(hierarchy_tree)
                hierarchy.Commit()
                logger.LOG("Updated Hierarchy <%s>"%hierarchy_name)

        except Exception as e:
            logger.ELOG("Exception in Hierarchy creation : %s"%str(e))

def create_hierarchy(hierarchy_obj):
    """ Create Hierarchy """
    is_created = False
    try:
        file_name = hierarchy_obj.xml_file_name
        extension_data = None

        context = acm.GetDefaultContext()
        ext_module = acm.FExtensionModule['DataLoader_Bloomberg']
        extension = ext_module.GetExtension('FXSLTemplate', 'FObject', file_name)
        extension_data = extension.Value()
        if not ext_module:
            logger.ELOG("Extension Module <DataLoader_Bloomberg> not found")
        elif not extension:
            logger.ELOG("FXSLTemplate <%s> not found"%file_name)
        elif extension_data:
            elem_tree_interface = xml.etree.ElementTree.fromstring(extension_data)
            elem_tree = xml.etree.ElementTree.ElementTree \
                                            (elem_tree_interface)
            if elem_tree:
                logger.DLOG("Creating Hierarchy <%s>"%hierarchy_obj.hierarchy_name)
                c = CreateDataLoaderSectorsHierarchy(elem_tree)
                c.create(hierarchy_obj.hierarchy_name, hierarchy_obj.hierarchy_type)
                is_created = True
        else:
            logger.ELOG("No data found in FXSLTemplate <%s>"%file_name)
    except Exception as e:
        logger.ELOG("EXception in create_hierarchy : %s"%str(e))
    return is_created

def dl_create_hierarchy(name=''):
    is_created = False
    if name == 'ICB':
        is_created = create_hierarchy(ICBHierarchy)
    elif name == 'BICS':
        is_created = create_hierarchy(BICSHierarchy)
    elif name == 'GICS':
        is_created = create_hierarchy(GICSHierarchy)
    return is_created
    
    
if __name__ == "FDLCreateHierarchy":
    dl_create_hierarchy('BICS')
    dl_create_hierarchy('ICB')
    dl_create_hierarchy('GICS')    

