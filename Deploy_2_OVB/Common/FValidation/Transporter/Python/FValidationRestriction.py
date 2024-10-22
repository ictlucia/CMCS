import ael

RESTRICTED_RECORD_TYPES = ['AccountingParameters', 'ValuationParameters', 'Context']
ALLOWED_GROUP = ['FIS_DEV']

def validate_transaction(transaction_list, *rest):

    for entity, operation in transaction_list:
        
        user = ael.User[ael.userid()]
        group = user.grpnbr.grpid 
        
        # Restrict changes to objects except FIS_DEV
        if group not in ALLOWED_GROUP:
            if entity.record_type in RESTRICTED_RECORD_TYPES and operation in ('Insert', 'Update'):
                raise UserWarning("Please reach out to FIS PS team for making any changes to this object!")

        # Only ARENASYS can update its details
        if entity.record_type == 'User' and entity.userid == 'ARENASYS':
            if user.userid != 'ARENASYS':
                raise UserWarning("Only ARENASYS can update ARENASYS details!")

    return transaction_list


