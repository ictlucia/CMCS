"""-------------------------------------------------------------------
MODULE
    FDLBBGConfig - DataPrep script

DESCRIPTION
    Data preparration script to create deafult entities in database

--------------------------------------------------------------------"""

import acm
import FIntegrationUtils
utils_obj = FIntegrationUtils.FIntegrationUtils()
import FLogger
logger = FLogger.FLogger("DL_DataPrep")

instrument_additional_info_specs = [{
                                    'FieldName':'DATA_PROVIDER',
                                      'Description':'Name of data source from where the data is uploaded',
                                      'Default':'',
                                      'TypeGroup':'Standard',
                                      'Type':'String',
                                      'Table':'Instrument',
                                    },
                                    {
                                  'FieldName':'UnderlyingID',
                                  'Description':'SecurityID for underlying instrument',
                                  'Default':'',
                                  'TypeGroup':'Standard',
                                  'Type':'String',
                                  'Table':'Instrument',
                                    },
                                {
                                  'FieldName':'BBG_INDUSTRY_GROUP',
                                  'Description':'Bloomberg data for IndustryGroup',
                                  'Default':'',
                                  'TypeGroup':'Standard',
                                  'Type':'String',
                                  'Table':'Instrument',
                                },
                                {
                                  'FieldName':'BBG_INDUSTRY_SECT',
                                  'Description':'Bloomberg data for IndustrySector',
                                  'Default':'',
                                  'TypeGroup':'Standard',
                                  'Type':'String',
                                  'Table':'Instrument',
                                  },
                                  {
                                  'FieldName':'BBG_INDUSTRY_SUBGRP',
                                  'Description':'Bloomberg data for Industry sub group',
                                  'Default':'',
                                  'TypeGroup':'Standard',
                                  'Type':'String',
                                  'Table':'Instrument',
                                  },

                                  {
                                  'FieldName':'SimilarIsin',
                                  'Description':'SimilarIsin data value',
                                  'Default':'',
                                  'TypeGroup':'Standard',
                                  'Type':'String',
                                  'Table':'Instrument',
                                  },
                                  {
                                  'FieldName':'SPREAD_TYPE',
                                  'Description':'Benchmark YieldCurve data',
                                  'Default':'',
                                  'TypeGroup':'Standard',
                                  'Type':'String',
                                  'Table':'Instrument',
                                  },
                                  {
                                  'FieldName':'BENCHMARK_SPREAD',
                                  'Description':'Benchmark YieldCurve data',
                                  'Default':'',
                                  'TypeGroup':'Standard',
                                  'Type':'String',
                                  'Table':'Instrument',
                                  },
                                  {
                                  'FieldName':'EQY_WEIGHTED_AVG_PX',
                                  'Description':'VWAP (Vol Weighted Average Price)',
                                  'Default':'',
                                  'TypeGroup':'Standard',
                                  'Type':'Double',
                                  'Table':'Instrument',
                                  },
                                  {
                                  'FieldName':'EQY_SH_OUT',
                                  'Description':'Current Shares Outstanding',
                                  'Default':'',
                                  'TypeGroup':'Standard',
                                  'Type':'Double',
                                  'Table':'Instrument',
                                  },
                                  {
                                  'FieldName':'CUR_MKT_CAP',
                                  'Description':'Current Market Cap',
                                  'Default':'',
                                  'TypeGroup':'Standard',
                                  'Type':'Double',
                                  'Table':'Instrument',
                                  },
                                  {
                                  'FieldName':'CALC_TYP_DES',
                                  'Description':'Calculation Type Description',
                                  'Default':'',
                                  'TypeGroup':'Standard',
                                  'Type':'String',
                                  'Table':'Instrument',
                                  },
                                  {
                                  'FieldName':'CURVE_ID',
                                  'Description':'Curve Identifier',
                                  'Default':'',
                                  'TypeGroup':'Standard',
                                  'Type':'String',
                                  'Table':'Instrument',
                                  }
                                ]
party_additional_info_specs = [{
                                'FieldName':'BBG_COMPANY',
                                  'Description':'Bloomberg CompanyID',
                                  'Default':'',
                                  'TypeGroup':'Standard',
                                  'Type':'String',
                                  'Table':'Party',
                                },
                                {
                                'FieldName':'BBG_ISSUER',
                                  'Description':'Bloomberg Issuer Name',
                                  'Default':'',
                                  'TypeGroup':'Standard',
                                  'Type':'String',
                                  'Table':'Party',
                                }
                                ]
yield_curve_additional_info_specs = [{
                                'FieldName':'BB_TICKER_CURVE',
                                  'Description':'Bloomberg Yieldurve BB_TICKER',
                                  'Default':'',
                                  'TypeGroup':'Standard',
                                  'Type':'String',
                                  'Table':'YieldCurve',
                                }
                                ]
