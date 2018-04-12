# -*- coding: utf-8 -*-

import random
import string

from datetime import datetime
from sqlalchemy import text

from db import db
from journalist_app import create_app

random.seed('ᕕ( ᐛ )ᕗ')


def random_bool():
    return bool(random.getrandbits(1))


def bool_or_none():
    return random.choice([None, True, False])


def random_bytes(min, max, nullable):
    if nullable and random_bool():
        return None
    else:
        # python2 just wants strings, fix this in python3
        return random_chars(random.randint(min, max))


def random_username():
    len = random.randint(3, 64)
    return random_chars(len)


def random_chars(len, chars=string.printable):
    return ''.join([random.choice(chars) for _ in range(len)])


def random_datetime(nullable):
    if nullable and random_bool():
        return None
    else:
        return datetime(
            year=random.randint(1, 9999),
            month=random.randint(1, 12),
            day=random.randint(1, 28),
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59),
            microsecond=random.randint(0, 1000),
        )


class UpgradeTester():

    '''This migration has no upgrade because there are no tables in the
       database prior to running, so there is no data to load or test.
    '''

    def __init__(self, config):
        pass

    def load_data(self):
        pass

    def check_upgrade(self):
        pass


class DowngradeTester():

    def __init__(self, config):
        self.config = config
        self.app = create_app(config)

    def load_data(self):
        with self.app.app_context():
            for _ in range(200):
                self.add_journalist()

            for _ in range(200):
                self.add_source()

            for jid in range(1, 200, 10):
                for _ in range(random.randint(1, 3)):
                    self.add_journalist_login_attempt(jid)

            for jid in range(1, 200, 10):
                for sid in range(1, 200, 10):
                    self.add_reply(jid, sid)

            for sid in range(1, 200, 10):
                self.add_source_star(sid)

            for sid in range(1, 200, 8):
                for _ in range(random.randint(1, 3)):
                    self.add_submission(sid)

            db.session.commit()

    @staticmethod
    def add_journalist():
        if random_bool():
            otp_secret = random_chars(16, string.ascii_uppercase + '234567')
        else:
            otp_secret = None

        is_totp = random_bool()
        if is_totp:
            hotp_counter = 0 if random_bool() else None
        else:
            hotp_counter = random.randint(0, 10000) if random_bool() else None

        last_token = random_chars(6, string.digits) if random_bool() else None

        params = {
            'username': random_username(),
            'pw_salt': random_bytes(1, 64, nullable=True),
            'pw_hash': random_bytes(32, 64, nullable=True),
            'is_admin': bool_or_none(),
            'otp_secret': otp_secret,
            'is_totp': is_totp,
            'hotp_counter': hotp_counter,
            'last_token': last_token,
            'created_on': random_datetime(nullable=True),
            'last_access': random_datetime(nullable=True),
        }
        sql = '''INSERT INTO journalists (username, pw_salt, pw_hash,
                    is_admin, otp_secret, is_totp, hotp_counter, last_token,
                    created_on, last_access)
                 VALUES (:username, :pw_salt, :pw_hash, :is_admin,
                    :otp_secret, :is_totp, :hotp_counter, :last_token,
                    :created_on, :last_access);
              '''
        db.engine.execute(text(sql), **params)

    @staticmethod
    def add_source():
        filesystem_id = random_chars(96) if random_bool() else None
        params = {
            'filesystem_id': filesystem_id,
            'journalist_designation': random_chars(50),
            'flagged': bool_or_none(),
            'last_updated': random_datetime(nullable=True),
            'pending': bool_or_none(),
            'interaction_count': random.randint(0, 1000),
        }
        sql = '''INSERT INTO sources (filesystem_id, journalist_designation,
                    flagged, last_updated, pending, interaction_count)
                 VALUES (:filesystem_id, :journalist_designation, :flagged,
                    :last_updated, :pending, :interaction_count)
              '''
        db.engine.execute(text(sql), **params)

    @staticmethod
    def add_journalist_login_attempt(journalist_id):
        params = {
            'timestamp': random_datetime(nullable=True),
            'journalist_id': journalist_id,
        }
        sql = '''INSERT INTO journalist_login_attempt (timestamp,
                    journalist_id)
                 VALUES (:timestamp, :journalist_id)
              '''
        db.engine.execute(text(sql), **params)

    @staticmethod
    def add_reply(journalist_id, source_id):
        params = {
            'journalist_id': journalist_id,
            'source_id': source_id,
            'filename': random_chars(50),
            'size': random.randint(0, 1024 * 1024 * 500),
        }
        sql = '''INSERT INTO replies (journalist_id, source_id, filename,
                    size)
                 VALUES (:journalist_id, :source_id, :filename, :size)
              '''
        db.engine.execute(text(sql), **params)

    @staticmethod
    def add_source_star(source_id):
        params = {
            'source_id': source_id,
            'starred': bool_or_none(),
        }
        sql = '''INSERT INTO source_stars (source_id, starred)
                 VALUES (:source_id, :starred)
              '''
        db.engine.execute(text(sql), **params)

    @staticmethod
    def add_submission(source_id):
        params = {
            'source_id': source_id,
            'filename': random_chars(50),
            'size': random.randint(0, 1024 * 1024 * 500),
            'downloaded': bool_or_none(),
        }
        sql = '''INSERT INTO submissions (source_id, filename, size,
                    downloaded)
                 VALUES (:source_id, :filename, :size, :downloaded)
              '''
        db.engine.execute(text(sql), **params)

    def check_downgrade(self):
        '''We don't need to check anything on this downgrade because the
           migration drops all the tables. Thus, there is notthing to do.
        '''
        pass
