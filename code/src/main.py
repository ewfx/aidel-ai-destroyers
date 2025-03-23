import os
from dotenv import load_dotenv
from google import genai
load_dotenv()


def get_request_types(mail_content):
    client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
    chat = client.chats.create(model="gemini-2.0-flash")

    prompt = f"""
        **Task**: Process the following email content to remove duplicate emails, extract request types, subtypes, the confidence score for that along with the reasoning, and other valuable information.
        The request types and subtypes are as follows:
        "Adjustment": [],
        "AU Transfer": [],
        "Closing Notice": ["Reallocation Fees", "Amendment Fees", "Reallocation Principal"],
        "Commitment Change": ["Cashless Roll", "Decrease", "Increase"],
        "Fee Payment": ["Ongoing Fee", "Letter of Credit Fee"],
        "Money Movement-Inbound": ["Principal", "Interest", "Principal and Interest", "Principal and Interest and Fees"],
        "Money Movement-Outbound": ["Timebound", "Foreign Currency"]

        **Email Content**:
        {mail_content}

        **Output Format**:
        {{
          "request_types": [
            {{
              "type": "Closing Notice",
              "subtype": "Reallocation Principal",
              "confidence_score": "0.95",
              "reasoning": "The email mentions 'reallocation of funds'. The email also specifies a reallocation of funds amounting to INR 1,500.00 from Department A to Department B, indicating reallocation of principal."
            }},
            {{
              "type": "Commitment Change",
              "subtype": "Reallocation Fees",
              "confidence_score": "0.75",
              "reasoning": "The email asks about the process and associated fees for the reallocation, specifically mentioning a 'Reallocation Fee'. This suggests an inquiry related to reallocation fees."
            }}
          ],
          "extracted_information": {{
            "amount": "1500.00",
            "fee_type": "Reallocation Fee",
          }}
        }}
        """

    response = chat.send_message(prompt)
    print("Processed Email Content: ", response.text)

mails_dir = 'mails'
for mail_file in os.listdir(mails_dir):
    with open(os.path.join(mails_dir, mail_file), 'r') as file:
        content = file.read()
        get_request_types(content)