volatility_surface_additional_info_specs =[ {'FieldName':'Ref_Instrument',
                                  'Description':'Refrence instrument',
                                  'Default':'',
                                  'TypeGroup':'RecordRef',
                                  'Type':'Instrument',
                                  'Table':'Volatility',
                                    }
                                  ]

trade_additional_info_specs =[ {'FieldName':'RequestedInstrID',
                                  'Description':'Refrence to instrument security id',
                                  'Default':'',
                                  'TypeGroup':'RecordRef',
                                  'Type':'Instrument',
                                  'Table':'Trade',
                                    }
                                  ]

instrument_alias_type = [{
                        'FieldName':'BB_TICKER',
                          'Description':'Bloomberg TICKER',
                          'Table':'Instrument',
                        },
                        {
                        'FieldName':'BB_UNIQUE',
                          'Description':'Bloomberg Unique ID',
                          'Table':'Instrument',
                        },
                        {
                        'FieldName':'CUSIP',
                          'Description':'CUSIP',
                          'Table':'Instrument',
                        },
                        {
                        'FieldName':'CUSIP_8_CHR',
                          'Description':'CUSIP 8 Character',
                          'Table':'Instrument',
                        },
                        {
                        'FieldName':'FIGI',
                          'Description':'Bloomberg FIGI Code',
                          'Table':'Instrument',
                        },
                        {
                        'FieldName':'SEDOL',
                          'Description':'SEDOL',
                          'Table':'Instrument',
                        },
                         {
                        'FieldName':'WKN',
                          'Description':'Wertpapier Number',
                          'Table':'Instrument',
                        },
                         {
                        'FieldName':'VALOREN',
                          'Description':'Bloomberg TICKER',
                          'Table':'Instrument',
                        }]
party_alias_type = [    {
                        'FieldName':'BB_COMPANY_ID',
                        'Description':'Bloomberg Company ID',
                        'Table':'Party',
                        },
                        {
                        'FieldName':'BB_GLOBAL_COMPANY_ID',
                        'Description':'Bloomberg global Company ID',
                        'Table':'Party',
                        }
                                        
                    ]

default_instrument_types = ['DUMMY_UNDERLYING', 'Swap', 'DepositaryReceipt', 'Stock', 'Future', 'RateIndex', 'FreedefCashflow', 'MbsAbs',
                           'Bill', 'Option', 'ETF', 'Bond', 'Warrant', 'CFD', 'FRN', 'CommodityIndex', 'EquityIndex',
                           'Curr', 'IndexLinkedBond', 'future/forward', 'Deposit', 'Fund']

default_vola_types = ['Equity', 'Commodity', 'FX']

mandatory_fparameter_dict = {'BBG_INSTRUMENT_ADDITIONAL_INFO_ex' : dict,
                              'BBG_ISSUER_ADDITIONAL_INFO_ex' : dict,
                              'BBG_XSL_FILE_PATH' : 'file_path',
                              'BBG_DATA_FILE_PATH_ex' : 'file_path',                              
                              'BBG_REQUEST_FIELDS_LIST_FILE' : 'request_fields.txt',
                              'BBG_INSTRUMENT_RATINGS_ex' : dict,
                              'BBG_ISSUER_RATINGS_ex' : dict,
                              'MESSAGE_BROKER_ex' : str,
                              'MESSAGE_GROUP' : str,
                              'DATALOADER_SOURCE_ex' : str,
                              'DATALOADER_REQUEST_SOURCE' : str,
                              'NOTIFICATION_MEDIA_ex' : ['MAIL', 'MESSAGE', 'PRIME_LOG', 'PRIME_LOG_TRANSIENT', 'OFF'],
                              'NOTIFY_LEVEL_ex': ['DEBUG', 'TRACK', 'SUCCESS', 'WARNING', 'ERROR'],
                              'BBG_CREATE_MISSING_RATINGS_ex' : bool,
                              'BBG_INCOMPLETE_FLAG_ex' : bool,
                              'BBG_LOAD_UNDERLYING_FR_FILE_ex' : bool,
                              'BBG_MAP_SIMILAR_ISIN_ex' : bool,
                              'BBG_POPUP_INSTRUMENT_AFTER_UPLOAD' : ['Insert', 'ALL'],
                              'BBG_PRICE_LINK_ACTIVE_ex' : bool,
                              'BBG_TheorValidationUsed' : bool,
                              }


def set_instrument_additional_info_specs():
    """ Set instrument additional info specs """
    for addinfo in instrument_additional_info_specs:
        try:
            utils_obj.create_additional_info_spec(addinfo)
        except FIntegrationUtils.AddInfoSpecAlreadyExits as e:
            logger.LOG(str(e))
        except Exception as e:
            logger.ELOG("Exception in set_instrument_additional_info_specs : %s"%str(e))

