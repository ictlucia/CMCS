"""--------------------------------------------------------------------
MODULE
    PriceLinkDefinitionUpgrade - It is a Conversion Script

DESCRIPTION
    This script is a Conversion Script, means in PriceDefinition table in ADM,
    it copys all the columns and split the data[x] into specific fields and
    copy them into the new columns in PriceLinkDefinition table in ADM.
--------------------------------------------------------------------"""
import ael
import acm
import datetime

#""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Provider Type is defined as below
# 2  Reuters
# 3  Bloomberg
# 5  MarketMap
# 13 AMS
#""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

listofPLDfromPriceDefinition = [{}]
totalPLDsRead = 0
totalPLDsCached = 0
totalPLDsSuccessfullyUpgraded = 0
totalInvalidPLDs = 0
ADMVersionSupportingDelayedFlag=(4,28,600,0) # Added from ADM 2017.1, build 4.28.600.0, ADMNumber 42800600

#Is delayed flag is added in ADM version 4.28.600.0, so delayed flag need to be added in PriceLinkSpecification only if ADM version is greater than 4.28.600.0 
def admVersionSupportingDelayedFlag():
    # Find the ADM version
    server_data = ael.ServerData.select()[0]
    adm_version = server_data.adm_version.split(".")
    adm_version = tuple([ int(v) for v in adm_version])
    if adm_version >= ADMVersionSupportingDelayedFlag:
        return True
    else:
        return False

ADMSupportingDelayedFlag = admVersionSupportingDelayedFlag()

def getDistributorNameFromDisnbr(disnbr):
    '''Get price distributor name, disid from disnbr'''
    priceDistributorName = 'Invalid'
    priceDistributorAELObj = ael.PriceDistributor[int(disnbr)]
    if priceDistributorAELObj:
        priceDistributorName = priceDistributorAELObj.disid
    return priceDistributorName

#Create new market place if not available
def createMarketPlace(name):
    if acm.FMarketPlace[name]: 
        return
    mrkt = acm.FMarketPlace()
    mrkt.Name(name)
    mrkt.Commit()
    print "Market ", name, "created" 

#Extracts attribute price definition and returns the same    
def getAttributeFromOldPLD(pld_pd, attribute):
    retattribute = ''
    try:
        retattribute = getattr(pld_pd, attribute)
    except Exception, e:
        exc("WARNING: Unknown attribute error, 'attribute = %s''\
                            'for object type %s "%(attribute, type(pld_pd)), e)
    return retattribute

def exc(w, e):
    if w and e:
        print w + ". Exception:", str(e)
    elif w and not e:
        print w
    elif e:
        print str(e)

def checkInActive(serviceWithInActive,serviceRet,inactiveRet):
    if serviceWithInActive.find('!') == 0:
        serviceRet = serviceWithInActive.split('!')[1]
        inactiveRet = 1
    else:
        serviceRet = serviceWithInActive
        inactiveRet = 0
    return serviceRet,inactiveRet

def convert_time_in_int(time, time_val, marketCode, ins, cur, market):
    try:
        if time_val:
            HH = int(time_val)/100
            MM = int(time_val)%100
            if HH > 23 or MM > 59:
                print "WARNING: '%s' in HH:MM is '%s', should be less then "\
                      "23:59 for, \n Market code: '%s', \n Instrument : '%s', "\
                      "\n Currency   : '%s' \n Market	   : '%s', \n updating"\
                      " default value\n" %(time, (str(HH) + ':' + str(MM)), \
                      marketCode, ins, cur, market)
                return -1
            time_str = time_val.zfill(4)
            time_int = int(time_str[:2])*60 + int(time_str[2:])
            return time_int
    except Exception, e:
        return -1


