import acm, ael, random
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from time import sleep, perf_counter, strftime, strptime
from decimal import Decimal, getcontext
from Python_MO_Custom_Fields import *

context = acm.GetDefaultContext()
today = acm.Time.DateToday()
yesterday = acm.Time.DateAddDelta(today, 0, 0, -1)
next_month = acm.Time.DateAddDelta(today, 0, 1, 0)
next_year = acm.Time.DateAddDelta(today, 1, 0, 0)
all_trades = [
    trd
    for trd in acm.FTrade.Select("")
    if trd.OptKey3() is not None
    and trd.OptKey4() is not None
    and trd.OptKey1() is not None
    and trd.OptKey2() is not None
]
all_sources = [src.Name() for src in acm.FChoiceList.Select("list='Interface'")]
# print(all_sources)
temp_sources = ["EXB", "OPICS", "eMAS"]
pty_src_dicts = {}
stand_calc = acm.FStandardCalculationsSpaceCollection()
sheet_type = "FBreachSheet"


def getFilePathSelection():
    """Directory selector dialog"""
    selection = acm.FFileSelection()
    selection.PickDirectory(True)
    selection.SelectedDirectory = r"D:\HTML-Folder"
    return selection


# ================ DATA FILTER COLUMN ================
dict_of_column_filter = {
    "Country": {"Calculation": "Counterparty CEM Limit", "Keyword": "NY_Bond"},
    "Counterparty": {"Calculation": "Portfolio Position", "Keyword": "NY_Bond"},
    "FX": {"Calculation": "Counterparty CEM Limit", "Keyword": "FX"},
    "Bonds": {"Calculation": "Portfolio Position", "Keyword": "Bond"},
    "Money Market": {
        "Calculation": "Counterparty CEM Limit",
        "Keyword": "Money Market",
    },
    "Option": {"Calculation": "Counterparty CEM Limit", "Keyword": "Option"},
    "IRS": {"Calculation": "Counterparty CEM Limit", "Keyword": "IRS"},
    "CCS": {"Calculation": "Counterparty CEM Limit", "Keyword": "CCS"},
}
dict_of_trade_filter = {}


def big_decimal_number(val):
    getcontext().prec = 21
    util_num = float(Decimal(val))
    # util_num = round_half_up(util_num, jumlah_desimal=2)
    return util_num


def get_trades_by_prod_type_category(trade_list, ins_type):
    filtered_trades = []
    if (
        dict_of_trade_filter[ins_type]["Product Type PosNeg Flag"] == "Pos"
        and dict_of_trade_filter[ins_type]["Category PosNeg Flag"] == "Pos"
    ):
        for trade in trade_list:
            if (
                trade.OptKey3().Name() in dict_of_trade_filter[ins_type]["Product Type"]
                and trade.OptKey4().Name() in dict_of_trade_filter[ins_type]["Category"]
            ):
                filtered_trades.append((trade, "Trade"))
    elif (
        dict_of_trade_filter[ins_type]["Product Type PosNeg Flag"] == "Pos"
        and dict_of_trade_filter[ins_type]["Category PosNeg Flag"] == "Neg"
    ):
        for trade in trade_list:
            if (
                trade.OptKey3().Name() in dict_of_trade_filter[ins_type]["Product Type"]
                and trade.OptKey4().Name()
                not in dict_of_trade_filter[ins_type]["Category"]
            ):
                filtered_trades.append((trade, "Trade"))
    elif (
        dict_of_trade_filter[ins_type]["Product Type PosNeg Flag"] == "Neg"
        and dict_of_trade_filter[ins_type]["Category PosNeg Flag"] == "Pos"
    ):
        for trade in trade_list:
            if (
                trade.OptKey3().Name()
                not in dict_of_trade_filter[ins_type]["Product Type"]
                and trade.OptKey4().Name() in dict_of_trade_filter[ins_type]["Category"]
            ):
                filtered_trades.append((trade, "Trade"))
    elif (
        dict_of_trade_filter[ins_type]["Product Type PosNeg Flag"] == "Neg"
        and dict_of_trade_filter[ins_type]["Category PosNeg Flag"] == "Neg"
    ):
        for trade in trade_list:
            if (
                trade.OptKey3().Name()
                not in dict_of_trade_filter[ins_type]["Product Type"]
                and trade.OptKey4().Name()
                not in dict_of_trade_filter[ins_type]["Category"]
            ):
                filtered_trades.append((trade, "Trade"))
    return filtered_trades


