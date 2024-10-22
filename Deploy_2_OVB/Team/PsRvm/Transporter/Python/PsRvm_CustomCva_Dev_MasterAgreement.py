import Ps_CustomCva
reload(Ps_CustomCva)

import acm

print('loaded Ps_CustomCva_MasterAreement')


calcSpace = acm.FCalculationSpaceCollection().GetSpace('FPortfolioSheet', acm.GetDefaultContext())
counterpartyQF = acm.FStoredASQLQuery['PsRvm_CvaTrades_Counterparty1']
calcSpace.InsertItem(counterpartyQF)

val1 = calcSpace.CalculateValue(counterpartyQF,'CVA Supervisory Discount Factor DF')
print(val1)

val2 = calcSpace.CalculateValue(counterpartyQF,'CVA EAD')
print(val2)


query = acm.CreateFASQLQuery(acm.FTrade, 'AND')  # empty query
op = query.AddOpNode('OR')
op.AddAttrNode('Trade.Oid', 'EQUAL', 124)
val3 = calcSpace.CalculateValue(query,'Portfolio Position')
print(val3)

qf = acm.FStoredASQLQuery['PsRvm_CvaNsQueryFolder']
print("-00--")
#print(qf)
val = calcSpace.CalculateValue(qf,'Portfolio Position')
print(val)

qfQuery = qf.Query()
print(qfQuery)
qfQueryAsqlNodes = qfQuery.AsqlNodes()
qfQueryAsqlNodesOrOpNode = qfQuery.AsqlNodes()[0]
print("-0--")
val = calcSpace.CalculateValue(qfQuery,'Portfolio Position')
print(val)
print(qfQueryAsqlNodes)



op = qfQueryAsqlNodesOrOpNode.AddOpNode('AND')
op.AddAttrNode('Oid', 'GREATER_EQUAL', 65)
op.AddAttrNode('Oid', 'LESS_EQUAL', 65)
#op.Commit()

print("-0.1--")
print(qfQuery)
val = calcSpace.CalculateValue(qfQuery,'Portfolio Position')
print(val)



print("-1--")
print(qfQuery.AsqlNodes())
print(qfQuery.AsqlNodes()[0])
print(qfQuery.AsqlNodes()[0].AsqlNodes()[0])
print(qfQuery.AsqlNodes()[0].AsqlNodes()[1])
print(qfQuery.AsqlNodes()[0].AsqlNodes()[2])

