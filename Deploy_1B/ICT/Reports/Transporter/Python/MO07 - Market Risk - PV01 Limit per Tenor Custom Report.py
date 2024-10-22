import acm, ael, random

from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *

from time import sleep, perf_counter

from Python_Custom_Fields import *



context = acm.GetDefaultContext( )

today = acm.Time.DateToday()

yesterday = acm.Time.DateAddDelta(today, 0, 0, -1)

next_month = acm.Time.DateAddDelta(today, 0, 1, 0)

next_year = acm.Time.DateAddDelta(today, 1, 0, 0)

all_trades = acm.FTrade.Select('')

stand_calc = acm.FStandardCalculationsSpaceCollection()

sheet_type = 'FPortfolioSheet'    

calc_space = acm.Calculations( ).CreateCalculationSpace( context, sheet_type )



# ================ DATA FILTER COLUMN ================ 

dict_of_column_filter = {

    "Plain Vanilla": {

        "Product Type" : ["FX"],

        "Category" : ["TOD", "TOM", "SPOT", "FWD", "SWAP"]

    },

    "CCS": {

        "Product Type" : ["SWAP"],

        "Category" : ["CCS"]

    },

    "Par FWD": {

        "Product Type" : ["SP"],

        "Category" : ["MPF"]

    },

    "Surat Berharga/Fixed Income": {

        "Product Type" : ["BOND"],

        "Category" : ["RDPT"]

    },

    "IRS": {

        "Product Type" : ["SWAP"],

        "Category" : ["IRS"]

    },

    "Bond Forward": {

        "Product Type" : ["BOND"],

        "Category" : ["FWD"]

    },

    "Forward Rate Agreement": {

        "Product Type" : ["SWAP"],

        "Category" : ["FRA"]

    }

}



pattern_dict_list = {

    'TREASURY HO': {

        'Begin': ['TREASURY'],

        'End': ['HO']

    },

    'PDN': {

        'Begin': [''],

        'End': ['PDN']

    },

    'FXT': {

        'Begin': ['FXT'],

        'End': ['']

    },

    'IRT': {

        'Begin': ['IRT'],

        'End': ['']

    },

    'CLIENT_BOOK': {

        'Begin': ['CLIENT','','Banknotes','Wholesale','Retail', 'Clients'],

        'End': ['BOOK','Marktra','','','','']

    },

    'OVERSEAS': {

        'Begin': ['','BM','BM'],

        'End': ['OVERSEAS','Trading','Banking']

    }



}



def get_portfolios_by_ael_sql(port_pattern_begin, port_pattern_end):

    port_list = ael.asql("Select p.prfid, p.prfnbr from Portfolio p where p.prfid like '"+port_pattern_begin+"%"+port_pattern_end+"'")[1][0]

    return port_list





def get_trading_sheet_column_value(obj, sheet_obj, col_name):

    calc_space = acm.Calculations().CreateCalculationSpace(acm.GetDefaultContext(), sheet_obj)

    col_val = calc_space.CreateCalculation(obj, col_name).Value()

    try:

        num = float(col_val.Number())

        res_val = thousand_dot_sep(num)

    except:

        res_val = '-'

    return res_val



def thousand_dot_sep(val):

    if abs(val) >= 1000.0:

        res_val = "{:,.2f}".format(val).replace(',',' ').replace('.',',').replace(' ','.')

    else:

        res_val = "{:,.2f}".format(val).replace('.',',')

    return res_val

    





ael_gui_parameters={'runButtonLabel':'&&Run',

                    'hideExtraControls': True,

                    'windowCaption':'MO07 - Market Risk - PV01 Limit'}

#settings.FILE_EXTENSIONS

