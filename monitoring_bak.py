#!/usr/bin/python3
#import 
import RPi.GPIO as GPIO 
import time 
import sys
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from datetime import datetime
import pytz
import threading
import board
import busio
  
# Define GPIO to LCD mapping # Setup 
# ini disesuaikan
LCD_RS = 21 
LCD_E  = 20
LCD_D4 = 16 
LCD_D5 = 12 
LCD_D6 = 1
LCD_D7 = 7
channel = ADS.P0 # pake ads di channel 0
servoPIN = 24
relayPIN = 22
# batas

##i2c = busio.I2C(board.SCL, board.SDA)
##ads = ADS.ADS1115(i2c)

# Define some device constants 
LCD_WIDTH = 16    # Maximum characters per line 
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line 
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line 
# Timing constants 
E_PULSE = 0.0005 
E_DELAY = 0.0005 

# GPIO Setup
GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers 
  
GPIO.setup(LCD_E, GPIO.OUT)  # E 
GPIO.setup(LCD_RS, GPIO.OUT) # RS 
GPIO.setup(LCD_D4, GPIO.OUT) # DB4 
GPIO.setup(LCD_D5, GPIO.OUT) # DB5 
GPIO.setup(LCD_D6, GPIO.OUT) # DB6 
GPIO.setup(LCD_D7, GPIO.OUT) # DB7 
GPIO.setup(relayPIN, GPIO.OUT)
GPIO.setup(servoPIN, GPIO.OUT)
p = GPIO.PWM(servoPIN, 50) # PWM with 50Hz
p.start(2.5) # Initialization

global_ph = 0
  
def main():
  global global_ph
  # program utama yg berjalan terus menerus
  # mengambil nilai tegangan analog dari digital to analog converter
##    tegangan = read_voltage(channel)
  # convert tegangan menjadi ph
##    global_ph = convert2ph(tegangan)
  # tampilkan di lcd line bawah
##    lcd_string("PH Air: " + str(global_ph),LCD_LINE_2)

  # ambil tanggal dan waktu sekarang
  now = datetime.now()
  now = now.replace(tzinfo = pytz.utc)
  now = now.astimezone(pytz.timezone("Asia/Jakarta"))
  # dd/mm/YY H:M:S, sesuaikan formatnya
  dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
  # tampilkan tanggal dan waktu di line atas
  lcd_string(dt_string,LCD_LINE_1)

  # cek waktu matiin lampu setiap diatas jam 10 dan kurang dari jam 5
  hour = now.strftime("%H")
  if(int(hour) > 18 and int(hour) < 5):
    relayOn() # nyalakan lampu
  else:
    relayOff() # matikan lampu

  print('akhir program utama')
  # batas program utama
  global_ph += 1
  if global_ph > 999:
    global_ph = 0

def lcd_init():
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise 
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise 
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction 
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size 
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display 
  time.sleep(E_DELAY) 
  
def lcd_byte(bits, mode):   
  GPIO.output(LCD_RS, mode) # RS 
  GPIO.output(LCD_D4, False) 
  GPIO.output(LCD_D5, False) 
  GPIO.output(LCD_D6, False) 
  GPIO.output(LCD_D7, False) 
  if bits&0x10==0x10: 
    GPIO.output(LCD_D4, True) 
  if bits&0x20==0x20: 
    GPIO.output(LCD_D5, True) 
  if bits&0x40==0x40: 
    GPIO.output(LCD_D6, True) 
  if bits&0x80==0x80: 
    GPIO.output(LCD_D7, True) 
  
  lcd_toggle_enable() 
  
  GPIO.output(LCD_D4, False) 
  GPIO.output(LCD_D5, False) 
  GPIO.output(LCD_D6, False) 
  GPIO.output(LCD_D7, False) 
  if bits&0x01==0x01: 
    GPIO.output(LCD_D4, True) 
  if bits&0x02==0x02: 
    GPIO.output(LCD_D5, True) 
  if bits&0x04==0x04: 
    GPIO.output(LCD_D6, True) 
  if bits&0x08==0x08: 
    GPIO.output(LCD_D7, True) 
  
  lcd_toggle_enable() 
  
def lcd_toggle_enable(): 
  time.sleep(E_DELAY) 
  GPIO.output(LCD_E, True) 
  time.sleep(E_PULSE) 
  GPIO.output(LCD_E, False) 
  time.sleep(E_DELAY) 
  
def lcd_string(message,line): 
  message = message.ljust(LCD_WIDTH," ") 
  lcd_byte(line, LCD_CMD) 
  for i in range(LCD_WIDTH): 
    lcd_byte(ord(message[i]),LCD_CHR)

def read_voltage(channel):
  buf = list()    
  for i in range(10): # Take 10 samples
    chan = AnalogIn(ads, channel)
    buf.append(chan.voltage)
  buf.sort() # Sort samples and discard highest and lowest
  buf = buf[2:-2]
  avg = (sum(map(float,buf))/6) # Get average value from remaining 6
  print(round(avg,2),'V')
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
    print('besar ph: ', ph)
    return ph

def turnServo():
    p.ChangeDutyCycle(5) # servo
    time.sleep(2)
    p.ChangeDutyCycle(90)

def giveFood():
    # dibuat thread agar saat delay 2 detik tidak mempengaruhi proses yang lain
    x = threading.Thread(target=turnServo)
    x.start()

def relayOn():
    GPIO.output(relayPIN, GPIO.HIGH) # relay

def relayOff():
    GPIO.output(relayPIN, GPIO.LOW) # relay

def exit():
    lcd_byte(0x01, LCD_CMD) 
    lcd_string("Goodbye!",LCD_LINE_1) 
    GPIO.cleanup()

if __name__ == '__main__': 
  try: 
    lcd_init() # Initialise display
    while True:
      main()
  except KeyboardInterrupt:
    print("exited")
    pass 
  finally:
    exit()
