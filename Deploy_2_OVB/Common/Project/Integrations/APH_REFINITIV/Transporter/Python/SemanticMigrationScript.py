"""
#######################################################################
#                                                                     #
# PRICE SEMANTIC MIGRATION SCRIPT                                     #
#                                                                     #
#    DESCRIPTION:                                                     #
#      This script migrates Price Semantics from semantic.dat or      #
#      semantic.ini file to price_semantic and price_semantic_row     #
#      tables in ADM.                                                 #
#      This scripts also changes price link mapping from choice list  #
#      and adds a reference to reference semantic from price_semantic #
#      table.                                                         #
#                                                                     #
#######################################################################
"""

import string
import acm
import FPriceSemantic
import FPriceLinkApplication
import FUxCore

"""
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++                                                                ++
++      SEMANTIC PARSING OPERATIONS                               ++
++                                                                ++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""
def ParseSemanticFile(semanticFile, providerType):

    for CurrentLine in semanticFile:
        if CurrentLine[0] != '-':
            if CurrentLine.find('#') != -1:
                if CurrentLine.find('<') == -1:
                    semanticName     = CurrentLine[CurrentLine.rfind('#')+1:].split(' ')[0].strip()
                    print('Migrating Semantic: ' + semanticName + ' from file to the database.')
                    priceSemantic = acm.FPriceSemantic.Select01('name="%s"' % semanticName, None)
                    if not priceSemantic:
                        try:
                            priceSemantic = acm.FPriceSemantic()
                            priceSemantic.Name(semanticName)
                            priceSemantic.ProviderType(providerType)
                            priceSemantic.Commit()
                        except Exception as e:
                            print(str(e) + ': Error migrating semantic: ' + priceSemantic.Name())
                            continue
                    else:
                         print('Semantic ' + priceSemantic.Name() + ' already exists. Trying to migrate mapping...')
                else:
                    return 0
            elif CurrentLine.find(',') != -1:
                spaceRemoved = CurrentLine.lstrip()
                if spaceRemoved.find(',') != -1:
                    AdmField = spaceRemoved[0:spaceRemoved.find(',')]
                    IdpField = spaceRemoved[len(AdmField):spaceRemoved.rfind(',')]
                    IdpField = (IdpField.lstrip(',')).lstrip()
                    priceSemantic = acm.FPriceSemantic.Select01('name="%s"' % semanticName, None)
                if priceSemantic:
                    try:
                        priceSemanticRow = acm.FPriceSemanticRow()
                        priceSemanticRow.AdmName(AdmField)
                        priceSemanticRow.IdpName(IdpField)
                        if CurrentLine.rfind('-') != -1:
                            priceSemanticRow.Comment(CurrentLine[CurrentLine.rfind('-')+1:])
                        priceSemanticRow.SemanticSeqNbr(priceSemantic.Oid())
                        priceSemanticRow.Commit()

                    except Exception as e:
                        print(str(e) + ': Error migrating semantic: ' + priceSemantic.Name() + ' and mapping: ' + priceSemanticRow.AdmName() + '-' + priceSemanticRow.IdpName())
                        continue
    return 1

"""
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++                                                                ++
++      SEMANTIC UPDATE OPERATIONS                                ++
++                                                                ++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""
def UpdateSemanticSeqNoToPLDs():
    priceLinkSuccessCnt = 0
    priceDistSuccessCnt = 0
    priceLinkFailCnt = 0
    priceDistFailCnt = 0
    priceLinkDisHasSem = 0
    invalidDistList = []
    distributorList = acm.FPriceDistributor.Select('')
    for distributor in distributorList:
        if distributor.Semantic():
            priceSemantic = acm.FPriceSemantic[distributor.Semantic().Name().strip()]
            if priceSemantic:
                try:
                    distributor.SemanticSeqNbr(priceSemantic)
                    distributor.Commit()
                    priceDistSuccessCnt = priceDistSuccessCnt+1
                except Exception as e:
                    print(str(e) + ': Error setting Semantic: ' + priceSemantic.Name() + ' for Distributor: ' + distributor.Name())
                    invalidDistList.append(distributor.Name())
            else:
                priceDistFailCnt = priceDistFailCnt+1
                invalidDistList.append(distributor.Name())
                print('Semantic ' + distributor.Semantic().Name() + ' was not found in SemanticTable for distributor: '+ distributor.Name())

    print('Semantics mapped in the the Price Distributors of selected distributor type.')
    print('Mapping the semantics for individual Price Links...')
    priceLinkList = acm.FPriceLinkDefinition.Select('')
    priceLinkCount = priceLinkList.Size()
    count = 0
    percent = 0
    for priceLink in priceLinkList:

        count = count+1
        if count % (priceLinkCount/10) == 0:
            percent = percent+10
            print(str(percent) + '% Completed')

        if priceLink.Semantic() and priceLink.PriceDistributor().Name() not in invalidDistList:
            priceSemantic = acm.FPriceSemantic[priceLink.Semantic().Name().strip()]
            if priceSemantic:
                try:
                    priceLink.SemanticSeqNbr(priceSemantic)
                    priceLink.Commit()
                    priceLinkSuccessCnt = priceLinkSuccessCnt +1
                except Exception as e:
                    print(str(e) + ': Error setting Semantic: ' + priceSemantic.Name() + 'for PriceLink: ' + priceLink.IdpCode() + ', in Distributor: ' + priceLink.PriceDistributor().Name())
            else:
                priceDist = priceLink.PriceDistributor()
                if not priceDist.SemanticSeqNbr():
                    print('Unable to set SemanticSeqNbr for Ticker: ' +  priceLink.IdpCode() + ' and semantic: ' + priceLink.Semantic().Name() + ' Distributor: ' + priceLink.PriceDistributor().Name())
                    priceLinkFailCnt = priceLinkFailCnt+1
                else:
                    priceLinkDisHasSem = priceLinkDisHasSem+1

    print('Distributors successfully processed: ' + str(priceDistSuccessCnt))
    print('Distributors ignored - distributor type mismatch: ' + str(invalidDistList))
    print('PriceLinks successfully processed: ' + str(priceLinkSuccessCnt))
    print('PriceLinks ignored - distributor type mismatch: ' + str(priceLinkCount-priceLinkSuccessCnt))
    print('PriceLinks Failed Count: ' + str(priceLinkFailCnt))
    if priceLinkFailCnt:
        return 0
    return 1

