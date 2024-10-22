import ael, acm
import FPriceXMLValidation

# PriceSemantic table supported from ADM 2016.4, build 4.26.1166.0, ADMNumber 42601166
ADMVersionSupportingPriceSemanticTable=(4,26,1166,0) # Added from ADM 2016.4, build 4.26.1166.0, ADMNumber 42601166
ADMVersionSupportingDelayedFlag=(4,28,600,0) # Added from ADM 2017.1, build 4.28.600.0, ADMNumber 42800600
ADMVersionSupportingDelayedTriStateFlag=(4,39,289,0) # Added from ADM 2019.4, build 4.39.289.0, ADMNumber 43928900
ADMVersionSupportingLastFollowInterval=(4,28,600,0) # Added from ADM 2017.1, build 4.28.600.0, ADMNumber 42800600
ADMVersionSupportingIgnoreClearPrice=(4,31,304,0) # Added from ADM 2017.4, build 4.31.304.0, ADMNumber 43100301

class optionType:
    MANDATORY = 1
    OPTIONAL  = 2

class dataTypes:
    STRING     = 'string'
    INT        = 'int'
    FLOAT      = 'float'
    CHOICELIST = 'choice'
    TIME       = 'time'
    BOOL       = 'bool'
    ALL        = [STRING, INT, FLOAT, CHOICELIST, TIME, BOOL]

class validationStatus:
    FAILURE    = 0
    SUCCESS    = 1
    INCOMPLETE = 2

class attributeStatus:
    STATUS_UNKNOWN           = -1
    STATUS_OKAY              = 1
    MANDATORY_ATTRIB_MISSING = 2
    OUT_OF_RANGE             = 3
    SYNTAX_MISMATCH          = 4
    INVALID_DATATYPE         = 5
    UNKNOWN_ATTRIBUTE        = 6
    DATATYPE_VALUE_MISMATCH  = 7
    UNSUPPORTED_VALUE        = 8

class attributeSubStatus:
    STATUS_UNKNOWN           = -1
    STATUS_NONE              = 1
    # Sub types for OUT_OF_RANGE#
    MIN_RANGE_FAILURE        = 2
    MAX_RANGE_FAILURE        = 3
    RANGE_ARGS_INVALID       = 4
    # Sub types for TIME
    HOURS_OUT_OF_RANGE       = 5
    MINS_OUT_OF_RANGE        = 6

class FAttributesSyntax:
    '''(prettyName, type, type argument list, exclude list, optionType)'''
    def __init__(self):
        self.niceName     = None  # String used to identify the attribute\
                                                   #(Same as attribute name)
        self.dataType     = None  # Data type of the attribute.
        self.argumentList = None  # Allowed range of the attribute.
        self.excludeList  = None  # NA
        self.option       = None  # Type of the attribute(Mandatory/Optional).
        self.value        = None  # Value of the attrinbute.
        self.status       = attributeStatus.STATUS_OKAY #Status of the \
                                          #attribute for validation purposes.
        self.subStatus    = attributeSubStatus.STATUS_NONE #Sub Status of \
                                #attribute. Value depends on value of status.

class infoType:
    '''This is used in FPriceDistributorValidation class'''
    INFO    = 1
    WARNING = 2
    ERROR   = 3
    LOG     = 4

#***************************************************************************#
#******PRICE DISTRIBUTOR ATTRIBUTES AND ASSOCIATED SYNTAX*******************#
#***************************************************************************#

def admVersionSupportingNewPriceSemanticTable():
    # Find the ADM version
    server_data = ael.ServerData.select()[0]
    adm_version = server_data.adm_version.split(".")
    adm_version = tuple([ int(v) for v in adm_version])
    if adm_version >= ADMVersionSupportingPriceSemanticTable:
        return True
    else:
        return False
def admVersionSupportingDelayedFlag():
    # Find the ADM version
    server_data = ael.ServerData.select()[0]
    adm_version = server_data.adm_version.split(".")
    adm_version = tuple([ int(v) for v in adm_version])
    if adm_version >= ADMVersionSupportingDelayedFlag:
        return True
    else:
        return False

def admVersionSupportingDelayedTriStateFlag():
    # Find the ADM version
    server_data = ael.ServerData.select()[0]
    adm_version = server_data.adm_version.split(".")
    adm_version = tuple([ int(v) for v in adm_version])
    if adm_version >= ADMVersionSupportingDelayedTriStateFlag:
        return True
    else:
        return False
        
