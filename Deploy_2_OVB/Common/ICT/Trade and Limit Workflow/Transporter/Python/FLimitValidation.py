import acm,ael
from datetime import datetime, timedelta

def validate_transaction(transaction_list):
    checkLimitForTransaction(transaction_list)
    return transaction_list
    
def getPriceIDR(val,curr):
    if curr == 'IDR':
        return abs(val)

    else:
        all_prices = acm.FPrice.Select(f"instrument = '{curr}' and market='EOD_MtM'")
        price_value = 0
        if all_prices:
            latest_day = all_prices.Last().Day()
            yesterday_date = str(datetime.strptime(latest_day, "%Y-%m-%d") - timedelta(days=1)).split(" ")[0]
            
            for price in all_prices:

                if price.Day() >= latest_day and price.Currency().Name() == "IDR":
                    price_value = price.Settle()
                    latest_day = price.Day()
                    break

                elif price.Day() >= yesterday_date and price.Currency().Name() == "IDR":
                    price_value = price.Settle()
                    latest_day = price.Day()        
                    
            return abs(val * price_value)

def compare_amount(origin_value, clone_value):

#if it is different, return true to check for hierarchy

    if origin_value != clone_value:
        return True
    else:
        return False
    

def filter_by_hierarchy(hierarchy,prem,curr, usergroup,stat):

    convertedPremium = getPriceIDR(prem, curr)

    for h1 in hierarchy.HierarchyNodes():
        if len(h1.HierarchyDataValues()) > 0:
            if str(stat)==str(h1.HierarchyDataValues()[0].DataValue()) and str(usergroup)==str(h1.HierarchyDataValues()[1].DataValue()) and convertedPremium > float(h1.HierarchyDataValues()[2].DataValue()):
                raise Exception("You are not allowed to trade more than : ",h1.HierarchyDataValues()[2].DataValue())

def checkLimitForTransaction(transaction_list):

    limit = 0

    hierarchyBO = acm.FHierarchy['BO Limit']

    hierarchySettlement = acm.FHierarchy['Settlement Limit']

    hierarchyJournal = acm.FHierarchy['Journal Limit']

    usergroup = ael.user().grpnbr.grpid

    user = ael.user().userid

    for (entity, operation) in transaction_list:

        if str(entity.record_type) == "Trade":
        
            trade = acm.FTrade[entity.trdnbr]

            if entity.insaddr.instype == "Future/Forward":
                
                origin_amount = trade.Quantity()*trade.Intrument().ContractSize()
                entity_amount = entity.quantity*entity.insaddr.contr_size
                
                if compare_amount(origin_amount, entity_amount):

                    filter_by_hierarchy(hierarchyBO, entity_amount, entity.curr.insid, usergroup,entity.status)

            elif entity.type=="Account Transfer":

                origin_amount = acm.FTrade[entity.trdnbr].Payments()[0].Amount()
                entity_amount = entity.payments().members()[0].amount()
                
                if compare_amount(origin_amount, entity_amount):
                
                    filter_by_hierarchy(hierarchyBO,entity_amount, entity.curr.insid, usergroup,entity.status)

            else:

                filter_by_hierarchy(hierarchyBO,entity.premium, entity.curr.insid, usergroup,entity.status)

            

        elif str(entity.record_type) == "Settlement" and str(operation) == "Update":

            if entity.trdnbr is None:
                continue

            if acm.FTrade[entity.trdnbr.trdnbr].AdditionalInfo().SSIChangeCPTY() == user:
                raise Exception("User who last changed the SSI Account is not allowed to release the settlement")
            
            filter_by_hierarchy(hierarchySettlement,entity.amount, entity.curr.insid, usergroup,entity.status)

        elif str(entity.record_type) == "Journal" and (str(operation) == "Update" or str(operation) == "Insert"):

            filter_by_hierarchy(hierarchyJournal,entity.amount, entity.currency_insaddr.insid, usergroup,entity.journal_type)

    return transaction_list



     

