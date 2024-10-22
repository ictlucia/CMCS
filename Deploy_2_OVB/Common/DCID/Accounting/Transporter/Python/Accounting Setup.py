import acm 
import FLogger
from datetime import datetime, date, time

logger = FLogger.FLogger(__name__)

scenario = [1]

s1 = '01. Extract DCID account mapping file'
s2 = '02. Update client specific chart of accounts'

FOLDER = 'C:\\Temp\\'
FILE = 'DCID Client Account Mapping.csv'

for i in scenario:
    s = eval('s' + str(i))
    print (s)


class DataLine:


    data = []
    listOfColumns = []
    
    def __init__(self, listOfColumns, defaultValue = None):
        self.listOfColumns = listOfColumns
        self.data = []
        for i in range(len(listOfColumns)):
            self.data.append(defaultValue)

    def _getIndex(self,key):
        if isinstance(key, int):
            idx = key
        else:
            try:
                idx = self.listOfColumns.index(key)
            except:
                print ('ValueError: %s not in list' % key)
                raise
        return idx
        
    def __setitem__(self,key,value):
        idx = self._getIndex(key)
        self.data[idx] = value

    def __getitem__(self,key):
        return self.data[self._getIndex(key)]


class Extractor:


    _tAccBuf = ''
    
    def ReadLines(self):
        fileName = FOLDER + FILE
        fo = open(fileName, "r")
        lines = fo.readlines()
        fo.close()
        return lines
    
    def WriteLine(self, list, separator):
        if list == None:
            return ''
        s = ''
        for item in list:
            s+=str(item)
            s+=separator
        
        s=s[:-1]
        s+='\n'
        return s

    def WriteToFile(self, strBuf, fileName):
        fo = open(fileName, "w")
        fo.write(strBuf)
        fo.close()
    
    
    def ConvertDate(self, dateStr, toDateFormat = '%d/%m/%Y'):
        ''' ?                 15/6/2019
            %d/%m/%Y          15/06/2019
        '''
        isoFormat = "%Y-%m-%d"
        
        if dateStr == '':
            return ''
        else:
            formattedDate = ''
            try:
                dt = datetime.strptime(dateStr, isoFormat)
                formattedDate = dt.strftime(toDateFormat)
            except:
                dt = datetime.strptime(dateStr, "%m/%d/%Y")
                formattedDate = dt.strftime("%Y%m%d")
            return formattedDate



    def ExtractTAccountMapping(self):

        columns = [''] * 4
        columns[0] = 'DCID TAccount Name'
        columns[1] = 'DCID TAccount Number'
        columns[2] = 'Client TAccount Name' 
        columns[3] = 'Client TAccount Number'
                
                
        self._tAccBuf = self.WriteLine(columns, ',')

        for tAccount in acm.FTAccount.Select(''):
            if tAccount:
                columns[0] =  tAccount.Name()
                columns[1] =  tAccount.Number()
                columns[2] =  tAccount.Name()
                columns[3] =  tAccount.Number()
                
                self._tAccBuf += self.WriteLine(columns, ',')


        self.WriteToFile(self._tAccBuf, FOLDER + FILE)

    def UpdateClientSpecificCoA(self):
        logger.LOG('TAccount Old Name | New Name | Old Number | New Number')
        for tAccount in self.ReadLines():
            (dcidTAccName, dcidTAccNum, cliTAccName, cliTAccNum) = tAccount.split(',')
            if (dcidTAccName != cliTAccName ) or (dcidTAccNum != cliTAccNum):
                tAcc = acm.FTAccount[dcidTAccNum]
                
                if tAcc:
                    tAcc.Name(cliTAccName)
                    tAcc.Number(cliTAccNum)
                    #tAcc.Commit()
                    logger.LOG('%s | %s | %s | %s' % (dcidTAccName, cliTAccName, dcidTAccNum, cliTAccNum))
                    
                    
x = Extractor()

if 1 in scenario:
    x.ExtractTAccountMapping()
    
if 2 in scenario:
    x.UpdateClientSpecificCoA()

