import acm, ael
import pandas as pd

def getFilePathSelection(status):
    """ Directory selector dialog """
    selection = acm.FFileSelection()
    selection.PickDirectory(status)
    selection.SelectedDirectory = 'c:\\'
    return selection  

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'CTP Mandiri - Import CTP File'}

ael_variables=[
['import_path', 'Source File Path', getFilePathSelection(False), None, getFilePathSelection(False), 1, 1]
]  

def ael_main(parameter):
    import_path = str(parameter['import_path'])
    
    f = open(import_path, "r")
    csv_file = f.read().split('\n')
    titles = csv_file[0].split(',')
    rows = csv_file[1:]
    ctp_number_idx = titles.index('CTP Number')
    ctp_reference_idx = titles.index('CTP Reference')
            
    for i in rows:
        print(i)
        if i == "":
            break
        else:
            i = i.split(',')
        
        try:
            ctp_number = str(i[ctp_number_idx])
            trade_no = ael.asql("""select add.recaddr 'TRADENO', add.addinf_specnbr, add.value
            from AdditionalInfo add
            where (add.addinf_specnbr=70) and (add.value=""" + str(ctp_number) + ")")[1][0][0][0]
            trade = acm.FTrade[trade_no]
            ctp_number = trade.AddInfoValue('CTP Number')
            ctp_reference = trade.AddInfoValue('CTP Reference')
            ctp_status = trade.AddInfoValue('CTP Matching Status')
                    
            if str(i[ctp_reference_idx]) == ctp_reference:
                trade.AddInfoValue('CTP Matching Status', 'OK')
            else:
                trade.AddInfoValue('CTP Matching Status', 'NOK')
                    
        except Exception as e: 
            print(e)
            trade = acm.FTrade[int(i[ctp_reference_idx])]
            trade.AddInfoValue('CTP Number', str(i[ctp_number_idx]))
            trade.AddInfoValue('CTP Reference', i[ctp_reference_idx])
            trade.AddInfoValue('CTP Matching Status', 'OK')
        
        trade.Commit()

