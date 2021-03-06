'''
Created on May 31, 2018
This service will forward logging messages to LearnLocker as well as log them to a file.
@author: auerbach, Alicia Tsai
'''
from SuperGLU.Core.MessagingGateway import BaseService
from SuperGLU.Services.LoggingService.Constants import XAPI_LOG_VERB
import requests
import uuid
import json
import statement


class LearnLockerConnection(BaseService):

    def __init__(self, gateway, url, key):
        super(LearnLockerConnection, self).__init__(gateway=gateway)
        self._url = url
        self._key = key
        self.logFile = open(r"log.txt", 'w')
        self.errorLog = open(r"errorLog.txt", "w")

    def receiveMessage(self, msg):
        super(LearnLockerConnection, self).receiveMessage(msg)

        if msg.getVerb() == XAPI_LOG_VERB:
            statementAsJson = msg.getResult()
            headerDict = {'Authorization' : self._key,
                          'X-Experience-API-Version': '1.0.3',
                          'Content-Type' : 'application/json'
                          }
            
            # --- quick fix for invalid xAPI statement to avoid bad request ----- #
            # these should be fixed in xAPI_Learn_Logger
            statement = json.loads(statementAsJson)
            #statement['context']['extensions'] = {}
            #statement['object']['id'] = "http://example.com/activities/solo-hang-gliding"
            statement['actor'].pop('openid', None)
            # ------------------------------------------------------
            response = requests.put(url=self._url + '/data/xAPI/statements?statementId=' + str(uuid.uuid4()), data=json.dumps(statement), headers=headerDict)

            # log bad request message into errorLog file
            if str(response) == "<Response [400]>":
                print('Warning: ', str(response), response.text)
                self.errorLog.write(response.text)
                self.errorLog.write("\n")

            # write xAPI statement to log file
            self.logFile.write(statementAsJson)
            self.logFile.write("\n")