"""
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++                                                                ++
++      SCRIPT EXECUTION POINT                                    ++
++                                                                ++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""
def executeScript(parameter):

    print('--------------- SEMANTIC MIGRATION SCRIPT EXECUTION BEGINS ---------------\n')
    g_providerType = parameter['providerType']
    g_filePath     = parameter['path']

    if g_providerType == 'None':
        print('Invalid Distributor Type: None')

    else:
        result = 0
        print('Distributor Type set to: ' + str(g_providerType))
        filePath = open(g_filePath)
        if filePath:
            print('Semantic File from loaction:' + g_filePath)
            result = ParseSemanticFile(filePath, g_providerType)
            if result:
                print('Semantic File parsed successfully. Mapping the Semantics in the Price Distributors')
                if UpdateSemanticSeqNoToPLDs():
                    print('Semantic Migration completed successfully. Please check log for more details.')
                else:
                    print('Something went wrong during Semantic Migration. Please check logs for details.')
            else:
                print('No Semantic File Selected! Exiting!!')

    print('\n---------------- SEMANTIC MIGRATION SCRIPT EXECUTION ENDS ----------------')


"""
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++                                                                ++
++      GET DISTRIBUTOR (PROVIDER) TYPES                          ++
++                                                                ++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""
PermittedDistributorTypes = ["AMS", "Reuters", "Bloomberg", "MarketMap", "Open Price Feed", "Custom 1", "Custom 2", "Custom 3", "None"]
providerType = ''

def getDistibutorTypeFromDB():
    provider_type_list = []
    for provider in acm.FEnumeration['enum(PrincipalType)'].Enumerators().Sort():
        if provider in PermittedDistributorTypes:
            provider_type_list.append(provider)
    return provider_type_list

"""
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++                                                                ++
++      AEL VARIABLES                                             ++
++                                                                ++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""
ael_gui_parameters = {  'runButtonLabel'        : '&&Ok',
                        'InsertItemsShowExpired': True,
                        'hideExtraControls'     : False,
                        'closeWhenFinished'     : True,
                        'windowCaption'         : 'Select Semantic file and Provider Type for migration.'}
ael_variables = [
                ['providerType', 'Distributor Type', 'string', getDistibutorTypeFromDB(), 'Reuters', 1, 0, \
                            'Select a distributor type appropriate to the semantic file'],
                ['path', 'Complete File Path', 'string', "", 'C:\Program Files\Front\Front Arena\APH\APH_Reuters\APH\etc\ReutersSemantic_Template.dat', 1, 0, \
                            'Enter the complete path of the Semantic File to be migrated.']
                ]

"""
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++                                                                ++
++      AEL MAIN                                                  ++
++                                                                ++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""

parameter = dict()

parameter['providerType'] = 'Reuters'
parameter['path'] = 'ReutersSemantic.dat'

try:
    executeScript(parameter)
except Exception as e:
    print(e)

"""
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++                                                                ++
++      END OF SCRIPT                                             ++
++                                                                ++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""