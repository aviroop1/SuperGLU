from uuid import uuid4
from SuperGLU.Util.Serialization import Serializable
from SuperGLU.Core.MessagingGateway import BaseService
from SuperGLU.Core.Messaging import Message
from SuperGLU.Util.ErrorHandling import logInfo
from SuperGLU.Core.MessagingDB import KC_SCORE_VERB, SESSION_ID_CONTEXT_KEY, DATE_TIME_FORMAT, TASK_ID_CONTEXT_KEY, TASK_HINT_VERB, TASK_FEEDBACK_VERB, MASTERY_VERB, CLASS_ID_CONTEXT_KEY
from SuperGLU.Core.FIPA.SpeechActs import INFORM_ACT, REQUEST_ACT
from SuperGLU.Services.StudentModel.PersistentData import DBStudentAlias, DBStudentModel, DBStudent, DBSession, DBClasssAlias, DBClass
from SuperGLU.Services.StudentModel.StudentModelFactories import BasicStudentModelFactory
from datetime import datetime


"""
    This module contains the message handling code for building and modifying student models.  May also contain code for querying the student model.
"""

STUDENT_MODEL_SERVICE_NAME = "Student Model Service"


class StudentModelMessaging(BaseService):
    
    studentCache = {}
    sessionCache = {}
    classCache = {}
                
    def receiveMessage(self, msg):
        logInfo('{0} received message: {1}'.format(STUDENT_MODEL_SERVICE_NAME, self.messageToString(msg)), 1)
        
        if msg is not None:
            reply = self.routeMessage(msg)
        
        if reply is not None:
            logInfo('{0} is sending reply:{1}'.format(STUDENT_MODEL_SERVICE_NAME, self.messageToString(reply)), 1)
            self.sendMessage(reply)
        
    def routeMessage(self, msg):
        #depending on the content of the message react differently
        logInfo('Entering StudentModelMessaging.routeMessage', 5)
        
        result = None
        #Only considering 
        if msg.getSpeechAct() == INFORM_ACT:
        
            if msg.getVerb() == KC_SCORE_VERB:
                logInfo('{0} is processing a {1},{2} message'.format(STUDENT_MODEL_SERVICE_NAME, KC_SCORE_VERB, INFORM_ACT), 4)
                session = self.retrieveSessionFromCacheOrDB(msg.getContextValue(SESSION_ID_CONTEXT_KEY))
                clazz = self.retrieveClassFromCacheOrDB(msg.getContextValue(CLASS_ID_CONTEXT_KEY), msg)
        
                if session is None:
                    session = self.createSession(msg)
            
                self.updateSession(msg, session)
                
                student = self.retrieveStudentFromCacheOrDB(msg.getActor(), msg)
                student.addSession(session)
                session.addStudent(student)
                
                if clazz is not None:
                    if student.studentId not in clazz.students:
                        clazz.addStudent(student)
                    if msg.getObject() not in clazz.kcs:
                        clazz.kcs.append(msg.getObject)
                    clazz.save()
                
                if student.studentId not in session.performance.keys():
                    session.performance[student.studentId] = {}
                
                session.performance[student.studentId][msg.getObject()] = msg.getResult()
                
                session.save()    
                logInfo('{0} finished processing {1},{2}'.format(STUDENT_MODEL_SERVICE_NAME, KC_SCORE_VERB, INFORM_ACT), 4)
            elif msg.getVerb() == TASK_HINT_VERB:
                logInfo('{0} is processing a {1},{2} message'.format(STUDENT_MODEL_SERVICE_NAME, TASK_HINT_VERB, INFORM_ACT), 4)
                session = self.retrieveSessionFromCacheOrDB(msg.getContextValue(SESSION_ID_CONTEXT_KEY))
        
                if session is None:
                    session = self.createSession(msg)
            
                self.updateSession(msg, session)
                
                session.hints.append(msg.getResult())
                session.save()
                logInfo('{0} finished processing {1},{2}'.format(STUDENT_MODEL_SERVICE_NAME, TASK_HINT_VERB, INFORM_ACT), 4)
            elif msg.getVerb() == TASK_FEEDBACK_VERB:
                logInfo('{0} is processing a {1},{2} message'.format(STUDENT_MODEL_SERVICE_NAME, TASK_FEEDBACK_VERB, INFORM_ACT), 4)
                session = self.retrieveSessionFromCacheOrDB(msg.getContextValue(SESSION_ID_CONTEXT_KEY))
        
                if session is None:
                    session = self.createSession(msg)
            
                self.updateSession(msg, session)
                session.feedback.append(msg.getResult())
                session.save()
                logInfo('{0} finished processing {1}, {2}'.format(STUDENT_MODEL_SERVICE_NAME, TASK_FEEDBACK_VERB, INFORM_ACT), 4)
        elif msg.getSpeechAct() == REQUEST_ACT:
            #I'm going to assume the that the student id is the object, but that may not be the case
            if msg.getVerb() == MASTERY_VERB:
                logInfo('{0} is processing a {1}, {2} message'.format(STUDENT_MODEL_SERVICE_NAME, MASTERY_VERB, REQUEST_ACT), 4)
                newStudentModel = self.createNewStudentModel(msg.getObject())
                result = Message(actor=STUDENT_MODEL_SERVICE_NAME, verb=MASTERY_VERB, object=newStudentModel.studentId, result=newStudentModel.kcMastery, context=msg.getContext())
                logInfo('{0} finished processing {1},{2}'.format(STUDENT_MODEL_SERVICE_NAME, MASTERY_VERB, REQUEST_ACT), 4)
        
        return result
            
            
    
    def createStudent(self, studentId, msg):
        logInfo('{0} could not find student with id: {1} in database.  Creating new student'.format(STUDENT_MODEL_SERVICE_NAME, studentId), 3)
        studentUUID = str(uuid4())
        student = DBStudent(id=studentUUID, sessionIds=[], oAuthIds={}, studentModelIds=[], kcGoals={})
        student.save()
        self.studentCache[studentId] = student
        newStudentAlias = DBStudentAlias(trueId=studentUUID, alias=studentId)
        newStudentAlias.save()
        return student
    
    def createSession(self, msg):
        logInfo("Could not find session with id:{0}.  Creating new Session".format(msg.getContextValue(SESSION_ID_CONTEXT_KEY)), 3)
        session = DBSession(sessionId = msg.getContextValue(SESSION_ID_CONTEXT_KEY))
        session.messageIds = []
        session.hints = []
        session.feedback = []
        session.performance = {}
        session.startTime = datetime.utcnow().strftime(DATE_TIME_FORMAT)
        session.duration = 0
        session.id = msg.getContextValue(SESSION_ID_CONTEXT_KEY)
        session.task = msg.getContextValue(TASK_ID_CONTEXT_KEY)
        session.save()
        self.sessionCache[session.id] = session
        return session
    
    def createClass(self, classId, msg):
        logInfo('{0} could not find class with id: {1} in database.  Creating new class'.format(STUDENT_MODEL_SERVICE_NAME, classId), 3)
        classUUID = str(uuid4())
        clazz = DBClass(id=classUUID, ids=[classId], name='', roles={}, students=[], kcs=[])
        clazz.save()
        self.classCache[classId] = clazz
        newClassAlias = DBClasssAlias(trueId=classUUID, alias=classId)
        newClassAlias.save()
        return clazz    
    
    
    def createNewStudentModel(self, studentId):
        #DBStudentAlias List
        studentsWithId = DBStudentAlias.find_by_index("AliasIndex", studentId)
        
        for studentAlias in studentsWithId:
            student = DBStudent.find_one(studentAlias.trueId)
            
            if student is None:
                logInfo('failed to find student with Id: {0} and alias {1}'.format(studentAlias.trueId, studentAlias.alias), 1)
            else:
                BasicStudentModelFactory().buildStudentModel(student)
    
    
    
    def updateSession(self, msg, session):
        session.messageIds.append(msg.getId())
        startTime = datetime.strptime(session.startTime, DATE_TIME_FORMAT)
        msgTimestamp = datetime.strptime(msg.getTimestamp(), DATE_TIME_FORMAT)
        delta = msgTimestamp - startTime
        #only update if the duration increases
        if delta.seconds > session.duration:
            session.duration = delta.seconds
        
    def retrieveSessionFromCacheOrDB(self, sessionId, useCache=True):
        if sessionId is None:
            return None
        
        if sessionId in self.sessionCache.keys() and useCache:
            logInfo('{0} found cached session object with id:{1}'.format(STUDENT_MODEL_SERVICE_NAME, sessionId), 4)
            return self.sessionCache[sessionId]
        
        logInfo('{0} could not find cached session object with id: {1}.  Falling back to database.'.format(STUDENT_MODEL_SERVICE_NAME, sessionId), 3)
        session = DBSession.find_one(sessionId)
        
        if session is not None:
            logInfo('{0} found session {1}.  Storing in Cache'.format(STUDENT_MODEL_SERVICE_NAME, session.sessionId), 5)
            self.sessionCache[session.id] = session 
                    
        return session
                
    def retrieveStudentFromCacheOrDB(self, studentId, msg, useCache=True):
        logInfo("Entering retrieveStudentFromCacheOrDB", 5)
        student = self.studentCache.get(studentId)
        if student is not None and useCache:
            logInfo('{0} found student object with id:{1}'.format(STUDENT_MODEL_SERVICE_NAME, studentId), 4)
            return student
        else:
            logInfo('{0} could not find cached student object with id: {1}.  Falling back to database.'.format(STUDENT_MODEL_SERVICE_NAME, studentId), 3)
            studentAliasList = DBStudentAlias.find_by_index("AliasIndex", studentId)
            
            if len(studentAliasList) > 0:
                #there should only be one object returned, should put it a log statement if that isn't correct.
                for studentAlias in studentAliasList:
                    student = studentAlias.getStudent()
                    
            if student is None:
                student = self.createStudent(studentId, msg)
            #Cache the result so we don't need to worry about looking it up again.
            self.studentCache[studentId] = student
            return student
        
        
    def retrieveClassFromCacheOrDB(self, classId, msg, useCache=True):
        logInfo("Entering retrieveClassFromCacheOrDB with arguments {0}".format(classId), 5)
        if classId is None or classId == '':
            return None
        clazz = self.studentCache.get(classId)
        if clazz is not None and useCache:
            logInfo('{0} found classroom object with id:{1}'.format(STUDENT_MODEL_SERVICE_NAME, clazz), 4)
            return clazz
        else:
            logInfo('{0} could not find cached classroom object with id: {1}.  Falling back to database.'.format(STUDENT_MODEL_SERVICE_NAME, classId), 3)
            classAliasList = DBClasssAlias.find_by_index("AliasIndex", classId)
            if len(classAliasList) > 0:
                #there should only be one object returned, should put it a log statement if that isn't correct.
                for classAlias in classAliasList:
                    clazz = classAlias.getStudent()
                    
            if clazz is None:
                clazz = self.createClass(classId, msg)
            #Cache the result so we don't need to worry about looking it up again.
            self.classCache[classId] = clazz
            return clazz  