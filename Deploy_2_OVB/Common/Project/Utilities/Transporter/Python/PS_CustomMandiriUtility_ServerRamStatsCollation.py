import acm
import os
import datetime
import FBDPGui
import FRunScriptGUI
import socket

from FLogger import FLogger
logger = FLogger(level=1)
log_level_dict = {'INFO' : 1, 'DEBUG' : 2, 'WARN' : 3, 'ERROR' : 4}

datetimePidAndServiceNameDict = {}  #dict(hhmmss_ddmmyyyy_PID: serviceName)
datetimePidAndServiceNameWithRAMDict = {}  #dict(hhmmss_ddmmyyyy_PID: [date,serviceName,RAM])

'''
    first: cycle all Wmic to get all keys hhmmss_ddmmyyyy_PID
    then: cycle all Tasklist to populate datetimePidAndServiceNameWithRAMDict by [date,serviceName,RAM]
'''

def getTimePointFromFileName(_fileName):

    timehhmmss = _fileName[:6]
    dateddmmyyyy = _fileName[7:15]
    logger.DLOG("getTimePointFrom_fileName dateddmmyyyy %s" %[dateddmmyyyy])
    logger.DLOG("getTimePointFrom_fileName timehhmmss %s" %[timehhmmss])
    logger.DLOG("getTimePointFrom_fileName yyyy mm dd hh mm %s" %[int(dateddmmyyyy[4:8]), int(dateddmmyyyy[0:2]), int(dateddmmyyyy[2:4]), int(timehhmmss[0:2]), int(timehhmmss[2:4])])
    theDate = datetime.date(int(dateddmmyyyy[4:8]), int(dateddmmyyyy[0:2]), int(dateddmmyyyy[2:4]))
    theTime = datetime.time(int(timehhmmss[0:2]), int(timehhmmss[2:4]))
    timePoint = datetime.datetime.combine(theDate,theTime)
    timePoint = timePoint.strftime('%Y-%m-%d %H:%M')
    logger.DLOG("getTimePointFromFileName [type(timePoint),timePoint] %s" %[type(timePoint),timePoint])
    return timePoint
        
    
def builddatetimePidAndServiceNameDict(_filePath,_fileList):
    
    for fileName in _fileList:
        logger.LOG('Parsing file %s ' %fileName)
        statsType = fileName[16:]
        if statsType == "wmic.txt":
            newKeyPrefix = fileName[0:14].strip()
            timePoint = getTimePointFromFileName(fileName)
            logger.DLOG("builddatetimePidAndServiceNameDict timePoint %s" %[timePoint])
                       
            file = open(_filePath+fileName, encoding='utf-16')
            fileLines = file.readlines()
            file.close()

            for singleFileLine in fileLines:
                isFaService = singleFileLine.find("Front Arena") > 0 
                #logger.DLOG("[isFaProcess,singleFileLine] %s" %[isFaService,singleFileLine])
                if isFaService:
                    singleFileLine = singleFileLine.replace(".exe",".exe,")
                    singleFileLine = singleFileLine.replace(".EXE",".exe,")
                    singleFileLine = singleFileLine.replace(" ", "")
                    singleFileLine = singleFileLine.rstrip()  # remove newline character
                    [serviceName,processId] = singleFileLine.split(",")
                    #logger.DLOG("found process [isFaProcess,singleFileLine] %s" %[isFaService,singleFileLine])
                    
                    newKey = newKeyPrefix + "_" + processId
                    logger.DLOG("adding newKey %s to datetimePidAndServiceNameDict" %[newKey])
                    if newKey not in datetimePidAndServiceNameDict:
                        datetimePidAndServiceNameDict[newKey] = serviceName

def builddatetimePidAndServiceNameWithRAMDict(_filePath,_fileList):
    
    for fileName in _fileList:
        statsType = fileName[16:]
        if statsType == "tasklist.txt":
            newKeyPrefix = fileName[0:14].strip()
            timePoint = getTimePointFromFileName(fileName)
            
            logger.DLOG("parsing fileName %s" %[fileName])
            file = open(_filePath+fileName, encoding='utf-8')
            fileLines = file.readlines()
            file.close()

            for singleFileLine in fileLines[1:]:
                #singleFileLine = singleFileLine.replace('"','')  file already contains commas, cannot split by comma
                singleFileLine = singleFileLine.rstrip()  # remove newline character
                
                firstComma = singleFileLine.find(",")
                fourthQuotation = singleFileLine.find('"',firstComma+2)
                secondLastQuotation = singleFileLine.rfind('"',0,len(singleFileLine)-1)
                logger.DLOG("builddatetimePidAndServiceNameWithRAMDict singleFileLine %s" %[singleFileLine])
                logger.DLOG("builddatetimePidAndServiceNameWithRAMDict firstComma,fourthQuotation,secondLastQuotation %s" %[firstComma,fourthQuotation,secondLastQuotation])
                [PID,RAM] = [singleFileLine[firstComma+2:fourthQuotation],singleFileLine[secondLastQuotation+1:]]
                logger.DLOG("builddatetimePidAndServiceNameWithRAMDict before RAM string replacement [PID,RAM] %s" %[PID,RAM])
                RAM = RAM.replace(" K","")
                RAM = RAM.replace('"',"")
                RAM = RAM.replace(",","") #US locale uses comma for decimal seperator
                RAM = RAM.replace(".","") #Indonesia locale uses point for decimal seperator
                logger.DLOG("builddatetimePidAndServiceNameWithRAMDict [PID,RAM] %s" %[PID,RAM])
                logger.DLOG("RAM.isnumeric() %s" %[RAM.isnumeric()])
                if RAM.isnumeric():
                    RAM = int(RAM)
                    RamMB = float(RAM)/float(1000)
                    RamGB = float(RamMB)/float(1000)
                    RAM = f'{RamGB:n}'
                else:
                    RAM = ""
                logger.DLOG("builddatetimePidAndServiceNameWithRAMDict [PID,RAM] %s" %[PID,RAM])
            
                lookUpKey = newKeyPrefix + "_" + PID
                logger.DLOG("builddatetimePidAndServiceNameWithRAMDict looking for lookUpKey %s" %[lookUpKey])
                if lookUpKey in datetimePidAndServiceNameDict:
                    logger.DLOG("builddatetimePidAndServiceNameWithRAMDict adding lookUpKey %s to datetimePidAndServiceNameDict" %[lookUpKey])
                    serviceName = datetimePidAndServiceNameDict[lookUpKey]
                    logger.DLOG("lookUpKey serviceName %s" %[lookUpKey,serviceName])
                    datetimePidAndServiceNameWithRAMDict[lookUpKey] = lookUpKey + "," + timePoint + "," + serviceName + "," + RAM

