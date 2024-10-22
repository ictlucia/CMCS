import acm

from FConfirmationDefaultEventHooks import *

def isCouponAdvice(trade):
    jakarta = acm.FCalendar['Jakarta']
    settledate = trade.ValueDay()
    if trade.Instrument().InsType()=="Bond":
        for legs in trade.Instrument().Legs():
            for cf in legs.CashFlows():
                recdate = acm.Time.DateAdjustPeriod(cf.PayDate(),'-1d',jakarta,2)
                if recdate == settledate:
                    return True
                else:
                    continue
    else:
        return False
        
    return False

def isPaymentAdvice(payment,trade):
    if payment.Type() == "MMLD Payment":
        ref_rec = acm.FConfirmation.Select("referencedRecordType='Payment' and referencedRecordAddress={}".format(payment.Oid()))
        if ref_rec:
            return True
        return payment.PayDay() == acm.Time.DateToday()
    else:
        return False
    
