import boto3
import time
import pandas as pd
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from botocore.exceptions import ClientError

# AWS Configuration
region = 'us-east-1'  # Replace with your AWS region
athena_output_location = 's3://1234555/QDeveloperLogs/by_user/'  # Replace with your S3 bucket
database = 'amazon_q_metrics'  # Replace with your Athena database name

# Email Configuration
smtp_server = 'smtp.abc123.com'  # Replace with your SMTP server
smtp_port = 465  # Standard port for TLS
sender_email = 'nirav@exampl.com'  # Replace with sender email
receiver_email = 'niravj@world.com'  # Replace with recipient email
email_password = '373777'  # Replace with email password or app password


def run_athena_query(query):
    athena_client = boto3.client('athena', region_name=region)
    
    # Start the query execution
    response = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': database
        },
        ResultConfiguration={
            'OutputLocation': athena_output_location
        }
    )
    
    query_execution_id = response['QueryExecutionId']
    print(f"Query execution ID: {query_execution_id}")
    
    # Wait for query to complete
    while True:
        response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
        state = response['QueryExecution']['Status']['State']
        
        if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
        
        print(f"Query is in {state} state, waiting...")
        time.sleep(5)
    
    if state == 'SUCCEEDED':
        print("Query completed successfully!")
        return query_execution_id
    else:
        error_message = response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
        print(f"Query failed: {error_message}")
        return None

#Function to Download Query Results as CSV
def download_query_results(query_execution_id, csv_file_path):
    athena_client = boto3.client('athena', region_name=region)
    s3_client = boto3.client('s3', region_name=region)
    
    # Get S3 path of results
    response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
    s3_path = response['QueryExecution']['ResultConfiguration']['OutputLocation']
    
    # Parse S3 path
    s3_path = s3_path.replace('s3://', '')
    bucket_name = s3_path.split('/', 1)[0]
    key = s3_path.split('/', 1)[1]
    
    # Download results from S3
    s3_client.download_file(bucket_name, key, csv_file_path)
    print(f"Query results saved to {csv_file_path}")
    
    # Alternative: Use pandas to process the results
    # results = pd.read_csv(csv_file_path)
    # return results

#Function to Send Email with CSV Attachment
def send_email_with_attachment(csv_file_path, subject="Athena Query Results"):
    # Create message container
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    
    # Add message body
    body = "Please find attached the results of your Athena query."
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach the CSV file
    with open(csv_file_path, 'rb') as file:
        attachment = MIMEApplication(file.read(), Name=os.path.basename(csv_file_path))
    
    attachment['Content-Disposition'] = f'attachment; filename="{os.path.basename(csv_file_path)}"'
    msg.attach(attachment)
    
    # Connect to SMTP server and send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(sender_email, email_password)
        server.send_message(msg)
        server.quit()
        print(f"Email sent successfully to {receiver_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

#Main Function 
def main():
    # Your Athena SQL query
    # query = """
    # SELECT *
    # FROM devq_userdata_logs
    # LIMIT 100;
    # """  # Replace with your actual query
    query = """SELECT DISTINCT REPLACE(userid, '"', '') as UserID,MAX(parse_datetime(data, 'MM-dd-YYYY')) as latest_activity_date FROM devq_userdata_logs GROUP BY userid ORDER BY latest_activity_date DESC""" 
    # Local path to save the CSV file
    csv_file_path = "/Users/niravj/Desktop/athena_results.csv"
    
    # Run the query
    query_execution_id = run_athena_query(query)
    
    if query_execution_id:
        # Download results as CSV
        download_query_results(query_execution_id, csv_file_path)
        
        # Send email with CSV attachment
        send_email_with_attachment(csv_file_path, "Your Athena Query Results")
        
        # Clean up the local file if needed
        # os.remove(csv_file_path)

if __name__ == "__main__":
    main()
