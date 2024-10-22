import acm

import CreditRiskNotional
reload(CreditRiskNotional)

import CreditRiskCustomOverrides
reload(CreditRiskCustomOverrides)

import FRTBCalculationsOverrides
reload(FRTBCalculationsOverrides)

ins = acm.FInstrument['rvm_MMLD_Fx']
print(getattr(ins.AdditionalInfo(),'StructureType')())
print(getattr(ins.AdditionalInfo(),'Sp_LeverageNotional')())

print(ins.AddInfos())


ins2 = acm.FInstrument['PsRvm_Mmld_2']
print(ins2.AddInfos())


ins2 = acm.FInstrument['PsRvm_Mmld_3_EURUSD']
print(ins2)
print(ins2.AddInfos())

print(ins)
print(ins2)

def checkDenominatedValue(value):
    try:
        if not value:
            return False
        if value.Type() and value.Type().Text() == 'InvalidPrice':
            return False
        if str(value.Number()) in INVALID_NUMBERS:
            return False
        if not value.Number() >= 0.0 and not value.Number() < 0.0:
            return False
    except Exception:
        return False
    return True

date = acm.Time().DateToday()
curr1 = acm.FCurrency["EUR"]
curr2 = acm.FCurrency["USD"]

def getFxRate(date, curr1, curr2):
    space = acm.FCalculationMethods().CreateStandardCalculationsSpaceCollection()
    if acm.Time().DateDifference(date, acm.Time().DateToday()) < 0:
        date = acm.Time().DateToday()
    val = curr1.Calculation().FXRate(space, curr2, date).Value()
    print(val.Number())
    if checkDenominatedValue(val):
        rate = val.Number()
        msg = "FX rate for {0}:{1} on {2} is {3:.5f}".format(curr1.Name(),
                curr2.Name(), date, rate)
    else:
        rate = 0.
        msg = "Invalid FX rate found for {0}:{1} on {2}. Returning 0.".format(
                curr1.Name(), curr2.Name(), date)
    return rate

print(getFxRate(date,curr1,curr2))
