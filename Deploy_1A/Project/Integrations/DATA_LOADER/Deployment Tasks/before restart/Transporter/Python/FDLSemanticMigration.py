"""
PRICE SEMANTIC MIGRATION SCRIPT

DESCRIPTION:
      This script migrates Price Semantics from FXSLtemplates
      to price_semantic and price_semantic_row tables in ADM.

"""

import string
import xml.etree.ElementTree
import acm
import FPriceSemantic
import FPriceLinkApplication
import FUxCore
import FLogger

import FDLADSOperations
import FDLFileOperations
import FDLConfigSingleton
config_variables_obj = FDLConfigSingleton.FDLConfigSingleton()
config = config_variables_obj.config_data()

file_ops_obj = FDLFileOperations.FDLFileHandlingOps(config_variables_obj)
logger = FLogger.FLogger('FDLSemanticMigration')

def execute_script(parameter):
    provider_type = parameter['providerType']
    from_fxsltemplate = parameter['fromFXSLTemplate']
    semantic_names = parameter['semantic']
    config['PROVIDER_ex'] = provider_type
    if provider_type == 'None':
        print('Invalid Distributor Type: None')
    else:
        result = 0
        print('Distributor Type set to: ' + str(provider_type))
    if str(from_fxsltemplate) == '1':
        for semantic in semantic_names:
            create_semantic_from_template(semantic, provider_type)

def create_semantic_from_template(semantic, provider):
    semantic_mapping_dict = file_ops_obj.get_price_semantic_fields_from_FXSLTemplate(semantic, provider=provider)
    if semantic_mapping_dict:
        parse_semantic_FXSLTemplate(provider, semantic, semantic_mapping_dict)
        logger.debug("Successfully parsed FXSLTemplate and inserted semantics in database.")
    else:
        logger.error('Unable to get %s semantic data from FXSLTemplate'%semantic)

def parse_semantic_FXSLTemplate(provider_type, semantic_name, semantics_dict):
    result = 1
    priceSemantic = acm.FPriceSemantic.Select01('name="%s"' % semantic_name, None)
    if not priceSemantic:
        try:
            priceSemantic = acm.FPriceSemantic()
            priceSemantic.Name(semantic_name)
            priceSemantic.ProviderType(provider_type)
            priceSemantic.Commit()
        except Exception as e:
            logger.error(str(e) + ': Error migrating semantic: ' + semantic_name)
            result = 0
    else:
         logger.info('Semantic ' + semantic_name + ' already exists. Migrating mappings')

    for smc in semantics_dict:
        adm_field = smc
        IdpField = semantics_dict[smc]
        priceSemantic = acm.FPriceSemantic.Select01('name="%s"' % semantic_name, None)
        if IdpField and priceSemantic:
            price_semantic_row = acm.FPriceSemanticRow.Select("semanticSeqNbr=%s"%semantic_name)
            if price_semantic_row:
                row_adm_fields = []
                for i in price_semantic_row:
                    row_adm_fields.append(i.AdmName())
                if adm_field in row_adm_fields:
                    for i in price_semantic_row:
                        if i.AdmName() == adm_field:
                            res = update_semantic_row(adm_field, IdpField, '', priceSemantic, i)
                            if not res:
                                continue
                else:
                    res = create_new_semantic_row(adm_field, IdpField, '', priceSemantic)
                    if not res:
                        continue
            else:
                res = create_new_semantic_row(adm_field, IdpField, '', priceSemantic)

    return result


def create_new_semantic_row(adm_field, idp_field, comment, price_semantic):
    result = 1
    try:
        price_semantic_row = acm.FPriceSemanticRow()
        price_semantic_row.AdmName(adm_field)
        price_semantic_row.IdpName(idp_field)
        if comment:
            price_semantic_row.Comment(comment)
        price_semantic_row.SemanticSeqNbr(price_semantic.Oid())
        price_semantic_row.Commit()

    except Exception as e:
        print(str(e) + ': Error migrating semantic: ' + price_semantic.Name() + ' and mapping: ' + adm_field + '-' + idp_field)
        result = 0
    return result


def update_semantic_row(adm_field, idp_field, comment, price_semantic, price_semantic_row):
    result = 1
    try:
        price_semantic_row_clone = price_semantic_row.Clone()
        price_semantic_row_clone.IdpName(idp_field)
        if comment:
            price_semantic_row_clone.Comment(comment)
        price_semantic_row.Apply(price_semantic_row_clone)
        price_semantic_row.Commit()
    except Exception as e:
        print(str(e) + ': Error migrating semantic: ' + price_semantic.Name() + ' and mapping: ' + adm_field + '-' + idp_field)
        result = 0
    return result

#----------------------------------GUI Fuctions---------------------------------------------

PermittedDistributorTypes = ["Refinitiv", "Bloomberg", "MarketMap"]
providerType = ''

def get_distributor_type():
    provider_type_list = []
    acm_version = acm.Version().split(',')[0][:6]
    for provider in acm.FEnumeration['enum(PrincipalType)'].Enumerators().Sort():
        if provider =='Reuters' and str(acm_version) < '2021.2':
            provider = 'Refinitiv'
        if provider in PermittedDistributorTypes:
            provider_type_list.append(provider)
    return provider_type_list

def enable_disable_from_FXSLTemplate_fields(index, fieldValues):
    if str(fieldValues[index]) == '1':
        ael_variables[index+1][9] = 1
        provider = str(fieldValues[index-1])
        semantic_val_list = file_ops_obj.semantics_from_xml_lookup(provider=provider)
        ael_variables[index+1][3] = semantic_val_list
    else:
        ael_variables[index+1][9] = 0
    return fieldValues

def on_provider_change(index, fieldValues):
    provider = fieldValues[index]
    semantic_val_list = file_ops_obj.semantics_from_xml_lookup(provider=provider)
    ael_variables[index+2][3] = semantic_val_list
    config['PROVIDER_ex'] = provider

    return fieldValues

def enable_price_semantics(index, fieldValues):
    provider = str(fieldValues[index-2])
    semantic_val_list = file_ops_obj.semantics_from_xml_lookup(provider=provider)
    return fieldValues


#---------------AEL VARIABLES------------------------------------------------------------

ael_gui_parameters = {  'runButtonLabel'        : '&&Ok',
                        'InsertItemsShowExpired': True,
                        'hideExtraControls'     : False,
                        'closeWhenFinished'     : False,
                        'windowCaption'         : 'Select Semantic file and Provider Type for migration.'}
ael_variables = [
                ['providerType', 'Distributor Type', 'string', get_distributor_type(), 'Bloomberg', 1, 0, \
                            'Select a distributor type appropriate to the semantic file', on_provider_change],

                ['fromFXSLTemplate','From FXSLTemplate','int',[1,0],0, 0, 0, None, enable_disable_from_FXSLTemplate_fields, 1],
                ['semantic', 'Semantic', 'string', [], '', 0, 1, 'Enter the names of semantic to import in database',None, 1],

                ]


def ael_main(parameter):
    if parameter:
        try:
            execute_script(parameter)
        except Exception as e:
            print(e)





