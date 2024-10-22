import ael, acm

import csv
import os

filenames = []

def getFilePathSelection():
    """ Directory selector dialog """
    selection = acm.FFileSelection()
    selection.PickDirectory(True)
    selection.SelectedDirectory = r"C:"
    return selection
    
def FolderChanged(index, fieldValues):
    folder = fieldValues[index]
    filenames.clear()

    if folder:
        for filename in sorted(os.listdir(folder)):
            if filename.lower().endswith('.csv'):
                filenames.append(filename)

    return fieldValues



ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'ICT_ModifyPartyTypeByAEL'}
                    
ael_variables=[
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1, 'Folder from which CSV files should be imported', FolderChanged, 1],
['csv_files', 'CSV Files', 'string', filenames, None, 0, 1]
]


def ael_main(parameter):
    
    folder = str(parameter['file_path'])
    csv_file_list = list(parameter['csv_files'])
    
    for file_name in csv_file_list:
        file_path = os.path.join(folder, file_name)
        
        ignored_pty_list = []
        
    
        all = []
        header = 1
        csv_dict_reader = []
        with open(file_path, mode='r', newline='') as file:
            # Create a CSV reader object
            csv_reader = csv.reader(file)
            
            for _ in range(header):
                next(csv_reader)
            
            header = next(csv_reader)
            
            csv_dict_reader = csv.DictReader(file, fieldnames=header) 
            
            modified_pty_count = 0
            ignored_pty_count = 0
            
            for row in csv_dict_reader:
                party = ael.Party[row['PTYID']]
                if party is not None:
                    clone = party.clone()
                    try:
                        clone.type = row['TYPE']
                        clone.commit()
                        modified_pty_count = modified_pty_count + 1
                    except:
                        ignored_pty_list.append(row['PTYID'] + ',' + row['TYPE'] + ',#Update cannot be committed into DB\n')
                        ignored_pty_count = ignored_pty_count + 1
                else:
                    ignored_pty_list.append(row['PTYID'] + ',' + row['TYPE'] + ',#Party Not Found\n')
                    ignored_pty_count = ignored_pty_count + 1
                    
                    
            
            
            print('='*50)
            print(file_name, '-', 'Updated Party Type: ', modified_pty_count, 'Ignored Party: ', ignored_pty_count)
            print('='*50)
            
        if len(ignored_pty_list) > 0:
            file_content = 'PARTY,,/PARTY\nPTYID,TYPE,\n'
            for pty in ignored_pty_list:
                file_content = file_content + pty
            
            err_file_path = os.path.join(folder, 'Ignored_Parties_' + file_name)
            
            with open(err_file_path, mode='w') as err_file:
                err_file.write(file_content)
            
            print('='*50)
            print('Generate CSV File for Ignored Parties: ', err_file_path)
            print('='*50)
