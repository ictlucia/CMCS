from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import acm, ael
ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'Target Monitoring'}
#settings.FILE_EXTENSIONS
ael_variables=[
['report_name','Report Name','string', None, 'FO47 - TAS Report - Target Monitoring', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, 'C:\Desktop', 1, 1],
['targetMTDPnL','Target Month PnL','float',None,'1000000',1,0],
['targetYTDPnL','Target Year PnL','float',None,'10000000',1,0],
['targetMTDVolume','Target Month Vol','float',None,'1000000',1,0],
['targetYTDVolume','Target Year Vol','float',None,'10000000',1,0],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.xls',0,1, 'Select Secondary Extensions Output'],
]  

def create_xsl_fo_file(file_name, file_path, list_table, title, current_datetime, folder_with_file_name=False):
    xsl_fo_content = """<?xml version="1.1" encoding="utf-8"?>
<fo:root xmlns:fo="http://www.w3.org/1999/XSL/Format">
 <fo:layout-master-set>
  <fo:simple-page-master master-name="my_page" margin="0.5in" page-width="25in">
   <fo:region-body/>
  </fo:simple-page-master>
 </fo:layout-master-set>
 <fo:page-sequence master-reference="my_page">
  <fo:flow flow-name="xsl-region-body">
    <fo:block font-weight="bold" font-size="30px" margin-bottom="30px">"""+str(title)+"""</fo:block>
"""
  
    for i in list_table :
        xsl_fo_content += i +"\n"
        
    xsl_fo_content += """ </fo:flow>
 </fo:page-sequence>
</fo:root>
    """
    
    if folder_with_file_name:
        folder_path = file_path+"\\"+file_name+"\\"+current_datetime
    else:
        folder_path = file_path+"\\report"+current_datetime
        
    try:
        os.makedirs(folder_path)
    except:
        #print('Path too long')
        pass
    
    file_url = folder_path+"\\"+file_name+".fo"
    f = open(file_url, "w")
    f.write(xsl_fo_content)
    f.close()
    
    return file_url 


def getPNLTrade(tradenumber):
    context = acm.GetDefaultContext()
    sheetType = 'FTradeSheet'
    ins = acm.FTrade[tradenumber]
    columnId = "Portfolio Total Profit and Loss"
    calcSpace = acm.Calculations().CreateCalculationSpace(context, sheetType)
    result1 = calcSpace.CreateCalculation(ins, columnId).FormattedValue()
    result2 = result1.replace("#","")
    result3 = result2.replace(",","")
    result4 = result3.replace(".","")
    return int(result4) / 1000000000

def getPremium(trdnbr, premium):
    if premium > 0 or premium < 0:
        premium = convert_premium_to_USD(trdnbr, premium)
        return abs(round(premium / 1000000, 2))
    return 0

def convert_premium_to_USD(trdnbr, premium):
    trade = acm.FTrade[trdnbr]
    if trade.Currency().Name() == 'USD':
        return premium
    
    PE = acm.FPrice.Select('currency=%s' % trade.Currency().Name())

    for price in PE:
        if price.Instrument().Name() == 'USD' and price.Market().Name() == 'REFINITIV_SPOT':
            return premium / price.Settle()
    
    for price in PE:
        if price.Instrument().Name() == 'USD' and price.Settle() > 0:
            return premium / price.Settle()
        