# Extract data[0],[1],[2] and their Additional Information Columns
def extractPLDFromOldPriceDistributor(pld_pd, data_x, retList_x):
    AMPH_disnbr = None
    APH_pld     = False
    AMPH_pld    = False
    serviceR    = ''
    inactiveR   = 0
    #Extract the data_x_ columns from the old PLD
    try:
        atr_data_x = getattr(pld_pd, data_x)
    except Exception, e:
        exc("getattr", e)

    #Check if the Distributor is APH or AMPH
    if atr_data_x:
        if getAttributeFromOldPLD(pld_pd, 'disnbr') != None:
            AMPH_disnbr = getAttributeFromOldPLD(pld_pd, 'disnbr').disnbr
            DistributorNumbers = ael.PriceDistributor.select()
            retList_x['Instrument'] = getAttributeFromOldPLD(pld_pd, 'insaddr').display_id()
            retList_x['Currency'] = getAttributeFromOldPLD(pld_pd, 'curr').display_id()
            retList_x['Market'] = getAttributeFromOldPLD(pld_pd, 'source_ptynbr').display_id()
            for disnbr in DistributorNumbers:
                disnumber = getAttributeFromOldPLD(disnbr, 'disnbr')
                if disnumber == AMPH_disnbr:
                    disName = getAttributeFromOldPLD(disnbr, 'disid')
                    retList_x['distributor_type'] = getAttributeFromOldPLD(disnbr, 'distributor_type')
                    retList_x['pd_service'] = getAttributeFromOldPLD(disnbr, 'service')
                    retList_x['pd_semantic'] = getAttributeFromOldPLD(disnbr, 'semantic')
                    retList_x['distributor_name'] = disName
                    if 'AMPH' == disName.upper().split('_')[0]:
                        AMPH_pld = True
                        retList_x['DISTRIBUTOR'] = 'AMPH'
                        #Write the defaults
                        retList_x['service'] = retList_x['idp_code'] = retList_x['semantic'] = retList_x['priority'] = retList_x['is_fraction'] = \
                        retList_x['ignore_last_interval'] = retList_x['addition_addend_present'] = retList_x['addition_addend'] = ''
                        retList_x['not_active'] = 0
                        retList_x['multiplication_factor'] = 1
                        retList_x['start_time'] = retList_x['stop_time'] = retList_x['update_interval'] = -1
                    else:
                        APH_pld = True
                        retList_x['DISTRIBUTOR'] = 'APH'
                        #Write the defaults
                        retList_x['service'] = retList_x['idp_code'] = retList_x['semantic'] = retList_x['priority'] = \
                        retList_x['is_fraction'] = retList_x['addition_addend'] = \
                        retList_x['ignore_last_interval'] = retList_x['addition_addend_present'] = ''
                        retList_x['not_active'] = 0
                        retList_x['multiplication_factor'] = 1
                        retList_x['start_time'] = retList_x['stop_time'] = retList_x['update_interval'] = -1
        else:
            return

    #Extract Additional Info Column
    try:
        defnbr = getAttributeFromOldPLD(pld_pd, 'defnbr')
        n = (data_x.split('['))[1].split(']')
        allAddInfoSpec = ael.AdditionalInfoSpec.select()
        for addinfpspec in allAddInfoSpec:
            fieldname = getAttributeFromOldPLD(addinfpspec, 'field_name')
            if  fieldname == ('PDTrans%dExt' % (int(n[0]) + 1)):
                specnbr = getAttributeFromOldPLD(addinfpspec, 'specnbr')
                allAddInfo = ael.AdditionalInfo.select('addinf_specnbr=%d'%specnbr)
                for addinfo in allAddInfo:
                    addinfspecnbr = getAttributeFromOldPLD(addinfo, 'addinf_specnbr')
                    if specnbr == addinfspecnbr.specnbr:
                        recaddr = getAttributeFromOldPLD(addinfo, 'recaddr')
                        if recaddr == defnbr:
                            ai = getAttributeFromOldPLD(addinfo, 'value')
                            if ai:
                                atr_data_x += " " # add space so we don't concatenate tokens by mistake
                                atr_data_x += ai

    except Exception, e:
        exc("AddInfoSpec", e)
        pass # No AddInfoSpec defined on this installation

    #Now Extract The individual Attributes of APH distributor
    if APH_pld:
        atr_data_x1 = ' '.join(atr_data_x.split())
        atr_data_x_spl = atr_data_x1.split('"')
        if len(atr_data_x_spl) == 1:
            #IDP Code is given without any ""
            atr_data_x_spl = atr_data_x1.split(' ')
            if len(atr_data_x_spl) == 1:
                retList_x['idp_code'] = atr_data_x_spl[0].strip(' ')
            elif len(atr_data_x_spl) == 2:
                if (atr_data_x_spl[0].strip(' ')).find('!') == 0:
                    retList_x['service'] = (atr_data_x_spl[0].strip(' ')).split('!')[1]
                    retList_x['not_active'] = 1
                else:
                    retList_x['service'] = atr_data_x_spl[0].strip(' ')

                retList_x['idp_code'] = atr_data_x_spl[1].strip(' ')
            else:
                for nbr in xrange(len(atr_data_x_spl)):
                    if nbr == 0:
                        if (atr_data_x_spl[nbr].strip(' ')).find('!') == 0:
                            retList_x['service'] = (atr_data_x_spl[nbr].strip(' ')).split('!')[1]
                            retList_x['not_active'] = 1
                        else:
                            retList_x['service'] = atr_data_x_spl[nbr].strip(' ')
                    elif nbr == 1:
                        retList_x['idp_code'] = atr_data_x_spl[nbr].strip(' ')
                    elif nbr == 2:
                        retList_x['semantic'] = atr_data_x_spl[nbr].strip(' ')
                    elif nbr == 3:
                        retList_x['priority'] = atr_data_x_spl[nbr].strip(' ')
                    elif nbr == 4:
                        retList_x['start_time'] = convert_time_in_int('Start time', atr_data_x_spl[nbr].strip(' '), retList_x['idp_code'], retList_x['Instrument'], retList_x['Currency'], retList_x['Market'])
                    elif nbr == 5:
                        retList_x['stop_time'] = convert_time_in_int('Stop time', atr_data_x_spl[nbr].strip(' '), retList_x['idp_code'], retList_x['Instrument'], retList_x['Currency'], retList_x['Market'])
                    elif nbr == 6:
                        retList_x['is_fraction'] = atr_data_x_spl[nbr].strip(' ')
                    elif nbr == 7:
                        retList_x['multiplication_factor'] = atr_data_x_spl[nbr].strip(' ')
                    elif nbr == 8:
                        retList_x['update_interval'] = atr_data_x_spl[nbr].strip(' ')
                    elif nbr == 9:
                        retList_x['ignore_last_interval'] = atr_data_x_spl[nbr].strip(' ')
                    elif nbr == 10:
                        retList_x['addition_addend_present'] = atr_data_x_spl[nbr].strip(' ')
                    elif nbr == 11:
                        retList_x['addition_addend'] = atr_data_x_spl[nbr].strip(' ')
        else:
            #IDP Code is given in ""
            extrasFields = atr_data_x_spl[2].lstrip(' ').split(' ')
            if len(extrasFields) == 1:
                if atr_data_x_spl[0] == '':
                    retList_x['idp_code'] = atr_data_x_spl[1].strip(' ')
                else:
                    if (atr_data_x_spl[0].strip(' ')).find('!') == 0:
                        retList_x['service'] = (atr_data_x_spl[0].strip(' ')).split('!')[1]
                        retList_x['not_active'] = 1
                    else:
                        retList_x['service'] = atr_data_x_spl[0].strip(' ')
                    retList_x['idp_code'] = atr_data_x_spl[1].strip(' ')
                    if atr_data_x_spl[2]:
                        retList_x['semantic'] = atr_data_x_spl[2].strip(' ')
            else:
                if (atr_data_x_spl[0].strip(' ')).find('!') == 0:
                    retList_x['service'] = (atr_data_x_spl[0].strip(' ')).split('!')[1]
                    retList_x['not_active'] = 1
                else:
                    retList_x['service'] = atr_data_x_spl[0].strip(' ')
                retList_x['idp_code'] = atr_data_x_spl[1].strip(' ')
                for extraval in xrange(len(extrasFields)):
                    if extraval == 0:
                        retList_x['semantic'] = extrasFields[extraval].strip(' ')
                    elif extraval == 1:
                        retList_x['priority'] = extrasFields[extraval].strip(' ')
                    elif extraval == 2:
                        retList_x['start_time'] = convert_time_in_int('Start time', extrasFields[extraval].strip(' '), retList_x['idp_code'], retList_x['Instrument'], retList_x['Currency'], retList_x['Market'])
                    elif extraval == 3:
                        retList_x['stop_time'] = convert_time_in_int('Stop time', extrasFields[extraval].strip(' '), retList_x['idp_code'], retList_x['Instrument'], retList_x['Currency'], retList_x['Market'])
                    elif extraval == 4:
                        retList_x['is_fraction'] = extrasFields[extraval].strip(' ')
                    elif extraval == 5:
                        retList_x['multiplication_factor'] = extrasFields[extraval].strip(' ')
                    elif extraval == 6:
                        retList_x['update_interval'] = extrasFields[extraval].strip(' ')
                    elif extraval == 7:
                        retList_x['ignore_last_interval'] = extrasFields[extraval].strip(' ')
                    elif extraval == 8:
                        retList_x['addition_addend_present'] = extrasFields[extraval].strip(' ')
                    elif extraval == 9:
                        retList_x['addition_addend'] = extrasFields[extraval].strip(' ')


    if AMPH_pld:
        atr_data_x1 = ' '.join(atr_data_x.split())
        atr_data_x_spl = atr_data_x1.split('"')
        if len(atr_data_x_spl) == 1:
            #IDP Code is given without any ""
            atr_data_x_spl = atr_data_x1.split(' ')
            if len(atr_data_x_spl) == 1:
                if (atr_data_x_spl[0].strip(' ')).find('!') == 0:
                    retList_x['idp_code'] = (atr_data_x_spl[0].strip(' ')).split('!')[1]
                    retList_x['not_active'] = 1
                else:
                    retList_x['idp_code'] = atr_data_x_spl[0].strip(' ')
            else:
                for nbr in xrange(len(atr_data_x_spl)):
                    if nbr == 0:
                        if (atr_data_x_spl[nbr].strip(' ')).find('!') == 0:
                            retList_x['idp_code'] = (atr_data_x_spl[nbr].strip(' ')).split('!')[1]
                            retList_x['not_active'] = 1
                        else:
                            retList_x['idp_code'] = atr_data_x_spl[nbr].strip(' ')
                    elif nbr == 1:
                        retList_x['priority'] = atr_data_x_spl[nbr].strip(' ')
                    elif nbr == 2:
                        retList_x['start_time'] = convert_time_in_int('Start time', atr_data_x_spl[nbr].strip(' '), retList_x['idp_code'], retList_x['Instrument'], retList_x['Currency'], retList_x['Market'])
                    elif nbr == 3:
                        retList_x['stop_time'] = convert_time_in_int('Stop time', atr_data_x_spl[nbr].strip(' '), retList_x['idp_code'], retList_x['Instrument'], retList_x['Currency'], retList_x['Market'])
                    elif nbr == 4:
                        retList_x['is_fraction'] = atr_data_x_spl[nbr].strip(' ')
                    elif nbr == 5:
                        retList_x['multiplication_factor'] = atr_data_x_spl[nbr].strip(' ')
                    elif nbr == 6:
                        retList_x['update_interval'] = atr_data_x_spl[nbr].strip(' ')
                    elif nbr == 7:
                        retList_x['ignore_last_interval'] = atr_data_x_spl[nbr].strip(' ')
                    elif nbr == 8:
                        retList_x['addition_addend_present'] = atr_data_x_spl[nbr].strip(' ')
                    elif nbr == 9:
                        retList_x['addition_addend'] = atr_data_x_spl[nbr].strip(' ')
        else:
            #IDP Code is given in ""
            extrasFields = atr_data_x_spl[2].lstrip(' ').split(' ')
            if len(extrasFields) == 1:
                if (atr_data_x_spl[1].strip(' ')).find('!') == 0:
                    retList_x['idp_code'] = (atr_data_x_spl[1].strip(' ')).split('!')[1]
                    retList_x['not_active'] = 1
                else:
                    retList_x['idp_code'] = atr_data_x_spl[1].strip(' ')
            else:
                if (atr_data_x_spl[1].strip(' ')).find('!') == 0:
                    retList_x['idp_code'] = (atr_data_x_spl[1].strip(' ')).split('!')[1]
                    retList_x['not_active'] = 1
                else:
                    retList_x['idp_code'] = atr_data_x_spl[1].strip(' ')
                for extraval in xrange(len(extrasFields)):
                    if extraval == 0:
                        retList_x['priority'] = extrasFields[extraval].strip(' ')
                    elif extraval == 1:
                        retList_x['start_time'] = convert_time_in_int('Start time',\
                        extrasFields[extraval].strip(' '), retList_x['idp_code'],\
                        retList_x['Instrument'], retList_x['Currency'], retList_x['Market'])
                    elif extraval == 2:
                        retList_x['stop_time'] = convert_time_in_int('Stop time',\
                        extrasFields[extraval].strip(' '), retList_x['idp_code'],\
                        retList_x['Instrument'], retList_x['Currency'], retList_x['Market'])
                    elif extraval == 3:
                        retList_x['is_fraction'] = extrasFields[extraval].strip(' ')
                    elif extraval == 4:
                        retList_x['multiplication_factor'] = extrasFields[extraval].strip(' ')
                    elif extraval == 5:
                        retList_x['update_interval'] = extrasFields[extraval].strip(' ')
                    elif extraval == 6:
                        retList_x['ignore_last_interval'] = extrasFields[extraval].strip(' ')
                    elif extraval == 7:
                        retList_x['addition_addend_present'] = extrasFields[extraval].strip(' ')
                    elif extraval == 8:
                        retList_x['addition_addend'] = extrasFields[extraval].strip(' ')


