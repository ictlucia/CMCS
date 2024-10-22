import acm, ael

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'BO22 - Mark to Market Nasabah (adhoc)'}

ael_variables=[
['cptyName','Counterparty FullName','string', [x.Fullname() for x in acm.FParty.Select("type = 'client'")], None, 1, 1, 'Please Choose 1 Counterparty'],
]

def ael_main(parameter):
    cptyFullName = str(parameter['cptyName'][0])
    
    sqlUsed = acm.FSQL['BO22 - Mark to Market Nasabah (adhoc) - Trade Filter']
    query = sqlUsed.Text().replace("{{FULLNAME}}", cptyFullName)
    
    sqlUsed.Text(query)
    sqlUsed.Commit()
    
    params = acm.FAelTask["BO22 - Mark to Market Nasabah (adhoc).xls"].Parameters() 
    
    emailCpty = acm.FParty.Select(f"fullname = '{cptyFullName}'")[0].Email()
    subjectEmail = "Mark to Market Nasabah (adhoc)  - <Date>"
    bodyEmail = "Dear Sir / Madam, <br><br>Please find enclosed report document. <br><br>Treasury Control and Reporting. <br>Cash and Trade Operation Group<br> email address : tcr@bankmandiri.co.id"
    ccEmail = "rhamdan.syahrul@inticorp.tech"
    
    params.AtPut("param", f"{emailCpty}\ {subjectEmail}\ {bodyEmail}\ {ccEmail}")
    acm.FAelTask["BO22 - Mark to Market Nasabah (adhoc).xls"].Parameters(params)
    acm.FAelTask["BO22 - Mark to Market Nasabah (adhoc).xls"].Commit()
    
    acm.FAelTask["BO22 - Mark to Market Nasabah (adhoc).xls"].Execute()
    
    params = acm.FAelTask["BO22 - Mark to Market Nasabah (adhoc).xls"].Parameters() 
    params.AtPut("param", "")
    acm.FAelTask["BO22 - Mark to Market Nasabah (adhoc).xls"].Parameters(params)
    acm.FAelTask["BO22 - Mark to Market Nasabah (adhoc).xls"].Commit()
    
    query = sqlUsed.Text().replace(cptyFullName, "{{FULLNAME}}")
    sqlUsed.Text(query)
    sqlUsed.Commit()
