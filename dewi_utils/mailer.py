# Copyright 2018-2022 Tóth, László Attila
# Distributed under the terms of the Apache License, Version 2.0

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid

from dewi_utils.render import TemplateRenderer


class MailRenderer:
    def __init__(self, template_dir: str, sender_address: str, recipient_address: str):
        self._template_dir = template_dir
        self._sender_address = sender_address
        self._recipient_address = recipient_address

    def render_email(self, subject: str, template_basename: str, template_data: dict):

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self._sender_address
        msg['To'] = self._recipient_address
        msg['Date'] = formatdate(localtime=True)
        msg['Message-Id'] = make_msgid(template_basename)

        t = TemplateRenderer(self._template_dir)

        plain_template_path = os.path.join(self._template_dir, f'{template_basename}.text.tpl')
        html_template_path = os.path.join(self._template_dir, f'{template_basename}.text.tpl')

        if os.path.exists(plain_template_path):
            msg.attach(MIMEText(t.render(f'{template_basename}.text.tpl', template_data), 'plain'))
        else:
            msg.attach(MIMEText(subject + ' - see HTML multipart data for further details', 'plain'))

        if os.path.exists(html_template_path):
            msg.attach(MIMEText(t.render(f'{template_basename}.html.tpl', template_data), 'html'))
        else:
            msg.attach(MIMEText(t.render(f'{template_basename}.tpl', template_data), 'html'))

        return msg.as_string()


def send_mails(smtp_host: str, sender_address: str, recipient_address: str, mails: list[str]):
    print("Count of emails: {}".format(len(mails)))
    if mails:
        print("Sending mails")
        s = smtplib.SMTP(smtp_host)

        for mail in mails:
            if mail:
                s.sendmail(sender_address, [recipient_address], mail)
        s.quit()