def readPriceDistributor(priceDistributorName):
    print '======================================================================='
    global totalPLDsRead
    global totalPLDsCached
    global totalInvalidPLDs

    if 'All' == priceDistributorName:
        print "Upgrade started for All price distributors at %s\n"\
                                                 %str(datetime.datetime.now())
        allPD = ael.PriceDefinition.select()
    else:
        print "Upgrade started for price distributor = %s at %s\n"\
                          %(priceDistributorName, str(datetime.datetime.now()))
        priceDistributorObj = ael.PriceDistributor[priceDistributorName]
        allPD = ael.PriceDefinition.select\
                            ("disnbr='%s'"%str(priceDistributorObj.disnbr))

    totalPLDsRead = len(allPD)
    print 'STATUS: Total price link definitions read for migration = %d'\
                                                            %totalPLDsRead

    for pd in allPD:
        listAttributeInPdCommon  = {}
        listAttributeInPD_data_0 = {}
        listAttributeInPD_data_1 = {}
        listAttributeInPD_data_2 = {}

        try:
            if getAttributeFromOldPLD(pd, 'disnbr') != None:
                listAttributeInPdCommon['disnbr'] =\
                                getAttributeFromOldPLD(pd, 'disnbr').disnbr
            else:
                print "ERROR: Invalid Price Link Definition rejected. "\
                "Price Distributor is NOT set for, "\
                "\n Instrument: '%s', \n Currency  : '%s' \n"\
                " Market    : '%s'\n"\
                %(getAttributeFromOldPLD(pd, 'insaddr').display_id(),\
                  getAttributeFromOldPLD(pd, 'curr').display_id(),\
                  getAttributeFromOldPLD(pd, 'source_ptynbr').display_id())
                totalInvalidPLDs  +=1
                continue

            listAttributeInPdCommon['archive_status'] = getAttributeFromOldPLD(pd, 'archive_status')
            if getAttributeFromOldPLD(pd, 'authorizer_usrnbr') != None:
                listAttributeInPdCommon['authorizer_usrnbr'] = getAttributeFromOldPLD(pd, 'authorizer_usrnbr').usrnbr
            else:
                listAttributeInPdCommon['authorizer_usrnbr'] = None
            listAttributeInPdCommon['continuous_subscription'] = getAttributeFromOldPLD(pd, 'continuous_subscription')
            listAttributeInPdCommon['creat_time'] = getAttributeFromOldPLD(pd, 'creat_time')
            if getAttributeFromOldPLD(pd, 'creat_usrnbr') != None:
                listAttributeInPdCommon['creat_usrnbr'] = getAttributeFromOldPLD(pd, 'creat_usrnbr').usrnbr
            else:
                listAttributeInPdCommon['creat_usrnbr'] = None
            if getAttributeFromOldPLD(pd, 'curr') != None:
                listAttributeInPdCommon['curr'] = getAttributeFromOldPLD(pd, 'curr').insaddr
            else:
                listAttributeInPdCommon['curr'] = None
            listAttributeInPdCommon['entitlement_handle'] = getAttributeFromOldPLD(pd, 'data[3]')
            listAttributeInPdCommon['defnbr'] = getAttributeFromOldPLD(pd, 'defnbr')

            listAttributeInPdCommon['errmsg'] = getAttributeFromOldPLD(pd, 'errmsg')
            listAttributeInPdCommon['four_eye_on'] = getAttributeFromOldPLD(pd, 'four_eye_on')
            if getAttributeFromOldPLD(pd, 'insaddr') != None:
                listAttributeInPdCommon['insaddr'] = getAttributeFromOldPLD(pd, 'insaddr').insaddr
            else:
                listAttributeInPdCommon['insaddr'] = None
            listAttributeInPdCommon['keep_intraday_prices'] = getAttributeFromOldPLD(pd, 'keep_intraday_prices')
            if getAttributeFromOldPLD(pd, 'owner_usrnbr') != None:
                listAttributeInPdCommon['owner_usrnbr'] = getAttributeFromOldPLD(pd, 'owner_usrnbr').usrnbr
            else:
                listAttributeInPdCommon['owner_usrnbr'] = None
            listAttributeInPdCommon['protection'] = getAttributeFromOldPLD(pd, 'protection')
            listAttributeInPdCommon['requested_subscription'] = getAttributeFromOldPLD(pd, 'requested_subscription')
            if getAttributeFromOldPLD(pd, 'source_ptynbr') != None:
                listAttributeInPdCommon['source_ptynbr'] = getAttributeFromOldPLD(pd, 'source_ptynbr').ptynbr
            else:
                listAttributeInPdCommon['source_ptynbr'] = None
            listAttributeInPdCommon['updat_time'] = getAttributeFromOldPLD(pd, 'updat_time')
            if getAttributeFromOldPLD(pd, 'updat_usrnbr') != None:
                listAttributeInPdCommon['updat_usrnbr'] = getAttributeFromOldPLD(pd, 'updat_usrnbr').usrnbr
            else:
                listAttributeInPdCommon['updat_usrnbr'] = None

        except Exception, extraInfo:
            totalInvalidPLDs  +=1
            errorStr = "ERROR: Exception Raised, %s while populating price link"\
                " definition into cache. Price link definition rejected. "\
		        "\n Instrument       : '%s',\n Currency         : '%s' \n"\
                " Market           : '%s',\n Price Distributor: '%s'"%\
		        (getAttributeFromOldPLD(pd, 'insaddr'      ).display_id(),\
                 getAttributeFromOldPLD(pd, 'curr'         ).display_id(),\
                 getAttributeFromOldPLD(pd, 'source_ptynbr').display_id(),\
                 getAttributeFromOldPLD(pd, 'disnbr'       ).display_id())
            exc(errorStr, None)

        extractPLDFromOldPriceDistributor(pd,'data[0]',listAttributeInPD_data_0)
        if len(listAttributeInPD_data_0) > 0:
            listofPLDfromPriceDefinition.append(dict(list(listAttributeInPdCommon.items()) + list(listAttributeInPD_data_0.items())))
        extractPLDFromOldPriceDistributor(pd,'data[1]',listAttributeInPD_data_1)
        if len(listAttributeInPD_data_1) > 0:
            createMarketPlace(listAttributeInPD_data_1['Market'] + "_1")
            listAttributeInPD_data_1['Market']=listAttributeInPD_data_1['Market'] + "_1"
            marketObj1 = acm.FMarketPlace[listAttributeInPD_data_1['Market']]
            listAttributeInPD_data_1['source_ptynbr']=marketObj1.Oid()
            listofPLDfromPriceDefinition.append(dict(list(listAttributeInPdCommon.items()) + list(listAttributeInPD_data_1.items())))
        extractPLDFromOldPriceDistributor(pd,'data[2]',listAttributeInPD_data_2)
        if len(listAttributeInPD_data_2) > 0:
            createMarketPlace(listAttributeInPD_data_2['Market'] + "_2")
            listAttributeInPD_data_2['Market']=listAttributeInPD_data_2['Market'] + "_2"
            marketObj2 = acm.FMarketPlace[listAttributeInPD_data_2['Market']]
            listAttributeInPD_data_2['source_ptynbr']=marketObj2.Oid()
            listofPLDfromPriceDefinition.append(dict(list(listAttributeInPdCommon.items()) + list(listAttributeInPD_data_2.items())))


    totalPLDsCached = (len(listofPLDfromPriceDefinition))
    print "\nINFO: Cache updated for PriceLinkDefinition table at", str(datetime.datetime.now())

    print "\nSTATUS: Total invalid price link definitions that are rejected"\
                                                      " = %d"%totalInvalidPLDs
    print "STATUS: Total price link definitions cached                    "\
                                                      "= %d"%totalPLDsCached