def set_party_additional_info_specs():
    """ Set party adiitonal info specs """
    for addinfo in party_additional_info_specs:
        try:
            utils_obj.create_additional_info_spec(addinfo)
        except FIntegrationUtils.AddInfoSpecAlreadyExits as e:
            logger.LOG(str(e))
        except Exception as e:
            logger.ELOG("Exception in set_party_additional_info_specs : %s"%str(e))

def set_yield_curve_additional_info_specs():
    """ Set yield curve adiitonal info specs """
    for addinfo in yield_curve_additional_info_specs:
        try:
            utils_obj.create_additional_info_spec(addinfo)
        except FIntegrationUtils.AddInfoSpecAlreadyExits as e:
            logger.LOG(str(e))
        except Exception as e:
            logger.ELOG("Exception in set_yield_curve_additional_info_specs : %s"%str(e))

def set_vola_surface_additional_info_specs():
    """ Set volatility surface adiitonal info specs """
    for addinfo in volatility_surface_additional_info_specs:
        try:
            utils_obj.create_additional_info_spec(addinfo)
        except FIntegrationUtils.AddInfoSpecAlreadyExits as e:
            logger.LOG(str(e))
        except Exception as e:
            logger.ELOG("Exception in set_vola_surface_additional_info_specs : %s"%str(e))

def set_trade_additional_info_specs():
    """ Set trade adiitonal info specs """
    for addinfo in trade_additional_info_specs:
        try:
            utils_obj.create_additional_info_spec(addinfo)
        except FIntegrationUtils.AddInfoSpecAlreadyExits as e:
            logger.LOG(str(e))
        except Exception as e:
            logger.ELOG("Exception in set_trade_additional_info_specs : %s"%str(e))

def set_instrument_alias_type():
    """ Set instrument alias type """
    for alias in instrument_alias_type:
        try:
            utils_obj.create_alias_type(alias.get('Table'), alias.get('Description'), alias.get('FieldName'), alias.get('FieldName'))
        except FIntegrationUtils.AliasTypeAlreadyExist as e: 
            logger.LOG(str(e))
        except Exception as e:
            logger.ELOG("Exception in set_instrument_alias_type : %s"%str(e))

def set_party_alias_type():
    """ Set party alias type """
    for alias in party_alias_type:
        try:
            utils_obj.create_alias_type(alias.get('Table'), alias.get('Description'), alias.get('FieldName'), alias.get('FieldName'))
        except FIntegrationUtils.AliasTypeAlreadyExist as e: 
            logger.LOG(str(e))
        except Exception as e:
            logger.ELOG("Exception in set_party_alias_type : %s"%str(e))

def create_information_queries_trade():
    """ Cretae information queries for external objects on trades"""
    try:
        s_query = acm.FSQL['DataLoader_ExternalObjects_Trade']
        if not s_query:
            s_query = acm.FSQL('')
            s_query.Name = 'DataLoader_ExternalObjects_Trade'
            s_query.Text = """
    /* Select external objects and display the missing security id and id type */
    select
    seqnbr,
    external_ref,
    creat_time,
    updat_time,
    integration_subtype,
    integration_type,
    ael_s(,'FDLProfile.get_sec_idtype_from_external_obj', seqnbr) 'Security IDType',
    ael_s(,'FDLProfile.get_sec_id_from_external_obj', seqnbr) 'Security ID'

    from
    ExternalObject

    where
    integration_subtype = 'Trade'
    and integration_type = 'DL_Complementor'"""
            s_query.Commit()
    except Exception as e:
        logger.ELOG("Exception in create_information_queries_trade : %s"%str(e))

def create_information_queries_instrument():
    """ Cretae information queries for external objects on instrument """
    try:
        s_query = acm.FSQL['DataLoader_ExternalObjects_Instrument']
        if not s_query:
            s_query = acm.FSQL('')
            s_query.Name = 'DataLoader_ExternalObjects_Instrument'
            s_query.Text = """
    /* Select external objects and display the missing security id and id type */
    select
    seqnbr,
    external_ref,
    creat_time,
    updat_time,
    integration_subtype,
    integration_type,
    ael_s(,'DL_Query.get_sec_idtype_from_external_obj', seqnbr) 'Security IDType',
    ael_s(,'DL_Query.get_sec_id_from_external_obj', seqnbr) 'Security ID'

    from
    ExternalObject

    where
    integration_subtype = 'Instrument'
    and integration_type = 'DL_Complementor'"""
            s_query.Commit()
    except Exception as e:
        logger.ELOG("Exception in create_information_queries_instrument : %s"%str(e))

def create_information_queries():
    """ Cretae information queries for external objects """
    create_information_queries_trade()
    create_information_queries_instrument()


