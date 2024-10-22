import acm 
import FLogger
import traceback
import sys


#scenario = [5,6,7,8,9,10,11,12,13]
scenario = [5,6]

'''----------------- Delete Utils ------------------------------'''

s1 =  '01. Delete journals linked to a trade - Text2 '
s2 =  '02. Delete journals in trade range'
s3 =  '03. Delete journals in time range'
s4 =  '04. Delete journal info in time range'
s5 =  '05. Delete all journals'
s6 =  '06. Delete all journal information'
s7 =  '07. Delete TAccountMapping'
s8 =  '08. Delete TAccount Alloc Link'
s9 =  '09. Delete Chart of Accounts'
s10 =  '10. Delete Accounting Instruction'
s11 =  '11. Delete Treatment'
s12 =  '12. Delete Book'
s13 =  '13. Delete TAccounts'
s14 =  '14. Delete accounting periods'

LOG_VERBOSITY = 2
logger = FLogger.FLogger(__name__, level = LOG_VERBOSITY) 

TRADE_RANGE = range (251,253)
JOURNAL_RANGE = range (480000, 545319)
TIME_RANGE = ('2021-04-25 06:22:23', '2021-04-25 21:56:23')
JOURNAL = 88
PARENT_ACCOUNT = 'Cash Accounts Nostro' 
BOOK = 'Treasury'
'''
, level = 1, keep=False, logOnce=True, \
                                logToConsole=True, logToPrime=True, )
                                
                                
'''

def DeleteJournal_LinkedJournals_JournalInformation(journals):
    journal_to_be_deleted_l = [] 
    journal_information_tbd_l = []
    
    for journal in journals:
        journal_to_be_deleted_l.append(journal)
        journal_information_tbd_l = journal_information_l.append(journal.JournalInformation())
        for linked_journal in journal.LinkedJournals():
            journal_to_be_deleted_l.append(linked_journal)
            journal_information_tbd_l = journal_information_tbd_l.append(linked_journal.JournalInformation())
    
    # Delete
    for journal in journal_to_be_deleted_l[:]:
        print ('\tDeleting journals' % journal.Oid())
        try:
            journal.Delete()
        except Exception as e:
            print ("Journal can't be removed" % e)
            pass

    for ji in journal_information_tbd_l[:]:
        print ('\tDeleting journal information' % ji.Oid()) # fix this later send a copy of the list
        try:
            ji.Delete()
        except Exception as e:
            print ("Journal information can't be removed" % e)
            pass
    

def DeleteJournals():
    journals = acm.FJournal.Select('')
    journals_c = journals.AsList().SortByProperty('Oid', False) # descending order
    for journal in journals_c:
        print ('\tDeleting journals :%s' % journal.Oid())
        try:
            journal.Delete()
        except Exception as e:
            print ("Journal can't be removed" % e)
            pass

def DeleteJournalInformation():
    for ji in acm.FJournalInformation.Select('').AsList().SortByProperty('Oid', False):
        print ('\tDeleting journal information: %s' % ji.Oid()) # fix this later send a copy of the list
        try:
            ji.Delete()
        except Exception as e:
            print ("Journal information can't be removed" % e)
            pass

        
def DeleteJournalInfos(jis):
    journal_infos_c = jis.AsList().SortByProperty('Oid', False) # descending order
    for journal_info in journal_infos_c:
        print ('\tDeleting journal information' % ji.Oid())
        try:
            ji.Delete()
        except Exception as e:
            print ("Journal information can't be removed" % e)            
            pass
            
def DeleteJournalsForTrade(trade):
    print ('Deleting journals for trade %s' % trade.Oid())
    tradeJournalInformations = acm.FJournalInformation.Select("trade='%d'" % (trade.Oid()))
    # Create the copy of the list and sort
    tji_c = tradeJournalInformations.AsList().SortByProperty('Oid', False)
    for ji in tji_c: 
        journals = ji.Journals().AsList().SortByProperty('Oid', False)   
        DeleteJournals(journals)
        
    contractTradeJournalInformations  = acm.FJournalInformation.Select("contractTrade='%d'" % (trade.Oid()))
    # Create the copy of the list and sort
    ctji_c = contractTradeJournalInformations.AsList().SortByProperty('Oid', False)
    for ji in ctji_c: 
        journals = ji.Journals().AsList().SortByProperty('Oid', False)
        DeleteJournals(journals)
        
    for ji in tji_c: 
        DeleteJournalInformation(ji)
    
    for ji in ctji_c: 
        DeleteJournalInformation(ji)


def DeleteTAccountMapping():
    for tam in acm.FTAccountMapping.Select('').AsList():
        print ('\tDeleting TAccount mapping: %s' % tam.Oid()) 
        try:
            tam.Delete()
        except Exception as e:
            print ("TAccount mapping can't be removed" % e)
            pass



def DeleteTAccountAllocLink():
    for tal in acm.FTAccountAllocationLink.Select('').AsList():
        print ('\tDeleting account alloc links: %s' % tal.Oid()) 
        try:
            tal.Delete()
        except Exception as e:
            print ("TAccount alloc link can't be removed" % e)
            pass


def DeleteCoA():
    for coa in acm.FChartOfAccount.Select('').AsList().SortByProperty('Oid', False):
        print ('\tDeleting chart of accounts: %s' % coa.Oid()) 
        try:
            coa.Delete()
        except Exception as e:
            print ("TAccounts can't be removed" % e)
            pass

