# fileencoding:utf-8
import logging
import logging.handlers
from conf import EMAILS, EMAIL_TITLE
import conf

class MailHandler(logging.Handler):
    def __init__(self, emails):
        logging.Handler.__init__(self)
        self.emails = emails
        self.emails_str = ','.join(emails)
    def emit(self,record):
        msg=self.format(record)
        import os
        f = os.popen("mail -s '%s' '%s'" % (EMAIL_TITLE, self.emails_str), 'w')
        f.write(msg)
        f.close()
 
import smtplib
from email.mime.text import MIMEText

class SMTPMailHandler(logging.Handler):
    def __init__(self, emails):
        logging.Handler.__init__(self)
        self.emails = emails
        self.emails_str = ','.join(emails)

    def emit(self, record):
        self.mailer = smtplib.SMTP_SSL(conf.SMTP_MAIL_URI)
        self.mailer.login(conf.SMTP_MAIL_FROM, conf.SMTP_MAIL_PASSWORD)
        mime = MIMEText(self.format(record))
        mime['Subject'] = conf.EMAIL_TITLE
        mime['From'] = conf.SMTP_MAIL_FROM
        mime['To'] = self.emails_str
        mime['msg'] = self.format(record)
        msg = mime.as_string()
        
        self.mailer.sendmail(conf.SMTP_MAIL_FROM, self.emails, msg)


def get_logger(name):
    path = "./log/" + name # 定义日志存放路径
    filename = path + '.log'    # 日志文件名称
    name = name    # 为%(name)s赋值
    logger = logging.getLogger(name)

    ch = logging.handlers.TimedRotatingFileHandler(filename + '.info', 'D', 1, 10)
    gs = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s[line:%(lineno)d] - %(message)s')
    ch.setFormatter(gs)
    ch.setLevel('INFO')
    logger.addHandler(ch)

    fh = logging.handlers.TimedRotatingFileHandler(filename, 'D', 1, 10)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s -   %(name)s[line:%(lineno)d] - %(message)s')
    fh.setFormatter(formatter)
    fh.setLevel('DEBUG')
    logger.addHandler(fh)

    if not conf.__dict__.get('USE_SMTP'):
        filehandler = MailHandler(EMAILS)
    else:
        filehandler = SMTPMailHandler(EMAILS)
    filehandler.setLevel('WARNING')
    logger.addHandler(filehandler)
    logger.setLevel('DEBUG')
    return logger

if __name__ == "__main__":
    log = get_logger('test')
    log.debug('1111')
    log.info('222')
    log.warning('333')
