import pigpio, time

ser = 27

pi = pigpio.pi()
pi.set_mode(ser, pigpio.OUTPUT)
pi.set_PWM_frequency(ser, 50)
pi.set_servo_pulsewidth(ser, 0)

while True:
    for i in range(500, 2500):
        pi.set_servo_pulsewidth(ser, i)
        time.sleep(.005)
        print(i)
    print("kanan")
    for i in range(2500, 500, -1):
        pi.set_servo_pulsewidth(ser, i)
        time.sleep(.005)
        print(i)
    print("kiri")