def setAttributeToNewPLD(newPLDobj,attributeToSet,attributeListInPLD):
    retattribute = ''
    if attributeListInPLD:
        try:
            retattribute = setattr(newPLDobj,attributeToSet, attributeListInPLD)
        except Exception, e:
            exc("setAttributeToNewPLD", e)

        return retattribute


def addChoiceListValue(key,val,descr='',sortO=0):
    newcl = acm.FChoiceList()
    newcl.List = key
    newcl.Name = val
    if descr: newcl.Description(descr)
    if sortO: newcl.SortOrder(sortO)
    try:
        newcl.Commit()
    except Exception, e:
            print e
            
def addPriceSemanticValue(semanticName,providerType):
    priceSemantic = acm.FPriceSemantic()
    priceSemantic.Name(semanticName)
    priceSemantic.ProviderType(providerType)
    try:
        priceSemantic.Commit()
    except Exception, e:
            print e

def getChoiceList(key, val):
    clval = acm.FChoiceList.Select("list=%s" %key)
    for eachChoice in clval:
        if eachChoice.Name() == val:
            return eachChoice.Oid()
            
def getPriceSemanticName(semanticName):    
    return acm.FPriceSemantic[semanticName]
    
def getPriceSemanticSeqNbr(semanticName):
    Seqnbr = acm.FPriceSemantic[semanticName]
    if Seqnbr:
        return Seqnbr.Oid()
    else:
        return 0

