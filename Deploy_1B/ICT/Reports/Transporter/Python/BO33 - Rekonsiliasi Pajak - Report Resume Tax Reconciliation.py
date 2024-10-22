from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *

import acm, ael



def get_total_faceValue(glno):
    query = f"""
        SELECT 
            j.seqnbr
        FROM 
            TAccount t, ChartOfAccount c, Journal j
        WHERE
            c.t_account = t.seqnbr
            AND j.chart_of_account_seqnbr = c.seqnbr 
            AND t.number IN {glno}
            AND (j.event_date >= date_add_delta(FIRSTDAYOFMONTH, 0, -1, 0) AND j.event_date < FIRSTDAYOFMONTH)
    """
    query_result = ael.asql(query)[1][0]
    print(query_result)
    
    total_faceVal = 0
    for seqnbr in query_result:
        curr = acm.FJournal[seqnbr[0]].Currency().Name()
        amount = acm.FJournal[seqnbr[0]].Amount()
        if curr == "IDR" :
            total_faceVal += abs(float(amount))
                
    return total_faceVal
    

def generate_html_file(report_name, titles, reviewer_list, file_path, output_file):

    html_gen = HTMLGenerator()

    title_style = """
        
        table {
            width: fit-content
        }

        .title {

            color: #800000;

            text-align: left;   

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

        .amount {

            font-weight: bold;

        }

    """
    
    html_content = html_gen.create_base_html_content(report_name, title_style)

    html_content = html_gen.prepare_html_table(html_content, titles)
    
    glno_used = [
        "('21011110_TaxDerivative')",
        "('21011110_TaxFIDomestic')",
        "('21011102_TaxFIForeign')",
        "('21011110_TaxBilateralLoan')"
    ]
    
    
    row_data = [
            ["1", "PPH Pasal 4 (2) - Derivative", "IDR", get_total_faceValue(glno_used[0]), "IDR", get_total_faceValue(glno_used[0])], 
            ["2", "PPH Pasal 4 (2) - Fixed Income", "IDR", get_total_faceValue(glno_used[1]), "IDR", get_total_faceValue(glno_used[1])], 
            ["3", "PPH Pasal 26 - Fixed Income", "IDR", get_total_faceValue(glno_used[2]), "IDR",get_total_faceValue(glno_used[2])],
            ["4", "PPH Pasal 26 - Derivative", "IDR", get_total_faceValue(glno_used[3]), "IDR",get_total_faceValue(glno_used[3])]
    ]

    html_content = html_gen.add_data_row(html_content, row_data, row_class='', cell_class="")
    
    
    for row in row_data :
        for i, cel_val in enumerate(row) :
            if i in [3, 5]:
                html_content = html_content.replace(f"<td >{cel_val}</td>", f'<td style="text-align:right">{abs(round(cel_val, 2)):,}</td>')
            elif i == 1 :
                html_content = html_content.replace(f"<td >{cel_val}</td>", f'<td style="text-align:left">{cel_val}</td>')
    
    total_sum = 0

        
    
    for row in row_data:
        
        #val_amount = float(row[-1].replace(",", ""))

        total_sum += row[-1]

 

    sum_row = [["TOTAL", "", f"{abs(float(total_sum)):,}"]]

    html_content = html_gen.add_data_row(html_content, sum_row, row_class='', cell_class="style='font-weight:bold;'")

    html_content = html_content.replace("<td style='font-weight:bold;'>TOTAL</td>", "<td colspan='4' style='font-weight:bold; text-align:right'>Total</td>")

    html_content = html_gen.close_html_table(html_content)

    

    html_content += "<br/><br/>"

    

    html_content = html_gen.prepare_html_table(html_content, [])

    

    row_data = [[" ", " ", " ", "Prepared by", "Reviewed by", "Accepted by"], 
                [" ", " ", " ", " ", " ", " "],  
                [" ", " ", " ", " ", " ", " "], 
                [" ", " ", " ", " ", " ", " "],
                [" ", " ", " ", " ", " ", " "],
                [" ", " ", " ", " ", " ", " "], 
                reviewer_list]

    html_content = html_gen.add_data_row(html_content, row_data, row_class='', cell_class="style='font-weight:bold'")

    html_content = html_content.replace("<td style='font-weight:bold'> </td>", "<td style='font-weight:bold;border:0px;'> </td>")

    html_content = html_gen.close_html_table(html_content)

    
    current_date = get_current_date("")
    
    html_file = html_gen.create_html_file(html_content, file_path, report_name, current_date, True)

    return html_file

    

ael_gui_parameters={'runButtonLabel':'&&Run',

                    'hideExtraControls': True,

                    'windowCaption':'BO33 - Rekonsiliasi Pajak - Report Resume Tax Reconciliation'}



ael_variables=[

    ['report_name','Report Name','string', None, 'BO33 - Rekonsiliasi Pajak - Report Resume Tax Reconciliation', 1,0],

    ['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],

    ['output_file','Secondary Output Files','string', ['.xls'], '.xls',0,1, 'Select Secondary Extensions Output'],

    ['prepared_by','Prepared By','string', None, 'Ahmad Syaihu', 1,0],

    ['reviewed_by','Reviewed By','string', None, 'Rulando Irawan', 1,0],

    ['accepted_by','Accepted By','string', None, 'Ristauli Gurning', 1,0]

]

def ael_main(parameter):

    report_name = parameter['report_name']

    file_path = str(parameter['file_path'])

    output_file = parameter['output_file']

    prepared_by = parameter['prepared_by']

    reviewed_by = parameter['reviewed_by']

    accepted_by = parameter['accepted_by']

    

    title_style = """

        .title {

            color: #800000;

            text-align: left;   

        }

        

        .subtitle-1 {

            color: #0000FF;

            font-size: 20px;

            text-align: left;   

        }

        

        .subtitle-2 {

            color: #000080;

            font-size: 16px;

            text-align: left;   

        }

    """    

    titles = ["NO", "JENIS PAJAK", "CURRENCY", "PAJAK", "CURRENCY", "TOTAL PAJAK"]

    reviewer_list = [" ", " ", " ", prepared_by, reviewed_by, accepted_by]

        

    for i in output_file:

        if i != '.pdf' :

            html_file = generate_html_file(report_name, titles, reviewer_list, file_path, output_file)

            generate_file_for_other_extension(html_file , i)

        #else:

            #xsl_fo_file = generate_xls_fo_file(report_name, titles, file_path, output_file, heading_1_list, heading_2_list, optkey3_list, optkey4_list)

            #generate_pdf_from_fo_file(xsl_fo_file)

