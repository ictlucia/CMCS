import acm, ael
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import HTMLGenerator
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import generate_file_for_other_extension

TITLE = ''
HEADERS = [ "<skyblue>Sight - 8 days", "<skyblue>8 days - 1 Month", "<skyblue>1 - 3 Months", "<skyblue>3 - 6 Months", "<skyblue>6 - 12 Months",
    "<skyblue>1 - 5 Years", "<skyblue>Over 5 Years", "<skyblue>Non-Interest Sensitive (Assets and Liabilities)", "<skyblue>Total"
]
ADDITIONAL_STYLE = """
table {
    margin: 0px;
}    
"""

html_gen = HTMLGenerator()
html_content = html_gen.create_base_html_content(TITLE, ADDITIONAL_STYLE)

    

def prepare_query_data():
    data_dict = {
        'Assets' : {
                'Repricing': [],
                'Maturing': []
            },
        'Liabilities' : {
                'Repricing' : [],
                'Maturing' : []
            }
    }
    
    other_assets_amount = 0
    # Query for Others assets
    # TODO: REMOVE COMMENT ON VALUE_DAY
    
    query_string = """
        SELECT t.trdnbr, nominal_amount(t) 'Nominal', t.value_day, t.maturity_date, t.curr
        FROM Trade t
        WHERE display_id(t, 'optkey3_chlnbr') = 'DL'
        AND display_id(t, 'optkey4_chlnbr') NOT IN ('CMP', 'CMT')
        /* AND t.value_day >= TODAY */
    """    
    query_results = ael.asql(query_string)[1][0]
    
    query_string = """
        SELECT t.trdnbr, nominal_amount(t) 'Nominal', t.value_day, t.maturity_date, t.curr
        FROM Trade t
        WHERE display_id(t, 'optkey3_chlnbr') = 'TD'
        AND display_id(t, 'optkey4_chlnbr') IN ('FASBI', 'BI')
        /* AND t.value_day >= TODAY */
    """    
    query_results = ael.asql(query_string)[1][0]
    
    query_string = """
        SELECT t.trdnbr, nominal_amount(t) 'Nominal', t.value_day, t.maturity_date, t.curr
        FROM Trade t
        WHERE display_id(t, 'optkey3_chlnbr') = 'TD'
        AND display_id(t, 'optkey4_chlnbr') IN ('FASBI', 'BI')
        /* AND t.value_day >= TODAY */
    """    
    query_results = ael.asql(query_string)[1][0]
    
    query_string = """
        SELECT t.trdnbr, nominal_amount(t) 'Nominal', t.value_day, t.maturity_date, t.curr
        FROM Trade t
        WHERE display_id(t, 'optkey3_chlnbr') IN ('REPO, REVREPO')
        /* AND t.value_day >= TODAY */
    """    
    query_results = ael.asql(query_string)[1][0]
    
    query_string = """
        SELECT t.trdnbr, nominal_amount(t) 'Nominal', t.value_day, t.maturity_date, t.curr
        FROM Trade t
        WHERE display_id(t, 'optkey3_chlnbr') = 'BOND'
        /* AND t.value_day >= TODAY */
    """    
    query_results = ael.asql(query_string)[1][0]
    
    
    

def prepare_repricing_assets(html_content):
    global HEADERS
    table_number = "39.1"
    
    header_list = [table_number, "ASSETS"] + HEADERS
    table_content = html_gen.prepare_html_table(html_content, header_list, row_style='', header_style='', table_styling='')
    table_content += "<caption style='text-align:left'>Interest Rate Repricing</caption>"
    
    asset_type = ["<skyblue>Cash and deposits", "<skyblue>Loans", "<skyblue>Investments", "<skyblue>Other assets", "<skyblue>Total"]
    query = ""
    query_data = [["<lightyellow>-" for _ in range(len(HEADERS))] for _ in range(len(asset_type) - 1)]
    query_data.append(["<aliceblue>" for _ in range(len(HEADERS))])

    row_data = []
    for i in range(len(asset_type)):
        temp_data = [f"{table_number}.{i + 1}", asset_type[i]]
        temp_data.extend(query_data[i])
        row_data.append(temp_data)
        
    table_content = html_gen.add_data_row(table_content, row_data, row_class='', cell_class="")
    table_content = html_gen.close_html_table(table_content)
    return table_content
    
def prepare_repricing_liabilities(html_content):
    global HEADERS
    table_number = "39.2"
    
    header_list = [table_number, "LIABILITES & EQUITY"] + HEADERS
    table_content = html_gen.prepare_html_table(html_content, header_list, row_style='', header_style='', table_styling='')
    
    asset_type = ["<skyblue>Deposits from banks", "<skyblue>Other deposits", "<skyblue>Repos, Term Debt and other Borrowings", "<skyblue>Other liabilites", "<skyblue>Equity", "<skyblue>Total"]
    query = ""
    query_data = [["<lightyellow>-" for _ in range(len(HEADERS))] for _ in range(len(asset_type) - 1)]
    query_data.append(["<aliceblue>" for _ in range(len(HEADERS))])

    row_data = []
    for i in range(len(asset_type)):
        temp_data = [f"{table_number}.{i + 1}", asset_type[i]]
        temp_data.extend(query_data[i])
        row_data.append(temp_data)
        
    table_content = html_gen.add_data_row(table_content, row_data, row_class='', cell_class='')
    table_content = html_gen.close_html_table(table_content)
    return table_content
    