def create_benchmark_precedence_query():
    NonGenFutFwd = 'NonGenFutFwd'
    query_obj = acm.FStoredASQLQuery[NonGenFutFwd]
    if not query_obj:
        query = acm.CreateFASQLQuery(acm.FInstrument, 'AND')
        node = query.AddOpNode('AND')
        node.AddAttrNode('InsType', 'EQUAL', 'Future/Forward')
        node = query.AddOpNode('AND')
        node.AddAttrNode('Generic', 'EQUAL', False)
        storedQuery = acm.FStoredASQLQuery()
        storedQuery.Query(query)
        storedQuery.Name(NonGenFutFwd)
        storedQuery.Commit()
        logger.LOG("Created benchmark precedence query '%s'" % (NonGenFutFwd))
    else:
        logger.LOG("Benchmark precedence query '%s' is already present" % (NonGenFutFwd))

    FXSwapFixedEndDay = 'FXSwapFixedEndDay'
    query_obj = acm.FStoredASQLQuery[FXSwapFixedEndDay]
    if not query_obj:
        query = acm.CreateFASQLQuery(acm.FInstrument, 'AND')
        node = query.AddOpNode('AND')
        node.AddAttrNode('InsType', 'EQUAL', 'FxSwap')
        node = query.AddOpNode('AND')
        node.AddAttrNode('Generic', 'EQUAL', False)
        node = query.AddOpNode('AND')
        node.AddAttrNode('FixedEndDay', 'EQUAL', True)
        storedQuery = acm.FStoredASQLQuery()
        storedQuery.Query(query)
        storedQuery.Name(FXSwapFixedEndDay)
        storedQuery.Commit()
        logger.LOG("Created benchmark precedence query '%s'" % (FXSwapFixedEndDay))
    else:
        logger.LOG("Benchmark precedence query '%s' is already present" % (FXSwapFixedEndDay))

    NonGenFutFwdFRA_IMM = 'NonGenFutFwdFRA_IMM'
    query_obj = acm.FStoredASQLQuery[NonGenFutFwdFRA_IMM]
    if not query_obj:
        query = acm.CreateFASQLQuery(acm.FInstrument, 'AND')
        node = query.AddOpNode('AND')
        node.AddAttrNode('InsType', 'EQUAL', 'Future/Forward')
        node = query.AddOpNode('AND')
        node.AddAttrNode('UnderlyingType', 'EQUAL', 'FRA')
        node = query.AddOpNode('AND')
        node.AddAttrNode('Generic', 'EQUAL', False)
        storedQuery = acm.FStoredASQLQuery()
        storedQuery.Query(query)
        storedQuery.Name(NonGenFutFwdFRA_IMM)
        storedQuery.Commit()
        logger.LOG("Created benchmark precedence query '%s'" % (NonGenFutFwdFRA_IMM))
    else:
        logger.LOG("Benchmark precedence query '%s' is already present" % (NonGenFutFwdFRA_IMM))

    NonGenFUTCshFlow = 'NonGenFUTCshFlow'
    query_obj = acm.FStoredASQLQuery[NonGenFUTCshFlow]
    if not query_obj:
        query = acm.CreateFASQLQuery(acm.FInstrument, 'AND')
        node = query.AddOpNode('AND')
        node.AddAttrNode('InsType', 'EQUAL', 'Cash Flow Future')
        node = query.AddOpNode('AND')
        node.AddAttrNode('Generic', 'EQUAL', False)
        storedQuery = acm.FStoredASQLQuery()
        storedQuery.Query(query)
        storedQuery.Name(NonGenFUTCshFlow)
        storedQuery.Commit()
        logger.LOG("Created benchmark precedence query '%s'" % (NonGenFUTCshFlow))
    else:
        logger.LOG("Benchmark precedence query '%s' is already present" % (NonGenFUTCshFlow))

def ael_main(parameter):
    logger.LOG('**** Creating Instrument Additional Info specifications ****')
    set_instrument_additional_info_specs()
    logger.LOG('**** Creating Party Additional Info specifications ****')
    set_party_additional_info_specs()
    logger.LOG('**** Creating Yield Curve Additional Info specifications ****')
    set_yield_curve_additional_info_specs()
    logger.LOG('**** Creating Volatility Surface Additional Info specifications ****')
    set_vola_surface_additional_info_specs()
    logger.LOG('**** Creating Trade Additional Info specifications ****')
    set_trade_additional_info_specs()
    logger.LOG('**** Creating Instrument AliasType specifications ****')
    set_instrument_alias_type()
    logger.LOG('**** Creating Party AliasType specifications ****')
    set_party_alias_type()
    logger.LOG('**** Creating Information manager SQL queries ****')
    create_information_queries()
    logger.LOG('**** Creating Precedence queries ****')
    create_benchmark_precedence_query()

    logger.LOG('**** Done ****')



