import ael, acm
import FParameterUtils

from ICTCustomFEmailTransfer import ICTCustomFEmailTransfer
from datetime import datetime, date
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *

def getAccountData():
    today_date = date.today().strftime("%y%m%d")
    
    query = """
        SELECT 
            a.accnbr
        FROM 
            PARTY p, Account a
        WHERE 
            p.ptynbr = a.ptynbr AND
            p.type = 'intern Dept' AND
            p.correspondent_bank = 'Yes'
    """
    
    accnbr_list = [x[0] for x in ael.asql(query)[1][0]]
    
    list_data_2d = []
    for accnbr in accnbr_list:
        account = acm.FAccount[accnbr]
        accFullName = account.Name()
        
        if accFullName == 'USD-BONY':
            print(accFullName)
        
        try :
            fullName = account.CorrespondentBank().FullName()
        except :
            fullName = ""
        
        try :
            curr = account.Currency().Name()
        except :
            curr = ""
        
        try :
            date_update, amount = account.AdditionalInfo().ClosingBalance().split("_")
            
            if amount :
                amount = float(amount.replace("C", "").replace("D", "-"))
            else :
                date_update, amount = "-", 0
        except :
            date_update, amount = ["-", 0]
            
        list_data = [fullName + " (" + accFullName + ")", curr, amount, date_update, "-", amount]
        list_data_2d.append(list_data)
   
    return list_data_2d

def get_html(data_2d, file_name, folder_path):
    html_gen = HTMLGenerator()
    date_today = acm.Time.DateToday()
    
    html_content = html_gen.create_base_html_content('NOSTRO BALANCE', "")
    html_content = html_gen.prepare_html_table(html_content,'')
    
    html_content = html_gen.open_table_row(html_content)
    
    html_content = html_gen.open_table_row(html_content)
    html_content = html_gen.add_cell_data(html_content, f"NOSTRO BALANCE PER " + date_today, 'style="text-align:left; width:500px"')
    html_content = html_gen.close_table_row(html_content)
    
    header = [["COUNTERPARTY", "CCY", "AMOUNT", "DATES", "AIP", "BALANCE"]]
    html_content = html_gen.add_data_row(html_content, header, '', 'style = "background-color:blue; color:white; font-weight:bold"')
    
    for data in data_2d:
        html_content = html_gen.open_table_row(html_content)
        html_content = html_gen.add_cell_data(html_content, data[0], 'style="text-align:left"')
        html_content = html_gen.add_cell_data(html_content, data[1])
        html_content = html_gen.add_cell_data(html_content, f"{data[2]:,}", 'style="text-align:right"')
        html_content = html_gen.add_cell_data(html_content, data[3])
        html_content = html_gen.add_cell_data(html_content, data[4])
        html_content = html_gen.add_cell_data(html_content, f"{data[5]:,}", 'style="text-align:right"')
        html_content = html_gen.close_table_row(html_content)
    
    html_content = html_gen.open_table_row(html_content)
    for i in range(5):
        style = 'style="background-color:orange"' if i > 2 else ""
        html_content = html_gen.add_cell_data(html_content, "", style)
    html_content = html_gen.add_cell_data(html_content, f"{sum([data[5] for data in data_2d]):,}", 'style="text-align:right; background-color:yellow"')
    html_content = html_gen.close_table_row(html_content)
        
    
    html_file = html_gen.create_html_file(html_content, file_name, folder_path, date_today, True, folder_with_file_name=False)
    return html_file

def process_subject(subject_string):
    subject_string = subject_string.replace("<Date>", acm.Time.DateToday())
    return subject_string

def sendEmailCpty(params, generated_reports):
    SMTPParameters = FParameterUtils.GetFParameters(acm.GetDefaultContext(), 'CustomReportSMTPParameters')
    hostname = str(SMTPParameters.At('SMTPServer'))
    port = int(SMTPParameters.At('SMTPPort').Text())
    username = SMTPParameters.At('EmailUserName').Text()
    password = SMTPParameters.At('SMTPPassword').Text()
    tls_mode = bool(SMTPParameters.At('SecureSMTPConnection').Text())

    # Setup SMTPServer Object
    SMTPServer = ICTCustomFEmailTransfer.SMTPServer(hostname=hostname, port=port, username=username, password=password, tls_mode=tls_mode)
    
    # Setup Message Object
    split_params = params.split("\\ ")
    recipients = split_params[0].split(", ")
    subject = process_subject(split_params[1])
    sender = SMTPParameters.At('EmailSender').Text()
    body = split_params[2]
    cc = None if len(split_params) <= 3 else split_params[3].split(", ")
    
    MessageObject = ICTCustomFEmailTransfer.Message(recipients, subject, sender, body, cc, generated_reports)
    
    # Send email
    EmailTransfer = ICTCustomFEmailTransfer(SMTPServer, MessageObject)
    
    try:
        EmailTransfer.Send()
        print("Email transfer successful for", recipients)
    except Exception as e:
        print("Email Transfer failed:", e)


ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'BO47 - Laporan Saldo Nostro'}

today_date = str(date.today())

ael_variables=[
['report_name','Report Name','string', None, 'BO47 - Laporan Saldo Nostro', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.xls',0,1, 'Select Secondary Extensions Output'],
['params','Parameter','string', None, '', 1,0]
]

def ael_main(parameter):
    html_gen = HTMLGenerator()
    xsl_gen = XSLFOGenerator()
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = parameter['output_file']
    params = str(parameter['params'])

    data = getAccountData()
    html_file = get_html(data, file_path, report_name)
    
    generated_reports = []
    for extension in output_file:
        filePath = generate_file_for_other_extension(html_file, extension)
        generated_reports.append(html_file.replace(".html", extension))
    sendEmailCpty(params, generated_reports)
