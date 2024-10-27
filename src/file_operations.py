import os
import re
import email
from email import policy
from email.parser import BytesParser
from bs4 import BeautifulSoup
from email.utils import parsedate_to_datetime
import datetime
import markdown

# Patterns to remove sensitive data
PRIVATE_MESSAGE_PATTERN = r'This is a PRIVATE message.*?purpose\.'
RESTRICTED_DATA_PATTERN = r'External xxxxxxxx correspondence:.*?if it is obtained from another source without restriction\.'
CONFIDENTIALITY_START = "CONFIDENTIALITY: This email and any accompa"

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code."""
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()

def extract_email_content(eml_file):
    """
    Extracts content from an email file (.eml).
    
    Args:
        eml_file (str): Path to the .eml file.
        
    Returns:
        tuple: (date, html_content, subject, reply_count)
    """
    with open(eml_file, 'rb') as email_file:
        email_message = BytesParser(policy=policy.default).parse(email_file)
    
    # Extract header information
    sender = email_message['From']
    subject = email_message['Subject']
    date = email_message['Date']
    message_id = email_message['Message-ID']

    # Extract attachments
    attachments = []
    for part in email_message.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        filename = part.get_filename()
        if filename:
            size = len(part.get_payload(decode=True))
            size_str = f"{size / 1024:.2f} KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.2f} MB"
            attachments.append(f"{filename} ({size_str})")

            # Extract and save attachment
            attachments_directory = os.path.join("attachments")
            os.makedirs(attachments_directory, exist_ok=True)
            filepath = os.path.join(attachments_directory, filename)
            with open(filepath, 'wb') as f:
                f.write(part.get_payload(decode=True))

    # Process email content
    content = []
    private_message_pattern = re.compile(PRIVATE_MESSAGE_PATTERN, re.DOTALL)
    restricted_data_pattern = re.compile(RESTRICTED_DATA_PATTERN, re.DOTALL)
    
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_type() == 'text/plain':
                part_content = part.get_payload(decode=True).decode()
                part_content = private_message_pattern.sub('', part_content)
                part_content = restricted_data_pattern.sub('', part_content)
                content.append(part_content)
            elif part.get_content_type() == 'text/html':
                html_content = part.get_payload(decode=True).decode()
                soup = BeautifulSoup(html_content, 'html.parser')
                # Remove sensitive content
                for p in soup.find_all('p'):
                    if p.text.startswith(CONFIDENTIALITY_START):
                        p.decompose()
                plain_content = soup.get_text()
                plain_content = private_message_pattern.sub('', plain_content)
                plain_content = restricted_data_pattern.sub('', plain_content)
                content.append(plain_content)
    else:
        email_content = email_message.get_payload(decode=True).decode()
        email_content = private_message_pattern.sub('', email_content)
        email_content = restricted_data_pattern.sub('', email_content)
        content.append(email_content)
    
    # Markdown formatting
    header = f"# Email Details\n\n| Field | Value |\n|-------|-------|\n| From | {sender} |\n| Subject | {subject} |\n| Date | {date} |\n| Message-ID | {message_id} |\n"
    if attachments:
        header += f"| Attachments | {', '.join(attachments)} |\n"
    full_content = header + '\n\n## Email Body\n\n' + '\n'.join(content)
    html_content = markdown.markdown(full_content, extensions=['tables', 'fenced_code'])

    def count_replies(body):
        return len(re.findall(r"wrote:", body, re.IGNORECASE))

    reply_count = count_replies('\n'.join(content))

    return date, html_content, subject, reply_count

def save_all_emails_to_one_file(email_data, output_file):
    """
    Saves all processed emails to a single HTML file with advanced styling and an index.
    
    Args:
        email_data (list): List of tuples containing email data.
        output_file (str): Path to save the combined HTML file.
    """
    combined_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Combined Emails</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            th {{ background-color: #3498db; color: white; }}
            blockquote {{ border-left: 4px solid #3498db; padding-left: 15px; color: #777; font-style: italic; }}
            a {{ color: #3498db; text-decoration: none; }}
        </style>
    </head>
    <body>
    <h1>Email Index</h1>
    <table>
    <tr><th>#</th><th>Date</th><th>Subject</th><th>EML File</th><th>Replies</th></tr>
    """
    for idx, (date, filename, email_content, subject, reply_count) in enumerate(email_data, 1):
        formatted_date = parsedate_to_datetime(date).strftime('%Y-%m-%d %H:%M:%S')
        combined_html += f"<tr><td>{idx}</td><td>{formatted_date}</td><td><a href='#email-{idx}'>{subject}</a></td><td>{filename}</td><td>{reply_count}</td></tr>\n"
    
    combined_html += "</table><hr>\n"
    
    for idx, (date, filename, email_content, subject, reply_count) in enumerate(email_data, 1):
        formatted_date = parsedate_to_datetime(date).strftime('%Y-%m-%d %H:%M:%S')
        combined_html += f"<h2 id='email-{idx}'>{idx}. Email from {formatted_date}</h2>\n<hr>\n{email_content}\n<br><br>\n"

    combined_html += "</body></html>"
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(combined_html)