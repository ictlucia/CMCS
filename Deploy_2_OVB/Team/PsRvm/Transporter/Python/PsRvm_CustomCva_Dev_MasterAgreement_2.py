import acm
import Ps_CustomCvaUtils
reload(Ps_CustomCvaUtils)

import(Ps_CustomCva)
reload(Ps_CustomCva)

qf = acm.FStoredASQLQuery["PsRvm_CvaNsQueryFolder_byMA"]

calcSpace = acm.FCalculationSpaceCollection().GetSpace('FPortfolioSheet', acm.GetDefaultContext())
val = calcSpace.CalculateValue(qf,'CVA EAD')
print(val)

qfTempNsBasedOnCpyAndMA = Ps_CustomCvaUtils.update_query_folder(qf.Clone(),"Counterparty 1","PsRvm_ISDA_2")

calcSpace = acm.FCalculationSpaceCollection().GetSpace('FPortfolioSheet', acm.GetDefaultContext())
val = calcSpace.CalculateValue(qfTempNsBasedOnCpyAndMA,'CVA EAD')
print(val)

trd = acm.FTrade[120]
print(trd.AgreementLinks()[0].MasterAgreement().Name())
