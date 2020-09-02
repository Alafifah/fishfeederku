#!/usr/bin/python3
#import 
#import RPi.GPIO as GPIO
import pigpio
import time 
import sys
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from datetime import datetime
import pytz
import threading
import board
import busio
import lcd_i2c
  
# Define GPIO to LCD mapping # Setup 
# ini disesuaikan
channel = ADS.P0 # pake ads di channel 0
servoPIN = 24
relayPIN = 22
# batas

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

# GPIO Setup
##GPIO.setwarnings(False) 
##GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers 
##
##GPIO.setup(relayPIN, GPIO.OUT)
##GPIO.setup(servoPIN, GPIO.OUT)
##p = GPIO.PWM(servoPIN, 50) # PWM with 50Hz
##p.start(2.5) # Initialization
pi = pigpio.pi()
pi.set_mode(servoPIN, pigpio.OUTPUT)
pi.set_mode(relayPIN, pigpio.OUTPUT)

pi.set_servo_pulsewidth(servoPIN, 0)

global_ph = 0
lcd = lcd_i2c.lcd()
lcd.lcd_clear()
  
def main():
  global global_ph
  # program utama yg berjalan terus menerus
  # mengambil nilai tegangan analog dari digital to analog converter
  tegangan = read_voltage(channel)
  # convert tegangan menjadi ph
  global_ph = convert2ph(tegangan)
  # tampilkan di lcd line bawah
  lcd.lcd_display_string("PH Air:         ",2,0)
  lcd.lcd_display_string(str(global_ph),2,8)

  # ambil tanggal dan waktu sekarang
  now = datetime.now()
  #now = now.replace(tzinfo = pytz.utc)
  #now = now.astimezone(pytz.timezone("Asia/Jakarta"))
  # dd/mm/YY H:M:S, sesuaikan formatnya
  dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
  # tampilkan tanggal dan waktu di line atas
  lcd.lcd_display_string(dt_string,1,0)

  # cek waktu matiin lampu setiap diatas jam 10 dan kurang dari jam 5
  hour = now.strftime("%H")
##  if(int(hour) > 18 and int(hour) < 5):
##    relayOn() # nyalakan lampu
##  else:
##    relayOff() # matikan lampu

##  print('akhir program utama')
  # batas program utama
  global_ph += 1
  if global_ph > 999:
    global_ph = 0

def read_voltage(channel):
  buf = list()    
  for i in range(10): # Take 10 samples
    chan = AnalogIn(ads, channel)
    buf.append(chan.voltage)
  buf.sort() # Sort samples and discard highest and lowest
  buf = buf[2:-2]
  avg = (sum(map(float,buf))/6) # Get average value from remaining 6
##  print(round(avg,2),'V')
  return (round(avg,2))

def convert2ph(voltage):
    ''' pakai rumus y = mx + b seperti di web, ubah sesuai yang telah diukur '''
    x1 = 3.11 # nilai analog saat memakai referensi tegangan sebesar y1
    y1 = 4.01 # tegangan referensi pertama

    x2 = 2.58 # nilai analog saat memakai referensi tegangan sebesar y2
    y2 = 7.00 # tegangan referensi kedua

    m = (y2-y1) / (x2-x1)
    b = y1 - (m*x1) # mencari nilai b menggunakan tegangan referensi pertama

    ph = m*voltage + b
##    print('besar ph: ', ph)
    return ph

def turnServo():
##    p.ChangeDutyCycle(5) # servo
    pi.set_servo_pulsewidth(servoPIN, 600)
    time.sleep(2)
##    p.ChangeDutyCycle(90)
    pi.set_servo_pulsewidth(servoPIN, 2400)

def giveFood():
    # dibuat thread agar saat delay 2 detik tidak mempengaruhi proses yang lain
    x = threading.Thread(target=turnServo)
    x.start()

def relayOn():
##    GPIO.output(relayPIN, GPIO.HIGH) # relay
    pi.write(relayPIN, 1)

def relayOff():
##    GPIO.output(relayPIN, GPIO.LOW) # relay
    pi.write(relayPIN, 0)

def exit():
    lcd.lcd_display_string("Good bye        ",1,0)
##    GPIO.cleanup()

if __name__ == '__main__': 
  try: 
    while True:
      main()
  except KeyboardInterrupt:
    print("exited")
    pass 
  finally:
    exit()
