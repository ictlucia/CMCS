import acm

import PsRvm_CemEad_Custom
reload(PsRvm_CemEad_Custom)

ins = acm.FInstrument['PsRvm_MMLD_RAFx_20230817']
print(PsRvm_CemEad_Custom.calculateMmldFullPremium(ins))

print(ins.AdditionalInfo().StructureType())
