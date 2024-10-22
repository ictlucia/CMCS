import acm

import PsRvm_AccountingMmldColumn
reload(PsRvm_AccountingMmldColumn)

import PsRvm_CemEad_Custom
reload(PsRvm_CemEad_Custom)

import PsRvm_MmldAccountingUtils
reload(PsRvm_MmldAccountingUtils)

instrument = acm.FInstrument['PsRvm_MmldFx_20230924_2']
#print(PsRvm_AccountingMmldColumn.calculateMmldDailyAccrual(instrument))
print(PsRvm_CemEad_Custom.calculateMmldMaxTotalReturnFullPremium(instrument))


mmldOption = acm.FOption['PsRvm_MmldFx_20230924_2']
print(PsRvm_MmldAccountingUtils.buildMmldPeriodCalDates(mmldOption))
