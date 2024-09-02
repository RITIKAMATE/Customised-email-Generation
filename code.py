import os
import pandas as pd
import openai
from langchain_openai import AzureOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Set environment variables
os.environ["OPENAI_API_VERSION"] = "2023-05-15"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://financial-email-generation-1.openai.azure.com/"
os.environ["AZURE_OPENAI_API_KEY"] = "85d2e491bfe64f82b49d5f3899840315"

# Initialize AzureOpenAI instance
llm = AzureOpenAI(
    deployment_name="Financial_report",  # Update with your deployment name
)

# Define the prompt template
template = """
You are an AI tasked with crafting a highly engaging and interactive email for a customer based on their spending patterns.
Customer Name: {name}
Customer Goal: {goal}
Customer Email: {email}
Spending Pattern: {spending_pattern}

Create a compelling subject line and email content with the following elements:
1. *Subject Line:* Craft an eye-catching subject line that grabs the customer's attention and highlights the benefit of the email content. Use emojis to make it stand out in their inbox.
2. *Greeting:* A warm and enthusiastic greeting that acknowledges the customer's recent activities, using emojis to add a friendly touch.
3. *Educational Course:* Introduce an educational course that is relevant to the customer's financial goals. Include a video link from YouTube or another platform to provide a preview of the course content. Example: [Watch this video](https://www.youtube.com/watch?v=example).
4. *Financial Report:* Provide a summary of the customer's recent financial activities in a tabular format. Include personalized insights and actionable advice to help them improve their financial health. Here is an example format:

| *Category*   | *Amount* |
|----------------|------------|
| Dining Out     | $100       |
| Theater        | $50        |
| Clothing       | $200       |
| Total Amount   | $350       |

5. *Financial Tip:* Share a relevant financial tip that includes actionable steps and explains the benefits of following the advice.
6. *Investment Schemes:* Recommend a few investment schemes from Bank of Baroda that align with the customer's financial goals and spending patterns. Explain the benefits and key features of each scheme.
7. *Closing Note:* A motivational closing note that encourages further engagement and includes a call to action, making the email feel personal and inspiring.

Ensure the email is conversational, inspiring, and encourages the customer to take positive financial actions. End the email with a professional note stating that the message is from Bank of Baroda.

Please format the final email with headings only for the "Subject Line," "Educational Course," "Financial Report," "Financial Tip," and "Investment Schemes." The greeting and closing note should be written as part of the passage without explicit headings.
"""


prompt = PromptTemplate(template=template, input_variables=["spending_pattern", "name", "goal", "email"])

# Use RunnableSequence
chain = RunnableSequence(prompt | llm)

# Function to generate email content
def generate_email_content(customer_profile, transaction_summary):
    spending_pattern = ", ".join(f"{k}: {v}" for k, v in transaction_summary.items())
    name = customer_profile['Name']
    goal = customer_profile['Goal']
    email = customer_profile['Email']

    # Create the input for the prompt
    prompt_input = {"spending_pattern": spending_pattern, "name": name, "goal": goal, "email": email}
    custom_message = chain.invoke(prompt_input)

    # Extract personalized subject and email content
    custom_message_lines = custom_message.strip().split('\n')
    subject = custom_message_lines[0]
    email_content = "\n".join(custom_message_lines[1:])

    return subject, email_content

# Load data from CSV files
customer_profiles = pd.read_csv('customer_profiles.csv')  # Update the path here
financial_transactions = pd.read_csv('financial_transactions.csv')  # Update the path here

# Function to merge and process data
def process_data():
    # Merge customer profiles with financial transactions on a common key (e.g., CustomerID)
    merged_data = pd.merge(customer_profiles, financial_transactions, on='CustomerID')

    # Process each row in the DataFrame to generate email content
    for index, row in merged_data.iterrows():
        customer_profile = row[['Name', 'Goal', 'Email']].to_dict()
        transaction_summary = row[['DiningOut', 'Theater', 'Clothing', 'TotalAmount']].to_dict()
        subject, email_content = generate_email_content(customer_profile, transaction_summary)
        print(f"Subject: {subject}")
        print(f"Email for {customer_profile['Name']}:\n{email_content}\n")

# SMTP configuration for Gmail
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_user = 'ritikamate9@gmail.com'  # Replace with your email
smtp_password = 'rodx zbjk zfsf dzrp'  # Replace with your app-specific password

# Function to send email
def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

# Main function to process data and generate emails
process_data()
# Merge based on common column, e.g., CustomerID
merged_data = pd.merge(customer_profiles, financial_transactions, on='CustomerID', how='inner')

# Remove duplicates
merged_data = merged_data.drop_duplicates()

# Handle missing values
merged_data = merged_data.dropna()

# Add a new column 'IsHighValueCustomer' based on total transaction amount
if 'TotalAmount' in merged_data.columns:
    merged_data['IsHighValueCustomer'] = merged_data['TotalAmount'] > 1000
else:
    print("Column 'TotalAmount' not found in merged data.")

for _, row in merged_data.iterrows():
    customer_profile = row[['Name', 'Goal', 'Email']].to_dict()
    transaction_summary = row[['DiningOut', 'Theater', 'Clothing', 'TotalAmount']].to_dict()
    subject, email_content = generate_email_content(customer_profile, transaction_summary)
    send_email(customer_profile['Email'], subject, email_content)









