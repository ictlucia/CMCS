import os, acm, ael, webbrowser, shutil, traceback, math
import FReportSettings as settings
from string import Template
from datetime import datetime
import time as tm

div_side_by_side = '<div class="side-by-side">'
end_div_side_by_side = "</div>"


class HTMLGenerator:
    def create_base_html_content(self, title, additional_styles=""):
        html_content = (
            """
            <!DOCTYPE html>
            <html>
            <head>
            <style>
            table {
              font-family: arial, sans-serif;
              border-collapse: collapse;
              white-space: nowrap;
              margin-left: 100px;
            }
            .side-by-side { 
              display: flex; 
            } 
            div { 
              margin-bottom: 5px; 
            } 
            td, th {
              border: 1px solid #dddddd;
              text-align: center;
              padding: 8px;
            }
            h1 {
                text-align: center;
            }
        """
            + additional_styles
            + """
            </style>
            </head>
            <body>
            <center><h1 class='title'><u>"""
            + str(title)
            + """</u></h1></center>"""
        )
        return html_content

    def add_body(self, list_table, additional_content):
        for i in list_table:
            html_content += i + "<br>"
        html_content += additional_content
        html_content += "</body></html>"

    def prepare_html_table(
        self, html_content, header_list, row_style="", header_style="", table_styling=""
    ):
        html_table = f"""
        <div> 
            <table {table_styling}>
        """
        html_table += f"<tr {row_style}>"
        for i in header_list:
            html_table += f"<th {header_style}>" + str(i) + "</th>"
        html_table += "</tr>"
        return html_content + html_table

    def close_html_table(self, html_content):
        html_content += "</table></div>"
        return html_content

    def add_data_row(self, html_content, row_data, row_class="", cell_class=""):
        for row in row_data:
            html_content += f"<tr {row_class}>"
            for cell in row:
                html_content += f"<td {cell_class}>" + str(cell) + "</td>"
            html_content += "</tr>"
        return html_content

    def add_subtitle_separator(
        self, html_content, title, style_string="", attribute_string=""
    ):
        html_content += (
            "<tr>"
            + f"<td style='{style_string}' {attribute_string}>"
            + title
            + "</td>"
            + "</tr>"
        )
        return html_content

    def create_html_file(
        self,
        html_content,
        file_path,
        file_name,
        current_date,
        open_html,
        folder_with_file_name=False,
    ):
        if folder_with_file_name:
            folder_path = file_path + "\\" + file_name + "\\" + current_date
        else:
            folder_path = file_path + "\\report" + current_date
        try:
            os.makedirs(folder_path)
        except:
            # print('Path too long')
            pass
        file_url = folder_path + "\\" + file_name + ".html"
        f = open(file_url, "w")
        f.write(html_content)
        f.close()
        url = "file://" + file_url
        if open_html:
            webbrowser.open(file_url, new=2)
        return file_url

    # Adding New Row to the Table
    def open_table_row(self, html_content, row_attribute=""):
        html_content += f"<tr {row_attribute}>"
        return html_content

    # Adding New Column to the Data Row
    def add_cell_data(self, html_content, data, cell_attribute=""):
        html_content += f"<td {cell_attribute}>{str(data)}</td>"
        return html_content

    # Closing the Data Row
    def close_table_row(self, html_content):
        html_content += "</tr>"
        return html_content


