import acm
'''
module description:
    1. update a stored FStoredTimeBuckets to generate daily time buckets up to a certain date and yearly 
    time buckets after this. The end date is determined by the maximum end date of trades selected in queries
footprint: 
    [20240810] Nencho Georgiev
'''

def CreateStoredTimeBuckets(name, datePeriods):
    storedTimeBuckets = acm.FStoredTimeBuckets.Select01('name="' + name + '" user = 0', '')
    if not storedTimeBuckets:
        buckets = []
        for datePeriod in datePeriods:
            bucket = acm.FDatePeriodTimeBucketDefinition()
            bucket.DatePeriod = datePeriod
            if datePeriod.endswith('Y'):
                bucket.Name = datePeriod
            else:
                bucket.DateAsName(True)
            bucket.Adjust = False
            bucket.RelativeSpot = False
            buckets.append(bucket)
        buckets.append(acm.FRestTimeBucketDefinition())
        
        config = acm.TimeBuckets.CreateTimeBucketsConfiguration(None, 0, 0)
        definition = acm.TimeBuckets.CreateTimeBucketsDefinition(0, buckets, False, False, False, False, False)
        defAndConfig = acm.TimeBuckets.CreateTimeBucketsDefinitionAndConfiguration(definition, config)
        timeBuckets = acm.TimeBuckets.CreateTimeBuckets(defAndConfig)
        
        storedTimeBuckets = acm.FStoredTimeBuckets()
        storedTimeBuckets.TimeBuckets = timeBuckets
        storedTimeBuckets.Name = name
        storedTimeBuckets.AutoUser = False
        storedTimeBuckets.User = None
        storedTimeBuckets.Commit()
    return storedTimeBuckets

def UpdateTimeBuckets(name, datePeriods):
    storedTimeBuckets = acm.FStoredTimeBuckets.Select01('name="' + name + '" user = 0', '')
    if storedTimeBuckets:
        print("Updating")
        buckets = []
        for datePeriod in datePeriods:
            bucket = acm.FDatePeriodTimeBucketDefinition()
            bucket.DatePeriod = datePeriod
            #bucket.Name = datePeriod
            bucket.DateAsName(True)
            bucket.Adjust = False
            bucket.RelativeSpot = False
            buckets.append(bucket)
        
        config = acm.TimeBuckets.CreateTimeBucketsConfiguration(None, 0, 0)
        definition = acm.TimeBuckets.CreateTimeBucketsDefinition(0, buckets, False, False, False, False, False)
        defAndConfig = acm.TimeBuckets.CreateTimeBucketsDefinitionAndConfiguration(definition, config)
        timeBuckets = acm.TimeBuckets.CreateTimeBuckets(defAndConfig)
        
        storedTimeBuckets.TimeBuckets = timeBuckets
        storedTimeBuckets.Commit()
    return storedTimeBuckets
 
def getMaxMaturityDate(storedQueries, minMaturity):
    today = acm.Time.DateToday()
    maxMaturity = minMaturity

    for storedSqlFolder in storedQueries:
        if storedSqlFolder is not None:
            for trade in storedSqlFolder.Query().Select():
                tradeInsExpiryDate = trade.Instrument().ExpiryDate()
                if acm.Time.DateDifference(tradeInsExpiryDate,maxMaturity) > 0 : maxMaturity = tradeInsExpiryDate
                #print('maxMaturity = ',maxMaturity)
    
    return maxMaturity
 
def get_all_timebuckets():
    all_timebuckets_name = []
    all_timebuckets = acm.FStoredTimeBuckets.Select('')
    for each_timebucket in all_timebuckets:
        all_timebuckets_name.append(each_timebucket.Name())
    return sorted(all_timebuckets_name)

def getBucketPeriods(startDate, endDateDaily, endDate):
    bucketPeriods = []
    
    numDaysDifferenceStartAndEndDaily = acm.Time.DateDifference(endDateDaily, startDate) + 1
    for n in range(1, numDaysDifferenceStartAndEndDaily):
        per = "{}D".format(n)
        bucketPeriods.append(per)
    
    numYearsDaily = numDaysDifferenceStartAndEndDaily // 365 + 1
    
    numDaysDifferenceDailyVsMax = acm.Time.DateDifference(endDate, endDateDaily)
    if numDaysDifferenceDailyVsMax > 0:    
        numYearsDifferenceEndDailyEnd = acm.Time.DateDifference(endDate, startDate) // 365 + 2
        
        for n in range(numYearsDaily, numYearsDifferenceEndDailyEnd):
            per = "{}Y".format(n)
            bucketPeriods.append(per)
    return bucketPeriods
    
ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'LIQ18_UpdateTimeStoredTimeBuckets'}
 
ael_variables=[
['time_bucket_name','Time Bucket Name','string',  get_all_timebuckets(),None, 1,0],
['daily_buckets','Daily buckets','int',  None, None, 1,0],
['queries','Queries', acm.FStoredASQLQuery,  [], None, 1, 1]
]
 
def ael_main(parameter):
    storedTimeBucketsName = parameter['time_bucket_name']
    queries = parameter['queries']
    switchToYearly = parameter['daily_buckets']

    startDate = acm.Time.DateToday()    
    endDateDaily = acm.Time.DateAddDelta(startDate, 0, 0, switchToYearly)
    maxEndDate = getMaxMaturityDate(queries, endDateDaily)
    print("Creating time buckets until {}".format(maxEndDate))
        
    datePeriods = getBucketPeriods(startDate, endDateDaily, maxEndDate)
    #UpdateTimeBuckets(storedTimeBucketsName, datePeriods)
    
    storedTimeBuckets = acm.FStoredTimeBuckets.Select01('name="' + storedTimeBucketsName + '" user = 0', '')
    if storedTimeBuckets:
        storedTimeBuckets.Delete()
    
    CreateStoredTimeBuckets(storedTimeBucketsName, datePeriods)
