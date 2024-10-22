import acm
import FLogger
import traceback
import sys
import FAccountingHooks as fah
import FAccountingHooksMoneyFlowBased as mfbh

scenario = [8]



s1 = '01. Identify mapping filters: TAccount, MoneyFlow, Trade and Treatment not in use'
s2 = '02. Update rolling convention for non periodic accounting instructions'
s3 = '03. Set Exclude FX Conversion for all accounting instructions'
s4 = '04. Update Nostro account'
s5 = '05. GetDynamic Account'
s6 = '06. Identifying T-Accounts created but not used'
s7 = '07. Move Trade to RecycleBin'
s8 = '08. Reload FAccountingHooks'
s9 = '09. Return trade account links for trade'
s10 = '10. Return trades given cash account name'
s11 = '11. Change party type from counterparty to client'
s12 = '12. Money flow for Journal'

LOG_VERBOSITY = 2
logger = FLogger.FLogger(__name__, level = LOG_VERBOSITY) 

TRADE_RANGE = range (251,253)
JOURNAL_RANGE = range (480000, 545319)
TIME_RANGE = ('2021-04-25 06:22:23', '2021-04-25 21:56:23')
JOURNAL = 88
PARENT_ACCOUNT = 'Cash Accounts Nostro' # Accrual_Assets, Treasury Settlement Account



for i in scenario:
    s = eval('s' + str(i))
    print (s)


'''identify filters created during accounting development but not used in the assignment tree (redundant) '''
if 1 in scenario:
    count = 1
    storedQuerySel = acm.FStoredASQLQuery.Select('')
    for filter in storedQuerySel:
        if filter.SubType() in ['tAccountMapping', 'accountingInstructionMoneyFlowMapping', 'treatmentMapping', 'accountingInstructionTradeMapping', 'bookMapping']:
            print (count, filter.Name(), filter.SubType())
            count +=1
        
                
'''2. Update rolling convention for non periodic accounting instructions'''
if 2 in scenario:
    for ai in acm.FAccountingInstruction.Select(''):
        if not ai.IsPeriodic() and ai.BusinessDayMethod() != 'None' :
            print (ai.Name())
            ai.BusinessDayMethod('None')
            ai.Commit()

'''3. Set Exclude FX Conversion for all accounting instructions'''
if 3 in scenario:
    for ai in acm.FAccountingInstruction.Select(''):
        if not ai.ExcludeFXConversion():
           print (ai.Name())
           ai.ExcludeFXConversion(True)
           ai.Commit()
  
         
if 4 in scenario:
    acquirer = acm.FParty['Acquirer 1']
    for account in acquirer.Accounts():
        if account.Depository() == '':
            depository_ac = account.Currency().Name() + ' Nostro Number'
            account.Depository(depository_ac) 
            acm.Log('Missing nostro on %s %s account set to %s' % (acquirer.Name(),  account.Name(), depository_ac))
            account.Commit()

       
'''5 Get Dynamic Account'''
if 5 in scenario:
    print ('Get Dynamic Account')
    import FAccountingHooks
    journal = acm.FJournal[JOURNAL]
    parentAccount = acm.FTAccount[PARENT_ACCOUNT]
    print (FAccountingHooks.GetDynamicAccount(journal, parentAccount))

if 6 in scenario:
    print ('06. Identifying T-Accounts created but not used')

'''7. Move Trade to RecycleBin'''
if 7 in scenario:

    portfolio = acm.FPhysicalPortfolio['SALES_FX']
    for trade in portfolio.Trades():
        #trade.Delete()
        clone = trade.Clone()
        
        clone.Portfolio('Recycle Bin')
        clone.Text2('SALES_FX')
        clone.Commit()


''' 8 Load FAccountingHooks'''
if 8 in scenario:
    import FAccountingHooks
    import AccountingColumnUtils
    import FAccountingParams
    print ('imoprt is Ok')

'''9. Return trade account links for trade'''
if 9 in scenario:
    #trade_list = [11750]
    for trdnbr in trade_list:
        trade = acm.FTrade[trdnbr]
        for accountLink in trade.AccountLinks():
            if accountLink.CashAccount():
                logger.DLOG("Trade: %s and cash account : %s " % (trade.Oid(), accountLink.CashAccount().Name()) ) 

'''10. Return trades given cash account name'''
if 10 in scenario:
    accountName = 'AE320010006000040601001'
    taLinks = acm.FTradeAccountLink.Select("cashAccount='%s'" % (accountName))
    for tal in taLinks:
        logger.DLOG("Trade: %s and cash account : %s " % (tal.Trade().Oid(), accountName )) 

'''11. Change party type from counterparty to client'''
if 11 in scenario:
    pty = acm.FParty['ITAN JEWELLS DMCC']
    pty.Type('Client')
    pty.Commit()

if 12 in scenario:
    journal = acm.FJournal[JOURNAL]
    insType = journal.LinkedTrade().Instrument().InsType()
    aMoneyFlow = mfbh.MoneyflowForJournal(journal, journal.JournalInformation().MoneyFlowType(),insType)
    logger.DLOG("Money flow for journal: %s  %s " % (journal.Oid(), aMoneyFlow )) 
    
