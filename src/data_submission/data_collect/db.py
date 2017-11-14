# -*- coding: utf-8 -*-

import os
import traceback

import psycopg2

from data_submission.settings import settings


class Database(object):
    def __init__(self, *args, **kwargs):
        self.conn = None

    def _connect(self):
        raise NotImplementedError

    def _close(self):
        raise NotImplementedError

    def _reconnect(self):
        self.close()
        self.connect()

    def query(self, sql):
        raise NotImplementedError

    def update(self, sql):
        raise NotImplementedError


class PostgreSQL(Database):
    def __init__(self, db_setting, *args, **kwargs):
        super(PostgreSQL, self).__init__(db_setting, *args, **kwargs)
        self.dbtype = 'postgresql'
        self.db_setting = db_setting


    def _connect(self):
        try:
            db_port = self.db_setting.get('port')
            if type(db_port) != int:
                self.db_setting['port'] = int(db_port)
            self.conn = psycopg2.connect(**self.db_setting)
            self.conn.autocommit = True
            #self.conn.set_client_encoding('utf8')
        except psycopg2.Error as e:
            print traceback.format_exc()
            print 'connect error: {0} - "{1}"'.format(e.pgcode, e.pgerror)

        return True if self.conn else False

    def _close(self):
        try:
            if self.conn:
                self.conn.close()
        except psycopg2.Error as e:
            print traceback.format_exc()
            print 'close error: {0} - "{1}"'.format(e.pgcode, e.pgerror)
        finally:
            self.conn = None

    def query(self, sql):
        ret = False
        rows = []
        try:
            self._connect()
            cur = self.conn.cursor()
            print(sql)
            cur.execute(sql)
            rows = cur.fetchall()
            ret = True
        except psycopg2.Error as e:
            print traceback.format_exc()
            print 'query error: {0} - "{1}"'.format(e.pgcode, e.pgerror)
        finally:
            self._close()
        return ret, rows

    def update(self, sql):
        ret = False
        try:
            self._connect()
            cur = self.conn.cursor()
            cur.execute(sql)
            ret = True
        except psycopg2.Error as e:
            print traceback.format_exc()
            print 'query error: {0} - "{1}"'.format(e.pgcode, e.pgerror)
        finally:
            self._close()
        return ret

guokr_auth_db = PostgreSQL(settings.get('DB_GUOKR_AUTH'))
guokr_community_db = PostgreSQL(settings.get('DB_GUOKR_COMMUNITY'))