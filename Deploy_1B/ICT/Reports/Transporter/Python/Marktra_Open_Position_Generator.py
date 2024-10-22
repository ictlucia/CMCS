import acm,ael,csv
from datetime import datetime
from Report_Python import get_cross_rate
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
date = acm.Time.DateToday()


ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'Open Position Generator'}
                    
#settings.FILE_EXTENSIONS
ael_variables=[
['report_name','Report Name','string', None, 'Open Position Generator', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1]
]


def get_data(currpair,rawdata):
    row_name = []
    egan = ['EUR','GBP','AUD','NZD']

    for each_curr_pair_usd in currpair:
        curr1 = each_curr_pair_usd.split('/')[0]
        curr2 = each_curr_pair_usd.split('/')[1]
        if curr1 == 'USD':
            main_curr = curr2
        else:
            main_curr = curr1
        
        net_amount = 0
        
        
        for each_trade in rawdata.Query().Select():
            trade_curr1 = each_trade.Instrument().Name()
            trade_curr2 = each_trade.Currency().Name()
            quantity = each_trade.Quantity()
            premium = each_trade.Premium()
            
            if trade_curr1 in egan and trade_curr2 in egan:
                if main_curr == trade_curr1:
                    net_amount += quantity
                    
                elif main_curr == trade_curr2:
                    net_amount += premium
                
                else:
                    net_amount += 0
            
            elif trade_curr1 in egan and trade_curr2 not in egan:
                if quantity < 0:
                
                    if main_curr == trade_curr1:
                        net_amount += abs(quantity)*-1
                        
                    elif main_curr == trade_curr2:
                        net_amount += abs(get_cross_rate(trade_curr2,date)*premium)*-1
                        
                elif quantity > 0:
                    
                    if main_curr == trade_curr1:
                        net_amount += abs(quantity)
                    
                    elif main_curr == trade_curr2:
                        net_amount += abs(get_cross_rate(trade_curr2,date)*premium)
                    
            
            elif trade_curr1 not in egan and trade_curr2 not in egan:
                if quantity < 0:
                    if main_curr == trade_curr1:
                        net_amount += abs(get_cross_rate(trade_curr1,date)*quantity)
                    elif main_curr == trade_curr2:
                        net_amount +=abs(get_cross_rate(trade_curr2,date)*premium)*-1
                        
                elif quantity > 0:
                    if main_curr == trade_curr1:
                        net_amount += abs(get_cross_rate(trade_curr1,date)*quantity)*-1
                    elif main_curr == trade_curr2:
                        net_amount += abs(get_cross_rate(trade_curr2,date)*premium)
                
            
        row_name.append([each_curr_pair_usd,round(net_amount,2)])
        
    return row_name

def ael_main(parameter):
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = ".csv"
    
    

    currencypair = ['AUD/USD', 'EUR/USD', 'GBP/USD','USD/JPY','USD/CHF','NZD/USD','USD/IDR']
    currencypair2 = ['USD/SGD', 'USD/CAD', 'USD/HKD', 'USD/SAR', 'USD/MYR', 'USD/THB', 'USD/CNY', 'USD/NOK', 'USD/SEK', 'USD/DKK']
    alltime_query = acm.FStoredASQLQuery['Marktra_Open_Position_1']
    
    
    open_pos1 = get_data(currencypair,alltime_query)
    open_pos2 = get_data(currencypair2,alltime_query)
    
    open_pos = open_pos1+open_pos2
    
    with open(file_path + "/openpos.csv",'w',newline='') as csvfile:
        item = csv.writer(csvfile,delimiter=",")
        for each_row in open_pos:
            item.writerow(each_row)
    
