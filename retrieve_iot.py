from web3 import Web3
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Konfigurasi Web3
w3 = Web3(Web3.HTTPProvider('http://10.6.6.11:6102', request_kwargs={'timeout': 60}))
abi=[{'inputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'name': 'dataList', 'outputs': [{'internalType': 'uint256', 'name': 'timestamp', 'type': 'uint256'}, {'internalType': 'string', 'name': 'data', 'type': 'string'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'getDataCount', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': '_index', 'type': 'uint256'}], 'name': 'retrieveData', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}, {'internalType': 'string', 'name': '', 'type': 'string'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'string', 'name': '_data', 'type': 'string'}], 'name': 'storeData', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}]

contract_address = '0xb52dCdf7DF184074087189897EcF8FdfCC830390'

def get_contract():
    """Membuat dan mengembalikan kontrak dengan error handling"""
    try:
        return w3.eth.contract(address=contract_address, abi=abi)
    except Exception as e:
        print(f"Error connecting to contract: {e}")
        return None

def get_data_count(contract, max_retries=3, delay=2):
    """Mendapatkan jumlah data dengan retry mechanism"""
    for attempt in range(max_retries):
        try:
            return contract.functions.getDataCount().call()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            print(f"Attempt {attempt + 1} failed. Retrying in {delay} seconds...")
            time.sleep(delay)

def retrieve_single_data(contract, index):
    """Mengambil data tunggal dengan error handling"""
    try:
        return contract.functions.retrieveData(index).call()
    except Exception as e:
        print(f"Error retrieving data at index {index}: {e}")
        return None, None

def display_data(index, timestamp, data):
    """Menampilkan data dalam format yang rapi"""
    if timestamp and data:
        dt = datetime.fromtimestamp(timestamp)
        print(f"{index}. [ {dt.strftime('%Y-%m-%d %H:%M:%S')} ] - {data}")

def monitor_blockchain_data(interval=10):
    """Fungsi utama dengan while loop untuk continuous monitoring"""
    print("Starting blockchain data monitor...")
    print("Press Ctrl+C to stop\n")

    contract = get_contract()
    if not contract:
        return

    last_count = 0
    try:
        while True:
            start_time = time.time()

            try:
                current_count = get_data_count(contract)

                if current_count > last_count:
                    print(f"\nNew data detected! Total entries: {current_count}")
                    print("Retrieving new data...")

                    # Hanya ambil data baru saja
                    new_data_indices = range(last_count, current_count)

                    # Gunakan thread pool untuk mengambil data baru secara paralel
                    with ThreadPoolExecutor() as executor:
                        results = list(executor.map(
                            lambda i: (i, *retrieve_single_data(contract, i)),
                            new_data_indices
                        ))

                    # Tampilkan data baru
                    for index, timestamp, data in results:
                        display_data(index, timestamp, data)

                    last_count = current_count
                else:
                    print(f"No new data. Current count: {current_count}", end='\r')

            except Exception as e:
                print(f"\nError during monitoring: {e}")
                print("Reconnecting...")
                contract = get_contract()
                if not contract:
                    print("Failed to reconnect. Exiting.")
                    break

            # Hitung waktu yang dibutuhkan dan sesuaikan delay
            processing_time = time.time() - start_time
            sleep_time = max(0, interval - processing_time)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")

if __name__ == "__main__":
    monitor_blockchain_data(interval=5)  # Periksa setiap 5 detik