import serial
import os
import csv
from datetime import datetime
import argparse

# Default configuration
DEFAULT_SERIAL_PORT = '/dev/ttyACM0'   # replace if needed
BAUD_RATE = 115200
OUTPUT_TMPL = 'uwb_dataset_'

# Map of board addresses to real distances (mm)
addresses_to_distance = {
    ('46BA', '0A1D'): 820,
    ('46BA', '541D'): 1440,
    ('46BA', '1DB5'): 1710,
    ('0A1D', '46BA'): 820,
    ('0A1D', '541D'): 1375,
    ('0A1D', '1DB5'): 1300,
    ('541D', '46BA'): 1440,
    ('541D', '0A1D'): 1375,
    ('541D', '1DB5'): 6620,
    ('1DB5', '46BA'): 1710,
    ('1DB5', '0A1D'): 1300,
    ('1DB5', '541D'): 620,
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
    try:
        parts = line.split(' ')
        addr = parts[1].split('>')[1].upper()

        measured_distances = parts[2].split('/')
        measure_distance = int(measured_distances[0])
        measure_distance_no_drift = int(measured_distances[1])

        drift = int(parts[3].split(':')[1])

        ip = parts[4].split(':')[1].split('/')
        fp_power = int(ip[0])
        rx_power = int(ip[1])

        return addr, measure_distance, measure_distance_no_drift, drift, fp_power, rx_power

    except IndexError as e:
        print(e)
        return 0, 0, 0, 0, 0, 0


def main():
    args = parse_args()
    ser = open_serial(args.port)

    source_addr = args.addr.upper()
    output_csv = OUTPUT_TMPL + source_addr + '.csv'

    # Count number of lines
    if os.path.exists(output_csv):
        with open(output_csv, 'r', newline='') as f:
            lines = sum(1 for _ in f)
    else:
        lines = 0

    with open(output_csv, mode='a', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Empty file
        if lines == 0:
            writer.writerow(['timestamp', 'measured_distance_mm', 'measured_distance_without_drift_mm', 'true_distance_mm', 'drift_ppm', 'FP_power', 'RX_power'])
            lines += 1

        try:
            samples = lines-1
            while samples < 5000*3*2:
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
                samples += 1
            ser.close()

        except KeyboardInterrupt:
            print("Stopping logging...")
            ser.close()

if __name__ == '__main__':
    main()
