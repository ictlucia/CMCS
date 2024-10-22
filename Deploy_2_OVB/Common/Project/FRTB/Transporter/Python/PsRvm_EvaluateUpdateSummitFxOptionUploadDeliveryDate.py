import acm

"""------------------------------------intro---------------------------------------
@Module: PsRvm_EvaluateUpdateSummitFxOptionUploadDeliveryDate.py
@Description: 
    Fx Option UI field "Delivery date" is a calcualted field value and not an ADM field that can be commited.
    User must enter PayDayOffset per instrument, which then calculates Delivery date as Expiry + PayDayOffset.
    Incoming instrument definition files from incumbant system (Summit(?)) cannot provide payDayOffset accounting 
    for business holiday dates.
    This script will parse a csv file containing data to state delivery date per instrument, 
    and amend payDayOffset if the dates in FA and incumbant are misaligned.
@Notes:
    - This script is a concept script for PT Bank Mandiri system support to amend for purpose.
    - method acm.Finstrument.DeliveryDate() returns the calculated delivery date
    - csv delimnator assumed to be comma "," -> can be changed if needed
@Author: richard.milford@fisglobal.com
---------------------------------------------------------------------------------"""

import FRunScriptGUI #for file selector
import FLogger
logger = FLogger.FLogger(level=1,
                    logToPrime=True,
                    logToConsole=False)
log_levl_dict = {'INFO' : 1, 'DEBUG' : 2, 'WARN' : 3, 'ERROR' : 4}
                    
"""------------------------------------body------------------------------------"""

def tryNewDate(__instrument,__externalDeliveryDate):

    fAPayDayOffset = __instrument.PayDayOffset()
    dateDifferenceDaysInt = acm.Time.DateDifference(__externalDeliveryDate,__instrument.DeliveryDate())
    
    tryNewPayDayOffset = fAPayDayOffset + dateDifferenceDaysInt
    __instrument.PayDayOffset(tryNewPayDayOffset)
    
    newDateDifferenceDaysInt = acm.Time.DateDifference(__externalDeliveryDate,__instrument.DeliveryDate())
    #logger.DLOG("debug %s,%s,%s" %(__instrument.Name(),newDateDifferenceDaysInt,tryNewPayDayOffset))
    return [newDateDifferenceDaysInt,tryNewPayDayOffset]

def compareAdjustCommit(_instrument,_externalDeliveryDate):

    fADeliveryDate = _instrument.DeliveryDate()
    fAPayDayOffset = _instrument.PayDayOffset()
    originalDateDifferenceDaysInt = acm.Time.DateDifference(_externalDeliveryDate,fADeliveryDate)
    #tryNewDate = acm.Time.DateAdjustPeriod(fADeliveryDate,dateDifferenceDaysInt     #not sure how to submit two calendars into DateAdjustPeriod, so will iterate using the instrument
    
    if originalDateDifferenceDaysInt != 0:
        
        newDateDifferenceDaysInt = 999
        loopBreakerCount = 0
        while (newDateDifferenceDaysInt != 0):
            loopBreakerCount = loopBreakerCount+1
            [newDateDifferenceDaysInt,newPayDayOffset] = tryNewDate(_instrument,_externalDeliveryDate)
            if loopBreakerCount > 15: 
                logger.ELOG('Could NOT successfully iterate a newPayDayOffset for instrument "%s". Suggest to validate that the expiry date "%s" is a valid business day.' %(_instrument.Name(),str(_externalDeliveryDate)))
                try:
                    _instrument.PayDayOffset(originalDateDifferenceDaysInt)
                    _instrument.Commit()
                except:
                    logger.ELOG('Could not commit instrument "%s" - please MANUALLY inspect' %str(_instrument.Name()))
                break
        
        if newDateDifferenceDaysInt == 0:
            try:
                _instrument.PayDayOffset(newPayDayOffset)
                _instrument.Commit()
                logger.LOG('Updated Fx Option instrument "%s" from payOffset=%s,deliveryDate=%s to payOffset=%s,deliveryDate=%s ' %(_instrument.Name(),fAPayDayOffset,fADeliveryDate,newPayDayOffset,_instrument.DeliveryDate()))
            except:
                logger.ELOG('Could not commit instrument "%s"' %str(_instrument.Name()))
                pass
         

