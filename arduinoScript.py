import serial
import time

ser = serial.Serial('/dev/cu.usbmodem1301', 9600)

speed = -150
delay_time = 1000  # Example delay time in milliseconds

time.sleep(2)
ser.write(f"SPEED:{speed}\n".encode('utf-8'))
time.sleep(1)
ser.write(f"DELAY:{delay_time}\n".encode('utf-8'))
time.sleep(1)
ser.write("START\n".encode('utf-8'))

exit()