def message_box_error(shell, type, message):
    """pops up an error message box"""
    acm.UX().Dialogs().MessageBox(shell, type, message, 'OK',
                                    None, None, 'Button1', 'Button2')
                                    
def updateSemantic(choicelistSEMANTIC, listofPLDs, providerType, idpcodeTypeForLog='idpcode', useSemanticChoiceList=0):
    if not useSemanticChoiceList:
        #PriceSemantic table
        if listofPLDs['semantic'] == '':
            if listofPLDs['pd_semantic'] == '':
                print "WARNING: Semantic: '%s' is required in PriceLinkDefinition with %s: '%s'"\
                                                        %(listofPLDs['semantic'], idpcodeTypeForLog, listofPLDs['idp_code'])
                listofPLDs['semantic'] = 'None'
        else:
            if not acm.FPriceSemantic[listofPLDs['semantic']]:
                addPriceSemanticValue(listofPLDs['semantic'], providerType)
            else:
                clval = getPriceSemanticName(listofPLDs['semantic'])
                if not clval:
                    addPriceSemanticValue(listofPLDs['semantic'], providerType)
    else:
        #PriceSemantics choice list
        if listofPLDs['semantic'] == '':
            if listofPLDs['pd_semantic'] == '':
                print "WARNING: Semantic: '%s' is required in PriceLinkDefinition with %s: '%s'"\
                                                        %(listofPLDs['semantic'], idpcodeTypeForLog, listofPLDs['idp_code'])
                listofPLDs['semantic'] = 'None'
        else:
            if not choicelistSEMANTIC:
                addChoiceListValue('PriceSemantics',listofPLDs['semantic'])
            else:
                clval = acm.FChoiceList.Select("list='PriceSemantics' and name='%s'" %listofPLDs['semantic'])
                if not clval:
                    addChoiceListValue('PriceSemantics',listofPLDs['semantic'])