def admVersionSupportinglastFollowInterval():
    # Find the ADM version
    server_data = ael.ServerData.select()[0]
    adm_version = server_data.adm_version.split(".")
    adm_version = tuple([ int(v) for v in adm_version])
    if adm_version >= ADMVersionSupportingLastFollowInterval:
        return True
    else:
        return False

def admVersionSupportingIgnoreClearPrice():
    # Find the ADM version
    server_data = ael.ServerData.select()[0]
    adm_version = server_data.adm_version.split(".")
    adm_version = tuple([ int(v) for v in adm_version])
    if adm_version >= ADMVersionSupportingIgnoreClearPrice:
        return True
    else:
        return False
    
#ADD ALL THE NEW PRICE DISTRIBUTOR ATTRIBUTES HERE.
#NOTE:- THE ASSOCIATED STRING SHOULD BE STRICTLY AS PER COLUMN NAME.
# If PriceSemantic table or PriceSemanitcs choice list
if admVersionSupportingNewPriceSemanticTable():
    attributeSemantic         ='price_semantic_seqnbr'
else:
    attributeSemantic         ='semantic'

attributeService              ='service'
attributeStartTime            ='start_time'
attributeStopTime             ='stop_time'
attributeDistributorType      ='distributor_type'
attributeUseEntitlement       ='use_entitlement'
attributeUTC_Offset           ='utc_offset'
attributeUseUTC_Offset        ='use_utc_offset'
attributeUpdateInterval       ='update_interval'
attributeDiscardZeroPrice     ='discard_zero_price'
attributeDiscardZeroQuantity  ='discard_zero_quantity'
attributeDiscardNegativePrice ='discard_negative_price'
attributeIsDelayed            ='is_delayed'
attributeIgnoreClearPrice     ='ignore_clear_price'
attributeLastFollowInterval   ='last_follow_interval'
attributeForceUpdate          ='force_update'
attributeErrmsg               ='error_msg'
attributeDoNotResetFields     ='donot_reset_fields'
attributeXmlData              ='xml_data'

#***********PRICE DISTRIBUTOR ATTRIBUTES AND ASSOCIATED SYNTAX ************#
# FORMAT (prettyName, type, type argument list, exclude list, optionType)
# prettyName is used for logging purposes.
# type is the data type of the attribute
# type argument list format:
#       typeString: ignored
#       typeInt:    None or [minval, maxval]
#       typeBool:   None or [minval, maxval]
#       typeFloat:  None or [minval, maxval]
#       typeChoice: list of valid values, like ['0', '1', '2']
#       typeTime:   ignored
# exclude argument list format: [[type, type argument list], ...]
#  if a value matches a given type but also an exclude type, it will be\
#                                                     considered invalid.
# optionType = Optional or mandatory
attributeSyntaxList = {
                        attributeService: ('Service', dataTypes.CHOICELIST, None, None, optionType.OPTIONAL),
                        attributeSemantic: ('Semantic', dataTypes.CHOICELIST, None, None, optionType.OPTIONAL),
                        attributeStartTime: ('Start Time', dataTypes.TIME, None, None, optionType.OPTIONAL),
                        attributeStopTime: ('Stop Time', dataTypes.TIME, [0, 1439], None, optionType.OPTIONAL),
                        attributeDistributorType: ('Distributor Type', dataTypes.STRING, None, None, optionType.MANDATORY),
                        attributeUseEntitlement:('Use Entitlement', dataTypes.BOOL, [0,1], None, optionType.OPTIONAL),
                        attributeUTC_Offset: ('UTC Offset', dataTypes.INT,[-1200,1300], None, optionType.OPTIONAL),
                        attributeUseUTC_Offset: ('Use UTC Offset',  dataTypes.BOOL, [0,1], None, optionType.OPTIONAL),
                        attributeUpdateInterval: ('Update Interval', dataTypes.INT, None, None, optionType.OPTIONAL),
                        attributeDiscardZeroPrice: ('Discard Zero Price', dataTypes.BOOL, [0, 1], None, optionType.OPTIONAL),
                        attributeDiscardZeroQuantity: ('Discard Zero Quantity', dataTypes.BOOL, [0, 1], None, optionType.OPTIONAL),
                        attributeDiscardNegativePrice: ('Discard Negative Price', dataTypes.BOOL, [0, 1], None, optionType.OPTIONAL),
                        attributeForceUpdate: ('Force Update', dataTypes.BOOL, [0, 1], None, optionType.OPTIONAL),
                        attributeErrmsg: ('Error Message', dataTypes.STRING, [0,63], None, optionType.OPTIONAL),
                        attributeDoNotResetFields: ('Do Not Reset Fields', dataTypes.INT,[-1, 32767], None, optionType.OPTIONAL),
                        attributeXmlData: ('XML Data', dataTypes.STRING, None, None, optionType.OPTIONAL)
                      }
 
