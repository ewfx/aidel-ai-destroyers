import os
from time import sleep

from dotenv import load_dotenv
from google import genai

from process_email import process_eml_file

load_dotenv()


def get_request_types(mail_content, file_name):
    client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
    chat = client.chats.create(model="gemini-2.0-flash")

    prompt = f"""
        **Task**: Process the following email content, and the attachments after deciding their type like pdf or eml or anything to extract request types, subtypes, the confidence score for that along with the reasoning, and other valuable information.
        Also remove duplicate emails based on their content.
        Prioritize the main gemail content over the attachments content.
        The request types and subtypes are as follows, and they should be populated in all cases:
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
        Just give output in this format with nothing else. No need to write json or ``` or anything.
        {{
          "request_types": [
            {{
              "type": "Closing Notice",
              "subtype": "Reallocation Principal",
              "confidence_score": "0.95",
              "reasoning": "Reasoning for the same"
            }},
            {{
              "type": "Commitment Change",
              "subtype": "Reallocation Fees",
              "confidence_score": "0.75",
              "reasoning": "Reasoning for the same"
            }}
          ],
          "extracted_information": {{
            "amount": "1500.00",
            "fee_type": "Reallocation Fee",
          }},
          "duplicate_emails": ["FWD: RE: Closing Notice received on March 7, 2024 2:08 pm (Duplicate of RE: Closing Notice has been received on March 7, 2024 12:05 pm)"]
        }}
        """

    response = chat.send_message(prompt)
    sleep(5)
    with open(os.path.join('output_mails', file_name), 'w') as op_file:
        print('Processed: ', file_name)
        op_file.write(response.text)

mails_dir = 'mails'
for mail_file in os.listdir(mails_dir):
    if mail_file.endswith('.eml'):
        content = process_eml_file(os.path.join(mails_dir, mail_file))
        print(content)
        get_request_types(content, mail_file)
