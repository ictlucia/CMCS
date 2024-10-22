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
    
    print(hasattr(insIssuer.AdditionalInfo(),'FRTB_Eq_Economy'))
    print(getattr(insIssuer.AdditionalInfo(),'FRTB_Eq_Economy')())
    
    if insIssuer.AdditionalInfo().FRTB_Eq_Economy(): 
        insEconomy = insIssuer.AdditionalInfo().FRTB_Eq_Economy()
        choiceListItem = acm.FChoiceList.Select("name='%s' and list='%s'" %(insEconomy,'FRTB_Eq_Economy'))[0]
        instrumentMappingKeyAsList.insert(0,choiceListItem.Name())
    
    if insIssuer.AdditionalInfo().FRTB_Eq_MarketCap(): 
        insMarketCap = insIssuer.AdditionalInfo().FRTB_Eq_MarketCap()
        choiceListItem = acm.FChoiceList.Select("name='%s' and list='%s'" %(insMarketCap,'FRTB_Eq_MarketCap'))[0]
        instrumentMappingKeyAsList.insert(1,choiceListItem.Name())
    
    if insIssuer.AdditionalInfo().FRTB_Eq_Sector(): 
        insSector = insIssuer.AdditionalInfo().FRTB_Eq_Sector()
        choiceListItem = acm.FChoiceList.Select("name='%s' and list='%s'" %(insSector,'FRTB_Eq_Sector'))[0]
        instrumentMappingKeyAsList.insert(2,choiceListItem.Name())
    
    instrumentMappingKeyListAsTuple = tuple(instrumentMappingKeyAsList)
    if not instrumentMappingKeyListAsTuple in FrtbEquityBucketNumberMappingDict:
        print("INFO: equity %s issuer %s does not have a complete list of equity FRTB equity BUCKETS data." %(instrument.Name(),insIssuer.Name()))
        return None
    else:
        return FrtbEquityBucketNumberMappingDict[instrumentMappingKeyListAsTuple]
    
    return None

instrument = acm.FStock['11000174578_TELKOM']
print(Override_FRTBEquityBucketNumber(instrument))
