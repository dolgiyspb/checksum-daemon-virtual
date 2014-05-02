#!/usr/bin/python
#  -*- coding: utf-8 -*-
__author__ = 'alex'

import hashlib
import pprint
import argparse


def generateMd5CheckSum(path):
    with open(path.strip(), 'r') as file:
        return {"path": path.strip(), "checksum": hashlib.md5(file.read()).hexdigest()}


def getFilesPathsAndChecksumsFromFile(filename):
    with open(filename, 'r') as file:
        return map(generateMd5CheckSum, file)


def writeChecksumsInFile(path, checksumsList):
    with open(path, 'w+') as file:
        print >> file, "#!/usr/bin/python\n#  -*- coding: utf-8 -*-\nlist=\\"
        pprint.pprint(checksumsList, file)


def generateFile(listFilePath, checkSumFilePath):
    writeChecksumsInFile(checkSumFilePath, getFilesPathsAndChecksumsFromFile(listFilePath))


def main():
    parser = argparse.ArgumentParser(
        description=u'Генерирует список файлов с контрольными суммами для дальнейшего контроля')
    parser.add_argument('-l', '--lpath', dest='listFile', required=True, action='store',
                        help=u'Путь к файлу, хранящему список путей файлов для контроля целостности')
    parser.add_argument('-c', '--cpath', dest='checkSumFile', required=True, action='store',
                        help=u'Путь к файлу, в который будет сохранен список файлов с контрольными суммами')
    args = parser.parse_args()
    generateFile(args.listFile, args.checkSumFile)


if __name__ == "__main__":
    main()


