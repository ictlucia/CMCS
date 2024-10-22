import acm, ael, os
from datetime import datetime

def check_ctp_criteria(trade_no):
    
    trade = acm.FTrade[trade_no]
    trd_status = trade.Status()
    ctp_status =  trade.AddInfoValue('CTP State Status')
    result = ''
    
    try:
        optkey2 = trade.OptKey2().Name()
        optkey2 = bool(optkey2.lower() != 'boris')
    except:
        optkey2 = False
        
    if optkey2 == False:
        return 'Skip' # Kalo Boris, gadiambil
    
    if trd_status == 'FO Confirmed' and (ctp_status == '' or ctp_status == None):
        result = 'New'
    elif ctp_status.lower() == 'new' or (ctp_status.lower() == 'success' and trd_status == 'FO Confirmed'):
        result = 'Success'
    elif trd_status != 'FO Confirmed' and trd_status != 'Void' and (ctp_status.lower()  == 'success' or ctp_status.lower()  == 'amend'):
        result = 'Amend'
    elif 'void' in trd_status.lower():
        result = 'Void'
    else:
        return 'Skip' # Trade nya gaada perubahan
    
    trade.AddInfoValue('CTP State Status', result)
    trade.Commit()
    
    return result

def getFilePathSelection(status):
    """ Directory selector dialog """
    selection = acm.FFileSelection()
    selection.PickDirectory(status)
    selection.SelectedDirectory = 'c:\\'
    return selection  

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'CTP Mandiri - Export CSV'}

ael_variables=[
['wb_name','Workbook Name','string', None, 'CTP Mandiri', 1,0],
['export_path', 'Destination File Path', getFilePathSelection(True), None, getFilePathSelection(True), 1, 1]
]

def ael_main(parameter):
    report_name = parameter['wb_name']
    export_path = str(parameter['export_path'])

    folder_path = export_path
    file_name = report_name

    task = acm.FAelTask['Task CTP Mandiri']
    params = task.Parameters()
    print(params)
    params.AtPut("File Path", folder_path)
    params.AtPut("HTML to File", "False")
    params.AtPut("HTML to Screen", "False")
    params.AtPut("Create directory with date", "False")
    params.AtPut("Secondary file extension", ".csv")
    params.AtPut("Secondary output", "True")
    params.AtPut("Secondary template", "FCSVTemplate")
    params.AtPut("wbName", file_name)
    task.Parameters = params
    task.Commit()
    task.Execute()

    complete_path = folder_path+"\\"+file_name+".csv"
    f = open(complete_path, "r")
    csv_file = f.read().split('\n')
    titles = ''
    dict_result_group = {
    'ONE' : {"New" : [], "Success" : [], "Amend" : [], "Void" : []}, 
    'TWO' : {"New" : [], "Success" : [], "Amend" : [], "Void" : []}
    }
    
    dict_result_group = {
        "New" : [], 
        "Success" : [], 
        "Amend" : [], 
        "Void" : []
    }

    for i in csv_file:
        if 'Table name' in i:
            idx = csv_file.index(i)
            titles = 'Trade'+csv_file[idx+1]
            titles = titles.split(',')
            break
    
    #trd_status_idx = 'Status'
    #ctp_status_idx = 'CTP State Status'
    #optkey2_idx = 'Source'
    ctp_report_type_idx = titles.index('CTP_Report_Type')
    buy_sell_idx = titles.index('B/S')
    time_idx = titles.index('Time')

    rows = csv_file[idx+2:]
    result_one, result_two = [], []
    
    for i in rows:
        temp_row = i.split(',')

        try:
            trade_no = int(temp_row[0])
            check_if_grouper_row = bool(temp_row[1] != '')
            
            if check_if_grouper_row :
                result = check_ctp_criteria(trade_no)
                print(trade_no, ' - ',result)
                if result != 'Skip' :
                    dict_result_group[result].append(i)

        except Exception as e:
            print(e)
            continue
    
    print(dict_result_group)
    
    now = datetime.now()
    current_date = now.strftime("%y%m%d")
    current_hour = now.strftime("%H%M%S")
    
    for status, value in dict_result_group.items():
        #final_csv = ','.join(titles) +'\n'+'\n'.join(value)
        
        '''
        single_list_value, list_result = [], []
        
        for v in value:
            single_list_value.append(v.split(','))
            
        list_value = sorted(single_list_value, key=lambda x:(x[buy_sell_idx], x[ctp_report_type_idx]))
        print(list_value)
        
        for j in list_value:
            list_result = ','.join(j)
        final_csv = '\n'.join(list_value)
        '''
        full_path = folder_path + "\\" + status.upper() + "\\"
        try:
            os.makedirs(full_path)
        except:
            #print('Path too long')
            pass
        
        data_sell, data_buy = [], []
        for j in value :
            temp_j = j.split(',')
            temp_j[buy_sell_idx] = temp_j[buy_sell_idx][0].upper() 
            temp_j[time_idx] = temp_j[time_idx][:-3]
            
            print(temp_j[time_idx])
            if temp_j[buy_sell_idx].lower() == 'sell' or temp_j[buy_sell_idx].lower() == 's':
                data_sell.append(','.join(temp_j))
            else:
                data_buy.append(','.join(temp_j))
        
        all_data = {'SELL' : data_sell, 'BUY' : data_buy}
        
        for bs, data in all_data.items():
            final_csv = '\n'.join(data)
            f = open(full_path+"\\CTP_"+ current_date + "_" + current_hour + "_" + bs + ".csv", "w")
            f.write(final_csv)
            f.close()
    
    try:
        os.remove(complete_path)
    except Exception as e:
        print(e)
        pass
        
