# AmongUs Controller V2
# Now supports "fine" control of the mouse via JoystickR (Pressing the Joystick results in left click)

import inputs
import pynput
import threading
import time

JOYSTICK = [0,0]
JOYSTICKR = [0,0]
LAST_Z_STATE = 0

MAX_JOYSTICK_N = (2**15)-1
MAX_MOUSE_MOV = 40

MENU_BUTTON_POS = (1610,70) # May (/will) need to be changed [this is for 1680x1050 resolution, since that's my current monitor's]

class MouseMovThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.joystickR = [0,0]
        self.mouse = pynput.mouse.Controller()
        
        self.daemon = True
        pass

    def run(self):
        joystickMouseRatio = MAX_MOUSE_MOV / MAX_JOYSTICK_N
        while True:
            self.mouse.move(
                self.joystickR[0] * joystickMouseRatio,
                -self.joystickR[1] * joystickMouseRatio
            )
            time.sleep(1/60)
            pass
        pass

MOUSETHREAD = MouseMovThread()
MOUSETHREAD.start()

def walk(event : inputs.InputEvent):
    global JOYSTICK
    if event.ev_type == "Absolute":
        if event.code == "ABS_X":
            if event.state > 0: return ("d",True)
            elif event.state < 0: return ("a",True)
            else: return ("da", False)

            pass
        elif event.code == "ABS_Y":
            if event.state > 0: return ("w",True)
            elif event.state < 0: return ("s",True)
            else: return ("ws",False)
        elif event.code == "ABS_HAT0X":
            if event.state == -1:
                return ("a",True)
            elif event.state == 1:
                return ("d",True)
            else:
                return ("da",False)
        elif event.code == "ABS_HAT0Y":
            if event.state == 1: return ("s",True)
            elif event.state == -1: return ("w",True)
            else: return("ws",False)
        pass

    return None

def useAndStuff(event : inputs.InputEvent):
    global LAST_Z_STATE
    if event.code in ("ABS_Z","BTN_TL"):
        if event.state != 0:
            return "q"
    elif event.code in ("ABS_RZ","BTN_TR"):
        if event.state != 0 and LAST_Z_STATE == 0:
            LAST_Z_STATE = event.state
            return "e"
        else: LAST_Z_STATE = event.state
        
    elif event.code in ("BTN_EAST"):
        if event.state != 0: 
            return "r"
    elif event.code in ("BTN_WEST"):
        if event.state != 0:
            return pynput.keyboard.Key.tab
    elif event.code in ("BTN_SELECT"):
        if event.state != 0:
            return MENU_BUTTON_POS # May need to be changed depending on Resolution
    return None

def mouseControl(event : inputs.InputEvent):
    if event.code == "ABS_RX":
        return ((event.state,None),0)
    elif event.code == "ABS_RY":
        return ((None,event.state),0)
    elif event.code == "BTN_THUMBR":
        return ((None,None),-1 if event.state==0 else 1)
    
    return ((None,None),0)

if __name__=="__main__":
    keyboard = pynput.keyboard.Controller()
    mouse = pynput.mouse.Controller()

    gamepads = inputs.devices.gamepads
    if len(gamepads) > 1:
        for i in range(len(gamepads)):
            print(f"{i}: {gamepads[i]}")
    
    inputted = "" if len(gamepads) > 1 else 0
    works = len(gamepads) <= 1

    mousePressed = False
    while works == False:
        inputted = input("Please select your gamepad: ")
        try:
            inputted = int(inputted)
            works = True
        except ValueError:
            print("That didn't look like a number to me. Please try again.")
    
    gamepad : inputs.GamePad = gamepads[inputted]
    print(f"Connected to {gamepad}!")

    isButtonPressed = False

    while True:
        try: events = gamepad.read()
        except KeyboardInterrupt: break

        lastMouseMotion = [0,0]
        mouseChanges = [[0,0],0]
        for event  in events:
            #print(event.ev_type,event.code,event.state)

            walked = walk(event)
            if walked != None:
                if not walked[1]:
                    if walked[0] == "ws":
                        keyboard.release("w")
                        keyboard.release("s")
                    else:
                        keyboard.release("a")
                        keyboard.release("d")
                
                else: keyboard.press(walked[0])
                pass

            button = useAndStuff(event)
            if button == None: pass
            elif type(button)==tuple:
                oldPos = mouse.position
                mouse.position = button
                mouse.click(pynput.mouse.Button.left)
                mouse.position = oldPos
                pass
            else: 
                keyboard.press(button)
                keyboard.release(button)

            # Mouse Pos Control
            
            mouseEventChanges = mouseControl(event)
            if mouseEventChanges[0][0] != None: JOYSTICKR[0] = mouseEventChanges[0][0]
            if mouseEventChanges[0][1] != None: JOYSTICKR[1] = mouseEventChanges[0][1]

            mouseChanges[1] += mouseEventChanges[1]

        joystickMouseRatio = MAX_MOUSE_MOV / MAX_JOYSTICK_N

        MOUSETHREAD.joystickR = JOYSTICKR

        if mouseChanges[1] >= 1:
            mouse.press(pynput.mouse.Button.left)
        elif mouseChanges[1] <= -1:
            mouse.release(pynput.mouse.Button.left)
        pass
    pass
            