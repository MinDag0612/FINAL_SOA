from __future__ import print_function
import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.message import EmailMessage
from email.utils import formataddr
from datetime import datetime

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.compose']


def send_email_v1(recipient, subject=None, content=None, port=0):
    try:
        creds = None
        if os.path.exists('Notification/token.json'):
            creds = Credentials.from_authorized_user_file('Notification/token.json', SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('Notification/credentials_desktop_apps.json', SCOPES)
                creds = flow.run_local_server(port=port)  # https://dhpit.com/go/f5kizi

            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
    except Exception as e:
        raise Exception("Lỗi xác thực Gmail API: " + str(e) + " -- from mailler api")

    # Call Gmail API
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)

        # Prepare a message
        message = EmailMessage()
        if subject is not None:
            message['Subject'] = str(subject)
        else:
            message['Subject'] = 'Test Message (' + str(datetime.now().strftime('%m/%d/%Y %H:%M:%S')) + ')'

        if content is not None:
            message.set_content(str(content))
        else:
            message.set_content('This is a test message sent from a Flask application.')

        message['To'] = recipient  # you should validate email address format
        message['From'] = formataddr(('Flask App', service.users().getProfile(userId='me').execute()['emailAddress']))

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {
            'raw': encoded_message
        }

        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        return True
    except HttpError as e:
        raise Exception(f'An error occurred: {e}' + " -- from mailler api")

# send_email_v1("523h0011@student.tdtu.edu.vn", "111", "111")