def get_trades_by_cpty_ins_type(pty, ins_type_list):
    # pty_list = get_party_data_by_ael_sql(country)
    trade_list = [(pty, "Party")]
    trades = [trade for trade in all_trades if trade.Counterparty() is pty]
    if len(trades) > 0:
        temp_trades = []
        for ins_type in ins_type_list:
            trades_vers_2 = get_trades_by_prod_type_category(trades, ins_type)
            temp_trades = temp_trades + trades_vers_2
        if len(temp_trades) > 0:
            for src in all_sources:
                trade_list.extend(
                    [
                        (trd, "Trade")
                        for trd in temp_trades
                        if trade.OptKey2().Name() == src
                    ]
                )
                trade_list.append((src + " Total", "Source"))
        # trade_list.append( (country+' Total', 'Total') )
    return trade_list


def get_risk_country_from_party(pty):
    try:
        return pty.RiskCountry().Name()
    except:
        return "-"


def get_business_status_from_party(pty):
    try:
        return pty.BusinessStatus().Name()
    except:
        return "-"


def get_party_data_by_ael_sql(country):
    country_pty_list = [country]
    pty_list = acm.FParty.Select(
        "riskCountry='" + country.Name() + "' and type='Counterparty'"
    )
    if pty_list.Size() > 0:
        country_pty_list.extend(pty_list)
    return country_pty_list


def get_branch_from_trade(trade):
    try:
        return trade.OptKey1().Name()
    except:
        return "-"


def get_source_from_trade(trade):
    try:
        return trade.OptKey2().Name()
    except:
        return "-"


def get_prod_code_from_trade(trade):
    try:
        return trade.OptKey3().Name()
    except:
        return "-"


def get_exp_date_from_trade(trade):
    if trade.Instrument().InsType() == "Curr":
        tempdate = trade.ValueDay()
    else:
        tempdate = trade.Instrument().ExpiryDateOnly()
    resdate = strftime("%d %b %Y", strptime(tempdate, "%Y-%m-%d"))
    return resdate


def get_journal_from_trade(trade):
    journal_infos = acm.FJournalInformation.Select("trade='" + str(trade.Oid()) + "'")
    try:
        journal_info = journal_infos[0]
        journals = acm.FJournal.Select(
            "journalInformation='" + str(journal_info.Oid()) + "'"
        )
        return journals[0]
    except:
        return None


def get_account_number_from_trade(obj, calc_space, col_name):
    col_val = calc_space.CreateCalculation(obj, col_name).Value()
    try:
        return col_val
    except:
        return "-"


def get_trading_sheet_column_value(obj, calc_space, col_name):
    col_val = calc_space.CreateCalculation(obj, col_name).Value()
    try:
        num = float(col_val.Number())
        res_val = thousand_dot_sep(num)
    except:
        res_val = "-"
    return res_val


def thousand_dot_sep(val):
    if abs(val) >= 1000.0:
        res_val = (
            "{:,.2f}".format(val).replace(",", " ").replace(".", ",").replace(" ", ".")
        )
    else:
        res_val = "{:,.2f}".format(val).replace(".", ",")
    return res_val


def percentage_removal(val):
    val = val.replace(",", ".")
    res = float(val[:-1])
    return res


def limit_indicator(val):
    if val < 75.0:
        return "Green"
    elif val >= 75.0 and val < 100:
        return "Yellow"
    else:
        return "Red"


def date_formatter(date_val):
    resdate = strftime("%d %b %Y", strptime(date_val, "%Y-%m-%d"))
    return resdate