def parseInputFile(_inputFileFullPath,_insColIndex,_deliveryDateColIndex,_startParsingAtRow):

    fileToParse = open(_inputFileFullPath.AsString(), encoding='utf-8-sig')
    #NOTE if the data in the input file contains "ï»¿" then open with open(_inputFileFullPath.AsString(), encoding='utf-8-sig') else open with fileToParse = open(_inputFileFullPath.AsString()) 
    for fileCsvRow in fileToParse.readlines()[_startParsingAtRow:]:
        [instrumentName,externalExpiryDate] = [fileCsvRow.split(",")[_insColIndex-1],fileCsvRow.split(",")[_deliveryDateColIndex-1]]  #user input start at 1, list[] starts at 0
        logger.DLOG("debug [instrumentName,externalExpiryDate] = %s,%s" %(instrumentName,externalExpiryDate))
        instrument = acm.FInstrument[instrumentName]
        if instrument: 
            compareAdjustCommit(instrument,externalExpiryDate)
        else:
            logger.WLOG('Fx Option instrument "%s" NOT FOUND' %str(instrumentName))        

"""--------------------------------define task UI------------------------------"""

# Tool Tips
fileSelection = FRunScriptGUI.InputFileSelection('CSV Files (*.csv)|*.csv|')
ttfilePath = 'CSV file containing instrument name and delivery date'
ttinsColumnIndexStartAt1 = 'Column index in external file, contianting the name of the instrument. Columns start at 1 and not at zero. Hence column A in Excel woudl be 1 and column B woudl be 2.'
ttdateColumnIndexStartAt1 = 'Column index in external file, contianting the name of the instrument. Columns start at 1 and not at zero. Hence column A in Excel woudl be 1 and column B woudl be 2'
ttLogMode = 'Defines the amount of logging produced.'
ttLogToCon = 'Whether logging should be done in the Log Console or not.'
ttLogToFile = 'Defines whether logging should be done to file.'
ttLogFile = r'Name of the logfile. Could include the whole path c:\log\...'

ael_variables = [
        # [VariableName,
        #       DisplayName,
        #       Type, CandidateValues, Default,
        #       Mandatory, Multiple, Description, InputHook, Enabled]
    ('file_path', 'File', fileSelection, None, fileSelection, 1, 1, ttfilePath, None, 1),
    ('insColumnIndexStartAt1', 'Column index of instrument name (>=1):', 'int', None, 1, False, ttinsColumnIndexStartAt1, None, 1),
    ('dateColumnIndexStartAt1', 'Column index of delivery date (>=1):', 'int', None, 2, False, ttdateColumnIndexStartAt1, None, 1),
    ('firstRowIsHeader', 'First row in input file is header row?:', 'bool', [True, False], True, False, None, None, 1),
    ('Logmode', 'Log mode_Logging', 'string', ['INFO','DEBUG','WARN','ERROR'], 'INFO', False, False, ttLogMode),
    ('LogToConsole', 'Log to console_Logging', 'int', [1, 0], 1, False, False, ttLogToCon),
    ('LogToFile', 'Log to file_Logging', 'int', [1 ,0], 0, False, False, ttLogToFile),
    ('Logfile', 'Log file_Logging', 'string', None, __name__ + '.log', False, False, ttLogFile),]

def ael_main(params):

    if params['LogToFile'] and params['Logfile']:
        logger.Reinitialize(log_levl_dict[params['Logmode']], None, None, params['LogToConsole'], True, params['Logfile'], None, None, None)
    else:
        logger.Reinitialize(log_levl_dict[params['Logmode']], None, None, params['LogToConsole'], True, None, None, None, None)
    logger.LOG('INITIATING PsRm_EvaluateUpdateSummitFxOptionUploadDeliveryDate script')
    if params['firstRowIsHeader']:
        startParsingAtRow = 1
    else:
        startParsingAtRow = 0
    parseInputFile(params['file_path'],params['insColumnIndexStartAt1'],params['dateColumnIndexStartAt1'],startParsingAtRow)