def writeToFile(_writeDir,_writeFileName):

    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)    
    IPAddr = socket.gethostbyname(hostname)
    now = datetime.datetime.now()
    now = now.strftime("%Y%m%d_%H%M")
    _writeFileName = _writeFileName + "_" + IPAddr + "_" + now
    
    with open(_writeDir+_writeFileName, "w") as file:
        file.write("ID,date time,service,RAM GB" + "\n")
        for key, value in datetimePidAndServiceNameWithRAMDict.items():
            file.write(value + "\n")
            
def generateMemoryStatsReport(_params):

    [_filePath,_fileList,_writeDir,_writeFileName] = _params
    
    '''
    first: cycle all Wmic to get all keys hhmmss_ddmmyyyy_PID
    '''
    builddatetimePidAndServiceNameDict(_filePath,_fileList)
    logger.LOG('Completed building dictionary builddatetimePidAndServiceNameDict')
    
    '''
    then: cycle all Tasklist to populate datetimePidAndServiceNameWithRAMDict by [date,serviceName,RAM]
    
    '''
    logger.LOG('Mapping [PID,RAM] to [PID,ServiceName] ... please wait this takes some time.')
    builddatetimePidAndServiceNameWithRAMDict(_filePath,_fileList)
    logger.LOG('Completed building dictionary builddatetimePidAndServiceNameWithRAMDict')
    
    logger.LOG('Writing [Timepoint,PID,ServiceName,RAM] to file')
    writeToFile(_writeDir,_writeFileName)
    logger.LOG('PS_CustomMandiriUtility_ServerRamStatsCollation is FINISHED')


#GUI config
ttLogMode = 'Defines the amount of logging produced.'
ttLogToCon = 'Whether logging should be done in the Log Console or not.'
ttLogToFile = 'Defines whether logging should be done to file.'
ttLogFile = r'Name of the logfile. Could include the whole path c:\log\...'

directory_selection = FRunScriptGUI.DirectorySelection()
ael_variables = FBDPGui.DefaultVariables(
    # Variable     Display                          Type           Candidate  Default  Mandatory   Description Input Enabled
    # name         name                                            values                    Multiple          hook
    ('inputFilePath', 'Path of input files (wmic & tasklist)', directory_selection, None, directory_selection, 1, 1, '', None, 1),
    ('writeFileName', 'Output Report File Name', 'string', None, "serverRamStatsCollation.csv", 1, 0, 'The file name of the output'),
    ('writeFilePath', 'Output Report File Path', directory_selection, None, directory_selection, 1, 1, 'The file path to the directory where the report should be put. Environment variables can be specified for Windows (%VAR%) or Unix ($VAR).', None, 1),
    ('Logmode', 'Log mode_Logging', 'string', ['INFO','DEBUG','WARN','ERROR'], 'INFO', False, False, ttLogMode),
    ('LogToConsole', 'Log to console_Logging', 'int', [1, 0], 1, False, False, ttLogToCon),
    ('LogToFile', 'Log to file_Logging', 'int', [1 ,0], 0, False, False, ttLogToFile),
    ('Logfile', 'Log file path and name_Logging', 'string', None, __name__ + '.log', False, False, ttLogFile),)


def ael_main(params):


    if params['LogToFile'] and params['Logfile']:
        logger.Reinitialize(log_level_dict[params['Logmode']], None, None, params['LogToConsole'], True, params['Logfile'], None, None, None)
    else:
        logger.Reinitialize(log_level_dict[params['Logmode']], None, None, params['LogToConsole'], True, None, None, None, None)
    
    logger.DLOG('params[inputFilePath] %s' %params['inputFilePath'])

    logger.LOG('Initialising PS_CustomMandiriUtility_ServerRamStatsCollation')
    
    inputFilePath = str(params['inputFilePath'])
    inputFileList = os.listdir(inputFilePath)
    
    writeFilePath = str(params['writeFilePath'])
    briefParams = [inputFilePath,inputFileList,writeFilePath,params['writeFileName']]
    generateMemoryStatsReport(briefParams)
    



