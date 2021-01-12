# PiRoast.py
# Author: Adam Thole

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from Packet import Packet
import serial
import MAX6675
import time
from datetime import datetime
from PID import PID
import math
import sys
from threading import Thread
from Recipe import Recipe
from RecipeSegment import RecipeSegment

HEAT_HIGH_MAX = 520
HEAT_MED_MAX = 460
HEAT_LOW_MAX = 430
HEAT_MIN = 150

HEAT_STATES = [ [0, 0, 0, 0],
                [0, 0, 0, 1],
                [0, 1, 0, 1],
                [0, 1, 1, 1],
                [1, 1, 1, 1],
                [1, 1, 1, 2],
                [1, 2, 1, 2],
                [1, 2, 2, 2],
                [2, 2, 2, 2],
                [2, 2, 2, 3],
                [2, 3, 2, 3],
                [2, 3, 3, 3],
                [3, 3, 3, 3] ]

MAX_FAN_STATE_INDEX = 33
FAN_STATES =  [ [0, 0, 0, 0],
                [1, 1, 1, 1],
                [1, 1, 1, 2],
                [1, 2, 1, 2],
                [1, 2, 2, 2],
                [2, 2, 2, 2],
                [2, 2, 2, 3],
                [2, 3, 2, 3],
                [2, 3, 3, 3],
                [3, 3, 3, 3],
                [3, 3, 3, 4],
                [3, 4, 3, 4],
                [3, 4, 4, 4],
                [4, 4, 4, 4],
                [4, 4, 4, 5],
                [4, 5, 4, 5],
                [4, 5, 5, 5],
                [5, 5, 5, 5],
                [5, 5, 5, 6],
                [5, 6, 5, 6],
                [5, 6, 6, 6],
                [6, 6, 6, 6],
                [6, 6, 6, 7],
                [6, 7, 6, 7],
                [6, 7, 7, 7],
                [7, 7, 7, 7],
                [7, 7, 7, 8],
                [7, 8, 7, 8],
                [7, 8, 8, 8],
                [8, 8, 8, 8],
                [8, 8, 8, 9],
                [8, 9, 8, 9],
                [8, 9, 9, 9],
                [9, 9, 9, 9], ]

