import acm

from FLogger import FLogger
logger = FLogger(level=2,logToPrime=True,logToConsole=True)
log_levl_dict = {'INFO' : 1, 'DEBUG' : 2, 'WARN' : 3, 'ERROR' : 4}

import CreditRiskNotional
reload(CreditRiskNotional)

import CreditRiskCustomOverrides
reload(CreditRiskCustomOverrides)

instrument = acm.FInstrument['PsRvm_MMLD_FX_20230815']
logger.DLOG(instrument.AddInfos()[0])
