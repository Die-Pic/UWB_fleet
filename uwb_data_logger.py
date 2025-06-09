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
    ('ABCD', '1234'): 1000,
    ('ABCD', '5678'): 1000,
    ('1234', '5678'): 1500,
    ('46BA', '541D'): 800,
    ('541D', '46BA'): 800,
}   # TODO add mappings here


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
    # TODO just an example, add parse actual line to values
    parts = line.split(' ')
    addr = parts[1].split('>')[1]
    raw = parts[2]
    print("addr:",addr, "raw:", raw)

    # Check measuring is correct
    if raw == 'RNG':
        return 0, 0

    raw = int(raw)
    #pwr = float(parts[2])
    return raw, addr, 0


def main():
    args = parse_args()
    ser = open_serial(args.port)

    source_addr = args.addr
    output_csv = OUTPUT_TMPL + source_addr + '.csv'

    with open(output_csv, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'raw_distance_m', 'true_distance_m', 'power'])

        try:
            while True:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if not line:
                    continue

                target_address, raw_dist, power = parse_line(line)

                if raw_dist == 0:
                    continue

                true_dist = addresses_to_distance[(source_addr, target_address)]
                if true_dist is None:
                    print(f"Unknown address {target_address}, skipping")
                    continue

                timestamp = datetime.now().isoformat()
                writer.writerow([timestamp, f"{raw_dist:.3f}", f"{true_dist:.3f}", power])
                csvfile.flush()
                print(f"Logged: {timestamp}, raw={raw_dist:.3f}, true={true_dist:.3f}, pwr={power}")

        except KeyboardInterrupt:
            print("Stopping logging...")
            ser.close()

if __name__ == '__main__':
    main()
