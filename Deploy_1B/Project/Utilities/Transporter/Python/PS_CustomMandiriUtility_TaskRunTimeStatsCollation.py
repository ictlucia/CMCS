import acm
import os
import datetime
import FBDPGui
import FRunScriptGUI

from FLogger import FLogger
logger = FLogger(level=2)
log_level_dict = {'INFO' : 1, 'DEBUG' : 2, 'WARN' : 3, 'ERROR' : 4}

timePointsList = []
taskNameByTimePointByRunTimeDict = {}

def getTimePointFromFileName(_fileName):

    dateddmmyyyy = _fileName[5:13]
    logger.DLOG("getTimePointFrom_fileName dateddmmyyyy %s" %[dateddmmyyyy])
    logger.DLOG("getTimePointFrom_fileName yyyy mmm dd %s" %[int(dateddmmyyyy[0:4]), int(dateddmmyyyy[4:6]), int(dateddmmyyyy[6:8])])
    theDate = datetime.date(int(dateddmmyyyy[0:4]), int(dateddmmyyyy[4:6]), int(dateddmmyyyy[6:8]))
    theDate = theDate.strftime('%Y-%m-%d')
    logger.DLOG("getTimePointFromFileName [type(theDate),theDate] %s" %[type(theDate),theDate])
    
    timePointsList.append(theDate)
    return theDate


def buildTasskNameByTimePointByRunTimeDict(_filePath,_fileList):

    for fileName in _fileList:
        timePoint = getTimePointFromFileName(fileName)
        logger.DLOG("builddatetimePidAndServiceNameDict timePoint %s" %[timePoint])
        
        logger.DLOG("_filePath %s" %[_filePath])
        logger.DLOG("fileName %s" %[fileName])
        file = open(_filePath + fileName)
        fileLines = file.readlines()
        file.close()
        
        for singleFileLine in fileLines[1:]:
            singleFileLine = singleFileLine.rstrip()  # remove newline character
            singleFileLine = singleFileLine.split(',')
            
            #logger.DLOG("fileName singleFileLine %s" %[fileName,singleFileLine])
            try:
                taskGroup = singleFileLine[0]
                taskName = singleFileLine[1]
                runTime = singleFileLine[4]
            except:
                continue
            
            #logger.DLOG("taskGroup taskName runTime%s" %[taskGroup,taskName,runTime])
            #taskGroup_taskName = taskGroup + "_###_" + taskName
            if taskName in taskNameByTimePointByRunTimeDict:
                taskNameByTimePointByRunTimeDict[taskName][timePoint] = runTime
            if taskName not in taskNameByTimePointByRunTimeDict:
                taskNameByTimePointByRunTimeDict[taskName] = {timePoint:runTime}

    
def writeToFile(_writeDir,_writeFileName):

    sortedTimePointsList = sorted(timePointsList, reverse=True)
    logger.DLOG("sortedTimePointsList %s" %[sortedTimePointsList])
    
    with open(_writeDir+_writeFileName, "w") as file:
        
        #write header, a new column per date
        file.write("Task Group,Task Name")
        for datePoint in sortedTimePointsList:
            file.write("," + datePoint)
        file.write("\n")
        
        for key, value in taskNameByTimePointByRunTimeDict.items():
            #[groupName,taskName] = key.split("_###_")
            groupName = "goup"
            file.write(groupName + "," + str(key))
            for datePoint in sortedTimePointsList:
                if datePoint in taskNameByTimePointByRunTimeDict[key]: 
                    file.write("," + taskNameByTimePointByRunTimeDict[key][datePoint])
                #if taskNameByTimePointByRunTimeDict[key][datePoint]: file.write("," + "a")
                else: file.write("," + ",")
            file.write("\n")
            
            
def generateTaskRunTimeStatsReport(_params):

    [_filePath,_fileList,_writeDir,_writeFileName] = _params
    
    buildTasskNameByTimePointByRunTimeDict(_filePath,_fileList)
    
    writeToFile(_writeDir,_writeFileName)


#GUI config
ttLogMode = 'Defines the amount of logging produced.'
ttLogToCon = 'Whether logging should be done in the Log Console or not.'
ttLogToFile = 'Defines whether logging should be done to file.'
ttLogFile = r'Name of the logfile. Could include the whole path c:\log\...'

directory_selection = FRunScriptGUI.DirectorySelection()
ael_variables = FBDPGui.DefaultVariables(
    # Variable     Display                          Type           Candidate  Default  Mandatory   Description Input Enabled
    # name         name                                            values                    Multiple          hook
    ('inputFilePath', 'Path of input files (run time per task)', directory_selection, None, directory_selection, 1, 1, '', None, 1),
    ('writeFileName', 'Output Report File Name', 'string', None, "taskRunTimeCollation.csv", 1, 0, 'The file name of the output'),
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

    logger.LOG('Initialising PS_CustomMandiriUtility_TaskRunTimeStatsCollation')
    
    inputFilePath = str(params['inputFilePath'])
    inputFileList = os.listdir(inputFilePath)
    
    writeFilePath = str(params['writeFilePath'])
    briefParams = [inputFilePath,inputFileList,writeFilePath,params['writeFileName']]
    generateTaskRunTimeStatsReport(briefParams)

