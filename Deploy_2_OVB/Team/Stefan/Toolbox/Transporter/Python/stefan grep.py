import acm
import os
import re
import pathlib


def PickInputFile():
    sel   = acm.FFileSelection()
    sel.PickDirectory(True)
    
    return sel


def SearchFile(path, keyword, baseFolder, caseSensitive, silent):
    res = False
    
    try:
        with open(path) as file:
            keywordLower = keyword.lower()
            
            for nbr, line in enumerate(file.readlines()):
                shortPath = os.path.relpath(path, baseFolder)
                match = keyword in line if caseSensitive else keywordLower in line.lower()
                
                if match:
                    stripped = line.strip()
                    pattern = f'................{keyword}................'
                    result = re.search(pattern, stripped, re.IGNORECASE)
                    print(f'{shortPath} {nbr}: {result.group(0)}')
                    res = True
    except Exception as e:
        if not silent:
            print(f'Failed to process {path}: {e}')
    
    return res
        

def Search(folder, keyword, caseSensitive, silent):
    print('-- Prime Grep --')
    print(f'Searching for {keyword}')
    
    count = 0
    
    for path, subfolder, filenames in os.walk(folder):
        for filename in filenames:
            if pathlib.Path(filename).suffix.lower() not in ['.pyc', '.pyd', '.dll', '.exe', '.png', '.ttf']:
                filePath = os.path.join(path, filename)
                matching = SearchFile(filePath, keyword, folder, caseSensitive, silent)
                
                if matching:
                    count += 1

    print(f'Found {count} matching files')


ael_variables = [
    ['folder', 'Start folder', PickInputFile(), None, PickInputFile(), 0, 1],
    ['keyword', 'Keyword', 'string', None, '', 0, 0],
    ['case_sensitive', 'Case Sensitive', 'bool', [0, 1], 1, 0, 0],
    ['silent', 'Silent on errors', 'bool', [0, 1], 1, 0, 0],
]


def ael_main(params):
    folder        = params['folder'].SelectedDirectory().AsString()
    keyword       = params['keyword']
    caseSensitive = params['case_sensitive']
    silent        = params['silent']
    
    Search(folder, keyword, caseSensitive, silent)
