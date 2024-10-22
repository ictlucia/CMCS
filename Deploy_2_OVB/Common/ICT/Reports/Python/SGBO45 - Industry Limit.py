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
    if trd.OptKey3() is not None and trd.OptKey4() is not None
]
stand_calc = acm.FStandardCalculationsSpaceCollection()
sheet_type = "FRuleValueHistorySheet"


def getFilePathSelection():
    """Directory selector dialog"""
    selection = acm.FFileSelection()
    selection.PickDirectory(True)
    selection.SelectedDirectory = r"D:\HTML-Folder"
    return selection


# ================ DATA FILTER COLUMN ================
dict_of_column_filter = {
    "Industry": {
        "Calculation": "Counterparty CEM Limit",
        "Keyword": "Local Government",
    },
    "Counterparty": {
        "Calculation": "Portfolio Position",
        "Keyword": "Local Government",
    },
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
dict_of_trade_filter = {
    "BOND": {
        "Product Type": ["BOND"],
        "Category": ["OPT", "FWD"],
        "Product Type PosNeg Flag": "Pos",
        "Category PosNeg Flag": "Neg",
    }
}


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


def get_trades_by_cpty_ins_type(industry, ins_type_list):
    pty_list = get_party_data_by_ael_sql(industry)
    trade_list = [(pty_list[0], "Industry")]
    if len(pty_list) > 0:
        for pty in pty_list[1:]:
            trade_list.append((pty, "Party"))
            trades = [trade for trade in all_trades if trade.Counterparty() is pty]
            if len(trades) > 0:
                for ins_type in ins_type_list:
                    trades_vers_2 = get_trades_by_prod_type_category(trades, ins_type)
                    trade_list = trade_list + trades_vers_2
            # trade_list.append( (industry+' Total', 'Total') )
    return trade_list


def get_industries_by_ael_sql(pty_list):
    """
    industry_list = []
    for pty in pty_list:
        industry = acm.FChoiceList[ pty[0] ]
        industry_list.append( industry )
    """
    industry_list = acm.FChoiceList.Select("list='Business Status'")
    return industry_list


def get_party_data_by_ael_sql(industry):
    industry_pty_list = [industry]
    pty_list = acm.FParty.Select(
        "businessStatus='" + industry.Name() + "' and type='Counterparty'"
    )
    if pty_list.Size() > 0:
        industry_pty_list.extend(pty_list)
    return industry_pty_list


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


def get_exp_date_from_trade(trade):
    if trade.Instrument().InsType() == "Curr":
        tempdate = trade.ValueDay()
    else:
        tempdate = trade.Instrument().ExpiryDateOnly()
        if tempdate == "":
            tempdate = trade.ValueDay()
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


def get_sub_industry_from_party(party):
    try:
        return party.BusinessStatus().Name()
    except:
        return "-"


def get_product_from_trade(trade):
    return trade.Instrument().Name()


def get_cust_type_from_party(party):
    try:
        return party.Free2ChoiceList().Name()
    except:
        return "-"


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
    "windowCaption": "SGBO45 - Industry Limit",
}
# settings.FILE_EXTENSIONS
ael_variables = [
    ["report_name", "Report Name", "string", None, "SGBO45 - Industry Limit", 1, 0],
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
    # party_list = [('Bank of America Frankfurt','United States',),('Bank of America New York','United States',)]
    # party_list = [('#100003','United States',)]
    # party_list = [('Counterparty 1','2.10.Local government, non-financial,..',), ('Counterparty 5','2.10.Local government, non-financial,..',)]
    party_list = ""
    industry_list = get_industries_by_ael_sql(party_list)
    product_list = ["BOND"]
    all_ports = []
    for i in industry_list:
        if i is not None:
            all_ports = all_ports + get_trades_by_cpty_ins_type(
                i, dict_of_trade_filter.keys()
            )
            all_ports.append((i.Name() + " Total", "Total"))
    # titles = ['Country', 'Limit', 'Utilisasi', '1 Day Change', '% Utilization', 'Status Limit', 'Limit Expiry', 'Status Limit Expiry', 'Notes']
    titles = [
        "IND CODE",
        "MAIN INDUSTRY NAME",
        "CUR",
        "MAIN IND LIMIT",
        "SUB INDUSTRY",
        "BR",
        "SOURCE",
        "SUBLMTNAME",
        "TYPE UTILIZATION",
        "CUSTOMER NAME",
        "ACCTNO",
        "PRODUCT",
        "ORICCY",
        "CUST TYPE",
        "DUE DATE",
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
    total_limit = 0
    for port in all_ports:
        if port[1] == "Industry":
            calculation = dict_of_column_filter["Industry"]["Calculation"]
            keyword = dict_of_column_filter["Industry"]["Keyword"]
            rule_name = keyword
            obj = port[0]
            temp_row = [obj.Oid()]  # Ind Code
            cyan_rows.append(str(obj.Oid()))
            temp_row.append(obj.Name())  # Main Industry Code
            cyan_rows.append(obj.Name())
            temp_row.append("USD")  # CurTyp
            # Main Ind Limit
            try:
                # temp_row.append( thousand_dot_sep( get_threshold_limit_by_rule_name(obj, rule_name) ) )
                temp_row.append(
                    big_decimal_number(get_threshold_limit_by_rule_name2(rule_name))
                )
                # temp_row.append( thousand_dot_sep( get_utilization_val_by_rule_name(obj, rule_name) ) )
            except:
                temp_row.append("-")
            temp_row.append(obj.Name())  # Sub Industry
            temp_row.append("-")  # Br
            temp_row.append("-")  # Source
            temp_row.append("-")  # SubLmtName
            temp_row.append(get_rule_type_by_rule_name(rule_name))  # Type Utilization
            temp_row.append("-")  # Customer Name
            temp_row.append("-")  # AcctNo
            temp_row.append("-")  # Product
            temp_row.append("USD")  # OrigCcy
            temp_row.append("-")  # Cust Type
            # Due Date
            try:
                temp_row.append(
                    date_formatter(get_end_date_by_rule_name(obj, rule_name))
                )
            except:
                temp_row.append("-")
            # Total
            try:
                # temp_row.append( thousand_dot_sep( get_threshold_limit_by_rule_name(obj, rule_name) ) )
                limit_val = get_threshold_limit_by_rule_name(obj, rule_name)
                temp_row.append(limit_val)
                # temp_row.append( thousand_dot_sep( get_utilization_val_by_rule_name(obj, rule_name) ) )
            except:
                limit_val = 0
                temp_row.append("-")
            total_limit = total_limit + limit_val
            if len(temp_row) > 1:
                rows.append(temp_row)
        elif port[1] == "Trade":
            calculation = dict_of_column_filter["Counterparty"]["Calculation"]
            keyword = dict_of_column_filter["Counterparty"]["Keyword"]
            obj = port[0].Counterparty()
            obj_trade = port[0]
            # rule_name = obj.Name() + ' ' + keyword
            rule_name = keyword
            temp_row = [" "]  # Ind Code
            temp_row.append(" ")  # Main Industry Code
            cyan_rows.append(" ")
            temp_row.append("")  # CurTyp
            # Main Ind Limit
            try:
                # temp_row.append( thousand_dot_sep( get_threshold_limit_by_rule_name(obj, rule_name) ) )
                temp_row.append(get_threshold_limit_by_rule_name2(rule_name))
                # temp_row.append( thousand_dot_sep( get_utilization_val_by_rule_name(obj, rule_name) ) )
            except:
                temp_row.append("-")
            temp_row.append(get_sub_industry_from_party(obj))  # Sub Industry
            temp_row.append(get_branch_from_trade(obj_trade))  # Br
            temp_row.append(get_source_from_trade(obj_trade))  # Source
            temp_row.append("-")  # SubLmtName
            temp_row.append(get_rule_type_by_rule_name(rule_name))  # Type Utilization
            temp_row.append(obj.Name())  # Customer Name
            # AcctNo
            journal = get_journal_from_trade(obj_trade)
            try:
                temp_row.append(
                    get_account_number_from_trade(
                        journal, calc_space, "Journal Account Number"
                    )
                )
            except:
                temp_row.append("-")
            temp_row.append(get_product_from_trade(obj_trade))  # Product
            temp_row.append("")  # OrigCcy
            temp_row.append(get_cust_type_from_party(obj))  # Cust Type
            # Due Date
            try:
                temp_row.append(
                    date_formatter(get_end_date_by_rule_name(obj, rule_name))
                )
            except:
                temp_row.append("-")
            # Total
            try:
                # temp_row.append( thousand_dot_sep( get_threshold_limit_by_rule_name(obj, rule_name) ) )
                limit_val = get_threshold_limit_by_rule_name(obj, rule_name)
                temp_row.append(limit_val)
                # temp_row.append( thousand_dot_sep( get_utilization_val_by_rule_name(obj, rule_name) ) )
            except:
                limit_val = 0
                temp_row.append("-")
            total_limit = total_limit + limit_val
            if len(temp_row) > 1:
                rows.append(temp_row)
        elif port[1] == "Party":
            calculation = dict_of_column_filter["Counterparty"]["Calculation"]
            keyword = dict_of_column_filter["Counterparty"]["Keyword"]
            obj = port[0]
            rule_name = keyword
            temp_row = [" "]  # Ind Code
            temp_row.append(" ")  # Main Industry Code
            cyan_rows.append(" ")
            temp_row.append("")  # CurTyp
            # Main Ind Limit
            try:
                # temp_row.append( thousand_dot_sep( get_threshold_limit_by_rule_name(obj, rule_name) ) )
                temp_row.append(get_threshold_limit_by_rule_name2(rule_name))
                # temp_row.append( thousand_dot_sep( get_utilization_val_by_rule_name(obj, rule_name) ) )
            except:
                temp_row.append("-")
            # print( obj.BusinessStatus() )
            temp_row.append(get_sub_industry_from_party(obj))  # Sub Industry
            temp_row.append("-")  # Br
            temp_row.append("-")  # Source
            temp_row.append("-")  # SubLmtName
            temp_row.append(get_rule_type_by_rule_name(rule_name))  # Type Utilization
            temp_row.append(obj.Name())  # Customer Name
            temp_row.append("-")  # AcctNo
            temp_row.append("-")  # Product
            temp_row.append("")  # OrigCcy
            temp_row.append(get_cust_type_from_party(obj))  # Cust Type
            # Due Date
            try:
                temp_row.append(
                    date_formatter(get_end_date_by_rule_name(obj, rule_name))
                )
            except:
                temp_row.append("-")
            # Total
            try:
                # temp_row.append( thousand_dot_sep( get_threshold_limit_by_rule_name(obj, rule_name) ) )
                limit_val = get_threshold_limit_by_rule_name(obj, rule_name)
                temp_row.append(limit_val)
                # temp_row.append( thousand_dot_sep( get_utilization_val_by_rule_name(obj, rule_name) ) )
            except:
                limit_val = 0
                temp_row.append("-")
            total_limit = total_limit + limit_val
            if len(temp_row) > 1:
                rows.append(temp_row)
        else:
            obj = port[0]
            blue_rows.append(obj)
            temp_row = ["", obj]  # Ind Code and Main Industry Code
            temp_row.append("")  # CurTyp
            temp_row.append("")  # Main Ind Limit
            temp_row.append("")  # Sub Industry
            temp_row.append("")  # Br
            temp_row.append("")  # Source
            temp_row.append("")  # SubLmtName
            temp_row.append("")  # Type Utilization
            temp_row.append("")  # Customer Name
            temp_row.append("")  # AcctNo
            temp_row.append("")  # Product
            temp_row.append("")  # OrigCcy
            temp_row.append("")  # Cust Type
            temp_row.append("")  # Due Date
            temp_row.append(total_limit)  # Total
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
            "<td>" + cyan + "</td>",
            '<td style="text-align: left; background-color: #00ccff;">'
            + cyan
            + "</td>",
        )
        table_xsl_fo = table_xsl_fo.replace(
            '<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>'
            + cyan
            + "</fo:block></fo:table-cell>",
            '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" text-align="left" background-color="#00ccff"><fo:block>'
            + cyan
            + "</fo:block></fo:table-cell>",
        )
    for blue in blue_rows:
        table_html = table_html.replace(
            "<tr><td></td><td>" + blue + "</td>",
            '<tr style="text-align: left; background-color: #0033cc;"><td></td><td>'
            + blue
            + "</td>",
        )
        table_xsl_fo = table_xsl_fo.replace(
            """
        <fo:table-row>
        <fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block></fo:block></fo:table-cell>
            <fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>{}</fo:block></fo:table-cell>
        """.format(
                blue
            ),
            """
        <fo:table-row background-color="#0033cc">
        <fo:table-cell border-width="1px" border-style="solid" padding="8pt" text-align="left"><fo:block></fo:block></fo:table-cell>
            <fo:table-cell border-width="1px" border-style="solid" padding="8pt" text-align="left"><fo:block>{}</fo:block></fo:table-cell>
        """.format(
                blue
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
    #'IND CODE','MAIN INDUSTRY NAME', 'CUR', 'MAIN IND LIMIT', 'SUB INDUSTRY', 'BR', 'SOURCE', 'SUBLMTNAME', 'TYPE UTILIZATION', 'CUSTOMER NAME', 'ACCTNO', 'PRODUCT', 'ORICCY', 'CUST TYPE', 'DUE DATE', 'TOTAL'
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
    <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>IND CODE</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>MAIN INDUSTRY NAME</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>CUR</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>MAIN IND LIMIT</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>SUB INDUSTRY</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>BR</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>SOURCE</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>SUBLMTNAME</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>TYPE UTILIZATION</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>CUSTOMER NAME</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>ACCTNO</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>PRODUCT</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>ORICCY</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>CUST TYPE</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>DUE DATE</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>TOTAL</fo:block></fo:table-cell>
        </fo:table-header>
    <fo:table-body>""",
        """<fo:table-body>
    <fo:table-row background-color="#000000" color="#ffffff" font-weight="bold">
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>IND CODE</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>MAIN INDUSTRY NAME</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>CUR</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>MAIN IND LIMIT</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>SUB INDUSTRY</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>BR</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>SOURCE</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>SUBLMTNAME</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>TYPE UTILIZATION</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>CUSTOMER NAME</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>ACCTNO</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>PRODUCT</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>ORICCY</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>CUST TYPE</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>DUE DATE</fo:block></fo:table-cell>
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
