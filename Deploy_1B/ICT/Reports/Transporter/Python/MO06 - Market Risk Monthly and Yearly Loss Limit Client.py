import acm
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *

current_date = get_current_date("")
current_hour = get_current_hour("")
date_today = acm.Time.DateToday()
date,month,year = current_date[:2],current_date[2:4],current_date[4:]

def get_all_compliance():
    list_comp = []
    compliancerule = acm.FComplianceRule.Select("definitionInfo=Exposure")
    for each_comp in compliancerule:
        list_comp.append(each_comp.Name())
    return list_comp

    
def getLimitMonthly(compname,portname):
    rule_monthly = acm.FComplianceRule[compname]
    limit_monthly =rule_monthly.AppliedRules()
    for each_limit in limit_monthly:
        if each_limit.Target().Name() == portname:
            return each_limit.ThresholdValues().First().Value()
        else:
            continue
            
def getLimitYearly(compname,portname):
    rule_yearly = acm.FComplianceRule[compname]
    limit_yearly =rule_yearly.AppliedRules()
    for each_limit in limit_yearly:
        if each_limit.Target().Name() == portname:
            return each_limit.ThresholdValues().First().Value()
        else:
            continue
            


# Initialize a dictionary to store trade set categories and their children
trade_set_categories = {
    "[Trade Set] Plain Vanilla": [],
    "[Trade Set] Cross Currency Swap": [],
    "[Trade Set] FX Option":[],
    "[Trade Set] Bonds": [],
    "[Trade Set] Interest Rate Swap":[],
    "[Trade Set] Par Forward": [],
    "[Trade Set] Bond Forward": [],
    "[Trade Set] Forward Rate Agreement": []
}

portfolio_categories = [
    "Plain Vanilla", "CCS", "Options", "Surat Berharga / Fixed", "IRS", "Par FWD", "Bond Forward", "Forward Rate Agreement"
]

category_mapping = {
    "[Trade Set] Plain Vanilla": "Plain Vanilla",
    "[Trade Set] Cross Currency Swap": "CCS",
    "[Trade Set] FX Option": "Options",
    "[Trade Set] Bonds": "Surat Berharga / Fixed",
    "[Trade Set] Interest Rate Swap": "IRS",
    "[Trade Set] Par Forward": "Par FWD",
    "[Trade Set] Bond Forward": "Bond Forward",
    "[Trade Set] Forward Rate Agreement": "Forward Rate Agreement"
}

def get_items(csvpath,csvname,list_port):
    current_category = None
    # Open the CSV file
    with open(csvpath+'\\report'+year+month+date+'\\'+csvname+'.csv', 'r') as csvfile:
        lines = csvfile.readlines()
        for line in lines:
            # Splitting each line by comma, assuming CSV format
            row = line.strip().split(',')
            if row:
                # Check if the row starts with a trade set category
                for category in trade_set_categories:
                    if row[0].startswith(category):
                        current_category = category
                        # Skip the header row, assuming it's just the category
                        break
                else:
                    # If current_category is set (meaning we are under a trade set category)
                    if current_category:
                        if row[0] in list_port:
                            trade_set_categories[current_category].append(row)
                            
    return trade_set_categories


ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'Montly & Yearly Limit Loss - Client'}

