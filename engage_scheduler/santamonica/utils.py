import logging
import os
import base64
from mailjet_rest import Client
api_key = os.getenv("MJ_API_KEY")
api_secret = os.getenv("MJ_API_SECRET")
log = logging.Logger(__name__)
TEST = os.getenv("ENGAGE_TEST", "False") == "True"
if not TEST:
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')


def send_mail(committee, subject, content, attachment_file_name=None, attachment_file_path=None):
    if TEST:
        return True
    with open(attachment_file_path, 'rb') as f:
        s = f.read()
        b64data = base64.b64encode(s)
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": "donotreply@engage.town",
                        "Name": "Engage"
                    },
                    "To": [
                        {
                            "Email": "eli.j.selkin@gmail.com",
                            "Name": committee.name
                        }
                    ],
                    "Subject": subject,
                    "TextPart": "",
                    "HTMLPart": content,
                    "Attachments": [{
                        "Filename": attachment_file_name,
                        "ContentType": "application/pdf",
                        "Base64Content": b64data
                    }]
                }
            ]
        }
        result = mailjet.send.create(data=data)
        if result.status_code > 300:
            return False
        return True
