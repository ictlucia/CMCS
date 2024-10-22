import acm
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from datetime import date, timedelta


ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'BOa24 - Customer Data Report - Report Data Permintaan Nasabah'}

today_date = str(date.today())

ael_variables=[
['report_name','Report Name','string', None, 'BOa24 - Customer Data Report - Report Data Permintaan Nasabah', 1,0],
['from_date','From Range','date', None, '', 0,0],
['to_date','To Range','date', None, '', 0,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.xls',0,1, 'Select Secondary Extensions Output'],
]

def get_changes_val(from_date='', to_date=''):
    if from_date and to_date :
        
        limit = acm.Time().DateAddDelta(to_date, 0, 0, 1)
        from_datetime = datetime.strptime(str(from_date), "%Y-%m-%d")
        to_datetime = datetime.strptime(str(limit), "%Y-%m-%d")
    
        time_query = f"h.creat_time >= '{from_datetime}' AND h.creat_time < '{to_datetime}'"
    
    else :
        
        time_query = "h.creat_time = TODAY"
    query_hist = f"""
    SELECT 
        h.seqnbr, h.updat_usrnbr, h.name
    FROM 
        TransHst h
    WHERE 
        {time_query} AND
        h.trans_record_type = 'Party' AND
        h.version = 0
    """
    
    list_party = ael.asql(query_hist)[1][0]
    
    query = "select * from party where ptyid = ''"
    field_names = ael.asql(query)[0]
    all_updated_list = []
    for party, owner_usrnbr, party_name in list_party:
        update_change = ""
        x = acm.FTransactionHistory[party]
        cust_name = x.NewFieldValue("ptyid",'Party')
        host_id = x.NewFieldValue("hostid",'Party')
        
        try :
            fullName = acm.FParty[party_name].FullName()
        except :
            fullName = ""
        
        user_name = acm.FUser[owner_usrnbr].Name()
        update_datetime_utc = datetime.utcfromtimestamp(x.UpdateTime()) + timedelta(hours=7)
        update_datetime = update_datetime_utc.strftime('%Y-%m-%d %H:%M:%S')
        all_updated_list.append([update_datetime, user_name, cust_name, fullName, host_id, "New Item"])
    
    return all_updated_list

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

    
    html_content = html_gen.create_base_html_content("BOa24 - Customer Data Report - Report Data Permintaan Nasabah as per. "+current_date, title_style)
    xsl_fo_content = xsl_gen.prepare_xsl_fo_content("BOa24 - Customer Data Report - Report Data Permintaan Nasabah as per. "+current_date)
    
    
    title = ['LSTMNTDTE','User Request','CMNE','Nama Nasabah','CIF Customer','Status NTCS IMPORT']
    
    html_content +="<div><table>"
    xsl_fo_content +="""<fo:table margin-bottom="50px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto"><fo:table-body>"""
    
    if parameter['from_date'] and parameter['to_date'] :
        from_date = acm.Time().AsDate(str(parameter['from_date']))
        to_date = acm.Time().AsDate(str(parameter['to_date']))
        query_result = get_changes_val(from_date, to_date)
    
    else :
        
        query_result = get_changes_val()
        
        
    html_content = html_gen.add_data_row(html_content,[title],'style=background-color:#F8FF8A;')
    html_content = html_gen.add_data_row(html_content, query_result)
    
    xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content,[title],'background-color="#F8FF8A"')
    xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content, query_result)

    html_content = html_gen.close_html_table(html_content)
    xsl_fo_content = xsl_gen.close_xsl_table(xsl_fo_content)
    
    date_report = str(datetime.now().strftime("%d%m%y"))
    
    
    html_file = html_gen.create_html_file(html_content, file_path, report_name, date_report, True)
    xsl_fo_file = xsl_gen.create_xsl_fo_file(report_name,file_path,xsl_fo_content,current_date)
    
    for i in output_file:
        if i != '.pdf' :
            generate_file_for_other_extension(html_file, i)
        else:
            generate_pdf_from_fo_file(xsl_fo_file)