if admVersionSupportingIgnoreClearPrice() == True:
    attributeSyntaxList[attributeIgnoreClearPrice] = ('Ignore Clear Price', dataTypes.BOOL, [0, 1], None, optionType.OPTIONAL)
if admVersionSupportinglastFollowInterval() == True:
    attributeSyntaxList[attributeLastFollowInterval] = ('Last Follow Interval', dataTypes.BOOL, [0, 1], None, optionType.OPTIONAL)
if admVersionSupportingDelayedFlag() == True:
    if admVersionSupportingDelayedTriStateFlag() == False:
        attributeSyntaxList[attributeIsDelayed] = ('Is Delayed', dataTypes.BOOL, [0, 1], None, optionType.OPTIONAL)
    else:
        attributeSyntaxList[attributeIsDelayed] = ('Is Delayed', dataTypes.CHOICELIST, [0, 1], None, optionType.OPTIONAL)

#*********************************************************************#
#************FAttributeValidation CLASS STARTS HERE*******************#
#*********************************************************************#

class FAttributeValidation:
    '''It provides the functionality of validating attributes'''
    def __init__(self):
        self.attributeList    = {}
        self.failedAttributes = []
        self.validationStatus = validationStatus.INCOMPLETE
        pass

    #************************PUBLIC FUNCTIONS************************#
    def getAttributeSyntaxObj(self, attribName):
        '''Return attribute syntax of a given attribute'''
        if attribName in self.attributeList:
            return self.attributeList[attribName]
        else:
            return None

    def addAttribute(self, attributeName, attributeSyntax):
        '''Add attribute to internal attribute list'''
        if attributeName and attributeSyntax:
            self.attributeList[attributeName] = attributeSyntax

    def validateAttribute(self):
        '''Validate each attribute from internal attribute list'''
        self.__validateSyntax()
        return self.getValidationStaus()

    def getValidationStaus(self):
        '''Returns validation status, self.validationStatus'''
        return self.validationStatus

    def getFailedAttributeList(self):
        '''Return list of all the attribute that failed in validation'''
        if len(self.failedAttributes):
            return self.failedAttributes
        else:
            return None

    #**********************PRIVATE FUNCTIONS************************#
    def __validateSyntax(self):
        '''Validate each attribute and its value'''
        for attributeName in list(self.attributeList.keys()):
            '''After passing attribute to each validation function check
               for the attribute's status. If it is validationStatus.FAILURE
               then bypass further validation for that attribute.'''

            attributeSyntaxObj = self.attributeList[attributeName]
            attribStatus = attributeSyntaxObj.status
            self.__validateMandatoryAttributes(attributeName)
            if attribStatus == attributeStatus.STATUS_OKAY:
                self.__validateDataType(attributeName)
                if attribStatus == attributeStatus.STATUS_OKAY:
                    self.__validateAttributeValue(attributeName)

    def __validateMandatoryAttributes(self, attributeName):
        '''Verify that all the mandatory attributes are properly populated'''
        attributeSyntaxObj = self.attributeList[attributeName]
        if (optionType.MANDATORY == attributeSyntaxObj.option) and \
                              (None == attributeSyntaxObj.value or \
                             'None' == attributeSyntaxObj.value or \
                                  0 == attributeSyntaxObj.value or \
                                 "" == attributeSyntaxObj.value):
            self.__setAllStatusFlags(attributeName,\
                        attributeStatus.MANDATORY_ATTRIB_MISSING)

    def __validateDataType(self, attributeName):
        '''Validate Data types of attributes and its Syntaxes'''
        attributeSyntaxObj = self.attributeList[attributeName]
        dataType = attributeSyntaxObj.dataType
        if not dataTypes.ALL.count(dataType):
            self.__setAllStatusFlags(attributeName,\
                        attributeStatus.INVALID_DATATYPE)


    def __validateAttributeValue(self, attributeName):
        '''validate value. check for value range and it actual data type'''
        attributeSyntaxObj = self.attributeList[attributeName]
        dataType = attributeSyntaxObj.dataType

        if dataTypes.INT == dataType:
            self.__validateINTvalue(attributeName)
        elif dataTypes.STRING == dataType:
            self.__validateSTRINGvalue(attributeName)
        elif dataTypes.TIME == dataType:
            self.__validateTIMEvalue(attributeName)
        elif dataTypes.BOOL == dataType:
            self.__validateBOOLvalue(attributeName)
        elif dataTypes.FLOAT == dataType:
            #Validation for float variables will be put here
            pass
        elif dataTypes.CHOICELIST == dataType:
            #Validation for float variables will be put here
            pass

    def __raiseAlarm(self, infoMessage):
        '''Raise exception and log the information'''
        print(infoMessage)
        ael.log(infoMessage)
        #raise Exception(infoMessage)

    def __setAllStatusFlags(self, attributeName,  \
                                attributeStatus,\
                                attributeSubStatus = \
                        attributeSubStatus.STATUS_NONE):
        '''Set all teh status variables of the class. it includes
           1). FAttributesSyntax.status
           2). FAttributesSyntax.subStatus
           3). validationStatus
           4). failedAttributes'''
        if attributeName and attributeStatus:

            attributeSyntaxObj = self.attributeList[attributeName]
            self.failedAttributes.append(attributeName)
            self.validationStatus = validationStatus.FAILURE
            if attributeStatus:
                attributeSyntaxObj.status = attributeStatus
            if attributeSubStatus:
                attributeSyntaxObj.subStatus = attributeSubStatus

    def __validateINTvalue(self, attributeName):
        '''1). Validate valid value for INT.
           2). Validate if the value falls within the given range.'''
        attributeSyntaxObj = self.attributeList[attributeName]
        attribValue        = attributeSyntaxObj.value

        testValue = None
        try:
            testValue = int(attribValue)
        except:
             self.__setAllStatusFlags(attributeName,\
                    attributeStatus.DATATYPE_VALUE_MISMATCH)
        #Verify Range
        if attributeSyntaxObj.status == attributeStatus.STATUS_OKAY:
           self.__validateINTvalueRange(attributeName, testValue)

    def __validateINTvalueRange(self, attributeName, attribValue):
        '''validate the attribute INT value for the given range'''
        attributeSyntaxObj = self.attributeList[attributeName]
        attribRange        = attributeSyntaxObj.argumentList

        if attribRange and attribValue:
            if (len(attribRange) > 0):
                try:
                    minValue = int(attribRange[0])
                    #Check if the value is less than minimum range.
                    if attribValue < minValue:
                        self.__setAllStatusFlags(attributeName,
                                  attributeStatus.OUT_OF_RANGE,
                          attributeSubStatus.MIN_RANGE_FAILURE)
                        return
                except:
                    self.__setAllStatusFlags(attributeName,
                                  attributeStatus.OUT_OF_RANGE,
                          attributeSubStatus.RANGE_ARGS_INVALID)
                    return

            if (len(attribRange) > 1):
                try:
                    maxValue = int(attribRange[1])
                    #Check if the value is more than maximum range.
                    if attribValue > maxValue:
                        self.__setAllStatusFlags(attributeName,
                                  attributeStatus.OUT_OF_RANGE,
                          attributeSubStatus.MAX_RANGE_FAILURE)
                        return
                except:
                    self.__setAllStatusFlags(attributeName,
                                  attributeStatus.OUT_OF_RANGE,
                          attributeSubStatus.RANGE_ARGS_INVALID)
                    return

    def __validateSTRINGvalue(self, attributeName):
        '''1). Validate valid value for STRING.
           2). Validate if the value falls within the given range.'''
        attributeSyntaxObj = self.attributeList[attributeName]
        attribValue        = attributeSyntaxObj.value

        testValue = None
        try:
            attribLen = len(attribValue)
        except:
            self.__setAllStatusFlags(attributeName,\
                    attributeStatus.DATATYPE_VALUE_MISMATCH)
        #Verify Range
        if attributeSyntaxObj.status == attributeStatus.STATUS_OKAY:
           self.__validateINTvalueRange(attributeName, attribLen)


    def __validateTIMEvalue(self, attributeName):
        '''1). Validate valid value for TIME.
           2). Validate if the value falls within the given range.
           3). Validate format of the time, HH:MM
           NOTE: We are not doing validation on custom range (range
           provided in parameters syntax list) for Time.'''

        #****************INTERNAL FUNCTIONS******************#
        def formatMinutesToHHMM(time_val):
            '''Convert minutes string to HHMM format'''
            hours = minutes = time_hm = ""
            hours = str(int(int(time_val)/60))
            hours = hours.zfill(2)
            minutes = str(int(time_val)%60)
            minutes = minutes.zfill(2)
            time_hm = hours + minutes
            return time_hm

        def validateTimeFormat(timeStrLen):
            '''Validate if the value if withing the given range'''
            if timeStrLen < 0 or timeStrLen > 4:
                self.__setAllStatusFlags(attributeName,
                                attributeStatus.UNSUPPORTED_VALUE)


        def validateAllowedTimeRange(timeInHHMM):
            '''Validate the attribute format with different formats allowed'''
            try:
                if 4 == len(timeInHHMM):
                    hour = int(str(timeInHHMM)[0:2]) #Pulling hours from HHMM.
                    mins = int(str(timeInHHMM)[2:4]) #Pulling mins from HHMM.

                    if hour < 0 or hour > 23:
                        self.__setAllStatusFlags(attributeName,
                                    attributeStatus.OUT_OF_RANGE,
                            attributeSubStatus.HOURS_OUT_OF_RANGE)
                        return
                    if mins < 0 or mins > 59:
                        self.__setAllStatusFlags(attributeName,
                                    attributeStatus.OUT_OF_RANGE,
                            attributeSubStatus.MINS_OUT_OF_RANGE)

                elif 3 == len(timeInHHMM):
                    hour = int(str(timeInHHMM)[0:1]) #Pulling hours from HMM.
                    mins = int(str(timeInHHMM)[1:3]) #Pulling mins from HMM.

                    if hour < 0 or hour > 9:
                        self.__setAllStatusFlags(attributeName,
                                    attributeStatus.OUT_OF_RANGE,
                            attributeSubStatus.HOURS_OUT_OF_RANGE)
                        return
                    if mins < 0 or mins > 59:
                        self.__setAllStatusFlags(attributeName,
                                    attributeStatus.OUT_OF_RANGE,
                            attributeSubStatus.MINS_OUT_OF_RANGE)

            except:
                self.__setAllStatusFlags(attributeName,
                                attributeStatus.UNSUPPORTED_VALUE)
                return attributeName

        #*****************************************************#

        attributeSyntaxObj = self.attributeList[attributeName]
        attribValue = attributeSyntaxObj.value
        timeInHHMM = ''
        timeStrLen = None

        if attribValue:
            try:
                timeInHHMM = str(formatMinutesToHHMM(attribValue))
                timeStrLen = len(timeInHHMM)
            except:
                self.__setAllStatusFlags(attributeName,\
                    attributeStatus.DATATYPE_VALUE_MISMATCH)
            #validate range
            if attributeSyntaxObj.status == attributeStatus.STATUS_OKAY:
                validateTimeFormat(timeStrLen)
            #Validate format
            if attributeSyntaxObj.status == attributeStatus.STATUS_OKAY:
                validateAllowedTimeRange(timeInHHMM)


    def __validateBOOLvalue(self, attributeName):
        '''1). Validate valid value for BOOL.
           2). Validate if the value falls within the given range.'''
        attributeSyntaxObj = self.attributeList[attributeName]
        attribValue = attributeSyntaxObj.value
        attribArgsList = attributeSyntaxObj.argumentList

        if not attribValue in attribArgsList:
            self.__setAllStatusFlags(attributeName,
                                attributeStatus.OUT_OF_RANGE)

