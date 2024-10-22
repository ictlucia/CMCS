import acm

def CreateProfileComponent(profile_names):
    comp = acm.FComponent()
    comp.CompName(profile_names)
    comp.Type('Application')
    comp.Commit()

profile_names = ['DepositSwap', 'MarketLinkedDepositDeal', 'MarketLinkedDepositIr', 'MarketLinkedDepositRaFX', 'FxRatioParForward', 'DualCurrencyDeposit', 'FX Option Pricer']

for profile_name in profile_names:
    try:
        CreateProfileComponent(profile_name)
    except Exception as e:
        print(e)
