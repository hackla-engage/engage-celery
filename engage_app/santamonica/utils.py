import logging
import os
import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
log = logging.Logger(__name__)
TEST = os.getenv('ENGAGE_TEST', "False") == "True"
log.error("XXXX {}".format(TEST))
if not TEST:
    ses_client = boto3.client('ses', aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                              aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
                              region_name=os.environ["AWS_REGION"])


def send_mail(committee, subject, content, attachment_file_name=None, attachment_file_path=None):
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['To'] = committee.email
    msg['From'] = 'do-not-reply@engage.town'
    part = MIMEText(content, 'html')
    msg.attach(part)
    log.error(os.path.isfile(attachment_file_path))
    if attachment_file_path is not None:
        with open(attachment_file_path, 'rb') as f:
            part = MIMEApplication(f.read(), _subtype='pdf')
            part.add_header('Content-Disposition', 'attachment',
                            filename=attachment_file_name)
            msg.attach(part)
    try:
        if not TEST:
            response = ses_client.send_raw_email(
                Source="engage team <do-not-reply@engage.town>",
                Destinations=[committee.email],
                RawMessage={'Data': msg.as_string()})
            if response['MessageId'] is not None:
                return True
            else:
                log.error("Could not send an email from {} to {} about {}".format(
                    "do-not-reply@engage.town", committee.email, subject))
                return False
        else:
            return True
    except Exception as exc:
        log.error("Could not send email and threw error {}".format(str(exc)))
        return False