#*********************************************************************#
#************FAttributeValidation CLASS ENDS HERE*********************#
#*********************************************************************#



#*********************************************************************#
#***********FValidatePriceDistributor CLASS STARTS HERE***************#
#*********************************************************************#

class FValidatePriceDistributor:
    '''It provides the functionality to validate price distributor attributes'''

    def __init__(self, priceDistributorAELObject):
        self.priceDistributorObject     = priceDistributorAELObject
        self.attributeValidationObject  = FAttributeValidation()
        self.validationStatus           = validationStatus.SUCCESS

    def validatePriceDistributor(self):
        '''Read all the price distributor attributes and Syntaxes from the
           table. Validates all the attributes of price distributor AEL object'''
        if validationStatus.FAILURE  == self.__handlePreValidationProcess():
            self.__raiseAlarm(infoType.ERROR, "Re-install "\
                                    "FPriceDistributorValidation script.")
        try:
           self.__validatePriceDistributorAttributes()
        except RuntimeError as extraInfo:
            self.__raiseAlarm(infoType.ERROR, "<%s> exception occurred while"\
                    " validating price distributor attributes."%str(extraInfo))

        if validationStatus.FAILURE  == self.validationStatus:
            self.__raiseAlarm(infoType.LOG, "Validation report for Price "\
                "Distributor: %s"%(self.__getAttributeValue("disid")))
            self.__handlePostValidationFailureProcess()
            self.__raiseAlarm(infoType.LOG, "VALIDATION STATUS : UNSUCCESSFUL")
            '''If the validation failed script will exit from this here where
               an exception has been raised.'''
            self.__raiseAlarm(infoType.ERROR, "")
        # commented, since NOT needed in log if SUCCESSFUL
        '''else:
            self.__raiseAlarm(infoType.LOG, "VALIDATION STATUS : SUCCESSFUL")'''

    def formatMinutesToHHMM(self, time_val):
        '''Convert minutes string to HHMM format'''
        hours = minutes = time_hm = ""
        hours = str(int(int(time_val)/60))
        hours = hours.zfill(2)
        minutes = str(int(time_val)%60)
        minutes = minutes.zfill(2)
        time_hm = hours + minutes
        return time_hm

    def __verifyAttributeSyntaxListFormat(self):
        '''Verify the format of attributeSyntaxList table'''
        try:
            if not len(attributeSyntaxList):
                self.__raiseAlarm(infoType.WARNING,\
                                "'attributeSyntaxList' is empty")
                return validationStatus.FAILURE
        
            for attributeName in list(attributeSyntaxList.keys()):
                attributeProperty = attributeSyntaxList[attributeName]
                if len(attributeProperty) < 5:
                    self.__raiseAlarm(infoType.WARNING,\
                    "Attribute %s do not contain proper syntax options"\
                                                        %attributeName)
                    return validationStatus.FAILURE

        except:
            self.__raiseAlarm(infoType.ERROR, "Attribute Syntax list in "\
                              "Validation file is corrupted. Re-install "\
                                    "FPriceDistributorValidation script.")
            return validationStatus.FAILURE

        return validationStatus.SUCCESS

    def __handlePreValidationProcess(self):
        '''Handle all the pre work before validation startes.
            1). Verify the attributes syntax list format.
            2). Add all the attributes to FAttributeValidation object'''
        if not self.__verifyAttributeSyntaxListFormat() or \
                    not self.__initPriceDistributorAttributes():
           return validationStatus.FAILURE
        else:
            return validationStatus.SUCCESS

    def __initPriceDistributorAttributes(self):
        '''Read all the price distributor attributes from internal list and
        send it to FValidationAttributes class'''
        try:
            for attributeName in list(attributeSyntaxList.keys()):
                attributeProperty = attributeSyntaxList[attributeName]
                if attributeProperty:
                    attributeSyntaxObj = FAttributesSyntax()
                    attributeSyntaxObj.niceName     = attributeProperty[0]
                    attributeSyntaxObj.dataType     = attributeProperty[1]
                    attributeSyntaxObj.argumentList = attributeProperty[2]
                    attributeSyntaxObj.excludeList  = attributeProperty[3]
                    attributeSyntaxObj.option       = attributeProperty[4]
                    attributeSyntaxObj.value        = \
                                    self.__getAttributeValue(attributeName)

                    self.attributeValidationObject.addAttribute(attributeName,\
                                                        attributeSyntaxObj)
        except:
            self.__raiseAlarm(infoType.ERROR, "Unknown exception occurred in"\
                                        " __initPriceDistributorAttributes()")
            return validationStatus.FAILURE

        return validationStatus.SUCCESS

    def __validatePriceDistributorAttributes(self):
        '''validates syntax and values of every attribute of price
            distributor'''
        self.validationStatus = self.attributeValidationObject.validateAttribute()
        try:
            self.__validatePriceDistributorRules()
        except :
            self.__raiseAlarm(infoType.ERROR, "Unknown exception occurred"\
                                    " __validatePriceDistributorRules().")
            self.validationStatus = validationStatus.FAILURE


    def __validatePriceDistributorRules(self):
        '''Do validation for price distributor specific rules.
           All the new rules that will be added in future will be added here.'''

        priceDistributorName = self.__getAttributeValue("disid")
        priceDistributorType = self.__getAttributeValue(attributeDistributorType)
        service = self.__getAttributeValue(attributeService)
        semantic = self.__getAttributeValue(attributeSemantic)
        xml_data = self.__getAttributeValue(attributeXmlData)

        if xml_data:
           if(FPriceXMLValidation.ValidateXMLData(xml_data) == validationStatus.FAILURE):
                self.validationStatus = validationStatus.FAILURE

        #RULE FOR BBG: Service, Semantic setting if Distributor type is BLOOMBERG.
        if 'Bloomberg' == priceDistributorType:
            #Semantic is required if Distributor type is BLOOMBERG.
            if semantic == None or semantic.display_id() == '':
                self.__raiseAlarm(infoType.WARNING, "Semantic is required for"\
                                        " price distributor of type BLOOMBERG.")
                self.validationStatus = validationStatus.FAILURE
        #RULE FOR MARKETMAP: Service and Semantic setting if Distributor type is MARKETMAP.
        elif 'MarketMap' == priceDistributorType:
            #Service is not required if Distributor type is MARKETMAP.
            if service != None or \
                        (service != None and service.display_id() != ''):
                self.__raiseAlarm(infoType.WARNING, "Service, %s is not "\
                      "required for price distributor of type MARKETMAP."\
                                                    %service.display_id())
                self.validationStatus = validationStatus.FAILURE

            #Semantic is required if Distributor type is MARKETMAP.
            if semantic == None or semantic.display_id() == '':
                self.__raiseAlarm(infoType.WARNING,"Semantic is required for "\
                                                                        "price distributor of type MARKETMAP.")
                self.validationStatus = validationStatus.FAILURE

        #RULE FOR REUTERS: Service and Semantic setting if Distributor type is Reuters.
        elif 'Reuters' == priceDistributorType:
            #Service is required if Distributor type is REUTERS.
            if service == None or service.display_id() == '':
                self.__raiseAlarm(infoType.WARNING, "Service is required for"\
                                       " price distributor of type REUTERS.")
                self.validationStatus = validationStatus.FAILURE
            #Semantic is required if Distributor type is REUTERS.
            if semantic == None or semantic.display_id() == '':
                self.__raiseAlarm(infoType.WARNING, "Semantic is required for"\
                                         " price distributor of type REUTERS.")
                self.validationStatus = validationStatus.FAILURE

        #RULE FOR AMAS: Service and Semantic setting if Distributor type is AMS.
        elif 'AMS' == priceDistributorType:
            #Service is not required if Distributor type is AMS.
            if service != None or \
                        (service != None and service.display_id() != ''):
                self.__raiseAlarm(infoType.WARNING, "Service, %s is not "\
                        "required for price distributor of type AMS."\
                                                    %service.display_id())
                self.validationStatus = validationStatus.FAILURE
        #RULE FOR OPEN: Service and Semantic setting if Distributor type is AMS.
        elif 'Open Price Feed' == priceDistributorType:
            #Service is not required if Distributor type is OPEN.
            if service != None or \
                        (service != None and service.display_id() != ''):
                self.__raiseAlarm(infoType.WARNING, "Service, %s is not "\
                        "required for price distributor of type 'Open Price Feed'."\
                                                    %service.display_id())
                self.validationStatus = validationStatus.FAILURE
                    
            #Semantic is required if Distributor type is Open Price Feed.
            if semantic == None or semantic.display_id() == '':
                self.__raiseAlarm(infoType.WARNING, "Semantic is required for"\
                                    " price distributor of type Open Price Feed.")
                self.validationStatus = validationStatus.FAILURE

        return self.validationStatus

    def __getAttributeValue(self, attributeName):
        '''Get value from price distributor AEL object'''
        returnValue = None
        try:
            returnValue = getattr(self.priceDistributorObject, attributeName)
        except Exception as extraInfo:
            self.__printAttributeObject(attributeName)
            self.__raiseAlarm(infoType.WARNING, "__getAttributeValue() failed for "\
                    "attribute = %s. ErrorInfo : %s"%(attributeName, str(extraInfo)))

        return returnValue

    def __handlePostValidationFailureProcess(self):
        '''This function will log all the validation info and status'''
        failedAttributeList = self.attributeValidationObject.\
                                        getFailedAttributeList()
        if failedAttributeList:
            for attribName in failedAttributeList:
                infoString = ''
                infoString = self.__getStatusInformationString(attribName)
                self.__raiseAlarm(infoType.WARNING, infoString)

    def __getStatusInformationString(self, attribName):
        '''Return status information string'''
        infoString = ''
        attributeSyntaxObj = self.attributeValidationObject.\
                                       getAttributeSyntaxObj(attribName)
        attribStatus       = attributeSyntaxObj.status
        attributeNiceName  = attributeSyntaxObj.niceName

        #**********************INTERNAL FUNCTION*******************************#
        def getOutOfRangeInfoString():
            '''Returns information string for status OUT_OF_RANGE'''
            infoString = ''
            if attribStatus ==  attributeStatus.OUT_OF_RANGE:
                attributeRange  = attributeSyntaxObj.argumentList
                attribSubStatus = attributeSyntaxObj.subStatus
                attribValue     = attributeSyntaxObj.value
                attribDataType  = attributeSyntaxObj.dataType

                if attributeSubStatus.MIN_RANGE_FAILURE == attribSubStatus:
                    infoString = "Attribute's, %s value(%s) less than the "\
                                                          "lower range[%s]"\
                               %(attributeNiceName, attribValue, attributeRange)

                elif attributeSubStatus.MAX_RANGE_FAILURE == attribSubStatus:
                    infoString = "Attribute's, %s value(%s) greater than the "\
                                                             "upper range[%s]"\
                               %(attributeNiceName, attribValue, attributeRange)

                elif attributeSubStatus.HOURS_OUT_OF_RANGE == attribSubStatus:
                    timeInHHMM =  self.formatMinutesToHHMM(attribValue)
                    hhmmstring = "%s:%s"%(str(timeInHHMM)[0:2],
                                                        str(timeInHHMM)[2:4])
                    infoString = "Attribute, %s has invalid Hour range, %s."\
                    " Allowed Range is [00:00 - 23:59]."\
                                                %(attributeNiceName, hhmmstring)

                elif attributeSubStatus.MINS_OUT_OF_RANGE == attribSubStatus:
                    timeInHHMM =  self.formatMinutesToHHMM(attribValue)
                    hhmmstring = "%s:%s"%(str(timeInHHMM)[0:2],
                                                        str(timeInHHMM)[2:4])
                    infoString = "Attribute, %s has invalid Mins range, %s"\
                    " Allowed Range is [00:00 - 23:59]."\
                                               %(attributeNiceName, hhmmstring)
                elif attribDataType == dataTypes.BOOL:
                    infoString = "Attribute, %s has invalid value, %s. Allowed "\
                           "values are 0 and 1."%(attributeNiceName, attribValue)

            return infoString
        #************************************************************************#

        if  attribStatus == attributeStatus.MANDATORY_ATTRIB_MISSING:
            infoString = "Mandatory attribute, %s  is missing"\
                                                    %attributeNiceName
        elif attribStatus == attributeStatus.OUT_OF_RANGE:
            infoString = getOutOfRangeInfoString()
        elif attribStatus == attributeStatus.INVALID_DATATYPE:
            dataType = attributeSyntaxObj.dataType
            infoString = "Unknown Data type, %s for attribute %s"\
                                       %(dataType, attributeNiceName)
        elif attribStatus == attributeStatus.UNKNOWN_ATTRIBUTE:
            infoString = "Unknown attribute, %s."%attributeNiceName
        elif attribStatus == attributeStatus.DATATYPE_VALUE_MISMATCH:
            infoString = "%s data type is expected for attribute %s for"\
            " value %s."%(attributeSyntaxObj.dataType, attributeNiceName,
                                                attributeSyntaxObj.value)
        elif attribStatus == attributeStatus.UNSUPPORTED_VALUE:
            if  dataTypes.TIME == attributeSyntaxObj.dataType:
                timeInHHMM =  self.formatMinutesToHHMM\
                                            (attributeSyntaxObj.value)
                infoString = "Attribute, %s has invalid time value, %s"\
                " . Valid formats are HH:MM and H:MM"\
                %(attributeNiceName, timeInHHMM)

        return infoString


    def __raiseAlarm(self, infomationType, infoMessage = None):
        '''Raise exception and log the information'''
        infoStr = ""

        if infoType.WARNING == infomationType:
            if infoMessage:
                infoStr = "WARNING: %s"%infoMessage
                ael.log(infoStr)
                print(infoStr)

        if infoType.ERROR == infomationType:
            if not infoMessage or infoMessage == "":
                print("Validation failed.")
            else:
                infoStr = "ERROR: %s"%infoMessage

            print(infoStr)
            raise Exception(infoStr)

        if infoType.INFO == infomationType:
            if infoMessage:
                infoStr = "INFO: %s"%infoMessage
                print(infoStr)
                ael.log(infoStr)

        if infoType.LOG == infomationType:
            if infoMessage:
                ael.log(infoMessage)
                print(infoMessage)

    def __printAttributeObject(self, attribName):
        attributeSyntaxObj = self.attributeValidationObject.\
                                       getAttributeSyntaxObj(attribName)
        print('Attribute Name   = ', attribName)
        print('Object type      = ', type(attributeSyntaxObj))
        print('Nice Name        = ', attributeSyntaxObj.niceName)
        print('Attribute Value  = ', attributeSyntaxObj.value)
        print('Status Value     = ', attributeSyntaxObj.status)
        print('Sub Status Value = ', attributeSyntaxObj.subStatus)
        print('Data type        = ', attributeSyntaxObj.dataType)
        print('Argument list    = ', attributeSyntaxObj.argumentList)

#*********************************************************************#
#***********FValidatePriceDistributor CLASS ENDS HERE*****************#
#*********************************************************************#    
def validate_transaction(p_AelObject):
    validationObj = FValidatePriceDistributor(p_AelObject)
    if validationStatus.SUCCESS == validationObj.validatePriceDistributor():
        return True
    else:
        return False


