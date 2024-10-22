import ael

COST_AS_PREMIUM = ael.enum_from_string('FeeAllocMethod', 'In Cost As Premium')
EXCLUDED = ael.enum_from_string('FeeAllocMethod', 'None')
FEE_TRADE_DAY = ael.enum_from_string('FeeAllocMethod', 'As Fee On Trade Day')
FEE_LINEAR = ael.enum_from_string('FeeAllocMethod', 'As Fee Depr Linear')

def fee_alloc_method_from_payment_type(type):
    if type == 'Attributable Fee':
        return COST_AS_PREMIUM
    elif type == 'Modification PV Fee':
       return COST_AS_PREMIUM    
    elif type == 'Non-Attributable Fee (Linear)':
        return FEE_LINEAR
    elif type == 'Non-Attributable Fee (As Fee)':
        return FEE_TRADE_DAY
    return EXCLUDED