class Roaster:
    def __init__(self):
        # Raspberry Pi software SPI configuration.
        CLK = 11
        CS = 22
        DO = 9
        self.internalTemp = 0
        self.tcTemp = 0
        self.deltaTemp = 0
        self.tempProbe = MAX6675.MAX6675(CLK, CS, DO)

        self.isRunning = True
        self.packet = Packet()
        self.startTime = datetime.now()
        self.log = []
        self.elapsedTime = self.startTime - self.startTime
        self.isRoasting = False
        self.isAutoTemp = False
        self.IsRecipeRunning = False
        self.targetTemp = 0
        self.heatStateIndex = 0
        self.heatRunningPosition = 0
        self.fanStateIndex = 0
        self.fanRunningPosition = 0
        self.gPidOutput = 0
        self.targetTempIndex = 0
        self.minHeatIndex = 0
        self.maxHeatIndex = 12
        self.isRoastInProgress = False

        p = 0.4
        i = 0.007
        d = 1.5
        self.pid = PID(p, i, d)
        self.error = 0

        self.Recipes = []
        self.CreateRecipes()

    def CreateRecipes(self):
        city13 = Recipe('City Roast (13 Minutes)')
        city13.segments.append(RecipeSegment(200, 250, MAX_FAN_STATE_INDEX, MAX_FAN_STATE_INDEX, 5 * 60, 'Drying', 0, 4))
        city13.segments.append(RecipeSegment(250, 415, MAX_FAN_STATE_INDEX, 2, 6 * 60, 'Ramp Up'))
        city13.segments.append(RecipeSegment(415, 425, 1, 1, 2 * 60, 'Hold'))
        self.Recipes.append(city13);

        city9 = Recipe('City Roast (9 Minutes)')
        city9.segments.append(RecipeSegment(200, 250, MAX_FAN_STATE_INDEX, MAX_FAN_STATE_INDEX, 3 * 60, 'Drying', 0, 4))
        city9.segments.append(RecipeSegment(250, 415, MAX_FAN_STATE_INDEX, 2, 4 * 60, 'Ramp Up'))
        city9.segments.append(RecipeSegment(415, 425, 1, 1, 2 * 60, 'Hold'))
        self.Recipes.append(city9);

        cityplus13 = Recipe('City+ (13 minutes)')
        cityplus13.segments.append(RecipeSegment(200, 250, MAX_FAN_STATE_INDEX, MAX_FAN_STATE_INDEX, 5 * 60, 'Drying', 0, 4))
        cityplus13.segments.append(RecipeSegment(250, 425, MAX_FAN_STATE_INDEX - 1, 2, 6 * 60, 'Ramp Up'))
        cityplus13.segments.append(RecipeSegment(425, 435, 1, 1, 2 * 60, 'Hold'))
        self.Recipes.append(cityplus13);

        cityPlus11 = Recipe('City+ (11 minutes)')
        cityPlus11.segments.append(RecipeSegment(175, 300, MAX_FAN_STATE_INDEX, MAX_FAN_STATE_INDEX, 4 * 60, 'Drying', 0, 4))
        cityPlus11.segments.append(RecipeSegment(300, 425, MAX_FAN_STATE_INDEX, 2, 5 * 60, 'Ramp Up'))
        cityPlus11.segments.append(RecipeSegment(425, 435, 1, 1, 2 * 60, 'Hold'))
        self.Recipes.append(cityPlus11);

        cityPlus10 = Recipe('City+ (10 minutes)')
        cityPlus10.segments.append(RecipeSegment(175, 300, MAX_FAN_STATE_INDEX, MAX_FAN_STATE_INDEX, 4 * 60, 'Drying', 0, 4))
        cityPlus10.segments.append(RecipeSegment(300, 425, MAX_FAN_STATE_INDEX, 2, 4 * 60, 'Ramp Up'))
        cityPlus10.segments.append(RecipeSegment(425, 435, 1, 1, 2 * 60, 'Hold'))
        self.Recipes.append(cityPlus10);

        cityPlus9 = Recipe('City+ (9 minutes)')
        cityPlus9.segments.append(RecipeSegment(175, 300, MAX_FAN_STATE_INDEX, MAX_FAN_STATE_INDEX, 3.5 * 60, 'Drying', 0, 4))
        cityPlus9.segments.append(RecipeSegment(300, 425, MAX_FAN_STATE_INDEX, 2, 3.5 * 60, 'Ramp Up'))
        cityPlus9.segments.append(RecipeSegment(425, 435, 1, 1, 2 * 60, 'Hold'))
        self.Recipes.append(cityPlus9);

        cityPlus8 = Recipe('City+ (8 minutes)')
        cityPlus8.segments.append(RecipeSegment(200, 250, MAX_FAN_STATE_INDEX, MAX_FAN_STATE_INDEX, 2 * 60, 'Drying', 0, 4))
        cityPlus8.segments.append(RecipeSegment(250, 425, MAX_FAN_STATE_INDEX - 1, 2, 4 * 60, 'Ramp Up'))
        cityPlus8.segments.append(RecipeSegment(425, 435, 1, 1, 2 * 60, 'Hold'))
        self.Recipes.append(cityPlus8);

        fullCity10 = Recipe('Full City (10 minutes)')
        fullCity10.segments.append(RecipeSegment(200, 250, MAX_FAN_STATE_INDEX, MAX_FAN_STATE_INDEX, 4 * 60, 'Drying', 0, 4))
        fullCity10.segments.append(RecipeSegment(250, 435, MAX_FAN_STATE_INDEX - 1, 2, 4 * 60, 'Ramp Up'))
        fullCity10.segments.append(RecipeSegment(435, 445, 1, 1, 2 * 60, 'Hold'))
        self.Recipes.append(fullCity10);
        
        fullCity13 = Recipe('Full City (13 minutes)')
        fullCity13.segments.append(RecipeSegment(200, 250, MAX_FAN_STATE_INDEX, MAX_FAN_STATE_INDEX, 5 * 60, 'Drying', 0, 4))
        fullCity13.segments.append(RecipeSegment(250, 435, MAX_FAN_STATE_INDEX - 1, 2, 6 * 60, 'Ramp Up'))
        fullCity13.segments.append(RecipeSegment(435, 445, 1, 1, 2 * 60, 'Hold'))
        self.Recipes.append(fullCity13);

        fullCityPlus13 = Recipe('Full City+ (13 minutes)')
        fullCityPlus13.segments.append(RecipeSegment(200, 250, MAX_FAN_STATE_INDEX, MAX_FAN_STATE_INDEX, 5 * 60, 'Drying', 0, 4))
        fullCityPlus13.segments.append(RecipeSegment(300, 450, MAX_FAN_STATE_INDEX - 1, 2, 5 * 60, 'Ramp Up'))
        fullCityPlus13.segments.append(RecipeSegment(450, 450, 1, 1, 3 * 60, 'Hold'))
        self.Recipes.append(fullCityPlus13);

        frenchRoast12 = Recipe('French Roast (12 Minutes)')
        frenchRoast12.segments.append(RecipeSegment(200, 250, MAX_FAN_STATE_INDEX, MAX_FAN_STATE_INDEX, 4 * 60, 'Drying', 0, 4))
        frenchRoast12.segments.append(RecipeSegment(300, 470, MAX_FAN_STATE_INDEX - 1, 2, 6 * 60, 'Ramp Up'))
        frenchRoast12.segments.append(RecipeSegment(470, 470, 1, 1, 2 * 60, 'Hold'))
        self.Recipes.append(frenchRoast12);

        self.SelectedRecipe = fullCity13;
        print(self.SelectedRecipe.name)
        
    def connect(self, port):
        self.setFanSpeed(0)
        self.setHeat(0)

        commThread = Thread(target=self.communicationWorker, args=[port])
        commThread.start()

        thermocoupleThread = Thread(target=self.thermocoupleWorker)
        thermocoupleThread.start()

        pidThread = Thread(target=self.pidWorker)
        pidThread.start()

        fanThread = Thread(target=self.fanWorker)
        fanThread.start()

    def startRoast(self):
        self.isAutoTemp = False
        self.isRoasting = True
        self.log = []
        self.startTime = datetime.now()
        self.fanStateIndex = MAX_FAN_STATE_INDEX
        self.setHeat(1)

    def coolRoast(self):
        self.isAutoTemp = False;
        self.targetTemp = 0
        self.minHeatIndex = 0
        self.setHeat(0)
        self.fanStateIndex = 1
        self.heatStateIndex = 0
        self.IsRecipeRunning = False

    def stopRoast(self):
        self.isAutoTemp = False
        self.targetTemp = 0
        self.minHeatIndex = 0
        self.isRoasting = False
        self.setHeat(0)
        self.fanStateIndex = 0
        self.IsRecipeRunning = False
        self.packet.timeRemaining = 0

    def autoTemp(self, target):
        self.isAutoTemp = True
        self.targetTemp = target

        self.targetTempIndex = math.floor(((target - HEAT_MIN) / HEAT_HIGH_MAX) * 12)

    def disconnect(self):
        self.isRunning = False

    def runRecipe(self):
        if (self.isRoastInProgress == True):
             return 'Roast In Progress!'

        self.isRoastInProgress = True
        print('Starting Recipe', file=sys.stderr)

        self.IsRecipeRunning = True
        self.startRoast()

        for segment in self.SelectedRecipe.segments:
            secondsTotal = segment.lengthInSeconds
            secondsIntoSegment = 0

            while (secondsIntoSegment < secondsTotal) and self.IsRecipeRunning:
                print('secondsTotal ' + str(secondsTotal), file=sys.stderr)
                pctDone = secondsIntoSegment / secondsTotal
                print('percentDone ' + str(pctDone), file=sys.stderr)
                targetTemp = segment.startTemp + (pctDone * (segment.endTemp - segment.startTemp))

                self.fanStateIndex = segment.startFanSpeed + round((pctDone * (segment.endFanSpeed - segment.startFanSpeed)))
                self.autoTemp(targetTemp)

                self.minHeatIndex = segment.minHeatIndex
                self.maxHeatIndex = segment.maxHeatIndex

                time.sleep(1)
                secondsIntoSegment = secondsIntoSegment + 1
                self.packet.timeRemaining = int(((secondsTotal - secondsIntoSegment) / 60) * 10)

        self.coolRoast()
        totalCoolTime = 3*60
        coolTime = 0

        while (coolTime < totalCoolTime):
            self.packet.timeRemaining = int(((totalCoolTime - coolTime) / 60) * 10)
            coolTime = coolTime + 1
            time.sleep(1)

        self.stopRoast()

        self.isRoastInProgress = False
        return 'Done!'

    def setKp(self, Kp):
        self.pid.setKp(Kp)

    def setKi(self, Ki):
        self.pid.setKi(Ki)

    def setKd(self, Kd):
        self.pid.setKd(Kd)

    def pidWorker(self):
        while (self.isRunning):
            if self.getFanSpeed() > 0 and self.isAutoTemp == True:

                self.gPidOutput = self.pid.update(self.tcTemp, self.targetTemp)

                pidOutput = self.targetTempIndex + self.gPidOutput

                if pidOutput <= self.minHeatIndex:
                    pidOutput = self.minHeatIndex
                elif pidOutput >= self.maxHeatIndex:
                    pidOutput = self.maxHeatIndex
                elif math.isnan(pidOutput):
                    pidOutput = 0
                else:
                    pidOutput = math.floor(pidOutput)

                self.heatStateIndex = pidOutput

            time.sleep(0.25)

    def thermocoupleWorker(self):
        while (self.isRunning):
            self.tcTemp = self.tempProbe.readTempF()
            self.deltaTemp = self.getDeltaTemp()

            currentHeatIndex = HEAT_STATES[self.heatStateIndex][self.heatRunningPosition]

            self.setHeat(currentHeatIndex)
            self.heatRunningPosition = self.heatRunningPosition + 1
            if self.heatRunningPosition >= 4:
                self.heatRunningPosition = 0

            time.sleep(0.25)

    def fanWorker(self):
        while (self.isRunning):
            #print('Fan State: ' + str(self.fanStateIndex), file=sys.stderr)

            self.setFanSpeed(FAN_STATES[self.fanStateIndex][self.fanRunningPosition])
            self.fanRunningPosition = self.fanRunningPosition + 1
            if self.fanRunningPosition >= 4:
                self.fanRunningPosition = 0

            time.sleep(0.25)

    def communicationWorker(self, port):
        byteList = []

        serialPort = serial.Serial(
            port=port,
            baudrate=9600,
            bytesize=8,
            parity='N',
            stopbits=1.5,
            timeout=.25,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False)

        # Send initialization packet
        initPacket = self.packet.initPacket
        serialPort.write(bytearray(initPacket))

        while self.isRunning:
            if self.isRoasting:
                self.elapsedTime = datetime.now() - self.startTime

            transmit = self.packet.getPacket()
            serialPort.write(bytearray(transmit))

            receivedData = list(serialPort.read(14))
            byteList = byteList + receivedData

            while (len(byteList) >= 14):
                if (byteList[0] == 0xAA and byteList[1] == 0xAA):
                    if self.isRoasting:
                        self.elapsedTime = datetime.now() - self.startTime
                    fullPacket = byteList[0:14]
                    self.getTempFromPacket(fullPacket)
                    byteList[0:14] = []
                else:
                    byteList.pop(0)

            time.sleep(0.2)

    def getTempFromPacket(self, packet):
        temp = packet[10:12]
        val = temp[0] * 256 + temp[1]
        if (val == 65280):
            val = 150

        self.internalTemp = val
        self.deltaTemp = self.getDeltaTemp()

        if (self.isRoasting):
            self.log.append([self.elapsedTime, self.internalTemp, self.targetTemp,
            self.tcTemp, self.deltaTemp, self.packet.fanSpeed, self.packet.heatSetting,self.gPidOutput,
            self.pid.P_value, self.pid.I_value, self.pid.D_value, self.heatStateIndex])

        #print("Time: " + str(elapsed) + " Temp: " + str(val) + "Thermo Temp: " + str(self.tcTemp))

    def getDeltaTemp(self):
        logLength = len(self.log)
        delta = 5*60

        if logLength > delta:
            deltaT = self.log[logLength - 1][3] - self.log[logLength - delta][3]
            if (deltaT > 0):
                return deltaT
        return 0

    def setHeat(self, heatSetting):
        if (heatSetting >= 0 and heatSetting <= 3):
            self.packet.heatSetting = heatSetting

    def setFanSpeed(self, fanSpeed):
        if (fanSpeed >= 0 and fanSpeed < 10):

            self.packet.fanSpeed = fanSpeed

    def getInternalTemp(self):
        return self.internalTemp;

    def getThermocoupleTemp(self):
        return self.tcTemp;

    def getHeatSetting(self):
        return self.packet.heatSetting;

    def getFanSpeed(self):
        return self.packet.fanSpeed;

    def getElapsedTime(self):
        return self.elapsedTime