def addupdateChoiceListAndTableForServiceAndSemantic(listofPLDs, useSemanticChoiceList):
    choiceListSERVICE = 'PriceServices'
    choiceListSEMANTIC = 'PriceSemantics'

    choicelistSERVICE = acm.FChoiceList.Select("list=%s"%choiceListSERVICE)
    choicelistSEMANTIC = acm.FChoiceList.Select("list=%s"%choiceListSEMANTIC)

    if listofPLDs['distributor_type'] == 'Bloomberg':
        updateSemantic(choicelistSEMANTIC, listofPLDs, 3, 'ticker', useSemanticChoiceList)
        if listofPLDs['service'] != '':
            if not choicelistSERVICE:
                addChoiceListValue('PriceServices',listofPLDs['service'])
            else:
                clval = acm.FChoiceList.Select("list='PriceServices' and name='%s'" %listofPLDs['service'])
                if not clval:
                    addChoiceListValue('PriceServices',listofPLDs['service'])

    elif listofPLDs['distributor_type'] == 'MarketMap':
        updateSemantic(choicelistSEMANTIC, listofPLDs, 5, 'alpha code', useSemanticChoiceList)
        if listofPLDs['service'] != '':
            print "WARNING: Service: '%s' is not required in PriceLinkDefinition with alpha code: '%s'" %(listofPLDs['service'], listofPLDs['idp_code'])
        listofPLDs['service'] = 'None'
            
    elif listofPLDs['distributor_type'] == 'Reuters':
        # Service
        if listofPLDs['service'] == '':
            if listofPLDs['pd_service'] == '':
                print "WARNING: Service: '%s' is required in PriceLinkDefinition with ric: '%s'" %(listofPLDs['service'], listofPLDs['idp_code'])
                listofPLDs['service'] = 'None'
        else:
            if not choicelistSERVICE:
                addChoiceListValue('PriceServices',listofPLDs['service'])
            else:
                clval = acm.FChoiceList.Select("list='PriceServices' and name='%s'" %listofPLDs['service'])
                if not clval:
                    addChoiceListValue('PriceServices',listofPLDs['service'])

        # Semantic
        updateSemantic(choicelistSEMANTIC, listofPLDs, 2, 'ric', useSemanticChoiceList)

    elif listofPLDs['distributor_type'] == 'AMS':
        # Service
        if listofPLDs['service'] != '':
            print "WARNING: Service: '%s' is not required in PriceLinkDefinition with order book ID: '%s', skipping Service" %(listofPLDs['service'], listofPLDs['idp_code'])
            listofPLDs['service'] = 'None'

        if listofPLDs['semantic'] != '':
            print "WARNING: Semantic: '%s' is not required in PriceLinkDefinition with order book ID: '%s', skipping Semantic" %(listofPLDs['semantic'], listofPLDs['idp_code'])
            listofPLDs['semantic'] = 'None'


