from email.mime.text import MIMEText
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os.path


class DraftManager:
    def __init__(self):
        SCOPES = ['https://mail.google.com/']
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        service = build('gmail', 'v1', credentials=creds)
        self.drafts = service.users().drafts()


    def create_message(self, message_content, user_email, message_subject):
        message = MIMEText(message_content)
        message['from'] = 'organiser.email@gmail.com'
        message['to'] = user_email
        message['subject'] = message_subject
        
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}


    def create_draft(self, message_content, user_email, message_subject):
        msg = self.create_message(message_content, user_email, message_subject)
        try:
            message = {'message': msg}
            draft = self.drafts.create(userId='me', body=message).execute()
            return draft['id']

        except HttpError as error:
            print(f'An error occurred: {error}')
            return None


    def update_draft(self, message_content, user_email, message_subject, draft_id):
        new_msg = self.create_message(message_content, user_email, message_subject)
        try:
            self.drafts.update(userId='me', id=draft_id, body={ 'message': new_msg }).execute()

        except HttpError as error:
            print(f'An error occurred: {error}')

            return None


    def update_draft_email_only(self, user_email, draft_id):
        msg = self.drafts.get(userId='me', id=draft_id, format='raw')
        msg['to'] = user_email
        try:
            self.drafts.update(userId='me', id=draft_id, body={ 'message': msg }).execute()

        except HttpError as error:
            print(f'An error occurred: {error}')

            return None


    def send_draft(self, draft_id):
        try:
            self.drafts.send(userId='me', body={ 'id': draft_id }).execute()
        
        except HttpError as error:
            print(f'An error occurred: {error}')

            return None


    def delete_draft(self, draft_id):
        try:
            self.drafts.delete(userId='me', id=draft_id).execute()
        
        except HttpError as error:
            print(f'An error occurred: {error}')

            return None

