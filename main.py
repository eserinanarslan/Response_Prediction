import os
import pandas as pd
import logging
import configparser
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify
import sys  # Import sys module for handling stream output

# Create a 'logs' directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set the logging level to DEBUG
logger = logging.getLogger(__name__)  # Create a logger instance for this module

# Add a file handler to save logs to a file
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

# Add a StreamHandler to redirect error messages to the terminal
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setLevel(logging.ERROR)
logger.addHandler(stream_handler)

# Read configuration from config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

# Read data from files
result_path = config['Paths']['result_path']
text_path = config['Paths']['text_path']
try:
    df = pd.read_csv(result_path)
    text = pd.read_csv(text_path)
    logger.info('Data loaded successfully from results.csv')
except Exception as e:
    logger.error(f'Error loading data from results.csv: {str(e)}')
    raise

# Function to format the columns
def column_format(data, text):
    try:
        data['response_score'] = data['response_score'].apply(lambda x: '{:.5f}'.format(x))
        text['response_score'] = text['response_score'].apply(lambda x: '{:.5f}'.format(x))

    except Exception as e:
        logger.error(f"Error formatting columns: {e}")
    return data, text

# Apply column formatting
df, text = column_format(df, text)

# Method to get random 50 records based on credentials
@app.route('/get_random_records', methods=['GET'])
def get_random_records():
    username = request.args.get('username')
    password = request.args.get('password')

    if not username or not password:
        logger.error('No username or password provided in the request')
        return jsonify({'error': 'Please provide both username and password parameters'}), 400

    valid_users = dict(config['Users'])
    if username in valid_users and valid_users[username] == password:
        try:
            # Retrieve 50 random records from the DataFrame
            random_records = df.sample(n=50)
            return jsonify(random_records.to_dict(orient='records'))
        except Exception as e:
            logger.error(f'Error fetching random records: {str(e)}')
            return jsonify({'error': 'An error occurred while processing the request'}), 500
    else:
        logger.warning('Invalid username or password')
        return jsonify({'error': 'Invalid username or password'}), 403

# Existing method to get predictions based on ID
@app.route('/get_prediction', methods=['GET'])
def get_predictions():
    id = request.args.get('id')
    if id is None:
        logger.error('No ID provided in the request')
        return jsonify({'error': 'Please provide id parameter'}), 400
    else:
        try:
            # Check if the provided id exists in the DataFrame
            if int(id) not in df['id'].values:
                logger.error('ID not found in the dataset')
                return jsonify({'error': 'ID not found in the dataset'}), 404

            # Filter DataFrame based on id and select required columns
            result = df[df['id'] == int(id)][['id', 'actual_response', 'response_score',
                                              'rf_prediction', 'xgb_prediction',
                                              'nb_prediction', 'nb_isotonic_prediction', 'nb_sigmoid_prediction']]
            return jsonify(result.to_dict(orient='records'))
        except Exception as e:
            logger.error(f'Error processing request: {str(e)}')
            return jsonify({'error': 'An error occurred while processing the request'}), 500

# Existing method to authenticate user and return responses
@app.route('/post_predictions', methods=['POST'])
def authenticate_user():
    # Get JSON data from the request
    request_data = request.json

    # Log the raw incoming request for debugging
    logger.debug(f"Received data: {request_data}")

    # Check if request_data is a list
    if isinstance(request_data, list):
        responses = []

        for item in request_data:
            username = item.get('username')
            password = item.get('password')

            valid_users = dict(config['Users'])
            if username in valid_users and valid_users[username] == password:
                try:
                    response = text[['ID', 'Name', 'Description',
                                     'xgb_prediction', 'rf_prediction', 'nb_prediction',
                                     'nb_isotonic_prediction', 'nb_sigmoid_prediction',
                                     'response_score',
                                     'response_v05', 'response_v07', 'response_v09']]
                    responses.append(response.to_dict(orient='records'))
                except Exception as e:
                    logger.error(f'Error processing request: {str(e)}')
                    responses.append({'error': 'An error occurred while processing the request'})
            else:
                logger.warning('Invalid username or password')
                responses.append({'error': 'Invalid username or password'})

        return jsonify(responses)

    else:
        logger.error('Invalid JSON format: Expected a list')
        return jsonify({'error': 'Invalid JSON format: Expected a list'}), 400

if __name__ == '__main__':
    host = config['Service']['host']
    port = int(config['Service']['port'])
    debug = config.getboolean('Service', 'debug')

    app.run(host=host, port=port, debug=debug)
