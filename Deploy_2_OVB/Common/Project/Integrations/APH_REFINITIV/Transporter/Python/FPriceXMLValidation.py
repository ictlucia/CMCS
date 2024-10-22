import ael, acm

class validationStatus:
    FAILURE    = 0
    SUCCESS    = 1
    INCOMPLETE = 2
	
def ValidateXMLData(xml_data):
    try:

        try:
            import xml.etree.cElementTree as ET
        except ImportError:
            import xml.etree.ElementTree as ET

        validStatus = validationStatus.SUCCESS
        xml_data = xml_data.strip()
    
        if(xml_data == ""):
            return validStatus
            
        element = ET.fromstring(xml_data)
        
        if(ET.iselement(element) == False):
            validStatus = validationStatus.FAILURE

        return validStatus

    except Exception as e:
        errmsg = "XML data parsing error %s"  % str(e)
        print(errmsg)
        ael.log(errmsg)
        validStatus = validationStatus.FAILURE
        return validStatus
