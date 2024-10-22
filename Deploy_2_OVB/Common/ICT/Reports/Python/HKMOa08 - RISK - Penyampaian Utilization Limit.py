import acm
import ael
import random
import locale
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *

locale.setlocale(locale.LC_ALL, '')
html_gen = HTMLGenerator()
xslfo_gen = XSLFOGenerator()
dateToday = acm.Time.DateToday()
thisYear = acm.Time.DateToYMD(dateToday).First()
default_report_name = "HKMOa08 - RISK - Penyampaian Utilization Limit"
status_color_code = {'white': '#ffffff', 'green': '#66ff8c', 'grey': '#b3b3b3', 'yellow': '#dfdf20', 'red': '#ff3333'}

def open_html_table():
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
        <style>
            table {{
                width: 1000px;
                }}
            .left-text {{
                text-align: left;
                }}
            .right-text {{
                text-align: right;
                }}
            .mid-text {{
                text-align: center;
                }}
            .th1 {{
                font-size: 20px; 
                background-color: #ffffff; 
                text-align: center; 
                padding: 10px; 
                }}
            .th2 {{
                font-size: 18px; 
                background-color: #abdbe3; 
                text-align: center; 
                }}
            .status-white {{
                text-align: center;
                background-color: {status_color_code['white']};
                color: black; /* Text color for white cells */
                }}
            .status-green {{
                text-align: center;
                background-color: {status_color_code['green']};
                color: black; /* Text color for green cells */
                }}
            .status-grey {{
                text-align: center;
                background-color: {status_color_code['grey']};
                color: black; /* Text color for grey cells */
                }}
            .status-yellow {{
                text-align: center;
                background-color: {status_color_code['yellow']};
                color: black; /* Text color for yellow cells */
                }}
            .status-red {{
                text-align: center;
                background-color: {status_color_code['red']};
                color: black; /* Text color for red cells */
                }}
        </style>
    </head>
    <body>
        <table>
            """

def number_reformat(value):
    locale.setlocale(locale.LC_ALL, '')
    return locale.format_string("%.2f", value, grouping=True)
 
def html_table(title, header_list, header_colspan, header_rowspan, content_align, content_list=None):
    today_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    str_date = f"{str(today_date)} (UTC+07:00)"
    title_table = f'<tr> <th class="th1" colspan="{sum(header_colspan)}">{title}</th></tr>\n'
    date_gen = f'<tr><td>{str_date}</th></tr>\n'
    skip_row = "<tr> <td>&nbsp;</td></tr>\n"
    str_header = ""
    for i, headers in enumerate(header_list):
        str_header += "<tr>\n"
        if not i:
            for header, m, n in zip(headers, header_colspan, header_rowspan):
                str_header += f'<th class="th2" colspan="{m}" rowspan="{n}">{header}</th>\n' 
            str_header += "</tr>\n"
        else:
            for header in headers:
                str_header += f'<th class="th2">{header}</th>\n' 
            str_header += "</tr>\n"
    str_content = ""
    for row_content in content_list:
        str_content += "<tr>\n"
        for i in range(len(row_content)):
            if row_content[i] in status_color_code.keys():
                str_content += f'<td class = "status-{row_content[i]}"></td>\n'
            else:
                str_content += f'<td class = "{content_align[i]}-text">{row_content[i]}</td>\n'
        str_content += "</tr>\n"
    return title_table + date_gen + skip_row + str_header + str_content + "</table>\n" + "</body>\n" + "</html>"
 
def xslfo_gen(header_list, header_colspan, header_rowspan, data, file_name, file_path, date, title):
    gen = XSLFOGenerator()
    today_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    str_date = f"{str(today_date)} (UTC+07:00)"
    title_styling = 'margin-bottom="30px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto" font-weight = "bold" font-size = "24px"'
    xsl_fo_content = gen.prepare_xsl_fo_content(title, title_styling)
    xsl_fo_content += '<fo:block margin-bottom="30px" text-align="left" display-align="left" inline-progression-dimension="auto" table-layout="auto" font-weight = "bold" font-size = "12px"> {} </fo:block>"'.format(str_date)
    header = header_list[0] + header_list[1]
    xsl_fo_content = gen.add_xsl_fo_table_header(xsl_fo_content, header)
    xsl_fo_content = xsl_fo_content.replace('<fo:table-column border-width="1px" border-style="solid"/>', '')
    for i, header_column in enumerate(header):
        if header_column in header_list[0]:
            xsl_fo_content = xsl_fo_content.replace(
                f'><fo:block>{header_column}</fo:block></fo:table-cell>', 
                f' number-columns-spanned="{header_colspan[i]}" number-rows-spanned="{header_rowspan[i]}"><fo:block>{header_column}</fo:block></fo:table-cell>'
                )
            if header_column == header_list[0][-1]:
                xsl_fo_content = xsl_fo_content.replace(
                                f'<fo:block>{header_column}</fo:block></fo:table-cell>',
                                f'<fo:block>{header_column}</fo:block></fo:table-cell>\n</fo:table-row>\n<fo:table-row>'
                                )
                break
    xsl_fo_content = gen.add_xsl_data_row(xsl_fo_content, data)
    for color in status_color_code.keys():
        xsl_fo_content = xsl_fo_content.replace(
                        f'><fo:block >{color}</fo:block>',
                        f' background-color="{status_color_code[color]}"><fo:block ></fo:block>'
                        )
    xsl_fo_content = gen.close_xsl_table(xsl_fo_content)
    xsl_fo_file = gen.create_xsl_fo_file(file_name, file_path, xsl_fo_content, date)
    return xsl_fo_file

def get_currency(compliance_name):
    cr = acm.FComplianceRule[compliance_name]
    appliedRule = cr.AppliedRules().First()
    try:
        param = appliedRule.ParameterNames().First()
        ccy = appliedRule.GetParameter(param).At('FixedCurr').Name()
    except:
        try:
            ccy = cr.Definition().Column().Configuration().ParamDict().At('columnParameters').At('FixedCurr').Name()
        except:
            ccy = "-"
    return ccy

def get_price(ccy):
    query = f"""
        SELECT 
            Display_id(p, 'insaddr') 'curr1', 
            Display_id(p, 'curr') 'curr2', 
            p.settle, 
            p.historical, 
            Display_id(p, 'ptynbr') 'market', 
            p.day 
        FROM 
            price p 
        WHERE 
            Display_id(p, 'insaddr') IN ('{ccy}', 'USD') 
            AND Display_id(p, 'curr') IN ('{ccy}', 'USD') 
            AND p.historical = 'Yes' 
            AND Display_id(p, 'ptynbr') = 'EOD_MtM' 
            AND p.day BETWEEN firstdayofyear 
            AND today 
        ORDER BY 
            p.day DESC
        """
    result = ael.asql(query)[1][0][0]
    return result[0], result[1], result[2]

def threshold_check(watermark, threshold, threshold_type, comparison_type):
    threshold_type = threshold_type.lower()
    comparison_type = comparison_type.lower()
    color_map = {
        'violation': 'red',
        'warning': 'yellow',
        'reporting': 'green'
        }
    comparison_ops = {
        'greater or equal': lambda w, t: w >= t,
        'greater': lambda w, t: w > t,
        'less or equal': lambda w, t: w <= t,
        'less': lambda w, t: w < t,
        'equal': lambda w, t: w == t,
        'not equal': lambda w, t: w != t
        }
    if threshold_type in color_map and comparison_type in comparison_ops:
        if comparison_ops[comparison_type](watermark, threshold):
            return color_map[threshold_type]
    return None
        
def convert_to_usd(value, currency):
    if currency == 'USD':
        return value
    else:
        rate = get_price(currency)
        if (rate[0] == currency) and (rate[1] == 'USD'):
            return value * rate[2]
        elif (rate[0] == 'USD') and (rate[1] == currency):
            return value / rate[2]
        else:
            return value
            
def get_data_content(report_name, report_year, *compliances):
    fx_compliance, ir_compliance, total_compliance = compliances[0], compliances[1], compliances[2]
    query = acm.FSQL[report_name].Text().format(
                year = report_year,
                fx_compliance_name = fx_compliance,
                ir_compliance_name = ir_compliance,
                total_compliance_name = total_compliance
        )
    raw_data = ael.asql(query)
    
    idx = {header: raw_data[0].index(header) for header in raw_data[0]}
    
    def reset_counters():
        return (
            {key: "-" for key in compliances},
            {key: "-" for key in compliances},
            {key: "-" for key in compliances},
            {key: "white" for key in compliances},
            {key: False for key in compliances},
        )

    def format_value(number: float, n, percent=False) -> str:
        try:
            formatted_number = locale.format_string(f"%.{n}f", abs(number), grouping=True)
            if number < 0:
                formatted_number = f"({formatted_number})"
            if percent:
                formatted_number = formatted_number.replace(")", "%)") if number < 0 else f"{formatted_number}%"
            return formatted_number
        except:
            return str(number)
            
    content_list = []
    real_data = raw_data[1][0]
    states = reset_counters()[-1]
    for i, data_row in enumerate(real_data, start=1):
        group_no = data_row[idx['t_group']]
        if states[fx_compliance] and states[ir_compliance] and states[total_compliance] and group_no.lower() != 'group 1':
            continue
            
        columns = {'fx_name': data_row[idx['fx_name']],
            'ir_name' : data_row[idx['ir_name']],
            'total_name' : data_row[idx['total_name']]
            }
        start_datetime = data_row[idx['start_time']]
        date = datetime.strptime(acm.Time.UtcToLocal(start_datetime), "%Y-%m-%d %H:%M:%S")
        
        if group_no.lower() == 'group 1':
            thresholds, watermarks, realisasis, statuses, states = reset_counters()
        for name in columns:
            compliance_name = str(columns[name])
            
            if compliance_name.strip() in ('', '-', None, 'None'):
                continue

            currency = get_currency(compliance_name)
            comp_type = name.split("_")[0]
            threshold_temp = data_row[idx[comp_type + '_threshold']].replace(",", "")
            watermark_temp = data_row[idx[comp_type + '_watermark']].replace(",", "")
            realisasi_temp = data_row[idx[comp_type + '_realisasi']].replace(",", "")
            
            threshold_type = data_row[idx[comp_type + '_threshold_type']]
            comparison_type = data_row[idx[comp_type + '_comparison_type']]
            
            if threshold_temp != "-":
                threshold_temp = convert_to_usd(float(threshold_temp), currency)
            if watermark_temp != "-":
                watermark_temp = convert_to_usd(float(watermark_temp), currency)
            if realisasi_temp != "-":
                realisasi_temp = float(realisasi_temp)
                
            if group_no.lower() == 'group 1':
                thresholds[compliance_name] = format_value(threshold_temp, 2)
                watermarks[compliance_name] = format_value(watermark_temp, 2)
                realisasis[compliance_name] = format_value(realisasi_temp, 2, True)
                
            ###
            if states[compliance_name]:
                continue
            else:
                if watermark_temp == "-" or threshold_temp == "-":
                    if group_no.lower() == 'group 1':
                        statuses[compliance_name] = 'grey'
                        continue
                elif watermark_temp != "-" and threshold_temp != "-":
                    status_color = threshold_check(watermark_temp, threshold_temp, threshold_type, comparison_type)
                    if status_color:
                        statuses[compliance_name] = status_color
                        states[compliance_name] = True
                    else:
                        if i == len(real_data):
                            if statuses[compliance_name] == 'white':
                                statuses[compliance_name] = 'green'
                                states[compliance_name] = True
                            elif statuses[compliance_name] == 'grey':
                                states[compliance_name] = True
                            continue
                            
                        if real_data[i][idx['t_group']].lower() == 'group 1':
                            if statuses[compliance_name] == 'white':
                                statuses[compliance_name] = 'green'
                                states[compliance_name] = True
                            elif statuses[compliance_name] == 'grey':
                                states[compliance_name] = True
                            continue
                        else:
                            states[compliance_name] = False
                            continue
            
        if i == len(real_data):
            for comp in compliances:
                states[comp] = True

        try:
            after_row = real_data[i][idx['t_group']].lower()
        except:
            pass
        if after_row == 'group 1':
            for comp in compliances:
                if statuses[comp] in ('white', 'grey'):
                    states[comp] = True
        '''
        print(i, thresholds[fx_compliance], watermarks[fx_compliance], realisasis[fx_compliance], statuses[fx_compliance], states[fx_compliance], '*'*3,
            thresholds[ir_compliance], watermarks[ir_compliance], realisasis[ir_compliance], statuses[ir_compliance], states[ir_compliance], '*'*3,
            thresholds[total_compliance], watermarks[total_compliance], realisasis[total_compliance], statuses[total_compliance], states[total_compliance])
        '''
        if states[fx_compliance] and states[ir_compliance] and states[total_compliance]:            
            content_list.append([str(date), str(thresholds[fx_compliance]), str(watermarks[fx_compliance]), str(realisasis[fx_compliance]), str(statuses[fx_compliance]),
                str(thresholds[ir_compliance]), str(watermarks[ir_compliance]), str(realisasis[ir_compliance]), str(statuses[ir_compliance]),
                str(thresholds[total_compliance]), str(watermarks[total_compliance]), str(realisasis[total_compliance]), str(statuses[total_compliance])])
            for comp in compliances:
                states[comp] = False
        
    return content_list
        
def get_compliance_collections(rule_category):
    query = f"""
        SELECT 
            cr.NAME, 
            cr.definition 
        FROM 
            compliancerule cr 
        WHERE 
            lower(cr.definition) IN (
            {tuple_to_string(rule_category) })
        """
    result = ael.asql(query)
    return [i[0] for i in result[1][0]]

def tuple_to_string(tup):
    return ', '.join(f"'{item}'" for item in tup)

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption': default_report_name}
ael_variables=[
['report_name','Report Name','string', None, default_report_name, 0, 0, 'Name for the Report'],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1,  'Directory Path for Report File'],
['output_file','Output Files','string', ['.pdf', '.xls'], '.pdf', 1 , 0, 'Select Output Extension Type'],
['report_type','Report Type','string', ('Net Open Position', 'Value at Risk', 'Monthly Loss', 'Yearly Loss'), '', 0, 0, 'Select Report Type of HKMOa08 Penyampaian Utilization Limit'],
['report_year','Report Year','int', None, thisYear, 1, 0, 'Year for the Report Filter'],
['fx_rule','Compliance Rule for FX', 'string', get_compliance_collections(('exposure',)), '', 1, 0, 'Select Compliance Rule Name for FX Type'],
['ir_rule','Compliance Rule for IR', 'string', get_compliance_collections(('exposure',)), '', 1, 0, 'Select Compliance Rule Name for IR Type'],
['total_rule','Compliance Rule for Total', 'string', get_compliance_collections(('exposure',)), '', 1, 0, 'Select Compliance Rule Name for Total Type']
]

def ael_main(parameter):
    ## DEFINE GUI PARAMETER IN VARIABLE
    report_name = str(parameter['report_name'])
    file_path = str(parameter['file_path'])
    output_file = str(parameter['output_file'])
    report_type = str(parameter['report_type'])
    report_year = str(parameter['report_year'])
    fx_rule = str(parameter['fx_rule'])
    ir_rule = str(parameter['ir_rule'])
    total_rule = str(parameter['total_rule'])

    ## GETING A DATA THAT NEEDED FOR TABLE
    title = " - ".join([report_name, report_type + ' Limit Monitoring', report_year])
    header_colspan, header_rowspan = (1, 4, 4, 4), (2, 1, 1, 1)
    header_list = [["Date", "FX", "IR", "Total"], ["Limit", "Realisasi", "%Realisasi", "Status"]*3]
    content_align = ["mid"]*sum(header_colspan)
    content_list = get_data_content(report_name, report_year, fx_rule, ir_rule, total_rule)
    date_today = datetime.today().strftime('%Y%m%d')

    ## GENERATE SAVING DATA TO HTML OR XLS
    html_code = open_html_table() + html_table(title, header_list, header_colspan, header_rowspan, content_align, content_list)
    html_code = html_code.replace('<th class="th2"', '<th style="border: 1px solid black;" class="th2"')
    html_code = html_code.replace("<td class", '<td style="border: 1px solid black;" class')

    if output_file == ".html" :
        generate_html = HTMLGenerator().create_html_file(html_code, file_path, title, date_today, False)
    elif output_file == ".xls" :
        generate_html = HTMLGenerator().create_html_file(html_code, file_path, title, date_today, False)
        generate_file_for_other_extension(generate_html, '.xls')
        os.remove(generate_html)
    elif output_file == ".pdf" :
        if len(content_list) != 0:
            xslfo_file = xslfo_gen(header_list, header_colspan, header_rowspan, content_list, title, file_path, date_today, title)
            generate_pdf_from_fo_file(xslfo_file)
            os.remove(xslfo_file)
