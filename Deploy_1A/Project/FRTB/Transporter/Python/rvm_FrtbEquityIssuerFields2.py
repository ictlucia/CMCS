import acm

def Override_FRTBEquityBucketNumber( instrument ):
    FrtbEquityBucketNumberMappingDict = {
                                        ('Large','Emerging','Sector'):1,
                                        ('Large','Emerging','Sector2'):2,
                                        ('Large','Emerging','Sector3'):3,
                                        ('Large','Emerging','Sector4'):4,
                                        ('Large','Advanced','Sector5'):5,
                                        ('Large','Advanced','Sector6'):6,
                                        ('Large','Advanced','Sector7'):7,
                                        ('Large','Advanced','Sector8'):8,
                                        ('Small','Emerging','Sector1'):9,
                                        ('Small','Emerging','Sector2'):9,
                                        ('Small','Emerging','Sector3'):9,
                                        ('Small','Emerging','Sector4'):9,
                                        ('Small','Advanced','Sector5'):10,
                                        ('Small','Advanced','Sector6'):10,
                                        ('Small','Advanced','Sector7'):10,
                                        ('Small','Advanced','Sector8'):10
                                        }
                                        
    instrumentMappingKeyAsList = []
    insIssuer = instrument.Issuer()  
    
    if hasattr(insIssuer.AdditionalInfo(),'FRTB_Eq_MarketCap'): instrumentMappingKeyAsList.insert(0,getattr(insIssuer.AdditionalInfo(),'FRTB_Eq_MarketCap')())
    if hasattr(insIssuer.AdditionalInfo(),'FRTB_Eq_Economy'): instrumentMappingKeyAsList.insert(1,getattr(insIssuer.AdditionalInfo(),'FRTB_Eq_Economy')())
    if hasattr(insIssuer.AdditionalInfo(),'FRTB_Eq_Sector'): instrumentMappingKeyAsList.insert(2,getattr(insIssuer.AdditionalInfo(),'FRTB_Eq_Sector')()) 
    
    instrumentMappingKeyListAsTuple = tuple(instrumentMappingKeyAsList)
    if not instrumentMappingKeyListAsTuple in FrtbEquityBucketNumberMappingDict:
        print("INFO: equity %s issuer %s does not have a complete list of equity FRTB equity BUCKETS data. Existing data: %s." %(instrument.Name(),insIssuer.Name(),instrumentMappingKeyListAsTuple))
        return None
    else:
        return FrtbEquityBucketNumberMappingDict[instrumentMappingKeyListAsTuple]
    
    return None

instrument = acm.FStock['1600005136_Stock']
print(Override_FRTBEquityBucketNumber(instrument))
