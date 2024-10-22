from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *

file_name = "SH13 - Interface System Between MO and FO System"
ael_gui_parameters = {
    "runButtonLabel": "&&Run",
    "hideExtraControls": True,
    "windowCaption": file_name,
}
ael_variables = [
    ["report_name", "Report Name", "string", None, file_name, 1, 0],
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
        ".xls",
        0,
        1,
        "Select Secondary Extensions Output",
    ],
]


def ael_main(parameter):
    report_name = parameter["report_name"]
    file_path = str(parameter["file_path"])
    output_file = parameter["output_file"]
    titles = [
        "",
        "STATUS",
        "OPICS_SECID",
        "SUMMIT_SECID",
        "OPICS_PRICE",
        "SUMMIT_PRICE",
        "OPICS_DATE",
        "SUMMIT_DATE",
    ]
    prices = acm.FPrice.Select("")
    row = []
    rows = []
    i = 0
    for p in prices:
        try:
            market_name = p.Market().Name()
        except:
            market_name = None
        if market_name == "OPICS":
            for p1 in acm.FInstrument[p.Instrument().Name()].Prices():
                try:
                    market_name_2 = p1.Market().Name()
                except:
                    market_name_2 = None
                if market_name_2 == "SUMMIT":
                    i += 1
                    if p.Last() == p1.Last():
                        status = "MATCHED"
                    else:
                        status = "UNMATCHED"
                    row = [
                        i,
                        status,
                        p.Instrument().Name(),
                        p1.Instrument().Name(),
                        p.Last(),
                        p1.Last(),
                        acm.Time.DateFromTime(p.CreateTime()),
                        acm.Time.DateFromTime(p1.CreateTime()),
                    ]
                    rows.append(row)
    table_html = create_html_table(titles, rows)
    table_xsl_fo = create_xsl_fo_table(titles, rows)
    current_date = get_current_date("")
    html_file = create_html_file(
        report_name, file_path, [table_html], report_name, current_date
    )
    xsl_fo_file = create_xsl_fo_file(
        report_name, file_path, [table_xsl_fo], report_name, current_date
    )
    xsl_f = open(xsl_fo_file, "r")
    xsl_contents = xsl_f.read().replace(
        '<fo:simple-page-master master-name="my_page" margin="0.5in">',
        '<fo:simple-page-master master-name="my_page" margin="0.5in" reference-orientation="90">',
    )
    xsl_f = open(xsl_fo_file, "w")
    xsl_f.write(xsl_contents)
    xsl_f.close()
    for i in output_file:
        if i != ".pdf":
            generate_file_for_other_extension(html_file, i)
        else:
            generate_pdf_from_fo_file(xsl_fo_file)