ael_variables=[
['report_name','Report Name','string', None, 'MO06 - Monthly & Yearly Limit - Client', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['csv_name','CSV File Name','string',None,'MO06',1,0], 
['compliancemonthly','Compliance Rule (Monthly Limit)','string',get_all_compliance(),'Limit Monthly Loss - Vania',1,1],
['complianceyearly','Compliance Rule (Yearly Limit)','string',get_all_compliance(),'Limit Yearly Loss - Vania',1,1],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.xls',0,1, 'Select Secondary Extensions Output'],
]  


def ael_main(parameter):
    html_gen = HTMLGenerator()
    xsl_gen = XSLFOGenerator()
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    csv_file_name = parameter['csv_name']
    output_file = parameter['output_file']
    compliancemonthly = str(parameter['compliancemonthly'][0])
    complianceyearly = str(parameter['complianceyearly'][0])
    
    limit_monthly = getLimitMonthly(compliancemonthly,'CLIENT_BOOK')
    limit_yearly = getLimitYearly(complianceyearly,'CLIENT_BOOK')
    
    portfolios = ['Marktra','Banknotes Branch Settlement','Banknotes Export Import','Banknotes Interbank','Banknotes Trader','Clients Bonds FI','Clients Bonds Retail','Clients Bonds Tax Amnesty','Retail FX BO','Retail FX Branch','Retail SP','Wholesale FX &#38; Derivative BO','Wholesale FX Branch','Wholesale SP']

    all_items = get_items(file_path,csv_file_name,portfolios)
    
    limit_dict = {}
    
    limit_dict_yearly = {}
    
    
    
    output = {portfolio: {category: ["-", "-"] for category in portfolio_categories} for portfolio in portfolios}
   
    # Fill the output structure based on the item_data
    for trade_set, items in all_items.items():
        simplified_category = category_mapping[trade_set]
        for item in items:
            if len(item) < 3:
                item.extend(["-"] * (3 - len(item)))  # Pad with "-" if not enough values
            portfolio, value1, value2 = item[0], item[1], item[2]
            if portfolio in portfolios:
                output[portfolio][simplified_category] = [value1, value2]
                

    

    title_style = """
        .title {
            color: #800000;
            text-align: center;   
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
        
        .bold {
            font-weight: bold;
        }
        
        .red {
            background-color:red;
        }
    
        .green {
            background-color:green;
        }
        
        .yellow {
            background-color:yellow;
        }

    """


    html_content = html_gen.create_base_html_content("MO06 - Monthly &#38; Yearly Limit - Client", title_style)
    xsl_fo_content = xsl_gen.prepare_xsl_fo_content("MO06 - Monthly &#38; Yearly Limit - Client")
    
    html_content = html_gen.prepare_html_table(html_content,'')
    xsl_fo_content += """<fo:table margin-bottom="50px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto"><fo:table-body>"""

    title = 'Portfolio','Monthly Loss (thousand USD)','Limit','&#37;','Status','Yearly Loss (thousand USD)','Limit','&#37;','Status'

    html_content = html_gen.open_table_row(html_content)
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)

    
    for each_title in title:

        if each_title == "Portfolio" or each_title == "Limit" or each_title == "&#37;" or each_title =="Status":

            html_content = html_gen.add_cell_data(html_content,each_title,'rowspan=2 class="bold"')

            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_title,'number-rows-spanned="2" font-weight="bold"')

        elif each_title == "Monthly Loss (thousand USD)" or each_title =="Yearly Loss (thousand USD)":

            html_content = html_gen.add_cell_data(html_content,each_title,'colspan=9 class="bold"')

            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_title,'number-columns-spanned="9" font-weight="bold"')

        else:

            html_content = html_gen.add_cell_data(html_content,each_title,'class="bold"')

            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_title,'font-weight="bold"')
        
    html_content = html_gen.close_table_row(html_content)

    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)      
    
    

    subtitle = 'Plain Vanila','CCS','Options','Surat Berharga / Fixed','IRS','Par FWD','Bond Forward','Forward Rate Agreement','Total','Plain Vanila','CCS','Options','Surat Berharga / Fixed','IRS','Par FWD','Bond Forward','Forward Rate Agreement','Total'

    html_content = html_gen.open_table_row(html_content)
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)

    for each_subtitle in subtitle:

        html_content = html_gen.add_cell_data(html_content,each_subtitle,'class="bold"')
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_subtitle,'font-weight="bold"')

    html_content = html_gen.close_table_row(html_content)
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    
    total_plainvanila_monthly,total_plainvanila_yearly = 0,0
    total_ccs_monthly,total_ccs_yearly = 0,0
    total_opt_monthly,total_opt_yearly = 0,0
    total_sb_monthly,total_sb_yearly = 0,0
    total_irs_monthly,total_irs_yearly =0,0
    total_pf_monthly,total_pf_yearly = 0,0
    total_bfwd_monthly,total_bfwd_yearly =0,0
    total_fra_monthly,total_fra_yearly=0,0
    
    
    
    for portfolio, data in output.items():
        html_content = html_gen.open_table_row(html_content)
        xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
        
        html_content = html_gen.add_cell_data(html_content, portfolio)
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,portfolio)
        
        monthly_total = 0.0
        yearly_total = 0.0
        monthly_values = []
        yearly_values = []
        
        # Process monthly values and calculate total
        for category in portfolio_categories:
            value1, value2 = data[category]
            if value1 != "-" and value1 != "NaN":
                try:
                    monthly_total += float(value1)
                    if category == "Plain Vanilla":
                        total_plainvanila_monthly+=float(value1)
                    elif category == "CCS":
                        total_ccs_monthly += float(value1)
                    elif category == "Options":
                        total_opt_monthly += float(value1)
                    elif category == "Surat Berharga / Fixed":
                        total_sb_monthly += float(value1)
                    elif category == "IRS":
                        total_irs_monthly += float(value1)
                    elif category == "Par FWD":
                        total_pf_monthly += float(value1)
                    elif category == "Bond Forward":
                        total_bfwd_monthly += float(value1)
                    elif category == "Forward Rate Agreement":
                        total_fra_monthly += float(value1)
                except ValueError:
                    pass
            if value1 not in ["-", "NaN"]:
                try:
                    value1 = float(value1)
                    value1 = f"{value1:,}"
                except ValueError:
                    pass
            monthly_values.append(value1)
        
        # Add monthly values to the HTML
        for value in monthly_values:
            html_content = html_gen.add_cell_data(html_content, value)
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,value)
        
        # Add total monthly value to the HTML
        monthly_total = monthly_total
        monthly_total_str = f"{monthly_total:,}"
        html_content = html_gen.add_cell_data(html_content, monthly_total_str)
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,monthly_total_str)
        
        html_content = html_gen.add_cell_data(html_content,f"{limit_monthly:,}")
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{limit_monthly:,}")
                
        total_percent_monthly = 0
        
        if limit_monthly < 0 and monthly_total > 0:
            total_percent_monthly = 0
        else :
            total_percent_monthly = round(monthly_total/limit_monthly*100,2)
        
        html_content = html_gen.add_cell_data(html_content,str(f"{abs(total_percent_monthly):,}") + ' %')
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,str(f"{abs(total_percent_monthly):,}") + ' %')
        
        status = ""
        if total_percent_monthly == 0:
            html_content = html_gen.add_cell_data(html_content,'','class="green"')
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,'','background-color="green"')  
            
        else:
            if (total_percent_monthly >85 and total_percent_monthly<100):
                html_content = html_gen.add_cell_data(html_content,'','class="yellow"')
                xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,'','background-color="yellow"')
            elif monthly_total>=limit_monthly:
                html_content = html_gen.add_cell_data(html_content,'','class="green"')
                xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,'','background-color="green"')  
            else:
                html_content = html_gen.add_cell_data(html_content,'','class="red"')
                xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,'','background-color="red"')  
 
        for category in portfolio_categories:
            value1, value2 = data[category]
            if value2 != "-" and value2 != "NaN":
                try:
                    yearly_total += float(value2)
                    if category == "Plain Vanilla":
                        total_plainvanila_yearly+=float(value2)
                    elif category == "CCS":
                        total_ccs_yearly += float(value2)
                    elif category == "Options":
                        total_opt_yearly += float(value2)
                    elif category == "Surat Berharga / Fixed":
                        total_sb_yearly += float(value2)
                    elif category == "IRS":
                        total_irs_yearly += float(value2)
                    elif category == "Par FWD":
                        total_pf_yearly += float(value2)
                    elif category == "Bond Forward":
                        total_bfwd_yearly += float(value2)
                    elif category == "Forward Rate Agreement":
                        total_fra_yearly += float(value2)
                except ValueError:
                    pass
            if value2 not in ["-", "NaN"]:
                try:
                    value2 = float(value2)
                    value2 = f"{value2:,}"
                except ValueError:
                    pass
            yearly_values.append(value2)
        
        # Add yearly values to the HTML
        for value in yearly_values:
            html_content = html_gen.add_cell_data(html_content, value)
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,value)
        
        # Add total yearly value to the HTML
        yearly_total = yearly_total
        yearly_total_str = f"{yearly_total:,}"
        html_content = html_gen.add_cell_data(html_content, yearly_total_str)
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,yearly_total_str)
        
        html_content = html_gen.add_cell_data(html_content,f"{limit_yearly:,}")
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{limit_yearly:,}")
                
        total_percent_yearly = 0
        
        if limit_yearly < 0 and yearly_total > 0:
            total_percent_yearly = 0
        else:
            total_percent_yearly = round(yearly_total/limit_yearly*100,2)
            
        
        html_content = html_gen.add_cell_data(html_content,str(f"{abs(total_percent_yearly):,}") + ' %')
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,str(f"{abs(total_percent_yearly):,}") + ' %')
        
        status = ""
        
        if total_percent_monthly  == 0:
            html_content = html_gen.add_cell_data(html_content,'','class="green"')
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,'','background-color="green"')  
        else:
            if (total_percent_yearly >85 and total_percent_yearly<100):
                html_content = html_gen.add_cell_data(html_content,'','class="yellow"')
                xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,'','background-color="yellow"')
            elif yearly_total>=limit_yearly:
                html_content = html_gen.add_cell_data(html_content,'','class="green"')
                xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,'','background-color="green"')  
            else:
                html_content = html_gen.add_cell_data(html_content,'','class="red"')
                xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,'','background-color="red"')  
        
    
        html_content = html_gen.close_table_row(html_content)
        xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    
    html_content = html_gen.open_table_row(html_content)
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)

    
    html_content = html_gen.add_cell_data(html_content,"CLIENT BOOK","style='font-weight:bold'")
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,"CLIENT BOOK",'font-weight="bold"')

    html_content = html_gen.add_cell_data(html_content,f"{total_plainvanila_monthly:,}","style='font-weight:bold'")
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{total_plainvanila_monthly:,}",'font-weight="bold"')
    
    html_content = html_gen.add_cell_data(html_content,f"{total_ccs_monthly:,}","style='font-weight:bold'")
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{total_ccs_monthly:,}",'font-weight="bold"')
    
    html_content = html_gen.add_cell_data(html_content,f"{total_opt_monthly:,}","style='font-weight:bold'")
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{total_opt_monthly:,}",'font-weight="bold"')
    
    html_content = html_gen.add_cell_data(html_content,f"{total_sb_monthly:,}","style='font-weight:bold'")
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{total_sb_monthly:,}",'font-weight="bold"')
    
    html_content = html_gen.add_cell_data(html_content,f"{total_irs_monthly:,}","style='font-weight:bold'")
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{total_irs_monthly:,}",'font-weight="bold"')
    
    html_content = html_gen.add_cell_data(html_content,f"{total_pf_monthly:,}","style='font-weight:bold'")
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{total_pf_monthly:,}",'font-weight="bold"')
    
    html_content = html_gen.add_cell_data(html_content,f"{total_bfwd_monthly:,}","style='font-weight:bold'")
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{total_bfwd_monthly:,}",'font-weight="bold"')
    
    html_content = html_gen.add_cell_data(html_content,f"{total_fra_monthly:,}","style='font-weight:bold'")
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{total_fra_monthly:,}",'font-weight="bold"')
    
    total_category_monthly = total_plainvanila_monthly + total_ccs_monthly + total_opt_monthly + total_sb_monthly + total_irs_monthly + total_pf_monthly + total_bfwd_monthly + total_fra_monthly
    
    html_content = html_gen.add_cell_data(html_content,f"{total_category_monthly:,}","style='font-weight:bold'")
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{total_category_monthly:,}",'font-weight="bold"')
    
    html_content = html_gen.add_cell_data(html_content,f"{limit_monthly:,}","style='font-weight:bold'")
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{limit_monthly:,}",'font-weight="bold"')
    
    if limit_monthly < 0 and total_category_monthly > 0:
        total_percent_cb = 0
    else :
        total_percent_cb = round(total_category_monthly/limit_monthly*100,2)
        
    html_content = html_gen.add_cell_data(html_content,f"{abs(total_percent_cb):,}" + ' %',"style='font-weight:bold'")
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{abs(total_percent_cb):,}" + ' %','font-weight="bold"')
    
    if total_percent_cb == 0:
        html_content = html_gen.add_cell_data(html_content,'','class="green"')
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,'','background-color="green"')  
        
    else:
        if (total_percent_cb >85 and total_percent_cb<100):
            html_content = html_gen.add_cell_data(html_content,'','class="yellow"')
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,'','background-color="yellow"')
        elif total_category_monthly>=limit_monthly:
            html_content = html_gen.add_cell_data(html_content,'','class="green"')
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,'','background-color="green"')  
        else:
            html_content = html_gen.add_cell_data(html_content,'','class="red"')
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,'','background-color="red"')  
            
            
    html_content = html_gen.add_cell_data(html_content,f"{total_plainvanila_yearly:,}","style='font-weight:bold'")
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{total_plainvanila_yearly:,}",'font-weight="bold"')
    
    html_content = html_gen.add_cell_data(html_content,f"{total_ccs_yearly:,}","style='font-weight:bold'")
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{total_ccs_yearly:,}",'font-weight="bold"')
    
    html_content = html_gen.add_cell_data(html_content,f"{total_opt_yearly:,}","style='font-weight:bold'")
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{total_opt_yearly:,}",'font-weight="bold"')
    
    html_content = html_gen.add_cell_data(html_content,f"{total_sb_yearly:,}","style='font-weight:bold'")
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{total_sb_yearly:,}",'font-weight="bold"')
    
    html_content = html_gen.add_cell_data(html_content,f"{total_irs_yearly:,}","style='font-weight:bold'")
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{total_irs_yearly:,}",'font-weight="bold"')
    
    html_content = html_gen.add_cell_data(html_content,f"{total_pf_yearly:,}","style='font-weight:bold'")
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{total_pf_yearly:,}",'font-weight="bold"')
    
    html_content = html_gen.add_cell_data(html_content,f"{total_bfwd_yearly:,}","style='font-weight:bold'")
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{total_bfwd_yearly:,}",'font-weight="bold"')
    
    html_content = html_gen.add_cell_data(html_content,f"{total_fra_yearly:,}","style='font-weight:bold'")
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{total_fra_yearly:,}",'font-weight="bold"')
    
    total_category_yearly = total_plainvanila_yearly + total_ccs_yearly + total_opt_yearly + total_sb_yearly + total_irs_yearly + total_pf_yearly + total_bfwd_yearly + total_fra_yearly
    
    html_content = html_gen.add_cell_data(html_content,f"{total_category_yearly:,}","style='font-weight:bold'")
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{total_category_yearly:,}",'font-weight="bold"')
    
    html_content = html_gen.add_cell_data(html_content,f"{limit_yearly:,}","style='font-weight:bold'")
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{limit_yearly:,}",'font-weight="bold"')
    
    if limit_yearly < 0 and total_category_yearly > 0:
        total_percent_cb_yearly = 0
    else :
        total_percent_cb_yearly = round(total_category_yearly/limit_yearly*100,2)
        
    html_content = html_gen.add_cell_data(html_content,f"{abs(total_percent_cb_yearly):,}" + ' %',"style='font-weight:bold'")
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{abs(total_percent_cb_yearly):,}" + ' %','font-weight="bold"')
    
    if total_percent_cb_yearly == 0:
        html_content = html_gen.add_cell_data(html_content,'','class="green"')
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,'','background-color="green"')  
        
    else:
        if (total_percent_cb_yearly >85 and total_percent_cb_yearly<100):
            html_content = html_gen.add_cell_data(html_content,'','class="yellow"')
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,'','background-color="yellow"')
        elif total_category_yearly>=limit_monthly_yearly:
            html_content = html_gen.add_cell_data(html_content,'','class="green"')
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,'','background-color="green"')  
        else:
            html_content = html_gen.add_cell_data(html_content,'','class="red"')
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,'','background-color="red"')  
    
    
    html_content = html_gen.close_table_row(html_content)
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    
    
    
    html_content = html_gen.close_html_table(html_content)
    xsl_fo_content = xsl_gen.close_xsl_table(xsl_fo_content)


    html_file = html_gen.create_html_file(html_content, file_path, report_name+" "+current_date+current_hour, current_date, True)
    xsl_fo_file = xsl_gen.create_xsl_fo_file(report_name+" "+current_date+current_hour,file_path, xsl_fo_content, current_date)


    for i in output_file:
        if i != '.pdf' :
            generate_file_for_other_extension(html_file, i)
        else:
            generate_pdf_from_fo_file(xsl_fo_file)

