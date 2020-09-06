import websocket
import threading
from time import sleep
import json
import monitoring
from urllib.request import urlopen

hwId = "unik"
hwKey = "pass"
serverAddress = "ws://13.68.217.149:8080"
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
                        monitoring.lcd.lcd_display_string("Nyala remoted   ",1,0)
                    else:
                        monitoring.relayOff()
                        monitoring.lcd.lcd_display_string("Mati remoted    ",1,0)
                    sleep(2)
                    
                if feed == True:
                    monitoring.lcd.lcd_display_string("Makan remoted   ",1,0)
                    monitoring.turnServo()
                    feed = False

                monitoring.main()

            except KeyboardInterrupt:
                exit()
                    
            except Exception as ex:
                print(ex)
                raise ValueError("exit")

def isInternet():
    try:
        response = urlopen('https://google.com', timeout=10)
        return True
    except:
        return False

if __name__ == "__main__":
    
    while (isInternet() == False):
        print('reconnecting')
        sleep(1)
    
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
                "ph": f"{monitoring.global_ph:,.3f}",
                "lamp": lamp
            })
            ws.send(payload)
            print("sent")
            sleep(1)
            
    except Exception as ex:
        runThread = False
        exit()
