import smtplib

# Establish SMTP Connection
s = smtplib.SMTP('mail.ditchflow.com', 587)

# Start TLS based SMTP Session
s.starttls()

# Login Using Your Email ID & Password
s.login("Alert@ditchflow.com", "SINCE1937")

# Email Body Content
message = """
Hello, this is a test message!
Illustrated for WTMatter Python Send Email Tutorial
<h1>How are you?</h1>
"""

# To Send the Email
s.sendmail("ilie.petrasco@gmail.com", "Alert@ditchflow.com", message)

# Terminating the SMTP Session
s.quit()
