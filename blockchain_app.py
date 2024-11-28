import hashlib
import random
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from flask import Flask, render_template, send_from_directory
import os

# Initialize Flask app
app = Flask(__name__)

start_time = datetime.now()
# Blockchain class to manage the chain and transactions
class Blockchain:
    def __init__(self):
        self.chain = []  # Initialize the blockchain
        self.current_transactions = []  # Current transactions in the block
        genesis_block = self.create_block(previous_hash='0', block_label='Genesis Block')
        self.chain.append(genesis_block)
    
    def add_transaction(self, sensor_id, temperature, humidity):
        """Add a transaction to the current block."""
        transaction = {
            'sensor_id': sensor_id,
            'temperature': temperature,
            'humidity': humidity,
            'timestamp': start_time
        }
        self.current_transactions.append(transaction)
    
    def add_block(self, previous_hash):
        """Create a new block and add it to the blockchain."""
        block_label = f'Block {len(self.chain)}'  # Block labeling
        new_block = self.create_block(previous_hash, block_label)
        self.chain.append(new_block)
        self.current_transactions = []  # Reset current transactions
    
    def create_block(self, previous_hash, block_label):
        """Create a block with the current transactions."""
        block = {
            'index': len(self.chain) + 1,
            'timestamp': start_time,
            'transactions': self.current_transactions,
            'previous_hash': previous_hash,
            'hash': self.calculate_hash(previous_hash),
            'label': block_label
        }
        return block
    
    def calculate_hash(self, previous_hash):
        """Calculate hash for the given block using SHA-256."""
        block_data = f"{len(self.chain)}{previous_hash}{str(self.current_transactions)}"
        return hashlib.sha256(block_data.encode('utf-8')).hexdigest()

    def simulate_tampering_without_blockchain(self, records):
        """Simulate tampering probabilities for the sensor records without blockchain."""
        tampering_probabilities = []
        for i, record in enumerate(records):
            # Base probability increases linearly
            base_probability = i / len(records) 
            # Reduced fluctuations for more controlled fluctuations
            fluctuation = random.uniform(-0.005, 0.005)  # Smaller fluctuation range
            tampering_probability = max(0, min(1, base_probability + fluctuation))  # Ensure it's between 0 and 1
            tampering_probabilities.append(tampering_probability)
        return tampering_probabilities

# Create the blockchain and simulate WSN data
blockchain = Blockchain()
num_seensors = int(input('Enter the number of sensors in the WSN Network: '))
sensor_ids = range(1, num_seensors+1)  # Simulate 1600 sensors

blockchain_data = []  # List to store blockchain data in tabular format
non_blockchain_data = [] # Data processed without blockchain

blockchain_processed_records = []  # List to store processed records count for blockchain
non_blockchain_processed_records = []  # List to store processed records count for non-blockchain

for i,sensor_id in enumerate(sensor_ids):
    temperature = random.randint(20, 40)
    humidity = random.randint(30, 99)
    blockchain.add_transaction(sensor_id, temperature, humidity)
    
    blockchain.add_block(blockchain.chain[-1]['hash'])
    
    # Collect data for the table
    #if i % blockchain.block_processing_limit == 0:
    block = blockchain.chain[-1]
    for tx in block['transactions']:
        blockchain_data.append({
            'Sensor ID': tx['sensor_id'],
            'Temperature (°C)': tx['temperature'],
            'Humidity (%)': tx['humidity'],
            'Timestamp': tx['timestamp']
        })
    blockchain_processed_records.append(i + 1)

    # Collect all data for non-blockchain processing (no delays or limits)
    non_blockchain_data.append({
        'Sensor ID': sensor_id,
        'Temperature (°C)': temperature,
        'Humidity (%)': humidity,
        'Timestamp': start_time
    })
    non_blockchain_processed_records.append(i + 1)  # Increment processed records for non-blockchain

# Convert the data to a DataFrame
df_blockchain_data = pd.DataFrame(blockchain_data)

# Simulate tampering probabilities for both with and without blockchain
tampering_probabilities_without_blockchain = blockchain.simulate_tampering_without_blockchain(df_blockchain_data['Sensor ID'])

# Blockchain tampering probability will always be 0
tampering_probabilities_with_blockchain = [0] * len(df_blockchain_data['Sensor ID'])

# Generate the tampering comparison plot
def generate_tampering_plot():
    plt.figure(figsize=(10, 6))
    
    # Plot tampering probability without blockchain (with fluctuations)
    plt.plot(df_blockchain_data['Sensor ID'], tampering_probabilities_without_blockchain, color='red', label='Without Blockchain', linestyle='-')
    
    # Plot tampering probability with blockchain (always 0)
    plt.plot(df_blockchain_data['Sensor ID'], tampering_probabilities_with_blockchain, color='green', label='With Blockchain', linestyle='-')
    
    plt.title('Tampering Probability Comparison (With vs Without Blockchain)')
    plt.xlabel('Number of Records')
    plt.ylabel('Record Tampering Probability')
    plt.grid(True)
    plt.legend(loc='upper left')
    plt.tight_layout()
    
    # Save the plot as a PNG image
    plot_file_path = 'tampering_comparison.png'
    plt.savefig(plot_file_path)
    plt.close()
    
# Generate the record comparison plot
def generate_comparison_plot():
    plt.figure(figsize=(10, 6))
    
    # Simulated time: Assume each sensor reading is taken at regular intervals (e.g., 1 unit = 1 second)
    time_intervals = range(1, len(sensor_ids) + 1)
    
    # Blockchain processes records with a delay
    blockchain_records = [i for i in time_intervals if i % 2 == 0]  # Blockchain processes half as fast
    blockchain_counts = [i for i in range(1, len(blockchain_records) + 1)]
    
    # Non-blockchain processes all records
    non_blockchain_counts = [i for i in time_intervals]
    
    plt.plot(time_intervals, non_blockchain_counts, color='red', label='Non-Blockchain (Processed Records)', linestyle='-')
    plt.plot(blockchain_records, blockchain_counts, color='green', label='Blockchain (Processed Records)', linestyle='-')
    
    plt.title('Processed Records Comparison Over Time')
    plt.xlabel('Time Interval')
    plt.ylabel('Number of Processed Records')
    plt.grid(True)
    plt.legend(loc='upper left')
    plt.tight_layout()
    
    # Save the plot as a PNG image
    plt.savefig('processed_records_comparison.png')
    plt.close()

# Generate the tampering plot when the app starts
generate_tampering_plot()

# Generate the record comparision plot when the app starts
generate_comparison_plot()

# Flask route to render the table
@app.route('/')
def index():
    # Render the table in HTML format
    return render_template('index.html', table_data=df_blockchain_data.to_html(classes='data', header=True, index=False))

# Flask route to display the plot
@app.route('/plot1')
def plot1():
    # Serve the plot image
    return send_from_directory(os.getcwd(), 'tampering_comparison.png')

@app.route('/plot2')
def plot2():
    # Serve the plot image
    return send_from_directory(os.getcwd(), 'processed_records_comparison.png')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
