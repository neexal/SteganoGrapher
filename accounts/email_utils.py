# email_utils.py

import magic
import os
from django.core.mail import EmailMessage

def send_email_with_attachment(subject, message, from_email, recipient_list, attachment_path):
    with open(attachment_path, 'rb') as file:
        file_content = file.read()

    mime_type = magic.from_buffer(file_content, mime=True)

    # Extract the filename from the attachment_path
    file_name = os.path.basename(attachment_path)

    email = EmailMessage(subject, message, from_email, recipient_list)
    email.attach(file_name, file_content, mime_type)

    # Send the email
    email.send()