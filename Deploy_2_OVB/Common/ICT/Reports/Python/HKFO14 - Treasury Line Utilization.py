import acm, ael, random
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from time import sleep, perf_counter, strftime, strptime
from decimal import Decimal, getcontext
from Python_MO_Custom_Fields import *
from datetime import datetime, date, timezone

context = acm.GetDefaultContext()
today = acm.Time.DateToday()
yesterday = acm.Time.DateAddDelta(today, 0, 0, -1)
next_month = acm.Time.DateAddDelta(today, 0, 1, 0)
next_year = acm.Time.DateAddDelta(today, 1, 0, 0)
all_trades = acm.FTrade.Select("")
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


def get_trades_by_cpty_ins_type(industry, pty_list, ins_type_list):
    trade_list = [(acm.FChoiceList[industry], "Industry")]
    for pty in pty_list:
        if pty[1] == industry:
            trade_list.append((acm.FParty[pty[0]], "Party"))
            trades = acm.FTrade.Select(
                "counterparty='" + pty[0] + "' and optKey4<>None"
            )
            # print(trades)
            # trades_vers_1 = [( trd.Oid(), trd.OptKey3(), trd.OptKey4() ) for trd in trades]
            # print(trades_vers_1)
            for ins_type in ins_type_list:
                trades_vers_2 = get_trades_by_prod_type_category(trades, ins_type)
                trade_list = trade_list + trades_vers_2
            # trade_list.append( (industry+' Total', 'Total') )
    return trade_list


def get_industries_by_ael_sql(pty_list):
    industry_list = []
    for pty in pty_list:
        if acm.FParty[pty[0]].BusinessStatus() not in industry_list:
            industry_list.append(acm.FParty[pty[0]].BusinessStatus())
    return industry_list


