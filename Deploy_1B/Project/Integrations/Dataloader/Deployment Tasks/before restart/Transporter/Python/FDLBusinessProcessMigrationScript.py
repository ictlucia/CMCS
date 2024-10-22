import sys, traceback, string
import ael, acm
import FDLBusinessProcess
import FIntegrationUtils
import FDLADSOperations

def get_traceback(message):
    t,v,tb = sys.exc_info()
    d = traceback.format_exception(t,v,tb)
    msg = string.join(d,'')
    ael.log(msg)

def update_textobject_type(provider=''):
    if not provider:
        ael.log("Invalid input provider to update_textobject_type, Please specify the provider as Bloomberg, Refinitiv or MarketMap")
        return
    provider_prefix_dict = {'Bloomberg':'BBG_', 'MarketMap':'MM_', 'Refinitiv' : 'RDS_'}
    query = """select seqnbr from TextObject where type = 'Instrument Extension' and name like '%s'"""%(provider_prefix_dict.get(provider, None) + '%')
    col, res = ael.asql(query)
    if res and res[0]:
        for txt_obj in res[0]:
            try:
                ael_txt_obj = ael.TextObject.read("seqnbr=%d"%txt_obj[0])
                if ael_txt_obj:
                    ael_txt_obj_clone = ael_txt_obj.clone()
                    if ael_txt_obj_clone.type != 'Customizable':
                        ael_txt_obj_clone.type = 'Customizable'
                    ael_txt_obj_clone.commit()
            except Exception as e:
                ael.log("Cannot update Textobject %d"%txt_obj[0])

def get_text_object(provider='', instrument=None):
    provider_alias_dict = {'Bloomberg':'BB_UNIQUE', 'MarketMap':'MM_TICKER', 'Refinitiv' : 'RIC'}
    provider_prefix_dict = {'Bloomberg':'BBG_', 'MarketMap':'MM_', 'Refinitiv' : 'RDS_'}
    text_object = None
    db_provider = None
    if instrument:
        try:
            db_provider = instrument.add_info('DATA_PROVIDER')
        except Exception as e:
            pass
        if db_provider and provider == db_provider:
            alias_val = instrument.Alias(provider_alias_dict.get(provider))
            if alias_val:
                text_object_name = provider_prefix_dict.get(provider) + alias_val
                try:
                    text_object = ael.TextObject.read("type='Customizable' and name = '%s'"%text_object_name)
                except Exception as e:
                    ael.log('Exception in get_text_object = %s'%str(e))
    return text_object

def create_external_object(ext_ref='', instrument='', provider=''):
    external_object = None
    try:
        external_object = acm.FExternalObject()
        if ext_ref:
            external_object.ExternalRef = ext_ref
        external_object.IntegrationType = 'DataLoader'
        if provider:
            external_object.IntegrationSubtype = provider
        external_object.StorageType = 'Dict'
        if instrument:
            external_object.Instrument = instrument
            text_object = get_text_object(provider, instrument)
            if text_object:
                external_object.Data = acm.FCustomTextObject[text_object.name]
        external_object.Commit()
    except Exception as e:
        ael.log( 'Exception in create_external_object = %s'%str(e))
    return external_object


def migrate_business_process(provider=''):
    if not provider:
        ael.log("Invalid input provider to migrate_business_process, Please specify the provider as Bloomberg, Refinitiv or MarketMap")
        return
    identifiers = {'ISIN':'I', 'CUSIP':'C', 'SEDOL':'S', 'BB_UNIQUE':'U','BB_TICKER':'T', 'FIGI':'G', 'MM_SYMBOL': 'M', 'RIC':'R'}
    state_chart_name = 'DataLoaderInstrumentUpload'
    # For all business process with given state chart, update the subject with ACM FExternalObject object
    # MIgrate Business Process only if it was created on ReconciliationItem as its subject. or old BusinessProcess, the subject was ReconciliationItem
    try:
        state_chart = acm.FStateChart[state_chart_name]
        bprs = acm.BusinessProcess.FindByStateChart(state_chart)
        for bpr in bprs:
            bpr_subject = bpr.Subject()  # For old BusinessProcess, the subject was ReconciliationItem
            if bpr_subject and bpr_subject.RecordType() == 'Instrument':
                ext_ref = None
                instrument = bpr_subject
                security_id = instrument.GetProviderDataFieldValue(provider, 'SecurityID')
                security_identifier = instrument.GetProviderDataFieldValue(provider, 'IdentifierType')
                if security_id and security_identifier:
                    ext_ref = FDLBusinessProcess.FDataLoaderExternalObject.get_ext_ref(security_identifier, security_id, 'Instrument')  # For Instrument only as BusinessProcess on CorporateAction was yet supoprted.
                external_obj = create_external_object(instrument=instrument, provider=provider, ext_ref=ext_ref)
                if external_obj:
                    bpr.Subject = external_obj
                    bpr.Commit()

            elif bpr_subject and bpr_subject.RecordType() == 'ReconciliationItem':
                recon_item = bpr_subject
                instrument = None
                external_values = recon_item.ExternalValues()
                identifier_type = external_values.At('1')['IDENTIFIER_TYPE']
                sec_id = external_values.At('1')['IDENTIFIER']
                if identifier_type and sec_id:
                    ext_ref = FDLBusinessProcess.FDataLoaderExternalObject.get_ext_ref(identifier_type, sec_id, 'Instrument')  # For Instrument only as BusinessProcess on CorporateAction was yet supoprted.
                    instrument = FDLBusinessProcess.get_instrument_from_ads(identifier_type, sec_id)
                external_obj = create_external_object(ext_ref=ext_ref, instrument=instrument, provider=provider)
                if external_obj:
                    bpr.Subject = external_obj
                    bpr.Commit()

    except Exception as e:
        ael.log('Exception in migrate_BPR_with_statechart : %s'%str(e))


try:
    # Update the type of all textobjects generated by DataLoader present in db from 'Instrument Extension' to 'Customizable'.
    # Please specify the provider as Bloomberg, Refinitiv or MarketMap
    update_textobject_type(provider='')

    # Migrate the exisitng Businessprocess to use ExternalObject . Please specify the provider as Bloomberg, Refinitiv or MarketMap
    migrate_business_process(provider='')
except Exception as e:
    ael.log("Exception in migration script : %s"%str(e))
    get_traceback(e)

ael.log( 'Migration Completed!!')
