# Instagram Chat Analysis 

## Overview
This script analyzes chat history from CSV files generated from Instagram chat export (in HTML). It provides insights into text message distribution, average response times, and sender statistics through visualizations.


## Installation
You can install the required packages using pip:
pip install -r requirements.txt


## Usage

1. **Prepare Input Files**: Ensure you have your chat history in HTML format by exporting from your instagram account. Place them in the `data` directory. The script is set to read a list of HTML files. For example:
   - `data/message_1.html`
   - `data/message_2.html`
   - `data/message_3.html`
   - `data/message_4.html`
   - `data/message_5.html`

2. **Specify Senders and Time Difference**: 
   - You can specify the sender names and the time difference in the main function. Otherwise the default time is in PST with sender names read from the chat history. This is how you can do it in chat_analysis.py:
     ```python
     sender1 = "Z"
     sender2 = "A"
     time_diff = 16  # e.g. convert to China time
    results = analyze_chat(chat_data, sender1 = sender1, sender2 = sender2, time_diff = time_diff)
     ```

3. **Run the Script**: Execute the script from the command line:
   ```bash
   python chat_analysis.py
   ```

4. **Output**: The script generates visualizations saved in the `plots` directory, including:
   - Percentage of texts by sender
   - Average response time and text length by sender
   - Average texts per weekday and hour


## License
This project is licensed under the MIT License.