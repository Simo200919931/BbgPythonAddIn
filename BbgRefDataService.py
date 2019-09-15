import blpapi
from BbgSession import BbgSession
import pandas as pd
import numpy as np
import BbgLogger

SECURITY_DATA = blpapi.Name("securityData")
SECURITY = blpapi.Name("security")
FIELD_DATA = blpapi.Name("fieldData")
FIELD_EXCEPTIONS = blpapi.Name("fieldExceptions")
FIELD_ID = blpapi.Name("fieldId")
ERROR_INFO = blpapi.Name("errorInfo")

logger = BbgLogger.logger

class BbgRefDataService(BbgSession):

    def __init__(self):
        BbgSession.__init__(self)
        self.startSession()
        self.service = self.openService(serviceUrl = "//blp/refdata")
    
    def createRequest(self):
        raise NotImplementedError("Subclass must implement this abstract method")
    
    def parseResponse(self, cid):
        try:
            while(True):
                ev = self.session.nextEvent(500)

                for msg in ev:
                    if cid in msg.correlationIds() and ev.eventType() in [blpapi.Event.RESPONSE, blpapi.Event.PARTIAL_RESPONSE]:
                        logger.info(msg)
                        yield(self.parseResponseMsg(msg))
                    
                if ev.eventType() == blpapi.Event.RESPONSE:
                    break
        finally:
            # Stop the session
            self.closeSession()
    
    def parseResponseMsg(self, msg):
        return {
            "messageType" : "{}".format(msg.messageType()),
            "corrIDs" : ["{}".format(corrID) for corrID in msg.correlationIds()],
            "topicName" : "{}".format(msg.topicName()),
            "content" : self.parseElementData(msg.asElement())
        }
    
    def parseElementData(self, element):
        if element.datatype() == blpapi.DataType.CHOICE:
            logger.info("Parsing CHOICE element {}".format(element.name()))
            return {str(element.name()): self.parseElementData(element.getChoice())}
        elif element.isArray():
            logger.info("Parsing ARRAY element {}".format(element.name()))
            return [self.parseElementData(val) for val in element.values()]
        elif element.datatype() == blpapi.DataType.SEQUENCE:
            logger.info("Parsing SEQUENCE element {}".format(element.name()))
            return {str(element.name()): {str(subElement.name()): self.parseElementData(subElement) for subElement in element.elements()}}
        elif element.isNull():
            logger.info("Parsing NULL element {}".format(element.name()))
            return None
        else:
            logger.info("Parsing VALUE element {}".format(element.name()))
            try:
                returnValue = element.getValue()
            except:
                returnValue = None
            finally:
                return returnValue
        
 # partial lookup table for events used from blpapi.Event
eDict = {
    blpapi.Event.SESSION_STATUS: 'SESSION_STATUS',
    blpapi.Event.RESPONSE: 'RESPONSE',
    blpapi.Event.PARTIAL_RESPONSE: 'PARTIAL_RESPONSE',
    blpapi.Event.SERVICE_STATUS: 'SERVICE_STATUS',
    blpapi.Event.TIMEOUT: 'TIMEOUT',
    blpapi.Event.REQUEST: 'REQUEST'
}       
    

    


#test = BbgRefData()
#test.dataPoint(securities = ["IBM US Equity", "MSFT US Equity"], fields = ["PX_LAST", "DS002", "EQY_WEIGHTED_AVG_PX"])
