import serial
import csv
from datetime import datetime
import argparse

# Default configuration
DEFAULT_SERIAL_PORT = '/dev/ttyACM0'   # replace if needed
BAUD_RATE = 115200                     # fixed baud rate
OUTPUT_TMPL = 'uwb_dataset_'

# Map of board addresses to real distances (mm)
addresses_to_distance = {
    ('46BA', '0A1D'): 1300,
    ('46BA', '541D'): 1430,
    ('46BA', '1DB5'): 1310,
    ('0A1D', '46BA'): 1300,
    ('0A1D', '541D'): 1260,
    ('0A1D', '1DB5'): 1910,
    ('541D', '46BA'): 1430,
    ('541D', '0A1D'): 1260,
    ('541D', '1DB5'): 935,
    ('1DB5', '46BA'): 1310,
    ('1DB5', '0A1D'): 1910,
    ('1DB5', '541D'): 935,
}


def parse_args():
    parser = argparse.ArgumentParser(description='UWB distance logger')
    parser.add_argument('-port', nargs='?', default=DEFAULT_SERIAL_PORT,
                        help='Serial device path')
    parser.add_argument('-addr',
                        help='Board address',
                        default=None)
    return parser.parse_args()


def open_serial(port):
    try:
        return serial.Serial(port, BAUD_RATE, timeout=1)
    except serial.SerialException as e:
        print(f"Error opening serial port {port}: {e}")
        raise


def parse_line(line):
    parts = line.split(' ')
    print(parts)
    addr = parts[1].split('>')[1].upper()

    measured_distances = parts[2].split('/')
    if measured_distances[0] == 'RNG':
        return 0, 0, 0, 0, 0, 0
    measure_distance = int(measured_distances[0])
    measure_distance_no_drift = int(measured_distances[1])

    drift = int(parts[3].split(':')[1])

    ip = parts[4].split(':')[1].split('/')
    fp_power = int(ip[0])
    rx_power = int(ip[1])

    return addr, measure_distance, measure_distance_no_drift, drift, fp_power, rx_power


def main():
    args = parse_args()
    ser = open_serial(args.port)

    source_addr = args.addr.upper()
    output_csv = OUTPUT_TMPL + source_addr + '.csv'

    with open(output_csv, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'measured_distance_mm', 'measured_distance_without_drift_mm', 'true_distance_mm', 'drift_ppm', 'FP_power', 'RX_power'])

        try:
            while True:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if not line:
                    continue

                target_address, measure_distance, measure_distance_no_drift, drift, fp_power, rx_power = parse_line(line)
                if target_address == 0:
                    continue

                true_distance = addresses_to_distance[(source_addr, target_address)]
                if true_distance is None:
                    continue

                timestamp = datetime.now().isoformat()
                writer.writerow([timestamp, measure_distance, measure_distance_no_drift, true_distance, drift, fp_power, rx_power])
                csvfile.flush()

        except KeyboardInterrupt:
            print("Stopping logging...")
            ser.close()

if __name__ == '__main__':
    main()
