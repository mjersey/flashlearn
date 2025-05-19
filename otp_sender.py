import smtplib
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Function to generate OTP
def generate_otp():
    otp = random.randint(100000, 999999)  # Ensuring it's a 6-digit OTP
    print(f"Generated OTP: {otp}")  # Debugging: Print the generated OTP
    return str(otp)

# Function to send OTP email
def send_otp_email(recipient_email, otp, username):
    print(f"Sending OTP {otp} to {recipient_email}")  # Debugging: Check the OTP being sent

    sender_email = "flashlearn.help@gmail.com"  # Replace with your email
    sender_password = "twdl uqmi eqsu tabo"  # Replace with your app-specific password
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Create the email content with bold OTP, username, and left-aligned text
    subject = "Your One-Time Password (OTP) for FlashLearn"
    body = f"""
    <div style="text-align:left;">
    <p>Hello {username},</p>
    <p>Your One-Time Password (OTP) for accessing your FlashLearn account is:</p>
    <p><b>{otp}</b></p>
    <p>This OTP is valid for the next 10 minutes. Please do not share this code with anyone.</p>
    <p>If you did not request this OTP, please contact our support team immediately.</p>
    <p>Thank you,<br>FlashLearn Team</p>
    </div>
    """

    # Set up the MIME structure for the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))  # Using 'html' to interpret the HTML content

    # Establish connection with SMTP server
    try:
        # Connecting to the Gmail SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection with TLS
        server.login(sender_email, sender_password)  # Login using email and app password
        text = msg.as_string()  # Convert message to string format
        server.sendmail(sender_email, recipient_email, text)  # Send the email
        server.quit()  # Quit the server connection
        print("OTP sent successfully!")  # Confirmation message
    except Exception as e:
        print(f"Error sending email: {e}")  # Print error if any occurs
