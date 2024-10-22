import acm
import ael
import requests
import json
import ParametersReader
import SoaCommonDef
import os
import APIRequestResponseMonitoring as Mo

SoaParams  = ParametersReader.get_params('SoaParams')

def generatePayloadData(currencyCode):
    """-----------------------------------------------------------------------------------------
    This function generate payload of request message that will be merge into the Main request message by using 
    generateMainRequest function
    :param currencyCode: string of currencyCode
    :return dict
    -----------------------------------------------------------------------------------------"""
    channelId = SoaParams["CHANNEL_ID"]
    dataPayload = dict({"channelId":channelId, "currencyCode":currencyCode})
    
    return dataPayload
    
def generateMainRequest(currencyCode):
    """-----------------------------------------------------------------------------------------
    This function generate main request body of the respective API/service which contains of soaHeader, property, payload. 
    :param currencyCode: string of currencyCode
    :return json
    -----------------------------------------------------------------------------------------"""
    dataSoaHeader = SoaCommonDef.generateSoaHeader("JSON", SoaParams["BOOKRATE_INQ_SUBTYPE"], "NTCS", "OMNI")
    property = SoaCommonDef.generatePropertyForMessageHeader(SoaParams["BOOKRATE_INQ_TRANCODE"])
    dictProperty = dict({"property":property})
    dataPayload= generatePayloadData(currencyCode)
    
    data = dict({"soaHeader":dataSoaHeader, "messageHeader":dictProperty, "payload":dataPayload})
    dataRequest = dict({"bookRateInquiryRequest":data})
    
    jsonDataRequest = json.dumps(dataRequest)
    return jsonDataRequest
    
def getBookRate(currencyCode):
    #print('start getBookRate')
    try:
        apiBaseUrl = SoaParams["API_BASE_URL"]
        bookRateInquiryURL = SoaParams["BOOKRATE_INQ_URL"]
        url = apiBaseUrl+bookRateInquiryURL
        #print('url:', url)
        httpHeaderReq = SoaCommonDef.genHttpHeader()
        httpBodyReq = generateMainRequest(currencyCode)
        #print('httpHeaderReq: ', httpHeaderReq)
        #print('httpBodyReq: ', httpBodyReq)
        #print('start call api')
        response = Mo.NTCSApiMonitoring(SoaParams["BOOKRATE_INQ_SUBTYPE"], url, httpHeaderReq, httpBodyReq, None, "POST")

        #print('response: ', response)
        if response.status_code == 200:
            jsonResp = response.json()
            bookRateInquiryResponse = jsonResp["bookRateInquiryResponse"]
            payloadResponse = bookRateInquiryResponse["payload"]
            responseCode = payloadResponse["responseCode"]
            responseMessage = payloadResponse["responseMessage"]
            
            if responseMessage == "OK":
                data = payloadResponse["data"]
                bookRateList = data["bookRateList"]
                #print('bookRateList: ', bookRateList)
                return bookRateList
            else:
                return {"error":responseMessage}
        else:
            return {"error":response.status_code}
    except Exception as e:
        print(e)
        return {"error":e}
