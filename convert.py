import pandas as pd
from bs4 import BeautifulSoup
import re

# Function to preprocess multiple HTML files into a single CSV
def html_to_csv(input_paths, output_path):
    all_data = []  # List to hold data from all files

    for input_path in input_paths:
        with open(input_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        # Extract message blocks
        messages = soup.find_all('div', class_='pam _3-95 _2ph- _a6-g uiBoxWhite noborder')

        # Prepare lists for extracted data
        senders = []
        texts = []
        timestamps = []

        for msg in messages:
            # Extract sender
            sender = msg.find('div', class_='_3-95 _2pim _a6-h _a6-i')
            senders.append(sender.get_text(strip=True) if sender else '')
            full_name = sender.get_text(strip=True) if sender else ''
            name = full_name.split(' ')[0]  # Get the first name

            # Extract message text
            text = msg.find('div', class_='_3-95 _a6-p')
            message_text = text.get_text(strip=True) if text else ''
            
            if message_text.startswith("You sent an attachment"):
                message_text = "sent an attachment"
            elif message_text.startswith(f"{name} sent an attachment"):
                message_text = "sent an attachment"
            elif message_text == '':
                message_text = "sent a picture"
            
            texts.append(message_text)

            # Extract timestamp
            timestamp = msg.find('div', class_='_3-94 _a6-o')
            if not timestamp:  # Check if timestamp is not found
                # Attempt to find a timestamp in the previous sibling or parent
                timestamp = msg.find_previous('div', class_='_3-94 _a6-o')
            timestamps.append(timestamp.get_text(strip=True) if timestamp else '')

        # Append the data from this file to the all_data list
        all_data.extend(zip(senders, texts, timestamps))

    # Create a DataFrame from all collected data
    data = pd.DataFrame(all_data, columns=['sender', 'message', 'timestamp'])

    # Convert timestamp to a consistent format
    data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce')

    # Save to CSV
    data.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Data saved to {output_path}")