class XSLFOGenerator:
    def prepare_xsl_fo_content(self, title, title_styling=""):
        xsl_fo_content = f"""<?xml version="1.1" encoding="utf-8"?>
        <fo:root xmlns:fo="http://www.w3.org/1999/XSL/Format">
         <fo:layout-master-set>
          <fo:simple-page-master master-name="my_page" margin="0.5in" page-width="25in">
           <fo:region-body/>
          </fo:simple-page-master>
         </fo:layout-master-set>
         <fo:page-sequence master-reference="my_page">
          <fo:flow flow-name="xsl-region-body">
            <fo:block {title_styling}> {title} </fo:block>
        """
        return xsl_fo_content

    def add_xsl_fo_table_header(
        self,
        xsl_fo_content,
        header_list,
        header_styling="padding='8pt' border-width='1px' border-style='solid'",
    ):
        xsl_fo_table = """<fo:table margin-bottom="50px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto">
        """
        for header in header_list:
            xsl_fo_table += """ <fo:table-column border-width="1px" border-style="solid"/>
            """
        xsl_fo_table += """<fo:table-header background-color="#666666" color="#ffffff" font-weight="bold">\n<fo:table-row>
        """
        for header in header_list:
            xsl_fo_table += (
                f"""<fo:table-cell {header_styling}><fo:block>"""
                + str(header)
                + """</fo:block></fo:table-cell>
            """
            )
        xsl_fo_table += """</fo:table-row></fo:table-header>\n<fo:table-body>
        """
        return xsl_fo_content + xsl_fo_table

    def add_xsl_subtitle_separator(
        self, xsl_content, title, style_string="", colspan=1
    ):
        xsl_content += (
            """<fo:table-row>"""
            + f"""<fo:table-cell border-width="1px" border-style="solid" padding="8pt" number-columns-spanned="{colspan}"><fo:block {style_string}>"""
            + title
            + """</fo:block></fo:table-cell>"""
            + """</fo:table-row>
        """
        )
        return xsl_content

    def add_xsl_data_row(
        self,
        xsl_content,
        row_data,
        cell_styling="border-width='1px' border-style='solid' padding='8pt'",
        block_styling="",
    ):
        xsl_content += """
        """
        for row in row_data:
            xsl_content += """<fo:table-row>
            """
            for cell in row:
                xsl_content += (
                    f"""<fo:table-cell {cell_styling}><fo:block {block_styling}>"""
                    + str(cell)
                    + """</fo:block></fo:table-cell>
                """
                )
            xsl_content += """</fo:table-row>
            """
        return xsl_content

    def close_xsl_table(self, xsl_content):
        xsl_content += """</fo:table-body></fo:table>"""
        return xsl_content

    # Adding New XSL Row
    def prepare_xsl_row(self, xsl_content, row_style=""):
        xsl_content += f"<fo:table-row {row_style}>"
        return xsl_content

    # Adding Column to the XSL Row
    def add_xsl_column(
        self,
        xsl_content,
        data,
        cell_style="border-width='1px' border-style='solid' padding='8pt'",
        block_style="",
    ):
        xsl_content += (
            f"<fo:table-cell {cell_style}><fo:block {block_style}>"
            + str(data)
            + "</fo:block></fo:table-cell>"
        )
        return xsl_content

    # Close XSL Row
    def close_xsl_row(self, xsl_content):
        xsl_content += f"</fo:table-row>"
        return xsl_content

    def create_xsl_fo_file(
        self,
        file_name,
        file_path,
        xsl_fo_content,
        current_datetime,
        folder_with_file_name=False,
    ):
        xsl_fo_content += """ </fo:flow>
             </fo:page-sequence>
            </fo:root>
        """
        if folder_with_file_name:
            folder_path = file_path + "\\" + file_name + "\\" + current_datetime
        else:
            folder_path = file_path + "\\report" + current_datetime
        try:
            os.makedirs(folder_path)
        except:
            # print('Path too long')
            pass
        file_url = folder_path + "\\" + file_name + ".fo"
        f = open(file_url, "w")
        f.write(xsl_fo_content)
        f.close()
        return file_url


def getFilePathSelection(status=True):
    """Directory selector dialog"""
    selection = acm.FFileSelection()
    selection.PickDirectory(status)
    selection.SelectedDirectory = "c:\\"
    return selection


def create_html_file(
    file_name,
    file_path,
    list_table,
    title,
    current_datetime,
    folder_with_file_name=False,
    open_html=True,
):
    html_content = (
        """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    table {
      font-family: arial, sans-serif;
      border-collapse: collapse;
      white-space: nowrap;
      margin-left: 100px;
    }
    .side-by-side { 
      display: flex; 
    } 
    div { 
      margin-bottom: 5px; 
    } 
    td, th {
      border: 1px solid #dddddd;
      text-align: center;
      padding: 8px;
    }
    h1 {
        text-align: center;
    }
    </style>
    </head>
    <body>
    <center><h1><u>"""
        + str(title)
        + """</u></h1></center>"""
    )
    for i in list_table:
        html_content += i + "<br>"
    html_content += "</body></html>"
    if folder_with_file_name:
        folder_path = file_path + "\\" + file_name + "\\" + current_datetime
    else:
        folder_path = file_path + "\\report" + current_datetime
    try:
        os.makedirs(folder_path)
    except:
        # print('Path too long')
        pass
    file_url = folder_path + "\\" + file_name + ".html"
    f = open(file_url, "w")
    f.write(html_content)
    f.close()
    url = "file://" + file_url
    if open_html:
        webbrowser.open(file_url, new=2)
    return file_url


def create_html_table(list_title, list_row):
    html_table = """
    <div> 
        <table>
    """
    html_table += "<tr>"
    for i in list_title:
        html_table += "<th>" + str(i) + "</th>"
    html_table += "</tr>"
    for i in list_row:
        html_table += "<tr>"
        for j in i:
            html_table += "<td>" + str(j) + "</td>"
        html_table += "</tr>"
    html_table += "</table></div>"
    return html_table


