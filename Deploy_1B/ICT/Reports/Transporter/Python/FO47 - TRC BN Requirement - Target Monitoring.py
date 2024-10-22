import acm,math
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *

current_date = get_current_date("")
current_hour = get_current_hour("")
date_today = acm.Time.DateToday()
date,month,year = current_date[:2],current_date[2:4],current_date[4:]
date_today = acm.Time.DateToday()


def get_items(csvpath,csvname,portlist):
    current_port = None
    items = {
            'Banknotes Interbank':[],
            'Banknotes Branch Settlement':[]
                }
    with open(csvpath+'\\report'+year+month+date+'\\'+csvname+'.csv', 'r') as csvfile:
        lines = csvfile.readlines()
        for line in lines:
            # Splitting each line by comma, assuming CSV format
            row = line.strip().split(',')
            if row:
                for portname in items:
                    if row[0].startswith(portname):
                        current_port = row[0]
                        break
                else:
                    if current_port:
                        items[current_port].append(row)
    
    return items


ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'TRC BN Requirement - Target Monitoring'}

ael_variables=[
['report_name','Report Name','string', None, 'FO47 - TRC BN Requirement - Target Monitoring', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['csv_name','CSV File Name','string',None,'FO47',1,0], 
['targetMTDPnL','Target Month PnL','float',None,'1000000',1,0],
['targetYTDPnL','Target Year PnL','float',None,'10000000',1,0],
['targetMTDVolume','Target Month Vol','float',None,'1000000',1,0],
['targetYTDVolume','Target Year Vol','float',None,'10000000',1,0],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.xls',0,1, 'Select Secondary Extensions Output'],
]  



def ael_main(parameter):
    html_gen = HTMLGenerator()
    xsl_gen = XSLFOGenerator()
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    csv_file_name = parameter['csv_name']
    output_file = parameter['output_file']
    targetMTDPnL = parameter['targetMTDPnL']
    targetYTDPnL = parameter['targetYTDPnL']
    targetMTDVolume = parameter['targetMTDVolume']
    targetYTDVolume = parameter['targetYTDVolume']
    style = """
    .title {
        color:black;
        text-align:left;
    }
    .bold {
        font-weight:bold;
    }
    """
    
    
    
    portnames = ['Banknotes Interbank','Banknotes Branch Settlement']
    csv_file = get_items(file_path,csv_file_name,portnames)
    
    html_content = html_gen.create_base_html_content('TRC BN Report - Target Monitoring as per. '+ date_today,style)
    xsl_fo_content = xsl_gen.prepare_xsl_fo_content('TRC BN Report - Target Monitoring as per. '+ date_today)    
    
    html_content = html_gen.prepare_html_table(html_content,'')
    xsl_fo_content += """<fo:table margin-bottom="50px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto"><fo:table-body>"""

    html_content = html_gen.open_table_row(html_content)
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
        
    html_content = html_gen.add_cell_data(html_content,'P&L','colspan=8 class="bold"')
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,'P&#38;L','number-columns-spanned="8" font-weight="bold"')
    
    html_content = html_gen.add_cell_data(html_content,'Volume in USD (in million USD)','colspan=8 class="bold"')
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,'Volume in USD (in million USD)','number-columns-spanned="8" font-weight="bold"')

    html_content = html_gen.close_table_row(html_content)
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)

    list_subtitle = ['Portfolio', 'Today','MTD','YTD','Target MTD','Target MTD%','Target YTD','Target YTD%','Today','MTD','YTD','Target MTD','Target MTD%','TargetYTD','Target YTD%']
    
    html_content = html_gen.add_data_row(html_content,[list_subtitle])
    xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content,[list_subtitle])
    
    for each_port,all_items in csv_file.items():
        portfolio = each_port
        todaypnl,mtdpnl,ytdpnl = 0,0,0
        todayvol,mtdvol,ytdvol = 0,0,0
        
        for each_item in all_items:
            if each_item[1].lower() != 'nan':
                todaypnl += float(each_item[1])/1000000
            if each_item[2].lower() != 'nan':
                mtdpnl += float(each_item[2])/1000000
            if each_item[3].lower() != 'nan':
                ytdpnl += float(each_item[3])/1000000
            if each_item[4].lower() != 'nan':
                todayvol += float(each_item[4])/1000000
            if each_item[5].lower() != 'nan':
                mtdvol += float(each_item[5])/1000000
            if each_item[6].lower() != 'nan':
                ytdvol += float(each_item[6])/1000000
        
        mtdpnlpercent = abs(mtdpnl/targetMTDPnL*100)
        ytdpnlpercent = abs(ytdpnl/targetYTDPnL*100)
        
        mtdvolpercent = abs(mtdvol/targetMTDVolume*100)
        ytdvolpercent = abs(ytdvol/targetYTDVolume*100)
        
        html_content = html_gen.open_table_row(html_content)
        xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
            
        html_content = html_gen.add_cell_data(html_content,portfolio)
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,portfolio)
        
        html_content = html_gen.add_cell_data(html_content,f"{round(todaypnl,2):,}")
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{round(todaypnl,2):,}")
        
        html_content = html_gen.add_cell_data(html_content,f"{round(mtdpnl,2):,}")
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{round(mtdpnl,2):,}")
        
        html_content = html_gen.add_cell_data(html_content,f"{round(ytdpnl,2):,}")
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{round(ytdpnl,2):,}")
        
        html_content = html_gen.add_cell_data(html_content,f"{targetMTDPnL:,}")
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{targetMTDPnL:,}")
        
        html_content = html_gen.add_cell_data(html_content,f"{round(mtdpnlpercent,2):,}")
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{round(mtdpnlpercent,2):,}")
        
        html_content = html_gen.add_cell_data(html_content,f"{targetYTDPnL:,}")
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{targetYTDPnL:,}")
        
        html_content = html_gen.add_cell_data(html_content,f"{round(ytdpnlpercent,2):,}")
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{round(ytdpnlpercent,2):,}")
        
        html_content = html_gen.add_cell_data(html_content,f"{round(todayvol,2):,}")
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{round(todayvol,2):,}")
        
        html_content = html_gen.add_cell_data(html_content,f"{round(mtdvol,2):,}")
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{round(mtdvol,2):,}")
        
        html_content = html_gen.add_cell_data(html_content,f"{round(ytdvol,2):,}")
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{round(ytdvol,2):,}")
        
        html_content = html_gen.add_cell_data(html_content,f"{targetMTDVolume:,}")
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{targetMTDVolume:,}")
        
        html_content = html_gen.add_cell_data(html_content,f"{round(mtdvolpercent,2):,}")
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{round(mtdvolpercent,2):,}")
        
        html_content = html_gen.add_cell_data(html_content,f"{targetYTDVolume:,}")
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{targetYTDVolume:,}")
        
        html_content = html_gen.add_cell_data(html_content,f"{round(ytdvolpercent,2):,}")
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{round(ytdvolpercent,2):,}")
        
        html_content = html_gen.close_table_row(html_content)
        xsl_fo_content = xsl_gen.close_xsl_table(xsl_fo_content)
        
        
    html_content = html_gen.close_html_table(html_content)
    xsl_fo_content = xsl_gen.close_xsl_table(xsl_fo_content)
    
    html_file = html_gen.create_html_file(html_content, file_path, report_name+" "+current_date+current_hour, current_date, True)
    xsl_fo_file = xsl_gen.create_xsl_fo_file(report_name+" "+current_date+current_hour,file_path, xsl_fo_content, current_date)

    for i in output_file:
        if i != '.pdf' :
            generate_file_for_other_extension(html_file, i)
        else:
            generate_pdf_from_fo_file(xsl_fo_file)
