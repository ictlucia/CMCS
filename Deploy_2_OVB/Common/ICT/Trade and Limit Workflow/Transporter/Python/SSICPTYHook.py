import acm,ael



import FValidationUtils





def validate_transaction(transaction_list):



    if not check_usergroup_in_hierarchy():



        return transaction_list



    



    for (entity, operation) in transaction_list:



        if str(entity.record_type) == "Trade" and str(operation) == "Update":



            if has_tradeAccountLink_changes(entity) and (str(entity.status) == 'BO-BO Confirmed' or str(entity.status) == 'BO Confirmed' or str(entity.status) == 'FO Confirmed'):



                change_ssi_cpty(entity)



    return transaction_list







def check_usergroup_in_hierarchy():



    hierarchy_list = ['BO Limit', 'Settlement Limit', 'Journal Limit']



    usergroup = ael.user().grpnbr.grpid



    for hierarchy in hierarchy_list:



        hierarchy = acm.FHierarchy[hierarchy]



        for node in hierarchy.HierarchyNodes():



            if len(node.HierarchyDataValues()) > 0:



                if usergroup == node.HierarchyDataValues()[1].DataValue():



                    return True



    return False







def has_tradeAccountLink_changes(entity):



    for children in entity.children():

        if str(children.record_type) == "TradeAccountLink" and (children.clone_is_modified() or children.original() is None):

            return True



    return False



    



def change_ssi_cpty(object):



    user = ael.user().userid



    addinfo = acm.FAdditionalInfoSpec['SSIChangeCPTY']



    if addinfo:

    

        FValidationUtils.set_addinfo(object,'SSIChangeCPTY',user)



    else:



        raise Exception("No Additional Info field named 'SSIChangeCPTY'")

