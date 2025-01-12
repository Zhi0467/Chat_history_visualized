# chat_analysis.py
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import re
import os
from convert import html_to_csv

# Load chat history from CSV
def load_chat_history(file_path):
    return pd.read_csv(file_path)

# Analyze text messages
def analyze_chat(data, sender1 = None, sender2 = None, time_diff = 0):
    if sender1 is not None:
        # Find the first unique sender
        first_sender = data['sender'].unique()[0]  
        data.loc[data['sender'] == first_sender, 'sender'] = sender1
    if sender2 is not None:
        # Find the second unique sender
        second_sender = data['sender'].unique()[1]  
        data.loc[data['sender'] == second_sender, 'sender'] = sender2

    # Convert timestamp to datetime and shift by hours
    data['timestamp'] = pd.to_datetime(data['timestamp']) + pd.Timedelta(hours=time_diff)
    
    # Extract date and hour
    data['date'] = data['timestamp'].dt.date
    data['hour'] = data['timestamp'].dt.hour
    data['weekday'] = data['timestamp'].dt.day_name()  # Get the weekday name
    
    # Count texts per weekday
    texts_per_weekday = data.groupby(['weekday', 'sender']).size().unstack(fill_value=0)
    texts_per_weekday = texts_per_weekday.reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], fill_value=0)

    # Calculate the number of weeks
    total_weeks = (data['timestamp'].max() - data['timestamp'].min()).days // 7 + 1
    texts_per_weekday = texts_per_weekday / total_weeks  # Average per week

    # Calculate response time
    data['prev_sender'] = data['sender'].shift(-1)
    time_diff = - data['timestamp'].diff().dt.total_seconds() / 60  # in minutes
    # Adjust for crossing midnight
    time_diff = time_diff.where(time_diff >= 0, time_diff + 1440)  # Add 1440 minutes (24 hours) if negative
    data['response_time'] = time_diff

    # Shift the response_time column by 1
    data['response_time'] = data['response_time'].shift(-1)

    # Filter out rows with invalid timestamps
    valid_data = data[data['timestamp'].notnull()]  # Only keep rows with valid timestamps
    valid_responses = valid_data[valid_data['sender'] != valid_data['prev_sender']]  # Only keep rows where sender changes
    # Remove rows with NaN response_time
    valid_responses = valid_responses[valid_responses['response_time'].notna()]  # Remove rows with NaN response_time

    avg_response_time = valid_responses.groupby('sender')['response_time'].mean()


    # Text message distribution over hours
    texts_per_hour = data.groupby(['hour', 'sender']).size().unstack(fill_value=0)
    
    # Calculate the number of days
    total_days = total_weeks * 7
    texts_per_hour = texts_per_hour / total_days  # Average per day
    
    # Average length of texts
    data['text_length'] = data['message'].apply(len)
    avg_text_length = data.groupby('sender')['text_length'].mean()
    
    # Get unique senders
    unique_senders = data['sender'].unique()
    if len(unique_senders) >= 2:
        sender_1, sender_2 = unique_senders[:2]  # Get the first two senders
        total_texts = len(data)
        sender_1_texts = len(data[data['sender'] == sender_1])
        sender_1_percentage = (sender_1_texts / total_texts) * 100 if total_texts > 0 else 0
    else:
        sender_1, sender_1_percentage = None, 0  # Handle case with less than 2 senders
    

    
    return texts_per_weekday, avg_response_time, texts_per_hour, avg_text_length, sender_1, sender_1_percentage, sender_2, 100 - sender_1_percentage

# Visualize results
def visualize_results(texts_per_weekday, texts_per_hour, avg_response_time, avg_text_length, sender_1, sender_2, sender_1_percentage, sender_2_percentage):
    # Create plots directory if it doesn't exist
    if not os.path.exists('plots'):
        os.makedirs('plots')

    # Plot percentage of texts by sender using a pie chart
    plt.figure(figsize=(8, 8))
    plt.pie([sender_1_percentage, sender_2_percentage],
            labels=[f"{sender_1} ({sender_1_percentage:.2f}%)", f"{sender_2} ({sender_2_percentage:.2f}%)"],
            autopct='%1.1f%%')
    plt.title('Percentage of Texts by Sender')
    plt.savefig('plots/percentage_of_texts_by_sender.png')  # Save the plot
    plt.close()  # Close the plot to free memory

    # Plot average response time for each sender using columns
    plt.figure(figsize=(12, 6))
    avg_response_time_sender = avg_response_time.reset_index()  # Reset index to get sender names
    plt.bar(avg_response_time_sender['sender'], avg_response_time_sender['response_time'], color=['red', 'green'])
    plt.title('Average Response Time by Sender')
    plt.xlabel('Sender')
    plt.ylabel('Average Response Time (min)')
    plt.savefig('plots/average_response_time_by_sender.png')  # Save the plot
    plt.close()  # Close the plot to free memory

    # Plot average texts per weekday for each sender with dot lines
    plt.figure(figsize=(12, 6))
    for sender in texts_per_weekday.columns:
        plt.plot(texts_per_weekday.index, texts_per_weekday[sender], marker='o', linestyle='-', label=sender)
    plt.title('Average Texts per Weekday by Sender')
    plt.xlabel('Weekday')
    plt.ylabel('Average Number of Texts per Week')
    plt.xticks(rotation=45)
    plt.legend(title='Sender')
    plt.savefig('plots/average_texts_per_weekday_by_sender.png')  # Save the plot
    plt.close()  # Close the plot to free memory

    # Plot average texts per hour for each sender with dot lines
    plt.figure(figsize=(12, 6))
    for sender in texts_per_hour.columns:
        plt.plot(texts_per_hour.index, texts_per_hour[sender], marker='o', linestyle='-', label=sender)
    plt.title('Average Texts per Hour by Sender')
    plt.xlabel('Hour of Day')
    plt.ylabel('Average Number of Texts per Day')
    plt.xticks(rotation=45)
    plt.legend(title='Sender')
    plt.savefig('plots/average_texts_per_hour_by_sender.png')  # Save the plot
    plt.close()  # Close the plot to free memory

    # Plot average text length for each sender
    plt.figure(figsize=(12, 6))
    avg_text_length_sender = avg_text_length.reset_index()  # Reset index to get sender names
    plt.bar(avg_text_length_sender['sender'], avg_text_length_sender['text_length'], color=['red', 'green'])
    plt.title('Average Text Length by Sender')
    plt.xlabel('Sender')
    plt.ylabel('Average Text Length (chars)')
    plt.savefig('plots/average_text_length_by_sender.png')  # Save the plot
    plt.close()  # Close the plot to free memory