ael_gui_parameters = {
    "runButtonLabel": "&&Run",
    "hideExtraControls": True,
    "windowCaption": "SGBO44 - Customer Limit",
}
# settings.FILE_EXTENSIONS
ael_variables = [
    ["report_name", "Report Name", "string", None, "SGBO44 - Customer Limit", 1, 0],
    [
        "file_path",
        "Folder Path",
        getFilePathSelection(),
        None,
        getFilePathSelection(),
        1,
        1,
    ],
    [
        "output_file",
        "Secondary Output Files",
        "string",
        [".pdf", ".xls"],
        ".pdf",
        0,
        1,
        "Select Secondary Extensions Output",
    ],
]


def ael_main(parameter):
    report_name = parameter["report_name"]
    file_path = str(parameter["file_path"])
    output_file = parameter["output_file"]
    """
    party_list = ael.asql('''
    Select cl.seqnbr, cl.entry 
    from ChoiceList cl 
    where cl.list='Country of Risk' 
    and cl.entry~='None'
    ''')[1][0]
    """
    # print(party_list)
    # party_list = [('Bank of America Frankfurt','United States',),('Bank of America New York','United States',)]
    # party_list = [('#100003','United States',)]
    # party_list = [('Bank of America Frankfurt','United States',)]
    party_list = acm.FParty.Select("type='Counterparty'")[:2]
    # country_list = get_countries_by_ael_sql(party_list)
    # print(country_list)
    product_list = ["BOND"]
    all_ports = []
    for i in party_list:
        all_ports = all_ports + get_trades_by_cpty_ins_type(
            i, dict_of_trade_filter.keys()
        )
        all_ports.append((i.Name() + " Total", "Total"))
    # titles = ['Country Name', 'CurTyp', 'Country Limit', 'Exp. Date', 'Branch', 'Source', 'SubLmtName', 'Type Utilization', 'Customer Name', 'AcctNo', 'OriCcy', 'Limit Due Date', 'Total']
    titles = [
        "CAT",
        "CUSTNAME",
        "CFCOUN",
        "CFCITZ",
        "BR",
        "SOURCE",
        "CUSTLMT",
        "SUBLMT",
        "SUB LIMIT NAME",
        "FACILITY NAME",
        "ACCOUNT NO",
        "R",
        "DUE DATE",
        "ORI",
        "CCY",
        "CFLCAS",
        "PRODUCT",
        "CUSTLMT (TOTAL)",
        "TOTAL",
    ]
    columns = ["Limit", "Utilisasi", "1 Day Change", "%"]
    # calc_space = acm.Calculations().CreateCalculationSpace(acm.GetDefaultContext(), sheet_type)
    calc_space = acm.Calculations().CreateCalculationSpace(
        acm.GetDefaultContext(), "FJournalSheet"
    )
    calc_space2 = acm.Calculations().CreateCalculationSpace(
        acm.GetDefaultContext(), "FAppliedRuleSheet"
    )
    rows = []
    cyan_rows = []
    blue_rows = []
    green_rows = []
    total_limit = 0
    for port in all_ports:
        if port[1] == "Party":
            calculation = dict_of_column_filter["Country"]["Calculation"]
            keyword = dict_of_column_filter["Country"]["Keyword"]
            rule_name = keyword
            obj = port[0]
            temp_row = ["CUST" + obj.Name(), obj.Name()]  # 1-2
            # cyan_rows.extend(temp_row)
            cyan_rows.append(("CUST" + obj.Name(), "CUST"))
            cyan_rows.append((obj.Name(), obj.Name()))
            country_name = get_risk_country_from_party(obj)
            temp_row.extend([country_name, country_name])  # 3-4
            br_name = "-"
            src_name = "-"
            limit_val = thousand_dot_sep(
                get_threshold_limit_by_rule_name(obj, rule_name)
            )
            limit_val2 = thousand_dot_sep(
                big_decimal_number(get_threshold_limit_by_rule_name2(rule_name))
            )
            limit_name = rule_name
            facility_name = "-"
            acc_no = "-"
            r_name = "-"
            temp_row.extend(
                [
                    br_name,
                    src_name,
                    limit_val,
                    limit_val,
                    limit_name,
                    facility_name,
                    acc_no,
                    r_name,
                ]
            )  # 5-12
            try:
                due_date = date_formatter(get_end_date_by_rule_name(obj, rule_name))
            except:
                due_date = "-"
            ori_ccy = "USD"
            ccy_name = "USD"
            business_status = get_business_status_from_party(obj)
            prod_code = "-"
            total = thousand_dot_sep(0.0)
            temp_row.extend(
                [
                    due_date,
                    ori_ccy,
                    ccy_name,
                    business_status,
                    prod_code,
                    limit_val2,
                    total,
                ]
            )  # 13-19
            if len(temp_row) > 1:
                rows.append(temp_row)
        elif port[1] == "Trade":
            calculation = dict_of_column_filter["Counterparty"]["Calculation"]
            keyword = dict_of_column_filter["Counterparty"]["Keyword"]
            obj = port[0].Counterparty()
            obj_trade = port[0]
            # rule_name = obj.Name() + ' ' + keyword
            rule_name = keyword
            temp_row = ["Trd", "Trd"]  # 1-2
            cyan_rows.append(("Trd", "-"))
            country_name = get_risk_country_from_party(obj)
            temp_row.extend([country_name, country_name])  # 3-4
            br_name = get_branch_from_trade(obj_trade)
            src_name = get_source_from_trade(obj_trade)
            limit_val = thousand_dot_sep(
                get_threshold_limit_by_rule_name(obj, rule_name)
            )
            limit_val2 = thousand_dot_sep(
                big_decimal_number(get_threshold_limit_by_rule_name2(rule_name))
            )
            limit_name = rule_name
            facility_name = "-"
            journal = get_journal_from_trade(obj_trade)
            try:
                acc_no = get_account_number_from_trade(
                    journal, calc_space, "Journal Account Number"
                )
            except:
                acc_no = "-"
            r_name = "-"
            temp_row.extend(
                [
                    br_name,
                    src_name,
                    limit_val,
                    limit_val,
                    limit_name,
                    facility_name,
                    acc_no,
                    r_name,
                ]
            )  # 5-12
            try:
                due_date = date_formatter(get_end_date_by_rule_name(obj, rule_name))
            except:
                due_date = "-"
            ori_ccy = "USD"
            ccy_name = "USD"
            business_status = get_business_status_from_party(obj)
            prod_code = get_prod_code_from_trade(obj_trade)
            total = thousand_dot_sep(0.0)
            temp_row.extend(
                [
                    due_date,
                    ori_ccy,
                    ccy_name,
                    business_status,
                    prod_code,
                    limit_val2,
                    total,
                ]
            )  # 13-19
            if len(temp_row) > 1:
                rows.append(temp_row)
        elif port[1] == "Source":
            calculation = dict_of_column_filter["Counterparty"]["Calculation"]
            keyword = dict_of_column_filter["Counterparty"]["Keyword"]
            src_name = port[0]
            rule_name = keyword
            temp_row = ["Src", "Src"]  # 1-2
            cyan_rows.append(("Src", "-"))
            temp_row.extend(["", "", ""])  # 3-5
            # temp_row.append('')
            limit_val = big_decimal_number(get_threshold_limit_by_rule_name2(rule_name))
            limit_val2 = thousand_dot_sep(limit_val)
            total = thousand_dot_sep(0.0)
            total_limit = total_limit + limit_val
            temp_cyan_row = [
                src_name,
                "Src",
                "Src",
                "Src",
                "Src",
                "Src",
                "Src",
                "Src",
                "Src",
                "Src",
                "Src",
                src_name + limit_val2,
                src_name + total,
            ]  # 6-19
            temp_row.extend(temp_cyan_row)
            cyan_rows.append((src_name + limit_val, limit_val))
            cyan_rows.append((src_name + total, total))
            if len(temp_row) > 1:
                rows.append(temp_row)
        else:
            obj = port[0]
            green_rows.extend([(obj, "Total"), ("Green", "")])
            temp_row = ["BlueTotal", obj]  # 1-2
            cyan_rows.append(("BlueTotal", ""))
            temp_green_rows = ["Green" for i in range(0, 15)]
            temp_row.extend(temp_green_rows)  # 3-17
            limit_val = thousand_dot_sep(total_limit)
            total = thousand_dot_sep(0.0)
            temp_row.extend([obj + limit_val, obj + total])  # 18-19
            green_rows.extend([(obj + limit_val, limit_val), (obj + total, total)])
            total_limit = 0
            if len(temp_row) > 1:
                rows.append(temp_row)
    table_html = create_html_table(titles, rows)
    table_xsl_fo = create_xsl_fo_table(titles, rows)
    for i in titles:
        table_html = table_html.replace(
            "<th>" + i + "</th>",
            '<th style="background-color: #000000; color: #ffffff;">' + i + "</th>",
        )
    for cyan in cyan_rows:
        table_html = table_html.replace(
            "<td>" + cyan[0] + "</td>",
            '<td style="text-align: left; background-color: #00ccff;">'
            + cyan[1]
            + "</td>",
        )
        table_xsl_fo = table_xsl_fo.replace(
            '<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>'
            + cyan[0]
            + "</fo:block></fo:table-cell>",
            '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" text-align="left" background-color="#00ccff"><fo:block>'
            + cyan[1]
            + "</fo:block></fo:table-cell>",
        )
    for green in green_rows:
        table_html = table_html.replace(
            "<td>" + green[0] + "</td>",
            '<td style="text-align: left; background-color: #99ff66;">'
            + green[1]
            + "</td>",
        )
        table_xsl_fo = table_xsl_fo.replace(
            '<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>{}</fo:block></fo:table-cell>'.format(
                green[0]
            ),
            '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" text-align="left" background-color="#99ff66;"><fo:block>{}</fo:block></fo:table-cell>'.format(
                green[1]
            ),
        )
    """
    for port in all_ports:
        if port[1] == 'Total':
            obj_name = port[0]
        else:
            obj_name = port[0].Name()
        table_html = table_html.replace('<td>'+obj_name+'</td>', '<td style="text-align: left;">'+obj_name+'</td>') 
        #table_html = table_html.replace('<td>'+obj.Name()+'</td>', '<td style="text-align: left;">'+obj.Name()+'</td>')  
        table_xsl_fo = table_xsl_fo.replace('<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>'+obj_name+'</fo:block></fo:table-cell>',
        '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" text-align="left"><fo:block>'+obj_name+'</fo:block></fo:table-cell>')
        #table_xsl_fo = table_xsl_fo.replace('<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>'+obj.Name()+'</fo:block></fo:table-cell>',
        #'<fo:table-cell border-width="1px" border-style="solid" padding="8pt" text-align="left"><fo:block>'+obj.Name()+'</fo:block></fo:table-cell>')
    """
    # HTML Table Customization
    # table_html = table_html.replace('<th style="background-color: #99ff66;">Exp. Date</th>', '<th style="background-color: #99ff66;">Exp&period; Date</td>')
    table_html = table_html.replace(
        "<td>Green</td>", '<td style="background-color: #00cc66;"></td>'
    )
    table_html = table_html.replace(
        "<td>Yellow</td>", '<td style="background-color: #ffcc00;"></td>'
    )
    table_html = table_html.replace(
        "<td>Red</td>", '<td style="background-color: #ff0000;"></td>'
    )
    table_html = table_html.replace("&", "&amp;")
    table_html = table_html.replace("%", "&#37;")
    # XSLFO Table Customization
    table_xsl_fo = table_xsl_fo.replace(
        '<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>Green</fo:block></fo:table-cell>',
        '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" background-color="#00cc66"><fo:block></fo:block></fo:table-cell>',
    )
    table_xsl_fo = table_xsl_fo.replace(
        '<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>Yellow</fo:block></fo:table-cell>',
        '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" background-color="#ffcc00"><fo:block></fo:block></fo:table-cell>',
    )
    table_xsl_fo = table_xsl_fo.replace(
        '<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>Red</fo:block></fo:table-cell>',
        '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" background-color="#ff0000"><fo:block></fo:block></fo:table-cell>',
    )
    table_xsl_fo = table_xsl_fo.replace("&", "&amp;")
    table_xsl_fo = table_xsl_fo.replace("%", "&#37;")
    current_hour = get_current_hour("")
    current_date = get_current_date("")
    html_file = create_html_file(
        report_name + " " + current_date + current_hour,
        file_path,
        [table_html],
        report_name,
        current_date,
    )
    html_f = open(html_file, "r")
    html_contents = html_f.read().replace(
        """td, th {
      border: 1px solid #dddddd;
      text-align: center;
      padding: 8px;
    }""",
        """ td, th {
      border: 1px solid #000000;
      text-align: center;
      padding: 8px;
    }
    """,
    )
    html_f = open(html_file, "w")
    html_f.write(html_contents)
    html_f.close()
    xsl_fo_file = create_xsl_fo_file(
        report_name + " " + current_date + current_hour,
        file_path,
        [table_xsl_fo],
        report_name,
        current_date,
    )
    xsl_f = open(xsl_fo_file, "r")
    #'CAT', 'CUSTNAME', 'CFCOUN', 'CFCITZ', 'BR', 'SOURCE', 'CUSTLMT', 'SUBLMT', 'SUB LIMIT NAME', 'FACILITY NAME', 'ACCOUNT NO', 'R', 'DUE DATE', 'ORI', 'CCY', 'CFLCAS', 'PRODUCT', 'CUSTLMT (TOTAL)', 'TOTAL'
    xsl_contents = xsl_f.read().replace(
        '<fo:simple-page-master master-name="my_page" margin="0.5in">',
        '<fo:simple-page-master master-name="my_page" margin="0.5in" page-height="25in" page-width="80in">',
    )
    xsl_contents = xsl_contents.replace(
        '<fo:block font-weight="bold" font-size="30px" margin-bottom="30px">'
        + report_name
        + "</fo:block>",
        '<fo:block font-weight="bold" font-size="30px" margin-bottom="30px" text-align="center">'
        + report_name
        + "</fo:block>",
    )
    xsl_contents = xsl_contents.replace(
        """<fo:table-header background-color="#666666" color="#ffffff" font-weight="bold">
    <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>CAT</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>CUSTNAME</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>CFCOUN</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>CFCITZ</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>BR</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>SOURCE</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>CUSTLMT</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>SUBLMT</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>SUB LIMIT NAME</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>FACILITY NAME</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>ACCOUNT NO</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>R</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>DUE DATE</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>ORI</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>CCY</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>CFLCAS</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>PRODUCT</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>CUSTLMT (TOTAL)</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>TOTAL</fo:block></fo:table-cell>
        </fo:table-header>
    <fo:table-body>""",
        """<fo:table-body>
    <fo:table-row background-color="#000000" color="#ffffff" font-weight="bold">
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>CAT</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>CUSTNAME</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>CFCOUN</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>CFCITZ</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>BR</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>SOURCE</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>CUSTLMT</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>SUBLMT</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>SUB LIMIT NAME</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>FACILITY NAME</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>ACCOUNT NO</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>R</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>DUE DATE</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>ORI</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>CCY</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>CFLCAS</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>PRODUCT</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>CUSTLMT (TOTAL)</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>TOTAL</fo:block></fo:table-cell>
    </fo:table-row>""",
    )
    xsl_f = open(xsl_fo_file, "w")
    xsl_f.write(xsl_contents)
    xsl_f.close()
    for i in output_file:
        if i != ".pdf":
            generate_file_for_other_extension(html_file, i)
        else:
            generate_pdf_from_fo_file(xsl_fo_file)
    """
    try:
        os.remove(xsl_fo_file)
    except:
        pass
    """
