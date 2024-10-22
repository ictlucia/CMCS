import acm, ael

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'BO58 - TMPG Claim Invoice'}

ael_variables=[
['cptyName','Counterparty FullName','string', [x.Fullname() for x in acm.FParty.Select("type = 'client'")], None, 1, 1, 'Please Choose 1 Counterparty'],
]

def editQueryCounterParty(cptyFullName):
    queryFolderOld = acm.FStoredASQLQuery["BO58 - TMPG Claim Invoice"].Query()
    queryFolderOld.AsqlNodes()[2].AsqlNodes()[0].AsqlValue(cptyFullName)

    queryFolder = acm.FStoredASQLQuery["BO58 - TMPG Claim Invoice"]
    queryFolder.Query(queryFolderOld)
    queryFolder.Commit()

def ael_main(parameter):
    cptyFullName = str(parameter['cptyName'][0])
    
    editQueryCounterParty(cptyFullName)
    acm.FAelTask["BO58 - TMPG Claim Invoice"].Execute()
    editQueryCounterParty("")