def writePriceLinkDefinition(useSemanticChoiceList):
    print "\nINFO: Updating PriceLinkDefinition table, started at", str(datetime.datetime.now())
    global totalPLDsSuccessfullyUpgraded
    global totalInvalidPLDs
    PLDsFailedToMigrate = 0

    for nbOfPLDs in listofPLDfromPriceDefinition:
        if len(nbOfPLDs)>1:
            newPLD = ael.PriceLinkDefinition.new()
            try:
                if nbOfPLDs['DISTRIBUTOR'] == 'APH':
                    addupdateChoiceListAndTableForServiceAndSemantic(nbOfPLDs, useSemanticChoiceList)

                if nbOfPLDs['archive_status'] != '':
                    setAttributeToNewPLD(newPLD,'archive_status', int(nbOfPLDs['archive_status']))

                if nbOfPLDs['authorizer_usrnbr'] != '':
                    if nbOfPLDs['authorizer_usrnbr'] == None:
                        setAttributeToNewPLD(newPLD,'authorizer_usrnbr', None)
                    else:
                        setAttributeToNewPLD(newPLD,'authorizer_usrnbr', nbOfPLDs['authorizer_usrnbr'])

                if nbOfPLDs['continuous_subscription'] != '':
                    setAttributeToNewPLD(newPLD,'continuous_subscription', int(nbOfPLDs['continuous_subscription']))

                if nbOfPLDs['creat_time'] != '':
                    setAttributeToNewPLD(newPLD,'creat_time', nbOfPLDs['creat_time'])

                if nbOfPLDs['creat_usrnbr'] != '':
                    if nbOfPLDs['creat_usrnbr'] == None:
                        setAttributeToNewPLD(newPLD,'creat_usrnbr', None)
                    else:
                        setAttributeToNewPLD(newPLD,'creat_usrnbr', nbOfPLDs['creat_usrnbr'])

                if nbOfPLDs['curr'] != '':
                    if nbOfPLDs['curr'] != None:
                        setAttributeToNewPLD(newPLD,'curr', nbOfPLDs['curr'])
                    else:
                        setAttributeToNewPLD(newPLD,'curr', None)

                if nbOfPLDs['entitlement_handle'] != '':
                    setAttributeToNewPLD(newPLD,'entitlement_handle', str(nbOfPLDs['entitlement_handle']))  # This is data[3] column in old PLD

                if nbOfPLDs['disnbr'] != '':
                    if nbOfPLDs['disnbr'] == None:
                        setAttributeToNewPLD(newPLD,'disnbr', None)
                    else:
                        setAttributeToNewPLD(newPLD,'disnbr', int(nbOfPLDs['disnbr']))

                if nbOfPLDs['errmsg'] != '':
                    setAttributeToNewPLD(newPLD,'errmsg', nbOfPLDs['errmsg'])

                if nbOfPLDs['four_eye_on'] != '':
                    setAttributeToNewPLD(newPLD,'four_eye_on', nbOfPLDs['four_eye_on'])

                if nbOfPLDs['insaddr'] != '':
                    if nbOfPLDs['insaddr'] == None:
                        setAttributeToNewPLD(newPLD,'insaddr', None)
                    else:
                        setAttributeToNewPLD(newPLD,'insaddr', int(nbOfPLDs['insaddr']))

                if nbOfPLDs['keep_intraday_prices'] != '':
                    setAttributeToNewPLD(newPLD,'keep_intraday_prices', nbOfPLDs['keep_intraday_prices'])

                if nbOfPLDs['owner_usrnbr'] != '':
                    if nbOfPLDs['owner_usrnbr'] == None:
                        setAttributeToNewPLD(newPLD,'owner_usrnbr', None)
                    else:
                        setAttributeToNewPLD(newPLD,'owner_usrnbr', nbOfPLDs['owner_usrnbr'])

                if nbOfPLDs['protection'] != '':
                    setAttributeToNewPLD(newPLD,'protection', nbOfPLDs['protection'])

                if nbOfPLDs['requested_subscription'] != '':
                    setAttributeToNewPLD(newPLD,'requested_subscription', nbOfPLDs['requested_subscription'])

                if nbOfPLDs['source_ptynbr'] != '':
                    if nbOfPLDs['source_ptynbr'] == None:
                        setAttributeToNewPLD(newPLD,'source_ptynbr', None)
                    else:
                        setAttributeToNewPLD(newPLD,'source_ptynbr', int(nbOfPLDs['source_ptynbr']))

                if nbOfPLDs['updat_time'] != '':
                    setAttributeToNewPLD(newPLD,'updat_time', nbOfPLDs['updat_time'])

                if nbOfPLDs['updat_usrnbr'] != '':
                    if nbOfPLDs['updat_usrnbr'] == None:
                        setAttributeToNewPLD(newPLD,'updat_usrnbr', None)
                    else:
                        setAttributeToNewPLD(newPLD,'updat_usrnbr', nbOfPLDs['updat_usrnbr'])

                if nbOfPLDs['DISTRIBUTOR'] == 'APH':
                    if nbOfPLDs['service'] != '':
                        setAttributeToNewPLD(newPLD,'service', getChoiceList('PriceServices', nbOfPLDs['service']))

                if nbOfPLDs['idp_code'] != '':
                    idp_code = nbOfPLDs['idp_code']
                    if ADMSupportingDelayedFlag == True:
                        if idp_code[0] == '/':
                            setAttributeToNewPLD(newPLD,'idp_code', str(nbOfPLDs['idp_code'])[1:])
                            setAttributeToNewPLD(newPLD,'is_delayed', "True")
                        else:
                            setAttributeToNewPLD(newPLD,'idp_code', str(nbOfPLDs['idp_code']))
                            setAttributeToNewPLD(newPLD,'is_delayed', "False")
                    else:
                        setAttributeToNewPLD(newPLD,'idp_code', str(nbOfPLDs['idp_code']))
						
                if nbOfPLDs['DISTRIBUTOR'] == 'APH':
                    if nbOfPLDs['semantic'] != '':
                        if not useSemanticChoiceList:
                            #PriceSemantic table
                            if getPriceSemanticSeqNbr(nbOfPLDs['semantic']) != 0:
                                setAttributeToNewPLD(newPLD,'price_semantic_seqnbr', getPriceSemanticSeqNbr(nbOfPLDs['semantic'])) 
                        else:
                            #PriceSemantic choicelist
                            setAttributeToNewPLD(newPLD,'semantic', getChoiceList('PriceSemantics', nbOfPLDs['semantic']))

                if nbOfPLDs['start_time'] != '':
                    setAttributeToNewPLD(newPLD,'start_time', int(nbOfPLDs['start_time']))

                if nbOfPLDs['stop_time'] != '':
                    setAttributeToNewPLD(newPLD,'stop_time', int(nbOfPLDs['stop_time']))

                if nbOfPLDs['is_fraction'] != '':
                    if nbOfPLDs['is_fraction'] == 'D':
                        setAttributeToNewPLD(newPLD,'is_fraction',0)
                    else:
                        setAttributeToNewPLD(newPLD,'is_fraction',1)

                if nbOfPLDs['multiplication_factor'] != '':
                    setAttributeToNewPLD(newPLD,'multiplication_factor', float(nbOfPLDs['multiplication_factor']))

                if nbOfPLDs['update_interval'] != '':
                    setAttributeToNewPLD(newPLD,'update_interval', int(nbOfPLDs['update_interval']))

                if nbOfPLDs['ignore_last_interval'] != '':
                    if int(nbOfPLDs['ignore_last_interval']) == 0:
                        setAttributeToNewPLD(newPLD,'last_follow_interval',1)
                    else:
                        setAttributeToNewPLD(newPLD,'last_follow_interval',0)

                if nbOfPLDs['addition_addend_present'] != '':
                    if nbOfPLDs['addition_addend_present'] == 'A':
                        setAttributeToNewPLD(newPLD,'addition_addend', float(nbOfPLDs['addition_addend']))

                setAttributeToNewPLD(newPLD,'not_active',nbOfPLDs['not_active'])

                setAttributeToNewPLD(newPLD,'donot_reset_fields',-1)

            except Exception, extraInfo:
                print "ERROR: %s, during setting new price link definition"\
                      " attributes"%str(extraInfo)
                print " Market code	  : '%s', \n Instrument 	  : '%s',"\
                      " \n Currency   	  : '%s' \n Market     	  : '%s',"\
                      " \n Price Distributor: '%s'"\
                      %(nbOfPLDs['idp_code'], nbOfPLDs['Instrument'],\
                        nbOfPLDs['Currency'], nbOfPLDs['Market'],\
                        getDistributorNameFromDisnbr( nbOfPLDs['disnbr']))
                PLDsFailedToMigrate +=1
                continue


            try:
                newPLD.commit()
                totalPLDsSuccessfullyUpgraded +=1
            except Exception, e:
                print "WARNING: Commit failure for idp"\
                                            " code = %s."%str(newPLD.idp_code)
                try:
                    newPLD.clone()
                except Exception, e:
                    PLDsFailedToMigrate +=1
                    errorStr = "ERROR: Retry failed."\
                                "unable to upgrade idp code = %s."\
                                %str(newPLD.idp_code)
                    exc(errorStr, e)

    print "\nUpgrade of PriceLinkDefinition completed at ", str(datetime.datetime.now())
    print "\n****************************SUMMARY**********************************"
    print 'Total price link definitions read for migration           = %d'\
                                                                %totalPLDsRead
    print "Total invalid price link definitions that are rejected    = %d"\
                                                             %totalInvalidPLDs
    print "Total price link definitions cached for migration         = %d"\
                                                              %totalPLDsCached
    print 'Total price link definitions successfully migrated        = %d'\
                                                %totalPLDsSuccessfullyUpgraded
    print "Total price link definitions cached but failed to migrate = %d"\
                                                          %PLDsFailedToMigrate
    print 'Total price link definitions failed to migrate            = %d'\
                               %(totalPLDsCached - totalPLDsSuccessfullyUpgraded)
    print '======================================================================='


