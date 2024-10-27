import csv

class BinanceAPIKeys:
    """
    A class to handle reading and writing Binance API keys from/to a CSV file.

    Attributes:
        csv_file_path (str): The path to the CSV file containing the API keys.
        api_key (str): The Binance API key.
        api_secret (str): The Binance API secret key.

    Methods:
        __init__(csv_file_path='.coindashboard_config/.binance_api_keys.csv'):
            Initializes the BinanceAPIKeys instance with the given CSV file path and reads the keys.
        
        read_keys():
            Reads the API keys from the CSV file and sets the api_key and api_secret attributes.
        
        write_keys(api_key, api_secret):
            Writes the given API keys to the CSV file and updates the api_key and api_secret attributes.
    """
    def __init__(self, csv_file_path='.coindashboard_config/.binance_api_keys.csv'):
        self.csv_file_path = csv_file_path
        self.api_key = None
        self.api_secret = None
        self.read_keys()

    def read_keys(self):
        """Reads the API keys from the CSV file."""
        try:
            with open(self.csv_file_path, mode='r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.api_key = row['api_key']
                    self.api_secret = row['api_secret']
                    break  # Only read the first row
            print(f"API keys read successfully from {self.csv_file_path}.")
        except FileNotFoundError:
            print(f"File {self.csv_file_path} not found. Please ensure the file exists.")
        except KeyError as e:
            print(f"Missing column in CSV: {e}. Ensure the CSV has 'api_key' and 'api_secret'.")
        except Exception as e:
            print(f"An error occurred while reading the CSV file: {e}")

    def write_keys(self, api_key, api_secret):
        """Writes the API keys to the CSV file."""
        try:
            with open(self.csv_file_path, mode='w', newline='') as csvfile:
                fieldnames = ['api_key', 'api_secret']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                writer.writerow({'api_key': api_key, 'api_secret': api_secret})

            self.api_key = api_key
            self.api_secret = api_secret
            print(f"API keys updated successfully in {self.csv_file_path}.")
        except Exception as e:
            print(f"An error occurred while writing to the CSV file: {e}")
