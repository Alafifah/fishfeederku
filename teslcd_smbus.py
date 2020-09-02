import lcd_i2c

lcd = lcd_i2c.lcd()
lcd.lcd_display_string("Hello World!", 2, 3)
