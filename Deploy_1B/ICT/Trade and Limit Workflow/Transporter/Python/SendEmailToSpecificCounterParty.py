import os
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import FParameterUtils
from ICTCustomFEmailTransfer import ICTCustomFEmailTransfer

def SendingEmailProcess(folderPath, FileName, EmailParameter):
    subject, body, cc = EmailParameter
    
    
    SMTPParameters = FParameterUtils.GetFParameters(acm.GetDefaultContext(), 'CustomReportSMTPParameters')
    hostname = str(SMTPParameters.At('SMTPServer'))
    port = int(SMTPParameters.At('SMTPPort').Text())
    username = SMTPParameters.At('EmailUserName').Text()
    password = SMTPParameters.At('SMTPPassword').Text()
    tls_mode = bool(SMTPParameters.At('SecureSMTPConnection').Text())
    
    # Setup SMTPServer Object
    SMTPServer = ICTCustomFEmailTransfer.SMTPServer(hostname=hostname, port=port, username=username, password=password, tls_mode=tls_mode)
    sender = SMTPParameters.At('EmailSender').Text()
    
    pdfPath = os.path.join(str(folderPath), str(FileName)) + ".pdf"
    generated_reports = [pdfPath if os.path.exists(pdfPath) else pdfPath.replace(".pdf", ".fo")]
    
    try :
        partyEmail = acm.FParty[str(FileName)].Email()
        print(partyEmail)
    except :
        partyEmail = None


    MessageObject = ICTCustomFEmailTransfer.Message(partyEmail, "testSendEmailTMPG", sender, body, cc, generated_reports)
    EmailTransfer = ICTCustomFEmailTransfer(SMTPServer, MessageObject)
    
    try:
        EmailTransfer.Send()
        try :
            print("Email transfer successful for", str(partyEmail), cc)
        except :
            print("Email transfer successful Sent")
    except Exception as e:
        print("Email Transfer failed:", e)
    

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'Send Email To Specific CounterParty'}

ael_variables=[
['FolderPath', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
]

def ael_main(parameter):
    FolderPath = str(parameter['FolderPath'])
    
    subject = "Test Email TMPG"
    body = "Test Email TMPG"
    cc = ["rhamdan.syahrul@inticorp.tech", "amalia.husna@inticorp.tech"]
    emailParameter = [subject, body, cc]
    
    counterPartyIdList = [f.split(".")[0] for f in os.listdir(FolderPath) if os.path.isfile(os.path.join(FolderPath, f))]
    
    for counterPartyId in counterPartyIdList:    
        SendingEmailProcess(FolderPath, counterPartyId, emailParameter)
    
    
    
    