def ael_main(parameter):
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = parameter['output_file']
    targetMTDPnL = parameter['targetMTDPnL']
    targetYTDPnL = parameter['targetYTDPnL']
    targetMTDVolume = parameter['targetMTDVolume']
    targetYTDVolume = parameter['targetYTDVolume']
    query = ael.asql("SELECT t.trdnbr, t.premium,p.prfid FROM trade t, portfolio p, portfoliolink pl where p.prfnbr=pl.member_prfnbr and pl.owner_prfnbr=10 and t.prfnbr=p.prfnbr and (t.optkey3_chlnbr=470 or t.optkey3_chlnbr=469) ORDER BY p.prfid DESC")
    titles=[]
    titlesfo=['']
    prfid=''
    rows = [['P&L','Volume in USD'],['Portfolio','Trade Number', 'Today','MTD','YTD','Target MTD','Target MTD%','Target YTD','Target YTD%','Today','MTD','YTD','Target MTD','Target MTD%','TargetYTD','Target YTD%']]
    length = len(query[1][0])
    base_title_row = len(rows)
    counter = 0
    counter_2 = 0
    for i in range(length):
        if query[1][0][i][2] == prfid:
            theoreticalval = getPNLTrade(query[1][0][i][0])
            premium = getPremium(query[1][0][i][0], query[1][0][i][1])
            if premium!="":
                rows.append(['', query[1][0][i][0], "{:,}".format(theoreticalval), "{:,}".format(round(theoreticalval*30,2)), "{:,}".format(round(theoreticalval*365,2)), '','','','',"{:,}".format(premium),"{:,}".format(round(premium*30,2)),"{:,}".format(round(premium*365,2)), '', '', '', ''])
                rows[title_row][2] += theoreticalval
                rows[title_row][3] += theoreticalval * 30
                rows[title_row][4] += theoreticalval * 365
                rows[title_row][9] += premium
                rows[title_row][10] += premium * 30
                rows[title_row][11] += premium * 365
                counter += 1
                counter_2 += 1
        else: 
            title_row = base_title_row + counter
            prfid=query[1][0][i][2]
            rows.append([prfid, '', 0, 0, 0, "{:,}".format(targetMTDPnL), 0, "{:,}".format(targetYTDPnL), 0, 0, 0, 0, "{:,}".format(targetMTDVolume), 0, "{:,}".format(targetYTDVolume),0])
            counter += 1
            if (title_row > base_title_row):
                rows[title_row - counter_2 - 1][2] = "{:,}".format(round(rows[title_row - counter_2 - 1][2], 2))
                rows[title_row - counter_2 - 1][6] = "{:,}".format(round(((rows[title_row - counter_2 - 1][3]/targetMTDPnL) * 100), 2))
                rows[title_row - counter_2 - 1][8] = "{:,}".format(round(((rows[title_row - counter_2 - 1][4]/targetYTDPnL) * 100), 2))
                rows[title_row - counter_2 - 1][13] = "{:,}".format(round(((rows[title_row - counter_2 - 1][10]/targetMTDVolume) * 100), 2))
                rows[title_row - counter_2 - 1][15] = "{:,}".format(round(((rows[title_row - counter_2 - 1][11]/targetYTDVolume) * 100), 2))
            counter_2 = 0
    rows[title_row][2] = "{:,}".format(round(rows[title_row][2], 2))
    rows[title_row][6] = "{:,}".format(round(((rows[title_row][3]/targetMTDPnL) * 100), 2))
    rows[title_row][8] = "{:,}".format(round(((rows[title_row][4]/targetYTDPnL) * 100), 2))
    rows[title_row][13] = "{:,}".format(round(((rows[title_row][10]/targetMTDVolume) * 100), 2))
    rows[title_row][15] = "{:,}".format(round(((rows[title_row][11]/targetYTDVolume) * 100), 2))
    rows[title_row][3] = "{:,}".format(round(rows[title_row][3], 2))
    rows[title_row][4] = "{:,}".format(round(rows[title_row][4], 2))
    rows[title_row][9] = "{:,}".format(round(rows[title_row][9], 2))
    rows[title_row][10] = "{:,}".format(round(rows[title_row][10], 2))
    rows[title_row][11] = "{:,}".format(round(rows[title_row][11], 2))
    
    table_html = create_html_table(titles, rows)
    table_xsl_fo = create_xsl_fo_table(titlesfo, rows)
    table_html = table_html.replace('<td>P&L</td>','<td colspan=9><b>P&L (in Billion)</b></td>')
    table_html = table_html.replace('<td>Volume in USD</td>','<td colspan=7><b>Volume (in million USD)</b></td>')

    table_xsl_fo = table_xsl_fo.replace('<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>P&L</fo:block></fo:table-cell>','<fo:table-cell number-columns-spanned="9" border-width="1px" border-style="solid" padding="8pt"><fo:block>P&L (in Billion)</fo:block></fo:table-cell>')
    table_xsl_fo = table_xsl_fo.replace('<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>Volume in USD</fo:block></fo:table-cell>','<fo:table-cell number-columns-spanned="7" border-width="1px" border-style="solid" padding="8pt"><fo:block>Volume (in Million USD)</fo:block></fo:table-cell>')
    table_xsl_fo = table_xsl_fo.replace('&','&amp;')
    table_xsl_fo = table_xsl_fo.replace('<fo:simple-page-master master-name="my_page" margin="0.5in">','<fo:simple-page-master master-name="my_page" margin="0.5in" page-width="25in">')
    current_hour = get_current_hour("")
    
    current_date = get_current_date("")
    html_file = create_html_file(report_name + " " +current_date+current_hour, file_path, [table_html], report_name, current_date)
    xsl_fo_file = create_xsl_fo_file(report_name + " " +current_date+current_hour, file_path, [table_xsl_fo], report_name, current_date)
    for i in output_file:
        if i != '.pdf' :
            generate_file_for_other_extension(html_file, i)
        else:
            generate_pdf_from_fo_file(xsl_fo_file)
"""    
    try:
        os.remove(xsl_fo_file)
    except:
        pass
"""