def prepare_repricing_off_balance(html_content):
    global HEADERS
    table_number = "39.3"
    table_content = html_gen.prepare_html_table(html_content, '', row_style='', header_style='', table_styling='')
    
    asset_type = ["<skyblue>Off-balance sheet items"]
    query = ""
    query_data = [["<lightyellow>-" for _ in range(len(HEADERS))] for _ in range(len(asset_type) - 1)]
    query_data.append(["<aliceblue>" for _ in range(len(HEADERS))])

    row_data = []
    for i in range(len(asset_type)):
        temp_data = [f"{table_number}", asset_type[i]]
        temp_data.extend(query_data[i])
        row_data.append(temp_data)
        
    table_content = html_gen.add_data_row(table_content, row_data, row_class='', cell_class='')
    table_content = html_gen.close_html_table(table_content)
    return table_content

def prepare_maturing_assets(html_content):
    global HEADERS
    table_number = "39.4"
    
    header_list = [table_number, "ASSETS"] + HEADERS
    table_content = html_gen.prepare_html_table(html_content, header_list, row_style='', header_style='', table_styling='')
    table_content += "<caption style='text-align:left'>Interest Rate Maturing</caption>"
    
    asset_type = ["<skyblue>Cash and deposits", "<skyblue>Loans", "<skyblue>Investments", "<skyblue>Other assets", "<skyblue>Total"]
    query = ""
    query_data = [["<lightyellow>-" for _ in range(len(HEADERS))] for _ in range(len(asset_type) - 1)]
    query_data.append(["<aliceblue>" for _ in range(len(HEADERS))])

    row_data = []
    for i in range(len(asset_type)):
        temp_data = [f"{table_number}.{i + 1}", asset_type[i]]
        temp_data.extend(query_data[i])
        row_data.append(temp_data)
        
    table_content = html_gen.add_data_row(table_content, row_data, row_class='', cell_class='')
    table_content = html_gen.close_html_table(table_content)
    return table_content
    
def prepare_maturing_liabilities(html_content):
    global HEADERS
    table_number = "39.5"
    
    header_list = [table_number, "LIABILITES & EQUITY"] + HEADERS
    table_content = html_gen.prepare_html_table(html_content, header_list, row_style='', header_style='', table_styling='')
    
    asset_type = ["<skyblue>Deposits from banks", "<skyblue>Other deposits", "<skyblue>Repos, Term Debt and other Borrowings", "<skyblue>Other liabilites", "<skyblue>Equity", "<skyblue>Total"]
    query = ""
    query_data = [["<lightyellow>-" for _ in range(len(HEADERS))] for _ in range(len(asset_type) - 1)]
    query_data.append(["<aliceblue>" for _ in range(len(HEADERS))])

    row_data = []
    for i in range(len(asset_type)):
        temp_data = [f"{table_number}.{i + 1}", asset_type[i]]
        temp_data.extend(query_data[i])
        row_data.append(temp_data)
        
    table_content = html_gen.add_data_row(table_content, row_data, row_class='', cell_class='')
    table_content = html_gen.close_html_table(table_content)
    return table_content
    
def prepare_maturing_off_balance(html_content):
    global HEADERS
    table_number = "39.6"
    table_content = html_gen.prepare_html_table(html_content, '', row_style='', header_style='', table_styling='')
    
    asset_type = ["<skyblue>Off-balance sheet items"]
    query = ""
    query_data = [["<lightyellow>-" for _ in range(len(HEADERS))] for _ in range(len(asset_type) - 1)]
    query_data.append(["<aliceblue>" for _ in range(len(HEADERS))])

    row_data = []
    for i in range(len(asset_type)):
        temp_data = [f"{table_number}", asset_type[i]]
        temp_data.extend(query_data[i])
        row_data.append(temp_data)
        
    table_content = html_gen.add_data_row(table_content, row_data, row_class='', cell_class='')
    table_content = html_gen.close_html_table(table_content)
    return table_content
    
html_content = prepare_repricing_assets(html_content)
html_content += "<br>"
html_content = prepare_repricing_liabilities(html_content)
html_content += "<br>"
html_content = prepare_repricing_off_balance(html_content)
html_content += "<br>"
html_content = prepare_maturing_assets(html_content)
html_content += "<br>"
html_content = prepare_maturing_liabilities(html_content)
html_content += "<br>"
html_content = prepare_maturing_off_balance(html_content)


html_content = html_content.replace("><skyblue>", "style='background:skyblue;'>")
html_content = html_content.replace("><aliceblue>", "style='background:aliceblue;'>")
html_content = html_content.replace("><lightyellow>", "style='background:lightyellow;'>")

file_url = html_gen.create_html_file(html_content, "C:\\temp\\", "CI01 - Maturity GAP", "11-01-2024", True, folder_with_file_name=False)
generate_file_for_other_extension(file_url, ".xls")














