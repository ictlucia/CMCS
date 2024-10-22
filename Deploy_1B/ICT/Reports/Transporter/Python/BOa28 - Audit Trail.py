import acm, ael
from datetime import datetime, time, date, timedelta
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *


ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'BOa28 - Audit Trail'}

today_date = str(date.today())

ael_variables=[
['report_name','Report Name','string', None, 'BOa28 - Audit Trail', 1,0],
['from_date','From Date','date', None, '', 0,0],
['to_date','To Date','date', None, '', 0,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.xls',0,1, 'Select Secondary Extensions Output']
]

def get_column_name(record_type):
    column_name = {
        "Trade" : 
            ["prfnbr", "insaddr", "acquire_day", "acquirer_ptynbr", "curr", "value_day", "quantity", "price", 
            "premium", "fee", "status", "counterparty_ptynbr", "optkey3_chlnbr", "optkey4_chlnbr"],
            
        "Settlement" :
            ["amount", "curr", "value_day", "to_prfnbr", "from_prfnbr", "status", "type", "delivery_type", 
             "acquirer_ptyid", "acquirer_accname", "acquirer_account_network_name", "party_ptyid", "party_account",
             "party_accname", "party_account_network_name", "text"],
        
        "Static data" : 
            ["ptyid", "type", "fullname", "fullname2", "attention", "address", "adress2", "zipcode", "city", "country", "telephone",
             "fax", "telex", "swift", "contact1", "contact2", "free1", "free2", "free3", "free4", "free5", "bis_status", "hostid",
             "pytid2", "time_zone", "email", "correspondent_bank"],
             
        "Calendar" :
            ["calid", 'spot_banking_days', 'description', 'business_center']
    }
        
    return column_name[record_type]

def change_nbr(result, column):
    if column in ["acquirer_ptynbr", "counterparty_ptynbr"]:
        return acm.FParty[result].Name()
    elif column in ["optkey3_chlnbr", "optkey4_chlnbr"]:
        try :
            return ael.asql(f"SELECT entry FROM ChoiceList WHERE seqnbr = {result}")[1][0][0][0]
        except :
            return "-"
    elif "prfnbr" in column:
        try :
            return ael.asql(f"SELECT prfid FROM Portfolio WHERE prfnbr = {result}")[1][0][0][0]
        except :
            return "-"
    elif column == ["insaddr", "curr"]:
        try:    
            return ael.asql(f"SELECT insid FROM Instrument WHERE insaddr = {result}")[1][0][0][0]
        except :
            return "-"
    else :
        return result

def get_data(from_date='', to_date=''):

    if from_date and to_date :
        
        limit = acm.Time().DateAddDelta(to_date, 0, 0, 1)

        from_datetime = datetime.strptime(str(from_date), "%Y-%m-%d")

        to_datetime = datetime.strptime(str(limit), "%Y-%m-%d")
    
        time_query = f"h.creat_time >= '{from_datetime}' AND h.creat_time < '{to_datetime}'"
    
    else :
        
        time_query = "h.updat_time BETWEEN time_of TODAY + 0*60*60 AND time_of TODAY + 24*60*60"
        

    query_hist = f"""
    SELECT 
        h.trans_record_type, h.name, h.version, h.updat_time, h.owner_usrnbr, h.oper, h.seqnbr
    FROM 
        TransHst h, User u
    WHERE 
        h.owner_usrnbr = u.usrnbr AND
        DISPLAY_ID(u, 'grpnbr') LIKE 'BO%' AND
        h.trans_record_type IN ('Trade', 'Settlement', 'Party', 'Calendar') AND
        h.oper IN ('Insert', 'Update') AND
        {time_query}
    """
    
    list_seq = ael.asql(query_hist)[1][0]
        
    
    list_fix = []
    for result_query_tuple in list_seq:
        
        result_query = list(result_query_tuple)
        
        if result_query[0] == "Settlement": 
            result_query.insert(1, "")
            result_query.insert(3, "")
            
            try :
                optkey_3 = acm.FSettlement[result_query[2]].Trade().OptKey3().Name()
            except :
                optkey_3 = ""
            
            result_query.insert(4, optkey_3)
        
        elif result_query[0] == "Trade": 
            result_query.insert(2, "")
            result_query.insert(3, "")
            
            try :
                optkey_3 = acm.FTrade[result_query[1]].Trade().OptKey3().Name()
            except :
                optkey_3 = ""
            
            result_query.insert(4, optkey_3)
        
        else :
            result_query.insert(1, "")
            result_query.insert(2, "")
            
            if result_query[0] == "Party":           
                result_query[0] = "Static data"
                result_query.insert(4, "Party Definition")
            if result_query[0] == "Calendar":  
                result_query.insert(4, "Calendar data")
            
        
        result_query[7] = acm.FUser[result_query[7]].Name()
        
        update_datetime_utc = datetime.strptime(result_query[6], '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
        update_datetime = update_datetime_utc.strftime('%Y-%m-%d %H:%M:%S')
        
        date_val, time_val = str(update_datetime).split(" ")
        result_query[6] = date_val
        result_query.insert(7, time_val)
        
        old_val_list = []
        new_val_list = []
        
        x = acm.FTransactionHistory[result_query[-1]]
        result_query.pop(-1)
        
        for field_name in get_column_name(result_query[0]):
            if result_query[-1] in ("Delete", "Insert"):
                break
            
            if result_query[0] == "Static data":
                old_val = x.OldFieldValue(field_name,"Party")
                new_val = x.NewFieldValue(field_name,"Party")
            else :
                old_val = x.OldFieldValue(field_name,result_query[0])
                new_val = x.NewFieldValue(field_name,result_query[0])
                
            if old_val != new_val:
                old_val, new_val = change_nbr(old_val, field_name), change_nbr(new_val, field_name)
                old_val_list.append(field_name + " = " + str(old_val) + "<br>") if old_val else None
                new_val_list.append(field_name + " = " + str(new_val) + "<br>") if old_val else None
            
            
        if old_val_list and new_val_list :
            result_query.extend([", ".join(old_val_list), ", ".join(new_val_list)])
            
            if result_query[9] != "Delete":
                list_fix.append(result_query)
        
    return list_fix

def ael_main(parameter):
    html_gen = HTMLGenerator()
    xsl_gen = XSLFOGenerator()
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = parameter['output_file']

    title_style = """
        .title {
            color: black;
            text-align: left;   
        }
        .subtitle-1 {
            color: #0000FF;
            font-size: 20px;
            text-align: left;
            font-weight: bold;
        }

        .subtitle-2 {
            color: #000080;
            font-size: 16px;
            text-align: left;
        }

        .amount {
            font-weight: bold;
        }
    """

    current_date =  acm.Time.DateToday()

    
    html_content = html_gen.create_base_html_content("BOa28 - Audit Trail as per. "+current_date, title_style)
    xsl_fo_content = xsl_gen.prepare_xsl_fo_content("BOa28 - Audit Trail as per. "+current_date)
    
    
    title = ['record type','Trade ID','Settlement ID','Descr','Product Type','version update','update date', 'update time', 'user update','operation','Old Value','Value']
    
    html_content +="<div><table>"
    xsl_fo_content +="""<fo:table margin-bottom="50px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto"><fo:table-body>"""
    
    if parameter['from_date'] and parameter['to_date'] :

        from_date = acm.Time().AsDate(str(parameter['from_date']))

        to_date = acm.Time().AsDate(str(parameter['to_date']))

        data_list = get_data(from_date, to_date)
        
        data_list.sort(key=lambda x : (x[0], x[4], x[1], x[2], x[3], x[5]))
    
    else :
        
        data_list = get_data()
                
        data_list.sort(key=lambda x : (x[0], x[4], x[1], x[2], x[3], x[5]))
    
   
    
    html_content = html_gen.add_data_row(html_content,[title],'style=background-color:#F8FF8A;')
    html_content = html_gen.add_data_row(html_content, data_list)
    
    xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content,[title],'background-color="#F8FF8A"')
    xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content, data_list)

    
    html_content = html_gen.close_html_table(html_content)
    xsl_fo_content = xsl_gen.close_xsl_table(xsl_fo_content)
    
    html_file = html_gen.create_html_file(html_content, file_path, report_name, current_date, True)
    xsl_fo_file = xsl_gen.create_xsl_fo_file(report_name,file_path,xsl_fo_content,current_date)
    
    for i in output_file:
        if i != '.pdf' :
            generate_file_for_other_extension(html_file, i)
        else:
            generate_pdf_from_fo_file(xsl_fo_file)
    

