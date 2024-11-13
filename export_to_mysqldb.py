#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
import logging
import pymysql
import json

class ResultsToMySQL():
    logger = None
    mysqlConn = None
    
    def __init__(self) -> None:
        scriptPath = os.path.dirname(os.path.abspath(__file__))
        if not os.path.exists(scriptPath + "/logs/"):
            os.makedirs(scriptPath + "/logs/")
        pass
        logname = 'mysql_export.log'
        logpath = scriptPath + '/logs/' + logname
        logformat = '%(asctime)s - %(funcName)s - %(levelname)s - %(message)s'
        loghandler = logging.FileHandler(logpath)
        loghandler.setFormatter(logging.Formatter(logformat)) 
        self.logger = logging.getLogger(logname)
        self.logger.addHandler(loghandler)
        self.logger.setLevel(logging.INFO)
        self.mysqlConn = self.connect()

    def connect(self):
        mysqlConn = pymysql.connect(
            host = os.getenv('MYSQL_PARKRUN_HOST', "127.0.0.1"),
            user = os.getenv('MYSQL_PARKRUN_USER', "parkrun"),
            password = os.getenv('MYSQL_PARKRUN_PASS', "pass"),
            db = os.getenv('MYSQL_PARKUN_DB', "parkrun"),
            charset = os.getenv('MYSQL_CHARSET', "utf8mb4"),
            cursorclass = pymysql.cursors.DictCursor,
            autocommit=True)
        if mysqlConn:
            self.logger.info("Mysql start - OK")
        else:
            self.logger.error("Mysql start - ERROR")
            self.logger.info(json.dumps(mysqlConn))
        return mysqlConn
    
    def start(self):
        self.logger.info("export result to MySQL database")
        pass


def main(args):
    resultsToDB = ResultsToMySQL()
    resultsToDB.start()
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))