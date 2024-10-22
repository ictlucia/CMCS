"""
DELETE REQUEST FROM TEXTOBJECT SCRIPT

DESCRIPTION:


      Input :
            dl_req_amb_id :  List of AMB Request IDs of Dataloader user requests (AMB channel:ADL_REQUEST_SND) sent to AMB. AMB request ID can
            be found in Dataloader ATS log window once a dataloader starts processing a user request.

            AMB request ID is enclosed within <> as shown below. Here 494447 is request ID.
        INFO [DataLoader] <Started : 494447> ['Instrument']: Uploading request for security ['IBM US Equity'] to Bloomberg

"""

import ael, datetime
import FDLLogger
logger = FDLLogger.FDLLogger(name='DataLoader')
user_provided_msg_id = [] # Enter AMB request ID here

text_object_name = 'DL_BBG_SFTP_Download_Process'  # TextObject name where Request details are stored

logger.DLOG("Started FDLDeleteRequestFromTextObject.py \n")

text_object = ael.TextObject.read("type='Instrument Extension' and name = '%s' " %text_object_name)
if text_object:
    try:
        text_object_data = eval(str(text_object.get_text()))
        logger.DLOG("Number of Requests found in TextObject : %s" %(len(text_object_data.keys())))
        logger.DLOG("User provided AMB Request IDs : %s \n\n" %(user_provided_msg_id))
        
        for time in text_object_data.keys():
            if text_object_data.get(time, None):
                msg_id_from_textobj = text_object_data.get(time, None).get('config_data').get('DL_AMB_REQUEST_ID')
                logger.DLOG("AMB Request ID from TextObject : %s" %(msg_id_from_textobj))
                if msg_id_from_textobj in user_provided_msg_id:
                    logger.DLOG("Deleting TextObject entry for AMB Request ID : %s \n" %(msg_id_from_textobj))
                    del text_object_data[time]
            else:
                logger.DLOG("Skipping TextObject request \n")

        
        
        text_object_clone = text_object.clone()
        text_object_clone.data = str(text_object_data)
        text_object_clone.commit()
    except Exception as e:
        logger.ELOG("Error while updating text object %s: . Error %s so deleting text object" %(text_object_name, str(e)))
        text_object.delete()
        logger.DLOG("Text object deleted")
        

logger.DLOG("FDLDeleteRequestFromTextObject.py Completed\n")



