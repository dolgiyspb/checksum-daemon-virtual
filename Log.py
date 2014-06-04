#  -*- coding: utf-8 -*-
__author__ = 'alex'
import psycopg2
import datetime

class EventTypesEnum:
    CHECKSUM_ERROR_FOUND = 0
    FILE_RESTORED_SUCCESS = 1

class Event(object):
    def __init__(self, type):
        self.type = type

class CheckSumErrorEvent(Event):
    def __init__(self, filePath):
        super(CheckSumErrorEvent, self).__init__(EventTypesEnum.CHECKSUM_ERROR_FOUND)
        self.filePath = filePath


class FileRestoredSuccessEvent(Event):
    def __init__(self, filePath):
        super(FileRestoredSuccessEvent, self).__init__(EventTypesEnum.FILE_RESTORED_SUCCESS)
        self.filePath = filePath



class Logger(object):
    user = None
    password = None
    dbName = None
    logger = None
    @staticmethod
    def set_credentials(user, password, dbname):
        Logger.user = user
        Logger.password = password
        Logger.dbName = dbname
    def __init__(self):
        if Logger.user == None or Logger.password == None:
            raise Exception("Set credentials first!")
        self.conn = psycopg2.connect(database=Logger.dbName, user=Logger.user, password=Logger.password)
    @staticmethod
    def getLogger():
        if Logger.logger == None:
            Logger.logger = Logger()
        return Logger.logger
    @staticmethod
    def onExit():
        if Logger.logger != None:
            Logger.logger.conn.commit()
            Logger.logger.conn.close()
    @staticmethod
    def log(text, success=True):
        logger = Logger.getLogger().logger
        logger.conn.cursor().execute("INSERT INTO events (event_date, event_note, event_status) VALUES (%s, %s, %s)", (datetime.datetime.now(), text, 0))
        logger.conn.commit()

def log(event):
    handlers = {
        EventTypesEnum.CHECKSUM_ERROR_FOUND : logChecksumError,
        EventTypesEnum.FILE_RESTORED_SUCCESS : logFileRestoredSuccess
    }
    handlers[event.type](event)

def logFileRestoredSuccess(e):
    message = u"Файл успешно восстановлен " + e.filePath
    Logger.log(message)
    print message

def logChecksumError(e):
    message = u"Обнаружно нарушение целостности файла " + e.filePath
    Logger.log(message)
    print message