import os
import csv
import acm

PAIRING_KEY = 0
AMOUNT_KEY = 1
BASEAMOUNT_KEY = 2
CATEGORY = 3
BOOK_KEY = 4
ACCOUNT_KEY =5
CURRENCY_KEY = 6
DEBIT_OR_CREDIT_KEY = 7
EVENT_DATE_KEY = 8
JOURNAL_TYPE_KEY = 9
PROCESS_DATE_KEY = 10
VALUE_DATE_KEY = 11
TRADE_KEY = 12
ADD_INFO_1_NAME_KEY = 13
ADD_INFO_1_VALUE_KEY = 14
ADD_INFO_2_NAME_KEY = 15
ADD_INFO_2_VALUE_KEY = 16
ADD_INFO_3_NAME_KEY = 17
ADD_INFO_3_VALUE_KEY = 18
ADD_INFO_4_NAME_KEY = 19
ADD_INFO_4_VALUE_KEY = 20
ADD_INFO_5_NAME_KEY = 21
ADD_INFO_5_VALUE_KEY = 22
ADD_INFO_6_NAME_KEY = 23
ADD_INFO_6_VALUE_KEY = 24


def getFileContents(filePathAndName):
    with open(filePathAndName) as sourceFile:
        reader = csv.reader(sourceFile, delimiter=',')
        fileContentsAsList = [row for index, row in enumerate(reader) if index > 0]
        
        return fileContentsAsList

def setAttributeValue(object, attribute, value):
    if hasattr(object, attribute):
        setattr(object, attribute, value)

def getChartOfAccounts(book, t_account_number):
    book_oid = book.Oid()
    t_account_list = acm.FTAccount.Select('number = %s' % t_account_number)
    
    for t_account in t_account_list:
        for chart_of_accounts in t_account.ChartOfAccounts():
            if chart_of_accounts.Book().Oid() == book_oid:
                return chart_of_accounts
    
    return None

def getJournalInfo(trade, book):
    journal_info = acm.FJournalInformation()
    
    if trade:
        journal_info.Trade(trade)
        journal_info.Acquirer(trade.Acquirer())
        journal_info.Counterparty(trade.Counterparty())
        journal_info.Instrument(trade.Instrument())
        journal_info.Portfolio(trade.Portfolio())
    
    if book:
        journal_info.Book(book)
        
    journal_info.Commit()

    return journal_info

def commitLinkedList(list):
    journal_link = acm.FJournalLink()
    
    try:
        journal_link.Commit()
        acm.BeginTransaction()
        
        for journal in list:
            journal.JournalLink(journal_link)
            journal.Commit()
            
        acm.CommitTransaction()
        
        print ('Committed Journals:')
        
        for journal in list:
            print (journal.Oid())
    except Exception as e:
        print(e)
        acm.AbortTransaction()

def ProcessContent(content):
    last_pair = -99
    linked = []
    
    try:
        for journal_data in content:
            journal = acm.FJournal()
            journal.RegisterInStorage()
            
            setAttributeValue(journal, 'Amount', journal_data[AMOUNT_KEY])
            setAttributeValue(journal, 'BaseAmount', journal_data[BASEAMOUNT_KEY])
            
            book = acm.FBook[journal_data[BOOK_KEY]]
            account_number = journal_data[ACCOUNT_KEY]
            
            setAttributeValue(journal, 'ChartOfAccount', getChartOfAccounts(book, account_number))
            setAttributeValue(journal, 'Currency', journal_data[CURRENCY_KEY])
            setAttributeValue(journal, 'DebitOrCredit', journal_data[DEBIT_OR_CREDIT_KEY])
            setAttributeValue(journal, 'EventDate', journal_data[EVENT_DATE_KEY])
            setAttributeValue(journal, 'JournalType', journal_data[JOURNAL_TYPE_KEY])
            setAttributeValue(journal, 'ProcessDate', journal_data[PROCESS_DATE_KEY])
            setAttributeValue(journal, 'ValueDate', journal_data[VALUE_DATE_KEY])
            setAttributeValue(journal, 'ManualJournal', True)
            setAttributeValue(journal, 'JournalCategory', journal_data[CATEGORY])
            
            period = book.FindPeriodByDate(journal_data[VALUE_DATE_KEY])
            
            if period:
                journal.AccountingPeriod(period)

            trade = acm.FTrade[journal_data[TRADE_KEY]]
            pair = journal_data[PAIRING_KEY]
            
            if pair != last_pair:
                journal_info = getJournalInfo(trade, book)
                
                if linked:
                    commitLinkedList(linked)
                    linked = []
                    
                last_pair = pair
            
            setAttributeValue(journal, 'JournalInformation', journal_info)
            setAttributeValue(journal.AdditionalInfo(), journal_data[ADD_INFO_1_NAME_KEY], journal_data[ADD_INFO_1_VALUE_KEY])
            setAttributeValue(journal.AdditionalInfo(), journal_data[ADD_INFO_2_NAME_KEY], journal_data[ADD_INFO_2_VALUE_KEY])
            setAttributeValue(journal.AdditionalInfo(), journal_data[ADD_INFO_3_NAME_KEY], journal_data[ADD_INFO_3_VALUE_KEY])
            setAttributeValue(journal.AdditionalInfo(), journal_data[ADD_INFO_4_NAME_KEY], journal_data[ADD_INFO_4_VALUE_KEY])
            setAttributeValue(journal.AdditionalInfo(), journal_data[ADD_INFO_5_NAME_KEY], journal_data[ADD_INFO_5_VALUE_KEY])
            if(len(journal_data) > ADD_INFO_6_NAME_KEY):
                setAttributeValue(journal.AdditionalInfo(), journal_data[ADD_INFO_6_NAME_KEY], journal_data[ADD_INFO_6_VALUE_KEY])
            
            linked.append(journal)
        
        commitLinkedList(linked)
        
        return 0
    except Exception as error:
        print('error:', error)
        return 1


def folderPicker(default):
    sel = acm.FFileSelection()
    
    sel.PickDirectory(True)
    sel.SelectedDirectory(default)
    
    return sel


ael_variables = \
    [['input_folder', 'Journal files location', 'FFileSelection', None, folderPicker(r'C:\temp\Journals\in'), 0, 1, 'Location of files created by Excel', None, 1],
    ['complete_folder', 'Archive folder', 'FFileSelection', None, folderPicker(r'C:\temp\Journals\complete'), 0, 1, 'Where to archive successfully imported files', None, 1],
    ['error_folder', 'Error folder', 'FFileSelection', None, folderPicker(r'C:\temp\Journals\error'), 0, 1, 'Where to move files that could not be imported', None, 1]]

def ael_main(params):
    input_folder = params['input_folder'].SelectedDirectory().AsString()
    complete_folder = params['complete_folder'].SelectedDirectory().AsString()
    error_folder = params['error_folder'].SelectedDirectory().AsString()
    files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f)) and f.endswith('csv')]
    
    for filename in files:
        file_path = os.path.join(input_folder, filename)
        content = getFileContents(file_path)
        status = ProcessContent(content)
        
        if status == 0:
            os.rename(file_path, os.path.join(complete_folder, filename))
        else:
            os.rename(file_path, os.path.join(error_folder, filename))


