#from PyQt5.QtCore import QObject

class FuncSerial():
 
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

    def getTile(modCounter, frame):
        print("FuncSerial.getTile()")
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

    def counter1(self, frame, tile):
        print("counter1()")
        frame[0:512, 0:512] = tile
        return frame

    def counter2(frame, tile):
        print("counter2()")
        frame[0:512, 512:1024] = tile
        return frame

    def counter3(frame, tile):
        print("counter3()")
        frame[0:512, 1024:1536] = tile
        return frame

    def counter4(frame, tile):
        print("counter4()")
        frame[0:512, 1536:2048] = tile

    def counter5(frame, tile):
        print("counter5()")
        frame[512:1024, 0:512] = tile

    def counter6(frame, tile):
        print("counter6()")
        frame[512:1024, 512:1024] = tile

    def counter7(frame, tile):
        #print("counter7()")
        self.frame[512:1024, 1024:1536] = self.tile

    def counter8(frame, tile):
        print("counter8()")
        self.frame[512:1024, 1536:2048] = self.tile

    def counter9(frame, tile):
        print("counter9()")
        self.frame[1024:1536, 0:512] = self.tile

    def counter10(frame, tile):
        #print("counter10()")
        self.frame[1024:1536, 512:1024] = self.tile

    def counter11(frame, tile):
        #print("counter11()")
        self.frame[1024:1536, 1024:1536] = self.tile

    def counter12(frame, tile):
        #print("counter12()")
        self.frame[1024:1536, 1536:2048] = self.tile

    def counter13(frame, tile):
        #print("counter13()")
        self.frame[1536:2048, 0:512] = self.tile

    def counter14(frame, tile):
        #print("counter14()")
        self.frame[1536:2048, 512:1024] = self.tile

    def counter15(frame, tile):
        #print("counter15()")
        self.frame[1536:2048, 1024:1536] = self.tile

    def counter16(frame, tile):
        #print("counter16()")
        self.frame[1536:2048, 1536:2048] = self.tile

    def concatTileAndFrame(self, modCounter, frame, tile):
        print("FuncSeriell.concatTileAndFrame(), modCounter=" + str(modCounter))
        
        switch = {
            1: self.counter1(frame, tile),
            2: counter2(frame, tile), 
            3: lambda: counter3(frame, tile),
            4: lambda: counter4(frame, tile),
            5: lambda: counter5(frame, tile),
            6: lambda: counter6(frame, tile),
            7: lambda: counter7(frame, tile),
            8: lambda: counter8(frame, tile),
            9: lambda: counter9(frame, tile),
            10: lambda: counter10(frame, tile),
            11: lambda: counter11(frame, tile),
            12: lambda: counter12(frame, tile),
            13: lambda: counter13(frame, tile),
            14: lambda: counter14(frame, tile),
            15: lambda: counter15(frame, tile),
            0 : lambda: counter16(frame, tile),
            }
        return switch.get(modCounter, lambda :  "fail")