#!/usr/bin/python
#  -*- coding: utf-8 -*-


__author__ = 'alex'



import hashlib
import argparse
import imp
import os
import time
import shutil
import Log
import signal


class FileErrorsEnum:
    NO_ERROR = 0
    DOES_NOT_EXIST = 1
    CHECKSUM_ERROR = 2

class FileContentAcc:
    def __init__(self):
        self.acc = ""
    def append(self, str):
        self.acc += str

class Constants:
    BACKUP_PATH = None

def importCheckSumListFromFile(path):
    path, name = os.path.split(path)
    name = name.split(".")[0]
    fp, pathname, description = imp.find_module(name, [path])
    return imp.load_module(name, fp, pathname, description).list


def checkFile(fileDict, acc):
    if os.path.isfile(fileDict["path"]):
        with open(fileDict["path"], "r") as file:
            return { "path": fileDict["path"], "error": getError(file, fileDict, acc)}
    else:
        return FileErrorsEnum.DOES_NOT_EXIST

def getError(file, fileDict, acc):
    content = file.read()
    checksum = hashlib.md5(content).hexdigest()
    acc.append(content)
    return FileErrorsEnum.NO_ERROR if fileDict["checksum"] == checksum else FileErrorsEnum.CHECKSUM_ERROR

def checkFileList(fileList):
    acc = FileContentAcc()
    return (map(lambda f: checkFile(f, acc), fileList), hashlib.md5(acc.acc).hexdigest())

def restoreFromBackup(pathToFile, backupPath):
    fullPath = os.path.normpath(backupPath)+"/"+os.path.normpath(pathToFile)
    shutil.copy(fullPath, pathToFile)
    Log.log(Log.FileRestoredSuccessEvent(pathToFile))

def processCheckSumError(file):
    Log.log(Log.CheckSumErrorEvent(file["path"]))
    restoreFromBackup(file["path"], Constants.BACKUP_PATH)

def processErrorFile(file):
    handlers = {
        FileErrorsEnum.CHECKSUM_ERROR : processCheckSumError,
        FileErrorsEnum.DOES_NOT_EXIST : processCheckSumError
    }
    handlers[file["error"]](file)

def daemonLoop(checksumsList, backupPath):
    while True:
        Constants.BACKUP_PATH = backupPath
        filesList, checksum = checkFileList(checksumsList)
        errorFiles = filter(lambda f: f["error"] != FileErrorsEnum.NO_ERROR, filesList)
        for file in errorFiles:
            processErrorFile(file)
        time.sleep(10)

def main():
    parser = argparse.ArgumentParser(
        description=u'После запуск контролирует целостность файлов из списка, заданного в файле')
    parser.add_argument('-p', '--path', dest='checkSumFile', required=True, action='store',
                        help=u'Путь к файлу, который содержит список файлов с контрольными суммами')
    parser.add_argument('-b', '--bpath', dest='backupPath', required=True, action='store',
                        help=u'Путь, относительно которого были сохранены резервные копии файлов')
    parser.add_argument('-u', '--username', dest='username', required=True, action='store',
                        help=u'Имя пользователя для базы данных')
    parser.add_argument('--password', dest='password', required=True, action='store',
                        help=u'Пароль для базы данных')
    parser.add_argument('--dbname', dest='dbname', required=True, action='store',
                        help=u'Пароль для базы данных')
    args = parser.parse_args()
    Log.Logger.set_credentials(args.username, args.password, args.dbname)
    config = importCheckSumListFromFile(args.checkSumFile)
    registerSignalHandlers()
    try:
        daemonLoop(config, args.backupPath)
    except:
        onExit()

def registerSignalHandlers():
    signal.signal(signal.SIGTERM, onSIGTERM)
    signal.signal(signal.SIGINT, onSIGTERM)

def onExit():
    Log.Logger.onExit()
    print "exit"

def onSIGTERM(signum, frame):
    onExit()
if __name__=="__main__":
    main()