def create_xsl_fo_file(
    file_name,
    file_path,
    list_table,
    title,
    current_datetime,
    folder_with_file_name=False,
):
    xsl_fo_content = (
        """<?xml version="1.1" encoding="utf-8"?>
<fo:root xmlns:fo="http://www.w3.org/1999/XSL/Format">
 <fo:layout-master-set>
  <fo:simple-page-master master-name="my_page" margin="0.5in">
   <fo:region-body/>
  </fo:simple-page-master>
 </fo:layout-master-set>
 <fo:page-sequence master-reference="my_page">
  <fo:flow flow-name="xsl-region-body">
    <fo:block font-weight="bold" font-size="30px" margin-bottom="30px">"""
        + str(title)
        + """</fo:block>
"""
    )
    for i in list_table:
        xsl_fo_content += i + "\n"
    xsl_fo_content += """ </fo:flow>
 </fo:page-sequence>
</fo:root>
    """
    if folder_with_file_name:
        folder_path = file_path + "\\" + file_name + "\\" + current_datetime
    else:
        folder_path = file_path + "\\report" + current_datetime
    try:
        os.makedirs(folder_path)
    except:
        # print('Path too long')
        pass
    file_url = folder_path + "\\" + file_name + ".fo"
    f = open(file_url, "w")
    f.write(xsl_fo_content)
    f.close()
    return file_url


def create_xsl_fo_table(list_title, list_row):
    xsl_fo_table = """<fo:table margin-bottom="50px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto">
    """
    xsl_fo_table += """<fo:table-header background-color="#666666" color="#ffffff" font-weight="bold">
    """
    for i in list_title:
        xsl_fo_table += (
            """<fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>"""
            + str(i)
            + """</fo:block></fo:table-cell>
        """
        )
    xsl_fo_table += """</fo:table-header>
    """
    xsl_fo_table += """<fo:table-body>
    """
    for i in list_row:
        xsl_fo_table += """<fo:table-row>
        """
        for j in i:
            xsl_fo_table += (
                """<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>"""
                + str(j)
                + """</fo:block></fo:table-cell>
            """
            )
        xsl_fo_table += """</fo:table-row>
        """
    xsl_fo_table += """</fo:table-body>
    </fo:table>
    """
    return xsl_fo_table


def generate_pdf_from_fo_file(foFilePath):
    foFilePath = foFilePath.replace(".fo", "")
    command = Template(settings.FOP_BAT)
    command = command.substitute({"extension": "pdf", "filename": foFilePath})
    ret = os.system(command)
    if ret == 0:
        print("Generate PDF Succesful")
    else:
        print("Somethings wrong when generating PDF.")
    # os.remove(foFilePath+'.fo')


def generate_file_for_other_extension(file_url, extension):
    pre, ext = os.path.splitext(file_url)
    shutil.copy(file_url, pre + extension)


def get_date_from_input(str_period, start_date="Today"):
    try:
        period_type = str_period[-1]
        period_nbr = int(str_period[:-1])
        if start_date == "Today":
            today = acm.Time.DateToday()
        else:
            today = start_date
        if period_type.lower() == "d":
            result = acm.Time.DateAddDelta(today, 0, 0, period_nbr)
        elif period_type.lower() == "w":
            period_nbr = period_nbr * 7
            result = acm.Time.DateAddDelta(today, 0, 0, period_nbr)
        elif period_type.lower() == "m":
            result = acm.Time.DateAddDelta(today, 0, period_nbr, 0)
        elif period_type.lower() == "y":
            result = acm.Time.DateAddDelta(today, period_nbr, 0, 0)
        else:
            result = period_nbr
    except Exception:
        # traceback.print_exc()
        result = str_period
    return result


def get_current_date(separator):
    now = datetime.now()
    current_date = now.strftime(f"%y{separator}%m{separator}%d")
    return current_date


def get_current_hour(separator):
    now = datetime.now()
    current_hour = now.strftime(f"%H{separator}%M{separator}%S")
    return current_hour


def get_decimal_without_rounding(angka, jumlah_desimal):
    # https://stackoverflow.com/questions/29246455/python-setting-decimal-place-range-without-rounding
    return math.floor(angka * 10**jumlah_desimal) / 10**jumlah_desimal


def round_half_up(angka, jumlah_desimal=0):
    # https://realpython.com/python-rounding/
    multiplier = 10**jumlah_desimal
    result = float(math.floor(angka * multiplier + 0.5) / multiplier)
    return result


def get_current_report_datetime(separator):
    current_tz = tm.strftime("%z", tm.localtime())
    tz_format = current_tz[0] + current_tz[1:3] + ":" + current_tz[3:]
    now = datetime.now()
    current_datetime = now.strftime(
        "%d"
        + separator
        + "%m"
        + separator
        + "%Y"
        + " "
        + "%H"
        + ":"
        + "%M"
        + ":"
        + "%S"
        + " UTC"
        + tz_format
    )
    return "Report Date: " + current_datetime