ael_variables=[

['report_name','Report Name','string', None, 'MO07 - Market Risk - PV01 Limit', 1,0],

['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],

['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.pdf',0,1, 'Select Secondary Extensions Output']

]  

def ael_main(parameter):

    report_name = parameter['report_name']

    file_path = str(parameter['file_path'])

    output_file = parameter['output_file']

    

    all_ports = []

    for i in pattern_dict_list:

        

        for j in range(0, len(pattern_dict_list[i]['Begin'])):

            all_ports = all_ports + get_portfolios_by_ael_sql(pattern_dict_list[i]['Begin'][j], pattern_dict_list[i]['End'][j])

    

    #all_ports = fxt_ports + irt_ports

    #print(all_ports)

    #ports = ["FXT"]

    #print(fxt_ports)



    titles = ['Hierarchy','Interest Rate Yield Delta Buckets']

    

    '''

    columns = []

    for ins in dict_of_column_filter.keys():

        columns.append(ins)

        

    columns_oper = columns[:4]

    columns_ir = columns[4:]

    '''

    columns = ['3M', '6M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '20Y', '30Y']

    

    calculation = "Portfolio Delta Yield"

    rule_type = "Exposure"

    rule_category = "Pre-Deal"

    

    rows = [columns]

    for port in all_ports:

        temp_row = [port[0]]

        

        temp_row.append(get_trading_sheet_column_value(acm.FPhysicalPortfolio[port[0]], sheet_type, 'Portfolio Market Value'))

        temp_row.append( thousand_dot_sep( port_threshold_limit(acm.FPhysicalPortfolio[port[0]], calculation, rule_type, rule_category, -2) ) )

        temp_row.append(get_trading_sheet_column_value(acm.FPhysicalPortfolio[port[0]], sheet_type, 'Portfolio Delta Yield'))

        temp_row.append(get_trading_sheet_column_value(acm.FPhysicalPortfolio[port[0]], sheet_type, '1DayChange_PV01'))

        temp_row.append( port_utilization_percentage(acm.FPhysicalPortfolio[port[0]], calculation, rule_type, rule_category, -2) )

        temp_row.append(get_trading_sheet_column_value(acm.FPhysicalPortfolio[port[0]], sheet_type, 'Instrument Convexity'))

        temp_row.append(get_trading_sheet_column_value(acm.FPhysicalPortfolio[port[0]], sheet_type, 'Flat Credit Spread Delta'))

        

        if len(temp_row) > 1:

            rows.append(temp_row)

    

    #print(rows[1][2])



    #print(rows[0])

    table_html = create_html_table(titles, rows)

    

    for i in titles:

        if i != 'PV01':

            table_html = table_html.replace('<th>'+i+'</th>', '<th rowspan="2" style="background-color: #99ff66;">'+i+'</th>')

        else:

            table_html = table_html.replace('<th>'+i+'</th>', '<th colspan="'+str(len(columns))+'" style="background-color: #99ff66;">'+i+'</th>')

            

    for col in columns:

        table_html = table_html.replace('<td>'+col+'</td>', '<td style="background-color: #99ff66;"><b>'+col+'</b></td>')

    

    table_html = table_html.replace('<td>FXT</td>', '<td style="text-align: left;">FXT</td>')

    table_html = table_html.replace('<td>IRT</td>', '<td style="text-align: left;">IRT</td>')

    table_html = table_html.replace('<td>PDN</td>', '<td style="text-align: left;">PDN</td>')

    table_html = table_html.replace('<td>CLIENT_BOOK</td>', '<td style="text-align: left;">CLIENT_BOOK</td>')

    table_html = table_html.replace('<td>OVERSEAS</td>', '<td style="text-align: left;">OVERSEAS</td>')

    table_html = table_html.replace('<td>TREASURY HO</td>', '<td style="text-align: left;">TREASURY HO</td>')

    

    current_hour = get_current_hour("")

    current_date = get_current_date("")

    #report_name = report_name + " - " + filter_currency

    html_file = create_html_file(report_name + " " +current_date+current_hour, file_path, [table_html], report_name, current_date)

    f = open(html_file, "r")

    #contents = f.read().replace('<fo:simple-page-master master-name="my_page" margin="0.5in">', '<fo:simple-page-master master-name="my_page" margin="0.5in" page-height="25in" page-width="80in">')

    contents = f.read().replace('''td, th {

      border: 1px solid #dddddd;

      text-align: center;

      padding: 8px;

    }''',

            ''' td, th {

      border: 1px solid #000000;

      text-align: center;

      padding: 8px;

    }''')

    f = open(html_file, "w")

    f.write(contents)

    f.close()





'''

fxt_ports = ael.asql("Select p.prfid from Portfolio p where p.prfid like 'FXT%'")[1][0]

fxt_ports.pop(2)

fxt_ports.pop(5)

fxt_ports.pop(8)

fxt_ports.pop(11)

fxt_ports.pop(-1)

#print(fxt_ports)





all_ports = {}

for port in fxt_ports:

    all_ports[port[0]] = {}

    

    data_optkey3, data_optkey4 = '', ''

    temp_list_optkey3, temp_list_optkey4 = [], []

    

    for ins in dict_of_column_filter:

        temp_list_optkey3 = dict_of_column_filter[ins]['Product Type']

        temp_list_optkey4 = dict_of_column_filter[ins]['Category']

        

        data_optkey3 = "('"+"','".join(list(set(temp_list_optkey3))) + "')"

        data_optkey4 = "('"+"','".join(list(set(temp_list_optkey4))) + "')"

        

        query = """

        select c3.entry 'ProductType', c4.entry 'Category', p.prfid

        from trade t, choicelist c3, choicelist c4, portfolio p

        where (t.optkey3_chlnbr=c3.seqnbr) and (t.optkey4_chlnbr=c4.seqnbr) and (p.prfnbr*=t.prfnbr)

        and (p.prfid = '"""+port[0]+"""')

        and (c3.entry in """+data_optkey3+""")

        and (c4.entry in """+data_optkey4+""")

        """

        trades_data = ael.asql(query)[1][0]

        all_ports[port[0]][ins] = trades_data





for key in all_ports:

    print(key, ': ', all_ports[key])

'''

