from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtGui import QImage, QPixmap
import sys
import time
import SiSoPyInterface as siso
from signals import WorkerSignals

import numpy as np
import cv2
import ctypes

# CL Config Tool Settings:
# Exposure: Timed
# InterfaceTaps: 8
# SensorDestinationTaps: Sixteen
# Trigger: not enabled

# Additional Class definition
# Data for APC Callback
class MyApcData:
    fg = None
    port = 0
    mem = None
    displayid = 0


    def __init__(self, fg, port, mem, displayid):
        self.fg = fg
        self.port = port
        self.mem = mem
        self.displayid = displayid


class SisoBoard(QtCore.QObject):
    def __init__(self, mainWindow):
        QtCore.QObject.__init__(self)
        self.mainWindow = mainWindow
        self.signals = WorkerSignals()
        

    def run(self):
        self.initBoard()

    # Lets the user select one of the available boards, returns the selected
    # board, or -1 if nothing is selected
    def selectBoardDialog(self):
        maxNrOfboards = 10
        nrOfBoardsFound = 0
        nrOfBoardsPresent = self.getNrOfBoards()
        maxBoardIndex = -1
        minBoardIndex = None

        if (nrOfBoardsPresent <= 0):
            print("No Boards found!")
            return -1

        print('Found', nrOfBoardsPresent, 'Board(s)')

        for i in range(0, maxNrOfboards):
            skipIndex = False
            boardType = siso.Fg_getBoardType(i)
            if boardType == siso.PN_MICROENABLE4AS1CL:
                boardName = "MicroEnable IV AS1-CL"
            elif boardType == siso.PN_MICROENABLE4AD1CL:
                boardName = "MicroEnable IV AD1-CL"
            elif boardType == siso.PN_MICROENABLE4VD1CL:
                boardName = "MicroEnable IV VD1-CL"
            elif boardType == siso.PN_MICROENABLE4AD4CL:
                boardName = "MicroEnable IV AD4-CL"
            elif boardType == siso.PN_MICROENABLE4VD4CL:
                boardName = "MicroEnable IV VD4-CL"
            elif boardType == siso.PN_MICROENABLE4AQ4GE:
                boardName = "MicroEnable IV AQ4-GE"
            elif boardType == siso.PN_MICROENABLE4VQ4GE:
                boardName = "MicroEnable IV VQ4-GE"
            elif boardType == siso.PN_MICROENABLE5AQ8CXP6B:
                boardName = "MicroEnable V AQ8-CXP"
            elif boardType == siso.PN_MICROENABLE5VQ8CXP6B:
                boardName = "MicroEnable V VQ8-CXP"
            elif boardType == siso.PN_MICROENABLE5VD8CL:
                boardName = "MicroEnable 5 VD8-CL"
            elif boardType == siso.PN_MICROENABLE5AD8CL:
                boardName = "MicroEnable 5 AD8-CL"
            elif boardType == siso.PN_MICROENABLE5AQ8CXP6D:
                boardName = "MicroEnable 5 AQ8-CXP6D"
            elif boardType == siso.PN_MICROENABLE5VQ8CXP6D:
                boardName = "MicroEnable 5 VQ8-CXP6D"
            elif boardType == siso.PN_MICROENABLE5AD8CLHSF2:
                boardName = "MicroEnable 5 AD8-CLHS-F2"
            elif boardType == siso.PN_MICROENABLE5_LIGHTBRIDGE_ACL:
                boardName = "MicroEnable 5 LB-ACL"
            elif boardType == siso.PN_MICROENABLE5_LIGHTBRIDGE_VCL:
                boardName = "MicroEnable 5 LB-VCL"
            elif boardType == siso.PN_MICROENABLE5_MARATHON_ACL:
                boardName = "MicroEnable 5 MA-ACL"
            elif boardType == siso.PN_MICROENABLE5_MARATHON_ACX_SP:
                boardName = "MicroEnable 5 MA-ACX-SP"
            elif boardType == siso.PN_MICROENABLE5_MARATHON_ACX_DP:
                boardName = "MicroEnable 5 MA-ACX-DP"
            elif boardType == siso.PN_MICROENABLE5_MARATHON_ACX_QP:
                boardName = "MicroEnable 5 MA-ACX-QP"
            elif boardType == siso.PN_MICROENABLE5_MARATHON_AF2_DP:
                boardName = "MicroEnable 5 MA-AF2-DP"
            elif boardType == siso.PN_MICROENABLE5_MARATHON_VCL:
                boardName = "MicroEnable 5 MA-VCL"
            elif boardType == siso.PN_MICROENABLE5_MARATHON_VCX_QP:
                boardName = "MicroEnable 5 MA-VCX-QP"
            elif boardType == siso.PN_MICROENABLE5_MARATHON_VF2_DP:
                boardName = "MicroEnable 5 MA-VF2-DP"
            else:
                boardName = "Unknown / Unsupported Board"
                skipIndex = True

            if not skipIndex:
                sys.stdout.write("Board ID " + str(i) + ": " + boardName + " 0x" + format(boardType, '02X') + "\n")
                nrOfBoardsFound = nrOfBoardsFound + 1
                maxBoardIndex = i
                if minBoardIndex == None: minBoardIndex = i

            if nrOfBoardsFound >= nrOfBoardsPresent:
                break

            if nrOfBoardsFound < 0:
                break
            
        if nrOfBoardsFound <= 0:
            print("No Boards found!")
            return -1

        inStr = "=====================================\n\nPlease choose a board[{0}-{1}]: ".format(minBoardIndex, maxBoardIndex)
        userInput = input(inStr)

        while (not userInput.isdigit()) or (int(userInput) > maxBoardIndex):
            inStr = "Invalid selection, retry[{0}-{1}]: ".format(minBoardIndex, maxBoardIndex)
            userInput = input(inStr)

        return int(userInput)

    # returns count of available boards
    def getNrOfBoards(self):
        nrOfBoards = 0
        (err, buffer, buflen) = siso.Fg_getSystemInformation(None, siso.INFO_NR_OF_BOARDS, siso.PROP_ID_VALUE, 0)
        if (err == siso.FG_OK):
            nrOfBoards = int(buffer)
        return nrOfBoards

    # Lets the user select one of the available applets, and returns the
    # selected applet
    def selectAppletDialog(self, boardIndex):
        iter, err = siso.Fg_getAppletIterator(boardIndex, siso.FG_AIS_FILESYSTEM, siso.FG_AF_IS_LOADABLE)
        appletName = None

        print()
        if err == 0:
            print("No Applets found!")
            return None

        if (err > 0):
            print('Found', err, 'Applet(s)')

            i = 0
            while True:
                item = siso.Fg_getAppletIteratorItem(iter, i)
                if item == None:
                    break
                appletPath = siso.Fg_getAppletStringProperty(item, siso.FG_AP_STRING_APPLET_PATH)
                appletName = siso.Fg_getAppletStringProperty(item, siso.FG_AP_STRING_APPLET_NAME)
                sys.stdout.write(str(i) + ": " + appletName + "(" + appletPath + ")\n")
                i += 1

            maxAppletIndex = i - 1
            inStr = "=====================================\n\nPlease choose an Applet [0-" + str(maxAppletIndex) + "]: "
            userInput = input(inStr)

            while (not userInput.isdigit()) or (int(userInput) > maxAppletIndex):
                inStr = "Invalid selection, retry[0-" + str(maxAppletIndex) + "]: "
                userInput = input(inStr)

            item = siso.Fg_getAppletIteratorItem(iter, int(userInput))
            appletName = siso.Fg_getAppletStringProperty(item, siso.FG_AP_STRING_APPLET_NAME)

            siso.Fg_freeAppletIterator(iter)

        return appletName


    def initBoard(self):
        #print('SisoRuntime Version:', siso.Fg_getSWVersion())   
        sString = "SisoRuntime Version: " + siso.Fg_getSWVersion() + "\n"
        self.mainWindow.console.setText(self.mainWindow.console.text() + sString)
        boardId = 0 #self.selectBoardDialog()
        # definition of resolution
        width = 2048
        height = 2048
        samplePerPixel = 1
        bytePerSample = 1
        useCameraSimulator = False
        camPort = siso.PORT_A

        # number of buffers for acquisition
        nbBuffers = 50
        totalBufferSize = width * height * samplePerPixel * bytePerSample * nbBuffers

        # number of image to acquire
        nrOfPicturesToGrab = -1
        frameRate = 30

        iter, err = siso.Fg_getAppletIterator(0, siso.FG_AIS_FILESYSTEM, siso.FG_AF_IS_LOADABLE)
        item = siso.Fg_getAppletIteratorItem(iter, 14)
        applet = siso.Fg_getAppletStringProperty(item, siso.FG_AP_STRING_APPLET_NAME)
        #applet = self.selectAppletDialog(boardId)
        #print(applet)
        #apString = "Applet: " + applet + "\n"
        #self.mainWindow.console.setText(self.mainWindow.console.text() + apString)
        global_imgNr = -1

        # Callback function definition
        def apcCallback(imgNr, userData):
            print("imgNr: " + imgNr)
            siso.DrawBuffer(userData.displayid, siso.Fg_getImagePtrEx(userData.fg, imgNr, userData.port, userData.mem), imgNr, "")
            return 0

        fg = siso.Fg_InitEx(applet, boardId, 0)
        # error handling
        err = siso.Fg_getLastErrorNumber(fg)
        mes = siso.Fg_getErrorDescription(err)

        if err < 0:
            print("Error", err, ":", mes)
            sys.exit()
        else:
            #print("ok")
            okString = "config ok" + "\n"
            self.mainWindow.console.setText(self.mainWindow.console.text() + okString)

        # allocating memory
        memHandle = siso.Fg_AllocMemEx(fg, totalBufferSize, nbBuffers)

        # Set Applet Parameters
        err = siso.Fg_setParameterWithInt(fg, siso.FG_WIDTH, width, camPort)
        if (err < 0):
            print("Fg_setParameter(FG_WIDTH) failed: ", siso.Fg_getLastErrorDescription(fg))
            siso.Fg_FreeMemEx(fg, memHandle)
            siso.Fg_FreeGrabber(fg)
            exit(err)

        err = siso.Fg_setParameterWithInt(fg, siso.FG_HEIGHT, height, camPort)
        if (err < 0):
            print("Fg_setParameter(FG_HEIGHT) failed: ", siso.Fg_getLastErrorDescription(fg))
            siso.Fg_FreeMemEx(fg, memHandle)
            siso.Fg_FreeGrabber(fg)
            exit(err)

        err = siso.Fg_setParameterWithInt(fg, siso.FG_BITALIGNMENT, siso.FG_LEFT_ALIGNED, camPort)
        if (err < 0):
            print("Fg_setParameter(FG_BITALIGNMENT) failed: ", siso.Fg_getLastErrorDescription(fg))
	        #s.Fg_FreeMemEx(fg, memHandle)
	        #s.Fg_FreeGrabber(fg)
	        #exit(err)
        
        if useCameraSimulator:
	    # Start Generator
            siso.Fg_setParameterWithInt(fg, siso.FG_GEN_ENABLE, siso.FG_GENERATOR, camPort)
            #	s.Fg_setParameterWithInt(fg, s.FG_GEN_ROLL, 1, camPort)
        else:
            siso.Fg_setParameterWithInt(fg, siso.FG_GEN_ENABLE, siso.FG_CAMPORT, camPort)


        # Read back settings
        (err, oWidth) = siso.Fg_getParameterWithInt(fg, siso.FG_WIDTH, camPort)
        if (err == 0):
            #print('Width =', oWidth)
            widthString = "Width: " + str(oWidth) + "\n"
            self.mainWindow.console.setText(self.mainWindow.console.text() + widthString)

        (err, oHeight) = siso.Fg_getParameterWithInt(fg, siso.FG_HEIGHT, camPort)
        if (err == 0):
            #print('Height =', oHeight)
            heightString = "Height: " + str(oHeight) + "\n"
            self.mainWindow.console.setText(self.mainWindow.console.text() + heightString)

        (err, oString) = siso.Fg_getParameterWithString(fg, siso.FG_HAP_FILE, camPort)
        if (err == 0):
            #print('Hap File =', oString)
            hapString = "Hap File: " + oString + "\n"
            self.mainWindow.console.setText(self.mainWindow.console.text() + hapString)

        # create a display window
        #dispId0 = siso.CreateDisplay(8 * bytePerSample * samplePerPixel,
        #width, height)
        #siso.SetBufferWidth(dispId0, width, height)

        #Define FgApcControl instance to handle the callback
        apcCtrl = siso.FgApcControl(5, siso.FG_APC_DEFAULTS)
        data = MyApcData(fg, camPort, memHandle, 0)
        siso.setApcCallbackFunction(apcCtrl, apcCallback, data)

        #Register the FgApcControl instance to the Fg_Struct instance
        err = siso.Fg_registerApcHandler(fg, camPort, apcCtrl, siso.FG_APC_CONTROL_BASIC)
        if err != siso.FG_OK:
            print("registering APC handler failed:", siso.Fg_getErrorDescription(err))
            siso.Fg_FreeMemEx(fg, memHandle)
            siso.CloseDisplay(dispId0)
            siso.Fg_FreeGrabber(fg)
            exit(err)

        # Start acquisition
        #print("Acquisition started")
        acString = "Acquisition started" + "\n"
        self.mainWindow.console.setText(self.mainWindow.console.text() + acString)

        err = siso.Fg_AcquireEx(fg, camPort, -1, siso.ACQ_BLOCK, memHandle)
        if (err != 0):
            print('Fg_AcquireEx() failed:', siso.Fg_getLastErrorDescription(fg))
            siso.Fg_FreeMemEx(fg, memHandle)
            siso.CloseDisplay(dispId0)
            siso.Fg_FreeGrabber(fg)
            exit(err)

        #m = np.ones((width, height), np.uint64)
        #m = np.ones((2, 2), np.uint64)
        #m = [0,0,0,0,0]
        #counter = 1
        while(not self.mainWindow.pushButton_stop.isChecked() and self.mainWindow.closeVariable==0):
            #time_start = time.time()
            bufNr = siso.Fg_getImageEx(fg, siso.SEL_ACT_IMAGE, 0, camPort, 2, memHandle)
            ulp_buf = siso.Fg_getImagePtrEx(fg, bufNr, camPort, memHandle)
            #print("str(ulp_buf): " + str(ulp_buf))
            #print("str(id(ulp_buf)): " + str(id(ulp_buf)))
            #print("str(hex(id(ulp_buf))): " + str(hex(id(ulp_buf))))
            #print("str(memHandle): " , str(memHandle))
            #print("str(id(memHandle)): " + str(id(memHandle)))
            #print("mat-type: ", str(m.dtype))
            #m[0:4] = ulp_buf
            nparray = siso.getArrayFrom(ulp_buf, 2048, 2048)
            #siso.DrawBuffer(dispId0, ulp_buf, bufNr,"name")
            #ctypes.memmove(id(m), id(memHandle), (2 * 2))
            #for i in range(4):
            #    m[i] = id(ulp_buf) + i
            #print(m.dtype)
            #cv2.imshow("test", nparray )
            #cv2.waitKey(0)
            #print(mat / 255)
            #print(m.shape)
            #qimage = QImage(m, 2048, 2048, QImage.Format_Grayscale8)
            self.signals.live_image.emit(nparray)
            #self.yieldCurrentThread()
            #print("emit_arrray")
            #QtWidgets.QApplication.processEvents()
            #time.sleep(0.5)
            #counter += 1
            siso.Fg_setStatusEx(fg, siso.FG_UNBLOCK, bufNr, camPort, memHandle)
            #time_end = time.time()
            #self.yoloThread.signals.output_signal.connect(self.display)
            #siso.memcpy(mat, ulp_buf, totalBufferSize)
            #writer.write(frame_rgb);
            #time.sleep(1);
            #diff = time_end - time_start
            #print("bufNr: " + str(bufNr) + " time: " + str(round(diff,6)))


        #siso.CloseDisplay(dispId0)
        # Clean up
        if (fg != None):
            siso.Fg_stopAcquire(fg, camPort)
            siso.Fg_FreeMemEx(fg, memHandle)
            siso.Fg_FreeGrabber(fg)
            stopString = "Acquisition stoped" + "\n" +"\n"
            self.mainWindow.console.setText(self.mainWindow.console.text() + stopString)
            #print("Acquisition stoped")
            #self.autoscroll()
