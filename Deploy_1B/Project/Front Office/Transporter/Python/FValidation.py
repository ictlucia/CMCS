import ael, acm
# FValidation files will be checked in the order as in the following list
#VALIDATION_MODULES = ['FValidationTradeWorkflow', 'FValidationPortfolio']
VALIDATION_MODULES = ['FValidationTradeWorkflow',
                        'FValidationWHTPayments',
                        'FValidationAccounting',
                        'FValidationSaveRateOnBOBOConfirmed', 
                        'FValidationPortfolio',
                        'FValidationMidRate',
                        'FValidationLimitPartyTarget',
                        'FValidationBrokerFee',
                        'SSICPTYHook',
                        'FLimitValidation',
                        'FValidationBack2Back',
                        'FValidationMMLDPremium',
                        'FValidationSecuritySettlementInstruction'                     ]

def validate_transaction(transaction_list, *rest):   
    for modname in VALIDATION_MODULES:
        try:
            mod = __import__(modname)
        except ImportError:
            print ('Python module "%s" not found' % modname)
            continue
        if mod:
            transaction_list = mod.validate_transaction(transaction_list)
    return transaction_list
def validate_entity(e, op):
    pass    
