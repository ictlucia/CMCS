import time
import acm
import FComplianceRulesUtils

trade = acm.FTrade.Select('')[-1]
compliance_rules = acm.FComplianceRule.Select('')

for compliance_rule in compliance_rules:
    interface = FComplianceRulesUtils.GetInterface(compliance_rule)()
    for applied_rule in compliance_rule.AppliedRules():
        before = time.time()
        interface.IsAffectedBy(applied_rule, trade)
        after = time.time()
        print(applied_rule.Name(), end = ": ")
        print(after - before)