def concatenate_plots(texts_per_weekday, texts_per_hour, avg_response_time, avg_text_length, sender_1, sender_2, sender_1_percentage, sender_2_percentage):
    # Create a figure with a grid of subplots
    fig, axs = plt.subplots(3, 2, figsize=(15, 15))  # 3 rows, 2 columns

    # Plot average texts per weekday for each sender with dot lines
    for sender in texts_per_weekday.columns:
        axs[0, 0].plot(texts_per_weekday.index, texts_per_weekday[sender], marker='o', linestyle='-', label=sender)
    axs[0, 0].set_title('Average Texts per Weekday by Sender')
    axs[0, 0].set_xlabel('Weekday')
    axs[0, 0].set_ylabel('Average Number of Texts per Week')
    axs[0, 0].legend(title='Sender')
    axs[0, 0].grid()

    # Plot average texts per hour for each sender with dot lines
    for sender in texts_per_hour.columns:
        axs[0, 1].plot(texts_per_hour.index, texts_per_hour[sender], marker='o', linestyle='-', label=sender)
    axs[0, 1].set_title('Average Texts per Hour by Sender')
    axs[0, 1].set_xlabel('Hour of Day')
    axs[0, 1].set_ylabel('Average Number of Texts per Day')
    axs[0, 1].legend(title='Sender')
    axs[0, 1].grid()

    # Plot average response time for each sender
    avg_response_time_sender = avg_response_time.reset_index()  # Reset index to get sender names
    axs[1, 0].bar(avg_response_time_sender['sender'], avg_response_time_sender['response_time'], color=['red', 'green'])
    axs[1, 0].set_title('Average Response Time by Sender')
    axs[1, 0].set_xlabel('Sender')
    axs[1, 0].set_ylabel('Average Response Time (min)')
    axs[1, 0].grid()

    # Plot average text length for each sender
    avg_text_length_sender = avg_text_length.reset_index()  # Reset index to get sender names
    axs[1, 1].bar(avg_text_length_sender['sender'], avg_text_length_sender['text_length'], color=['red', 'green'])
    axs[1, 1].set_title('Average Text Length by Sender')
    axs[1, 1].set_xlabel('Sender')
    axs[1, 1].set_ylabel('Average Text Length (chars)')
    axs[1, 1].grid()

    # Plot percentage of texts by sender using a pie chart
    axs[2, 0].pie([sender_1_percentage, sender_2_percentage],
                  labels=[f"{sender_1} ({sender_1_percentage:.2f}%)", f"{sender_2} ({sender_2_percentage:.2f}%)"],
                  autopct='%1.1f%%')
    axs[2, 0].set_title('Percentage of Texts by Sender')

    # Hide the empty subplot (if any)
    axs[2, 1].axis('off')

    # Adjust layout
    plt.tight_layout()
    plt.savefig('plots/summary.png')  # Save the combined plot
    plt.close()  # Close the plot to free memory

def plot(results):
    visualize_results(results[0], results[2], results[1], results[3], results[4], results[6], results[5], results[7])
    concatenate_plots(results[0], results[2], results[1], results[3], results[4], results[6], results[5], results[7])

# Main function
if __name__ == '__main__':
    # Replace with your desired input file paths and output file path
    input_files = ['data/message_1.html', 'data/message_2.html', 'data/message_3.html', 'data/message_4.html', 'data/message_5.html']  # Replace with your input file path
    output_file = 'data/chat_history.csv'  

    html_to_csv(input_files, output_file)
    chat_data = load_chat_history(output_file)
    """
    sender1 = "Bob"
    sender2 = "Amigo"
    time_diff = 16 (e.g. in China time, since the default time is PST)
    you can specificy sender names and time difference, and pass them 
    in the following line
    """
    results = analyze_chat(chat_data)
    
    # Visualize results
    plot(results)