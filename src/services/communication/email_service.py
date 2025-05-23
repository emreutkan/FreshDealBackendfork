import os
import base64
from azure.communication.email import EmailClient

# Load environment variables (if needed)
from dotenv import load_dotenv
load_dotenv()

SENDER_EMAIL_ADDRESS = os.getenv("SENDER_ADDRESS")
def send_email(recipient_address, subject, verification_code):
    try:
        # Retrieve the connection string
        connection_string = os.getenv("EMAIL_CONNECTION_STRING")
        if not connection_string:
            raise ValueError("EMAIL_CONNECTION_STRING is not set in the .env file.")

        client = EmailClient.from_connection_string(connection_string)

        # Construct the correct path to the logo
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'freshdeal-logo.png')
        attachments = []
        image_html = ""  # Default: no image

        # Check if the logo exists
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as logo_file:
                logo_content = logo_file.read()
                logo_base64 = base64.b64encode(logo_content).decode()

            logo_cid = "freshdeallogo"
            image_html = f"""
            <div style="text-align: center; margin-bottom: 20px;">
                <img src="cid:{logo_cid}" alt="FreshDeal Logo" style="max-width:200px;">
            </div>
            """
            attachments.append({
                "name": "freshdeal-logo.png",
                "contentInBase64": logo_base64,  # Correct key name
                "contentType": "image/png",
                "disposition": "inline",
                "contentId": logo_cid
            })
        else:
            print(f"Logo not found at {logo_path}. Sending email without the logo.")

        # Construct email content
        html_content = f"""
        <html>
            <body>
                {image_html}
                <h2 style="color: #2E86C1;">FreshDeal</h2>
                <p>Here is your verification code:</p>
                <h3>{verification_code}</h3>
            </body>
        </html>
        """

        email_message = {
            "senderAddress": SENDER_EMAIL_ADDRESS,
            "recipients": {"to": [{"address": recipient_address}]},
            "content": {"subject": subject, "html": html_content},
        }

        if attachments:
            email_message["attachments"] = attachments

        # Send the email
        poller = client.begin_send(email_message)
        result = poller.result()

        if "messageId" in result:
            print("Message sent successfully, Message ID:", result["messageId"])
        else:
            print("Message sent successfully, Response Details:", result)
    except Exception as e:
        print("Error occurred while sending email:", e)


if __name__ == "__main__":
    print("Testing email sending...")
    print("SENDER_ADDRESS:", SENDER_EMAIL_ADDRESS)
    print("EMAIL_CONNECTION_STRING:", os.getenv("EMAIL_CONNECTION_STRING"))

    test_recipient = os.getenv("TEST_EMAIL_ADDRESS")
    test_subject = "Test Email from FreshDeal"
    test_verification_code = "123456"

    send_email(test_recipient, test_subject, test_verification_code)