def DeleteAccountingInstruction():
    for aim in acm.FAccountingInstructionMapping.Select('').AsList().SortByProperty('Oid', False):
        print ('\tDeleting acct instr mapping: %s' % aim.Oid()) 
        try:
            aim.Delete()
        except Exception as e:
            print ("AI mapping can't be removed" % e)
            pass
    for tl in acm.FTreatmentLink.Select('').AsList().SortByProperty('Oid', False):
        print ('\tDeleting treatment links acct instr mapping: %s' % tl.Oid()) 
        try:
            tl.Delete()
        except Exception as e:
            print ("Treatment link AI mapping can't be removed" % e)
            pass


    for ai in acm.FAccountingInstruction.Select('').AsList().SortByProperty('Oid', False):
        print ('\tDeleting acct instr : %s' % ai.Oid()) 
        try:
            ai.Delete()
        except Exception as e:
            print ("AI can't be removed" % e)
            pass

def DeleteTreatment():

    for tm in acm.FTreatmentMapping.Select('').AsList().SortByProperty('Oid', False):
        print ('\tDeleting treatment mapping: %s' % tm.Oid()) 
        try:
            tm.Delete()
        except Exception as e:
            print ("Book mapping can't be removed" % e)
            pass

    for bl in acm.FBookLink.Select('').AsList().SortByProperty('Oid', False):
        print ('\tDeleting book link: %s' % bl.Oid()) 
        try:
            bl.Delete()
        except Exception as e:
            print ("Book link can't be removed" % e)
            pass

    for tr in acm.FTreatment.Select('').AsList().SortByProperty('Oid', False):
        print ('\tDeleting treatment mapping: %s' % tr.Oid()) 
        try:
            tr.Delete()
        except Exception as e:
            print ("Book mapping can't be removed" % e)
            pass


def DeleteBook():


    for bm in acm.FBookMapping.Select('').AsList().SortByProperty('Oid', False):
        print ('\tDeleting book mapping: %s' % bm.Oid()) 
        try:
            bm.Delete()
        except Exception as e:
            print ("Book mapping can't be removed" % e)
            pass
   

    for bk in acm.FBook.Select('').AsList().SortByProperty('Oid', False):
        print ('\tDeleting book: %s' % bk.Oid()) 
        try:
            bk.Delete()
        except Exception as e:
            print ("Book can't be removed" % e)
            pass
    

def DeleteTAccount():
    for ta in acm.FTAccount.Select('').AsList().SortByProperty('Oid', False):
        print ('\tDeleting Taccounts: %s' % ta.Oid()) 
        try:
            ta.Delete()
        except Exception as e:
            print ("TAccounts can't be removed" % e)
            pass


''' 14 Removing accounting periods'''
def DeleteAccountingPeriods():
    print ('Removing accounting periods')
    #endDate   = '2030-12-01'
    startDate   = '2019-01-01'
    
    book = acm.FBook[BOOK]
    for ap in book.AccountingPeriods().AsList():
        #if ap.StartDate() < endDate:
        if ap.EndDate() >= startDate:
            print (ap.Name())
            ap.Delete()


for i in scenario:
    s = eval('s' + str(i))
    print (s)

"""
''' 1 based on trade Text2'''
if 1 in scenario:    
    text2 = 'multiple ODF drawdown'
    for trade in acm.FTrade.Select('text2=%s' % text2 ):
        DeleteJournalsForTrade(trade)

''' 2 based on trade range'''
if 2 in scenario:
    trades_list = TRADE_RANGE # 
    for t in trades_list:
        trade = acm.FTrade[t]
        if trade:
            DeleteJournalsForTrade(trade)
    
'''Delete 3 journals in range'''
if 3 in scenario:
    start = TIME_RANGE[0]
    end = TIME_RANGE[1]
    query = "updateTime>'%s' and updateTime<'%s'" % (start, end)
    journals = acm.FJournal.Select(query)
    DeleteJournals(journals)

'''Delete 4 journal info in range'''
if 4 in scenario:
    start = TIME_RANGE[0]
    end = TIME_RANGE[1]
    query = "updateTime>'%s' and updateTime<'%s'" % (start, end)
    journalInfo = acm.FJournalInformation.Select(query)
    DeleteJournalInformation(journalInfo)  
    

''' 9 Delete accounts added Dynamically'''
if 9 in scenario:
    for account in acm.FTAccount.Select('').AsList():
        if account.ReportingClass() in ['Suspense', 'Summary']:
            continue
        if account.Name() not in ['FX Split Value Date Account', 'Pending NDF Settlement', 'Warning Using The Default Hook']:
            print ('Removing T-account' % (account.Name(), account.ReportingClass()))
            account.Delete()
        
            
        

''' 15 Remove Summary accounts'''            
if 15 in scenario:
    book = acm.FBook[BOOK]
    for coa in book.ChartOfAccounts():
        if (coa.TAccount().ReportingClass() == "Summary"):
            print ('Account removed' % coa.TAccount().Name())
            coa.Delete()

"""

if 5 in scenario: 
    DeleteJournals()
if 6 in scenario: 
    DeleteJournalInformation()
if 7 in scenario: 
    DeleteTAccountMapping()
if 8 in scenario: 
    DeleteTAccountAllocLink()
if 9 in scenario: 
    DeleteCoA()
if 10 in scenario: 
    DeleteAccountingInstruction()
if 11 in scenario: 
    DeleteTreatment()
if 12 in scenario: 
    DeleteBook()
if 13 in scenario: 
    DeleteTAccount()
if 14 in scenario: 
    DeleteAccountingPeriods()
