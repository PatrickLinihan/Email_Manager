import smtplib, ssl
import imaplib
import email
from email.header import decode_header
import re

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
logout = False
valid = True
managing = True
port = 465
    
# checking if email is valid
def valid_email(email):
    if(re.fullmatch(regex, email)):
        return False
    else:
        print("Invalid Email. Please enter a valid email address.")
    return True

# list of available inbox's to choose from to delete emails
# List all mailboxes
# some shit
def parse_mailbox(data):
    flags, b, c = data.partition(' ')
    separator, b, name = c.partition(' ')
    return (flags, separator.replace('"', ''), name.replace('"', ''))


#---------------------------------------------------------------------------------------------------------------------------------------------------------#
# entering email and password and error checking
while valid:
    my_email = input("Enter your email address: ")
    valid = valid_email(my_email)

my_password = input("%s password: " %(my_email))

while managing:
    logout = False
    gmail_option = input("Options include:\n\t\tsend email \n\t\tdelete email \n\t\topen email \n\t\tWhat would you like to do?: ")

    #---------------------------------------------------------------------------------------------------------------------------------------------------------#
    if gmail_option == "send email":
        receiver_email = input("Who do you want to send an email to?\n\t\tUse format -> '<email@emailaddress.com>': ")
        message = input("Type message here: ")

        # create a secure ssl context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(my_email, my_password)
            server.sendmail(my_email, receiver_email, message)

    #---------------------------------------------------------------------------------------------------------------------------------------------------------#
    elif gmail_option == "delete email":
        while not logout:
            # create an IMAP4 class with SSL
            imap = imaplib.IMAP4_SSL("imap.gmail.com")
            # authenticate
            imap.login(my_email, my_password)

            resp, data = imap.list('""', '*')
            if resp == 'OK':
                print("\n\nList of Mailboxes to choose from:")
                for mbox in data:
                    flags, separator, name = parse_mailbox(bytes.decode(mbox))
                    #fmt = '{0}    : [Flags = {1}; Separator = {2}'
                    print(name)

            imap.list()
            inbox = input("\nWhich inbox would you like to delete emails from?: ")
            if inbox == "logout":
                imap.logout()
                break
            # selecting that inbox
            imap.select(inbox)

            # searching for emails from this emailer
            emails_to_delete = input("\nWhat emails would you like to delete?\n\t\tUse format -> 'FROM <email@emailaddress.com': ")

            # convert messages to a list of email IDs
            status, messages = imap.search(None, emails_to_delete)
            messages = messages[0].split(b' ') 

            numberOfEmailsDeleted = 0;
            # traverse mail in array to delete
            print("working...")
            for mail in messages:
                _, msg = imap.fetch(mail, "(RFC822)")
                # you can delete the for loop for performance if you have a long list of emails
                # # because it is only for printing the SUBJECT of target email to delete
                # for response in msg:
                #     if isinstance(response, tuple):
                #         msg = email.message_from_bytes(response[1])
                #          # decode the email subject
                #         subject = decode_header(msg["Subject"])[0][0]
                #         if isinstance(subject, bytes):
                #              # if it's a bytes type, decode to str
                #             subject = subject.decode()
                #         print("Deleting", subject)
                # mark the mail as deleted
                imap.store(mail, "+FLAGS", "\\Deleted")
                numberOfEmailsDeleted += 1

            # permanently remove mails that are marked as deleted
            # from the selected mailbox (in this case, INBOX)
            imap.expunge()
            # close the mailbox
            imap.close()
            print("Success! %d emails deleted!" %(numberOfEmailsDeleted))
            # logout from the account
            imap.logout()
            logout = True
    keep_managing = input("Would you like to do anything else? (Yes/Y/y/No/N/n): ")
    if keep_managing == "Yes" or keep_managing == "Y" or keep_managing == "y":
        managing = True
    elif keep_managing == "No" or keep_managing == "N" or keep_managing == "n":
        managing = False
    #---------------------------------------------------------------------------------------------------------------------------------------------------------#


    #elif gmail_option == "open email":


