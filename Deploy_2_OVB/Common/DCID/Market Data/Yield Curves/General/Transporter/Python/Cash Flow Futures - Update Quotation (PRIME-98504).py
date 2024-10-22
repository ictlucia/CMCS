import acm

ael_variables = []

def Setup():
    cff = acm.FCashFlowFuture.Select('')
    for i in cff:
        i.Quotation('100-rate')
        i.UnderlyingType('RateIndex')
        i.Commit()

def ael_main(params):
    Setup()
