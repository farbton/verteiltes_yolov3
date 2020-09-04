#from PyQt5.QtCore import QObject

#class FuncSerial():
import cv2
 
def getTile(modCounter, frame):
    #print("FuncSerial.getTile()")
    switch = {
        1: frame[0:512, 0:512],
        2: frame[0:512, 512:1024], 
        3: frame[0:512, 1024:1536],
        4: frame[0:512, 1536:2048],
        5: frame[512:1024, 0:512],
        6: frame[512:1024, 512:1024],
        7: frame[512:1024, 1024:1536],
        8: frame[512:1024, 1536:2048],
        9: frame[1024:1536, 0:512],
        10: frame[1024:1536, 512:1024],
        11: frame[1024:1536, 1024:1536],
        12: frame[1024:1536, 1536:2048],
        13: frame[1536:2048, 0:512],
        14: frame[1536:2048, 512:1024],
        15: frame[1536:2048, 1024:1536],
        0 : frame[1536:2048, 1536:2048],
        }
    return switch.get(modCounter, "fail")

def getGlobalCoordinates(modCounter, x, y):
    switch = {
        1: (x, y),
        2: (x, y + 512), 
        3: (x, y + 1024),
        4: (x, y + 1536),
        5: (x + 512, y),
        6: (x + 512, y + 512),
        7: (x + 512, y + 1024),
        8: (x + 512, y + 1536),
        9: (x + 1024, y),
        10: (x + 1024, y + 512),
        11: (x + 1024, y + 1024),
        12: (x + 1024, y + 1536),
        13: (x + 1536, y),
        14: (x + 1536, y + 512),
        15: (x + 1536, y + 1024),
        0 : (x + 1536, y + 1536),
        }
    return switch.get(modCounter, lambda :  "fail") 

def concatTileAndFrame(modCounter, frame, tile):
    #print("functions.concatTileAndFrame(), modCounter=" + str(modCounter))
    
    def counter1(frame, tile):
        #print("counter1()")
        #print(str(frame.shape) + " " + str(tile.shape))
        frame[0:512, 0:512] = tile
        #cv2.imshow("test", frame)
        return frame

    def counter2(frame, tile):
        #print("counter2()")
        frame[0:512, 512:1024] = tile
        return frame

    def counter3(frame, tile):
        #print("counter3()")
        frame[0:512, 1024:1536] = tile
        return frame

    def counter4(frame, tile):
        #print("counter4()")
        frame[0:512, 1536:2048] = tile
        return frame

    def counter5(frame, tile):
        #print("counter5()")
        frame[512:1024, 0:512] = tile
        return frame

    def counter6(frame, tile):
        #print("counter6()")
        frame[512:1024, 512:1024] = tile
        return frame

    def counter7(frame, tile):
        #print("counter7()")
        frame[512:1024, 1024:1536] = tile
        return frame

    def counter8(frame, tile):
        #print("counter8()")
        frame[512:1024, 1536:2048] = tile
        return frame

    def counter9(frame, tile):
        #print("counter9()")
        frame[1024:1536, 0:512] = tile
        return frame

    def counter10(frame, tile):
        #print("counter10()")
        frame[1024:1536, 512:1024] = tile
        return frame

    def counter11(frame, tile):
        #print("counter11()")
        frame[1024:1536, 1024:1536] = tile
        return frame

    def counter12(frame, tile):
        #print("counter12()")
        frame[1024:1536, 1536:2048] = tile
        return frame

    def counter13(frame, tile):
        #print("counter13()")
        frame[1536:2048, 0:512] = tile
        return frame

    def counter14(frame, tile):
        #print("counter14()")
        frame[1536:2048, 512:1024] = tile
        return frame

    def counter15(frame, tile):
        #print("counter15()")
        frame[1536:2048, 1024:1536] = tile
        return frame

    def counter16(frame, tile):
        #print("counter16()")
        frame[1536:2048, 1536:2048] = tile
        return frame
    
    switch = {
        1: counter1,
        2: counter2, 
        3: counter3,
        4: counter4,
        5: counter5,
        6: counter6,
        7: counter7,
        8: counter8,
        9: counter9,
        10: counter10,
        11: counter11,
        12: counter12,
        13: counter13,
        14: counter14,
        15: counter15,
        0 : counter16,
        }
    func = switch.get(modCounter, lambda:  "fail")
    return func(frame, tile)
     