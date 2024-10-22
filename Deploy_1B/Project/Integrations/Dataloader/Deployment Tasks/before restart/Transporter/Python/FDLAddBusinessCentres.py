"""-------------------------------------------------------------------

MODULE
    FDLAddBusinessCentres - Add business center to calendar script

DESCRIPTION
    Setup test script to add business centers to calendars

--------------------------------------------------------------------"""

import acm
import FLogger
logger = FLogger.FLogger('AddBusinessCenters')

name = "BusinessCenter"
def setAddInfo(name,object,value):
    try:
        ai=getattr(object.AdditionalInfo(),name)
        if not ai():
            ais = acm.FAdditionalInfoSpec[name]
            ai = acm.FAdditionalInfo()
            ai.Recaddr(object.Oid())
            ai.AddInf(ais)
            ai.FieldValue(value)
            ai.Commit()
        else:
            logger.warn("This information is already present in DB, hence not adding for: {}".format(object.Name()))
            object.Commit()
    except:
        logger.error("Please check if required Additional Info Spec is present in DB")

def setBusinessCentres():
    'Update Business  Centre value to the calendars'
    is_created = True
    bsDict = {
        'Abu Dhabi':'AEAD', 'Luanda':'AOLU', 'Buenos Aires':'ARBS', 'Vienna':'ATVI',
        'Sydney':'AUSY', 'Brussels':'BEBR', 'Manama':'BHMA', 'Brasilia':'BRBR',
        'Gaborone':'BWGA', 'Toronto':'CATO', 'Zurich':'CHZU', 'Santiago':'CLSA',
        'Beijing':'CNBE', 'Bogota':'COBO', 'Prague':'CZPR', 'Frankfurt':'DEFR',
        'Copenhagen':'DKCO', 'Cairo':'EGCA', 'Madrid':'ESMA', 'TARGET':'EUTA',
        'Helsinki':'FIHE', 'Paris':'FRPA', 'London':'GBLO', 'Athens':'GRAT',
        'Hong Kong':'HKHK', 'Budapest':'HUBU', 'Dublin':'IEDU', 'Tel Aviv':'ILTA',
        'Mumbai, India':'INMU', 'Reykjavik':'ISRE', 'Rome':'ITRO', 'Tokyo':'JPTO',
        'Nairobi':'KENA', 'Seoul':'KRSE', 'Kuwait City':'KWKC', 'Colombo, Sri Lanka':'LKCO',
        'Luxembourg':'LULU', 'Valletta':'MTVA', 'Mexico City':'MXMC', 'Kuala Lumpur':'MYKL',
        'Amsterdam':'NLAM', 'Oslo':'NOOS', 'New York Fed':'NYFD', 'Wellington':'NZWE',
        'Panama City':'PAPC', 'Lima':'PELI', 'Manila':'PHMA', 'Karachi, Pakistan':'PKKA',
        'Warsaw':'PLWA', 'Lisbon':'PTLI', 'Doha':'QADO', 'Bucarest, Romania':'ROBU',
        'Moscow':'RUMO', 'Riyadh':'SARI', 'Stockholm':'SEST', 'Singapore':'SGSI',
        'Bratislava':'SKBR', 'Bangkok':'THBA', 'Ankara':'TRAN', 'Taipei':'TWTA',
        'Dar es Salaam':'TZDA', 'Kampala':'UGKA', 'New York':'USNY', 'Caracas, Venezuela':'VECA',
        'Hanoi, Vietnam':'VNHA', 'Johannesburg':'ZAJO', 'Lusaka':'ZMLU', 'Dubai': 'AEDU', 'Istanbul': 'TRIS',
        'Jakarta':'IDJA', 'Sofia, Bulgaria':'BGSO', 'Dusseldorf':'DEGE', 'Montreal':'CAML', 'Auckland':'NZN6',
        'No Holidays' : 'NOHL'
        }
    for cal in acm.FCalendar.Select(''):
      calN = cal.Name()
      if not calN in list(bsDict.keys()):
        logger.warn('Business Center is not provided for calendar - {}'.format(calN))
      else:
        try:
            cal.BusinessCenter(bsDict[calN])
            cal.Commit()
            logger.info("Updated calendar {} with business center {}".format(calN, bsDict[calN]))
        except Exception as ex:
            logger.error("Error while adding business center {} to calendar {}: {}".format(bsDict[calN], calN, str(ex)))
            is_created = False
    return is_created

def addInfoSpecs():
    oldais = acm.FAdditionalInfoSpec["BusinessCentre"]
    if oldais:
        cloned_ais = oldais.Clone()
        cloned_ais.FieldName(name)
        oldais.Apply(cloned_ais)
        oldais.Commit()
        logger.info('Renamed Business Centre to Business Center')
    else:
        ais = acm.FAdditionalInfoSpec[name]
        if ais:
            logger.info('Already have',name)
        else:
            ais = acm.FAdditionalInfoSpec()
            ais.FieldName = name
            ais.DataTypeGroup(acm.FEnumeration['enum(B92DataGroup)'].Enumeration('Standard'))
            typ = acm.FEnumeration['enum(B92StandardType)'].Enumeration('String')
            ais.DataTypeType(typ)
            ais.Description = "Business Day Calendar"
            ais.RecType('Calendar')
            ais.Commit()


def ael_main(parameter):
    #addInfoSpecs()
    setBusinessCentres()
