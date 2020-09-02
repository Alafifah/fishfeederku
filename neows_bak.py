import websocket
import threading
from time import sleep
import json
import monitoring

hwId = "unik"
hwKey = "pass"
serverAddress = "ws://13.67.75.133:8080"
lamp = False
llamp = True #untuk menyimpan perintah yg sebelumnya
feed = False
runThread = True

lock = threading.Lock()
def on_message(ws, message):
    global lamp
    global feed
    print(message)
    with lock:
        try:
            jObj = json.loads(message)
            if(jObj["command"] == "TOGGLELAMP"):
                lamp = True if lamp == False else False
                pass
            if(jObj["command"] == "FEED"):
                feed = True 
                pass
            
        except Exception as ex:
            print(ex)

def on_close(ws):
    print("### closed ###")

def to_hardware():
    global lamp
    global llamp
    global feed
    global runThread
    while runThread:
        sleep(1)
        with lock:
            try:
                if lamp != llamp:
                    llamp = lamp
                    if lamp == True:
                        monitoring.relayOn()
                        monitoring.lcd_string("Nyala remoted",monitoring.LCD_LINE_1)
                    else:
                        monitoring.relayOff()
                        monitoring.lcd_string("Mati remoted",monitoring.LCD_LINE_1)
                    sleep(2)
                    
                if feed == True:
                    monitoring.lcd_string("Makan remoted",monitoring.LCD_LINE_1)
                    monitoring.turnServo()
                    feed = False

                monitoring.main()

            except KeyboardInterrupt:
                exit()
                    
            except Exception as ex:
                print(ex)
                raise ValueError("exit")

if __name__ == "__main__":
    try: 
        # websocket.enableTrace(True)
        ws = websocket.WebSocketApp(serverAddress, on_message = on_message, on_close = on_close)
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()

        hwt = threading.Thread(target=to_hardware)
        hwt.daemon = True
        hwt.start()

        conn_timeout = 5
        while not ws.sock.connected and conn_timeout:
            sleep(1)
            conn_timeout -= 1

        print('Connection stablished. Client correcly connected')
        jsondata = json.JSONEncoder().encode({
            "type": "register",
            "ishw": True,
            "uniqueid": hwId,
            "uniquekey": hwKey
        })
        print(jsondata)
        ws.send(jsondata)

        while ws.sock.connected:
            payload = json.JSONEncoder().encode({
                "type": "feedback",
                "ph": str(monitoring.global_ph),
                "lamp": lamp
            })
            ws.send(payload)
            sleep(1)
            
    except Exception as ex:
        runThread = False
        exit()
