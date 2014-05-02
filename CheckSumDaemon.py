#!/usr/bin/python
#  -*- coding: utf-8 -*-


__author__ = 'alex'



import hashlib
import argparse
import imp
import os
import time

class FileErrorsEnum:
    NO_ERROR = 0
    DOES_NOT_EXIST = 1
    CHECKSUM_ERROR = 2

def importCheckSumListFromFile(path):
    path, name = os.path.split(path)
    name = name.split(".")[0]
    fp, pathname, description = imp.find_module(name, [path])
    return imp.load_module(name, fp, pathname, description).list


def checkFile(fileDict):
    if os.path.isfile(fileDict["path"]):
        with open(fileDict["path"], "r") as file:
            return { "path": fileDict["path"], "error": getError(file, fileDict)}
    else:
        return FileErrorsEnum.DOES_NOT_EXIST

def getError(file, fileDict):
    return FileErrorsEnum.NO_ERROR if fileDict["checksum"] == hashlib.md5(file.read()).hexdigest() else FileErrorsEnum.CHECKSUM_ERROR

def checkFileList(fileList):
    return map(checkFile, fileList)

def daemonLoop(checksumsList):
        print checksumsList
        print checkFileList(checksumsList)



def main():
    parser = argparse.ArgumentParser(
        description=u'После запуск контролирует целостность файлов из списка, заданного в файле')
    parser.add_argument('-p', '--path', dest='checkSumFile', required=True, action='store',
                        help=u'Путь к файлу, который содержит список файлов с контрольными суммами')
    args = parser.parse_args()
    config = importCheckSumListFromFile(args.checkSumFile)
    daemonLoop(config)


if __name__=="__main__":
    main()

