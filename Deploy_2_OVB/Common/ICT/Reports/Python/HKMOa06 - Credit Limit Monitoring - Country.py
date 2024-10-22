import acm
import ael
import locale
from datetime import datetime
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
 
##################################################################################
# CREATE HTML TEMPLATE TABLE
##################################################################################
## OPEN TABLE OF HTML & DEFINE A STYLE OF TABLE
 
def open_html_table():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <style>
        table {
            width: 1000px;
        }
        /* Text Align - Left */
        .left-text {
            text-align: left;
        }
        .right-text {
            text-align: right;
        }
        .mid-text {
            text-align: center;
        }
    </style>
</head>
<body>
    <table>
    """

def get_price(ccy):
    query = """
    select display_id(p, 'insaddr') 'curr1', display_id(p, 'curr') 'curr2', p.settle, p.historical, display_id(p, 'ptynbr') 'market', p.day
    from price p
    where  display_id(p,'insaddr') in ('{curr}', 'USD')
    and display_id(p, 'curr') in ('{curr}', 'USD')
    and p.historical = 'Yes'
    and display_id(p, 'ptynbr') = 'EOD_MtM'
    and p.day between FIRSTDAYOFYEAR and TODAY
    order by p.day desc
        """.format(curr=ccy)
    result = ael.asql(query)[1][0][0]
    return result[0], result[1], result[2]

def number_reformat(value):
    locale.setlocale(locale.LC_ALL, '')
    return locale.format_string("%.2f", value, grouping=True)
 
## FILLING A TABLE CONTENT IN HTML CODE
def html_table(title, header_list, content_align, content_list=None):
    today_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    str_date = f"{str(today_date)} (UTC+07:00)"
    title_table = f'<tr> <th colspan="{len(header_list)}">{title}</th></tr>\n'
    date_gen = f'<tr><td>{str_date}</th></tr>\n'
    skip_row = "<tr> <td>&nbsp;</td></tr>\n"
    str_header = "<tr>\n" #Open row of HTML Table
    for header in header_list:
        str_header += f"<th>{header}</th>\n" #List of header column of table
    str_header += "</tr>\n"
    ## Looping content for each column per row
    str_content = "<tr>\n"
    for row_content in content_list:
        for i in range(len(row_content)):
            str_content += f'<td class = "{content_align[i]}-text">{row_content[i]}</td>\n'
        str_content += "<tr>\n"
    return title_table + date_gen + skip_row + str_header + str_content + "</table>\n" + "</body>\n" + "</html>"
 
def xslfo_gen(header, title, data, file_name, file_path, date):
    gen = XSLFOGenerator()
    today_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    str_date = f"{str(today_date)} (UTC+07:00)"
    title_styling = 'margin-bottom="30px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto" font-weight = "bold" font-size = "24px"'
    xsl_fo_content = gen.prepare_xsl_fo_content(title, title_styling)
    xsl_fo_content += '<fo:block margin-bottom="30px" text-align="left" display-align="left" inline-progression-dimension="auto" table-layout="auto" font-weight = "bold" font-size = "12px"> {} </fo:block>"'.format(str_date)
    xsl_fo_content = gen.add_xsl_fo_table_header(xsl_fo_content, header)
    xsl_fo_content = gen.add_xsl_data_row(xsl_fo_content, data)
    xsl_fo_content = gen.close_xsl_table(xsl_fo_content)
    xsl_fo_file = gen.create_xsl_fo_file(file_name, file_path, xsl_fo_content, date)
    return xsl_fo_file
 
##################################################################################
# GENERATE DATA
##################################################################################
## SCRAPPING DATABASE USING AEL & ACM FOR COMPALIANCE RULE DATA
 
def get_content_list(compliance_rule_name):
    content_list = []
    cr = acm.FComplianceRule[compliance_rule_name]
    for appliedRule in [ars for ars in cr.AppliedRules() if ars.Inactive() == False]:
        targetName = appliedRule.TargetName()
        target = appliedRule.Target()
        targetType = appliedRule.TargetType()
        ########## COUNTRY_ID ##########
        if targetType == 'ChoiceList':
            Id = target.Description()
        elif targetType == 'Portfolio':
            Id = target.AssignInfo()
        elif targetType == 'Party':
            Id = target.Id2()
        elif targetType == 'HierarchyNode':
            Id = target.DisplayName()
        else:
            Id = "-"
    
        if (Id is None) or (Id.strip() == ""):
            Id = "-"
        
        ########## EXPDATE ##########
        expDate = appliedRule.EndDate()
        if (expDate is None) or (expDate.strip() == ""):
            expDate = "-"
     
        ########## CCY ##########
        try:
            param = appliedRule.ParameterNames().First()
            ccy = appliedRule.GetParameter(param).At('FixedCurr').Name()
        except:
            try:
                ccy = cr.Definition().Column().Configuration().ParamDict().At('columnParameters').At('FixedCurr').Name()
            except:
                ccy = "-"

        ########## LIMIT AMOUNT ##########
        try:
            limAmt = appliedRule.ThresholdValues().First().ValueAdjusted()
        except:
            try:
                limAmt = cr.Thresholds().First().ValueAdjusted()
            except:
                limAmt = 0
        ########## LIMIT AMOUNT in USD ##########
        try:
            if ccy == 'USD':
                limAmt_usd = limAmt
            else:
                rate = get_price(ccy)
                if (rate[0] == ccy) and (rate[1] == 'USD'):
                    limAmt_usd = limAmt * rate[2]
                elif (rate[0] == 'USD') and (rate[1] == ccy):
                    limAmt_usd = limAmt / rate[2]
                else:
                    limAmt_usd = 0
        except:
            limAmt_usd = 0
        ### convert format ###
        limAmt = number_reformat(limAmt)
        limAmt_usd = number_reformat(limAmt_usd)

        ########## EXPOSURE/WATERMARK VALUE ##########
        tv = appliedRule.ThresholdValues().First()
        try:
            rh = tv.ResultsHistory().Last()
            exposure = float(rh.ValuesHistory().Last().Watermark())
        except:
            exposure = 0
        
        ########## EXPOSURE/WATERMARK VALUE in USD ##########
        try:
            if ccy == 'USD':
                exposure_usd = exposure
            else:
                rate = get_price(ccy)
                if (rate[0] == ccy) and (rate[1] == 'USD'):
                    exposure_usd = exposure * rate[2]
                elif (rate[0] == 'USD') and (rate[1] == ccy):
                    exposure_usd = exposure / rate[2]
                else:
                    exposure_usd = 0
        except:
            exposure_usd = 0
        ### convert format ###
        exposure = number_reformat(round(exposure, 2))
        exposure_usd = number_reformat(round(exposure_usd, 2))
        
        ### COMBINE ###
        content_list.append([str(Id), str(targetName), str(ccy), str(limAmt), str(expDate), str(compliance_rule_name), str(limAmt_usd), str(exposure_usd)])
    return content_list
 
def get_compliance_rule_name(rule_category, rule_type):
    query = """
    SELECT cr.name, display_id(cr, 'category') 'category', cr.definition
    FROM ComplianceRule cr
    WHERE display_id(cr, 'category') = '{}'
    AND cr.definition = '{}'
    """.format(rule_category, rule_type)
    result = ael.asql(query)[1][0]
    return [row[0] for row in result]
 
##################################################################################
# CREATING A GUI PARAMETER
##################################################################################
 
ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'HKMOa06 - Credit Limit Monitoring - Country'}
ael_variables=[
['report_name','Report Name','string', None, 'HKMOa06 - Credit Limit Monitoring - Country', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Output Files','string', ['.pdf', '.xls'], '.pdf', 1, 0, 'Select Output Extension Type'],
['compliance_rule','Compliance Rule','string', get_compliance_rule_name('Pre-Deal', 'PositionAndRiskControl'), 'BMHK Country Limit', 1,0, 'Compliance Rule with Pre-Deal Category and Position Risk Control Type']
]
 
def ael_main(parameter):
    ## DEFINE GUI PARAMETER IN VARIABLE
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = "".join(parameter['output_file'])
    compliance_rule = str(parameter['compliance_rule'])
   
    ## GETING A DATA THAT NEEDED FOR TABLE
    title = "HKMOa06 - Credit Limit Monitoring - Country"
    header_list = ["CountryId", "LongName", "Ccy", "LimitAmt", "ExpDate", "ProductType", "LimAmt", "Exposure"]
    content_align = ["mid", "mid", "mid", "mid", "mid", "mid", "mid", "mid"]
    content_list = get_content_list(compliance_rule)
    content_list.sort()
    date_today = datetime.today().strftime('%y%m%d')
 
    ## GENERATE SAVING DATA TO HTML OR XLS
    html_code = open_html_table() + html_table(title, header_list, content_align, content_list)
    html_code = html_code.replace("<th>", '<th style="border: 1px solid black;">')
    html_code = html_code.replace("<td class", '<td style="border: 1px solid black;" class')
    
    if output_file == ".html" :
        generate_html = HTMLGenerator().create_html_file(html_code, file_path, report_name, date_today, False)
    elif output_file == ".xls" :
        generate_html = HTMLGenerator().create_html_file(html_code, file_path, report_name, date_today, False)
        generate_file_for_other_extension(generate_html, '.xls')
        os.remove(generate_html)
    elif output_file == ".pdf" :
        if len(content_list) != 0:
            xslfo_file = xslfo_gen(header_list, title, content_list, report_name, file_path, date_today)
            generate_pdf_from_fo_file(xslfo_file)
            os.remove(xslfo_file)