def get_party_data_by_ael_sql(pty_list, country_name):
    country_pty_list = [acm.FChoiceList[country_name]]
    for pty in pty_list:
        if pty[1] == country_name:
            country_pty_list.append(acm.FParty[pty[0]])
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
    "windowCaption": "HKFO14 - Treasury Line Utilization",
}
# settings.FILE_EXTENSIONS
ael_variables = [
    [
        "report_name",
        "Report Name",
        "string",
        None,
        "HKFO14 - Treasury Line Utilization",
        1,
        0,
    ],
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
    rulename = "Local Government"
    # party_list = ael.asql("Select p.ptyid, c.entry from Party p, ChoiceList c where p.business_status_chlnbr=c.seqnbr and p.type = 'Counterparty'")[1][0]
    # party_list = [('Bank of America Frankfurt','United States',),('Bank of America New York','United States',)]
    # party_list = [('#100003','United States',)]
    pty_list = acm.FParty.Select("type='Counterparty'")[:2]
    party_list = [pty_list[0], pty_list[1]]
    product_list = ["BOND"]
    all_ports = []
    for i in party_list:
        pty = i
        all_ports.append(pty)
    # titles = ['Country', 'Limit', 'Utilisasi', '1 Day Change', '% Utilization', 'Status Limit', 'Limit Expiry', 'Status Limit Expiry', 'Notes']
    titles = [
        "No",
        "Nama",
        "Swift Code",
        "Limit DN (Rp)",
        "Utilisasi DN (Rp)",
        "Limit LN (Rp)",
        "Utilisasi Luar Negeri (USD)",
        "Total",
    ]
    country_columns = ["Hongkong", "Singapore", "Cayman", "Timor Leste", "Shanghai"]
    total_columns = ["Treasury Line (Rp)", "Total Utilisasi (Rp)"]
    columns = country_columns + total_columns
    # calc_space = acm.Calculations().CreateCalculationSpace(acm.GetDefaultContext(), sheet_type)
    calc_space = acm.Calculations().CreateCalculationSpace(
        acm.GetDefaultContext(), "FJournalSheet"
    )
    calc_space2 = acm.Calculations().CreateCalculationSpace(
        acm.GetDefaultContext(), "FAppliedRuleSheet"
    )
    rows = [columns]
    cyan_rows = []
    blue_rows = []
    total_limit = 0
    row_count = 1
    for port in all_ports:
        keyword = dict_of_column_filter["Counterparty"]["Keyword"]
        obj = port
        rule_name = keyword
        temp_row = [str(row_count)]
        temp_row.append(obj.Name())
        temp_row.append(obj.Swift())
        try:
            # temp_row.append( thousand_dot_sep( get_threshold_limit_by_rule_name(obj, rule_name) ) )
            temp_row.append(get_threshold_limit_by_rule_name(obj, rule_name))
            # temp_row.append( thousand_dot_sep( get_utilization_val_by_rule_name(obj, rule_name) ) )
        except:
            temp_row.append("-")
        try:
            temp_row.append(get_utilization_val_by_rule_name(obj, rule_name))
        except:
            temp_row.append("-")
        try:
            temp_row.append(get_threshold_limit_by_rule_name(obj, rule_name))
        except:
            temp_row.append("-")
        temp_row.append("-")
        temp_row.append("-")
        temp_row.append("-")
        temp_row.append("-")
        temp_row.append("-")
        temp_row.append("-")
        temp_row.append("-")
        if len(temp_row) > 1:
            rows.append(temp_row)
        row_count += 1
    table_html = create_html_table(titles, rows)
    table_xsl_fo = create_xsl_fo_table(titles, rows)
    for i in titles:
        if i == "Total":
            table_html = table_html.replace(
                "<th>" + i + "</th>",
                '<th style="background-color: #000000; color: #ffffff;" colspan="'
                + str(len(total_columns))
                + '">'
                + i
                + "</th>",
            )
        elif i == "Utilisasi Luar Negeri (USD)":
            table_html = table_html.replace(
                "<th>" + i + "</th>",
                '<th style="background-color: #000000; color: #ffffff;" colspan="'
                + str(len(country_columns))
                + '">'
                + i
                + "</th>",
            )
        else:
            table_html = table_html.replace(
                "<th>" + i + "</th>",
                '<th style="background-color: #000000; color: #ffffff;" rowspan="2">'
                + i
                + "</th>",
            )
    table_html = table_html.replace(
        "<tr><td>" + columns[0] + "</td>",
        '<tr style="background-color: #000000; color: #ffffff; font-weight: bold"><td>'
        + columns[0]
        + "</td>",
    )
    table_xsl_fo = table_xsl_fo.replace(
        """
    <fo:table-row>
        <fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>{}</fo:block></fo:table-cell>
    """.format(
            columns[0]
        ),
        """
    <fo:table-row background-color="#000000" color="#ffffff" font-weight="bold">
        <fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>{}</fo:block></fo:table-cell>
    """.format(
            columns[0]
        ),
    )
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
    current_date2 = (
        "Report Date: "
        + datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        + f" UTC+{datetime.now().hour - datetime.now(timezone.utc).hour:02d}:00"
    )
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
    html_contents = html_contents.replace(
        "<table>", '<h1 style="text-align: left;">' + current_date2 + "</h1><table>"
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
    #'No','Name', 'Swift Code', 'Limit DN (Rp)', 'Utilisasi DN (Rp)', 'Limit LN (Rp)', 'Utilisasi Luar Negeri (USD)', 'Total'
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
        + "</fo:block>"
        + '<fo:block font-weight="bold" font-size="30px" margin-bottom="30px" text-align="left">'
        + current_date2
        + "</fo:block>",
    )
    xsl_contents = xsl_contents.replace(
        """<fo:table-header background-color="#666666" color="#ffffff" font-weight="bold">
    <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>No</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Name</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Swift Code</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Limit DN (Rp)</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Utilisasi DN (Rp)</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Limit LN (Rp)</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Utilisasi Luar Negeri (USD)</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Total</fo:block></fo:table-cell>
        </fo:table-header>
    <fo:table-body>""",
        '''<fo:table-body>
    <fo:table-row background-color="#000000" color="#ffffff" font-weight="bold">
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid" number-rows-spanned="2"><fo:block>No</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid" number-rows-spanned="2"><fo:block>Name</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid" number-rows-spanned="2"><fo:block>Swift Code</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid" number-rows-spanned="2"><fo:block>Limit DN (Rp)</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid" number-rows-spanned="2"><fo:block>Utilisasi DN (Rp)</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid" number-rows-spanned="2"><fo:block>Limit LN (Rp)</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid" number-columns-spanned="'''
        + str(len(country_columns))
        + '''"><fo:block>Utilisasi Luar Negeri (USD)</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid" number-columns-spanned="'''
        + str(len(total_columns))
        + """"><fo:block>Total</fo:block></fo:table-cell>
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
