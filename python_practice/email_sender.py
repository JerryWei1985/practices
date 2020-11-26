#!/usr/bin/env python3
# -*- coding: utf-8 -*-


'This module is used to send email'
__author__ = 'ghwei'

import json
import requests

class EmailClient(object):
    def __init__(self):
        self._url = 'http://mobvoi-email'
        self._author  = 'LM Trainer'
        self._receiver_list = None
        self._cc_list = None
        self._bcc_list = None
        self._subject = None
        self._message = None
        self._message_type = None
        self._ldap = None
        self._file_list = None

    def set_receiver_list(self, receivers):
        self._receiver_list = receivers

    def set_cc_list(self, cc_list):
        self._cc_list = cc_list

    def set_bcc_list(self, bcc_list):
        self._bcc_list = bcc_list

    def set_author(self, author):
        self._author = author

    def set_subject(self, subject):
        self._subject = subject

    def set_message(self, message):
        self._message = message

    def set_message_type(self, message_type):
        self._message_type = message_type

    # TODO(changwei):
    def set_ldap(self, ldap):
        self._ldap = ldap

    # TODO(changwei):
    def set_file_list(self, file_list):
        self._file_list = file_list

    def send(self):
        headers = {"Content-type": "application/json"}
        body = {}

        if self._receiver_list != None:
            body['receivers'] = ','.join(self._receiver_list)

        if self._cc_list != None:
            body['cc'] = ','.join(self._cc_list)

        if self._bcc_list != None:
            body['bcc'] = ','.join(self._bcc_list)

        if self._subject != None:
            body['subject'] = self._subject

        if self._message != None:
            body['message'] = self._message

        body['author'] = self._author
        body['priority'] = 'high'
        print('send body: %s' % body)

        try:
            res = requests.post(self._url, data = body, headers=headers)
            print("send mail return: %s" % res.ok)
        except Exception as ex:
            print("send mail error: %s" % ex)


def send_email(receiver_list, message, subject):
    email_client = EmailClient()
    email_client.set_receiver_list(receiver_list)
    email_client.set_message(message)
    email_client.set_subject(subject)

    email_client.send()


if __name__=='__main__':
    email_client = EmailClient()
    email_client.set_receiver_list(['ghwei@mobvoi.com'])
    email_client.set_cc_list(['ghwei@mobvoi.com'])
    email_client.set_subject('test for send email')
    email_client.set_message('message')

    email_client.send()
