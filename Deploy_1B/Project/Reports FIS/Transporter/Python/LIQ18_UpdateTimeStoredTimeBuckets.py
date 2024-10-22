import acm
'''
module description:
    1. update a stored FStoredTimeBuckets to generate TImeBuckets containing a TimeBucket for every date
        between today and maximum matuirty across all trades within LIQ18/LIQ19 report
    
footprint: 
    [20240723] richard.milford@fisglobal.com
'''

def getMaxMaturityDate():
    liq18StoredQueries = ['LIQ18_MM - Interbank Placement',
                        'LIQ18_MM - Interbank Taken',
                        'LIQ18_FX FW',
                        'LIQ18_FX Swap',
                        'LIQ18_Term Deposit',
                        'LIQ18_Repo BI',
                        'LIQ18_Rev Repo BI',
                        'LIQ18_Repo Interbank',
                        'LIQ18_Rev Repo Interbank',
                        'LIQ18_Surat Berharga Dimiliki',
                        'LIQ18_Surat Berharga Terbit',
                        'LIQ18_Cross Currency Swap',
                        'LIQ18_Interest Rate Swap',
                        'LIQ18_SBBI Valas'
                        ]

    today = acm.Time.DateToday()
    maxMaturity = today

    for queryName in liq18StoredQueries:
        storedSqlFolder = acm.FStoredASQLQuery[queryName]
        if storedSqlFolder is not None:
            for trade in storedSqlFolder.Query().Select():
                tradeInsExpiryDate = trade.Instrument().ExpiryDate()
                if acm.Time.DateDifference(tradeInsExpiryDate,maxMaturity) > 0 : maxMaturity = tradeInsExpiryDate
                #print('maxMaturity = ',maxMaturity)
    
    return maxMaturity


def createTimeBucketsDefinition(n):
    # startDate = '0000-01-01', endDate = '9999-12-12'):
    today = acm.Time.DateToday()
    definition = acm.FDatePeriodTimeBucketDefinition()
    name = '%sd' % n
    definition.DatePeriod(name)
    definition.Name(acm.Time.DateAddDelta(today, 0, 0, n))
    definition.Adjust(False)
    definition.RelativeSpot(False)
    return definition
    
    
def updateStoredTimeBuckets(_storedTimeBucketsName):

    startDate = acm.Time.DateToday()
    endDate = getMaxMaturityDate()
    numDaysDifferenceStartAndEnd = acm.Time.DateDifference(endDate, startDate)
    print('updateStoredTimeBuckets => [endDate,numDaysDifferenceStartAndEnd] %s ' %[endDate,numDaysDifferenceStartAndEnd])
    bucketDefinitions = acm.FArray()
    #for n in range(1, numDaysDifferenceStartAndEnd + 10):
    for n in range(1, numDaysDifferenceStartAndEnd + 10):
        defi = createTimeBucketsDefinition(n)
        bucketDefinitions.Add(defi)
        
    bucketDefinitions.Add(acm.FRestTimeBucketDefinition())
    timeBuckets = acm.Time().CreateTimeBucketsFromDefinitions(0,bucketDefinitions, None, 0, 0, 0, 0, 0, 0)

    storedTimeBuckets = acm.FStoredTimeBuckets[_storedTimeBucketsName]
    storedTimeBuckets.TimeBuckets(timeBuckets)
    storedTimeBuckets.Commit()

storedTimeBucketsName = 'LIQ18_StoredTimeBuckets'
updateStoredTimeBuckets(storedTimeBucketsName)
2