def checkDistributorType(priceDistributorList):
    '''Check if distributor type is present in the ael price distributor object list'''
    isDistributorTypeSet = True
    for priceDistributorAELObj in priceDistributorList:
        disName = getAttributeFromOldPLD(priceDistributorAELObj, 'disid')

        if (getAttributeFromOldPLD(priceDistributorAELObj, 'distributor_type')\
                                                == 'None') and (disName != ''):
            errorMessage = "'Distributor Type' is not set for price distributor = %s.Please set" \
            "'Distributor Type' and execute again."%priceDistributorAELObj.disid
            message_box_error(acm.UX().SessionManager().Shell(), 'Error', errorMessage)
            print errorMessage
            isDistributorTypeSet = False

    return isDistributorTypeSet


def checkAllPriceDistributorForDistributorType():
    '''Check if distributor type is present in All price distributor.'''
    retVal = False
    priceDistributorList = ael.PriceDistributor.select()
    if priceDistributorList:
        retVal = checkDistributorType(priceDistributorList)
        if not retVal:
            print "The upgrade script will not execute with 'All' option"\
                  " unless 'Distributor Type' is properly set in each price"\
                  " distributor.\nOR, select specific price distributor for"\
                  " migration."
    return retVal

def checkSelectedPriceDistributorForDistributortype(priceDistributorName):
    '''Check if distributor type is present in All price distributor.'''
    retVal = False
    if priceDistributorName:
        priceDistributor = ael.PriceDistributor[priceDistributorName]
        if priceDistributor:
            if 'None' == priceDistributor.distributor_type:
                retVal = False
                print 'Distributor type is not present in selected price '\
                'distributor, %s. Please set the distributor type and run the '\
                'upgrade script again.'%priceDistributorName

            else:
                retVal = True
        else:
            print 'Selected price distributor %s not found in ADS'\
                                                    %priceDistributorName
    return retVal


def checkDistributorTypeInPriceDistributor(priceDistributorName):
    isDistributorTypeSet = False
    if 'All' == priceDistributorName:
        isDistributorTypeSet = checkAllPriceDistributorForDistributorType()
    else:
        isDistributorTypeSet = checkSelectedPriceDistributorForDistributortype\
                                                         (priceDistributorName)
    return isDistributorTypeSet

def convertPriceDefinitionToPriceLinkDefinition(priceDistributorName, useSemanticChoiceList):
    if checkDistributorTypeInPriceDistributor(priceDistributorName):
        readPriceDistributor(priceDistributorName)
        writePriceLinkDefinition(useSemanticChoiceList)
    else:
        print "Failed to upgrade price link definition. Upgrade script ends."

def getPriceDistibutorListFromDB():
    #Get all Price Distributors from database
    price_dist_popup_lst = []
    price_dist_lst = acm.FPriceDistributor.Select('')
    if price_dist_lst:
        for price_dist in price_dist_lst:
            if price_dist:
                 price_dist_popup_lst.append(price_dist.Name())
    price_dist_popup_lst = sorted(price_dist_popup_lst)
    return price_dist_popup_lst


ael_gui_parameters = {  'runButtonLabel'        : '&&Upgrade',
                        'InsertItemsShowExpired': True,
                        'hideExtraControls'     : True,
                        'hideExtraControls'     : True,
                        'closeWhenFinished'     : True,
                        'windowCaption'         : 'Price Link Definition Upgrade'}
ael_variables = [
                ['disnbr', 'Price Distributor', 'string', getPriceDistibutorListFromDB(), 'All', 1, 0, \
                            'Select a price distributor to upgrade all the '\
                            'price link definitions in selected price distributor.'\
                             'Or, select \'All\' to upgrade all available price link definitions in ADS.'],
                ['useSemanticChoiceList', 'Use PriceSemantics Choice List', 'bool', '01', 0, 1, 0, \
                            'Use old PriceSemantics choice list or PriceSemantic ADM table (supported from ADM 2016.4.0 Build 4.26.664.0 and PRIME 2016.4.0 Build: 4.26.664.0 onwards) for creating PriceLinkDefinitions in PriceLinkSpecification application.'],
                ]


#Calling main Function
#---------------------------------------------------------------
def ael_main(parameter):
    useSemanticChoiceList = False
    global totalPLDsRead
    global totalPLDsCached
    global totalPLDsSuccessfullyUpgraded
    global totalInvalidPLDs

    if parameter:
        useSemanticChoiceList = parameter['useSemanticChoiceList']
        print '======================================================================='
        if not useSemanticChoiceList:
            print "Using PriceSemantic table (supported from ADM 2016.4.0 Build 4.26.664.0 and PRIME 2016.4.0 Build: 4.26.664.0 onwards)"
        else:
            print "Using PriceSemantics Choice List"
            
        del listofPLDfromPriceDefinition[:]
        totalPLDsRead = 0
        totalPLDsCached = 0
        totalPLDsSuccessfullyUpgraded = 0
        totalInvalidPLDs = 0
    
        convertPriceDefinitionToPriceLinkDefinition(parameter['disnbr'], useSemanticChoiceList)




