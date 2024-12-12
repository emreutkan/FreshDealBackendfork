# mail_logic.py
from azure.communication.email import EmailClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Immutable sender email
SENDER_EMAIL_ADDRESS = "DoNotReply@f8652524-c674-48ac-9648-4d601d0d4c3d.azurecomm.net"

def send_email(recipient_address, subject, message):
    """
    Send an email using Azure Email Client.
    """
    try:
        # Retrieve connection string from environment
        connection_string = os.getenv("EMAIL_CONNECTION_STRING")
        if not connection_string:
            raise ValueError("EMAIL_CONNECTION_STRING is not set in the .env file.")

        client = EmailClient.from_connection_string(connection_string)

        # Prepare the email message
        email_message = {
            "senderAddress": SENDER_EMAIL_ADDRESS,
            "recipients": {"to": [{"address": recipient_address}]},
            "content": {"subject": subject, "plainText": message},
        }

        # Send email and wait for completion
        poller = client.begin_send(email_message)
        result = poller.result()

        print("Message sent successfully:", result.message_id)
    except Exception as ex:
        print("Error occurred while sending email:", ex)
