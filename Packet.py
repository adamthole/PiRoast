# Packet.py
# Author: Adam Thole
# Based on Fresh Roast SR-700 communication protocol described here: http://freshroastsr700.readthedocs.io/en/latest/communication_protocol.html
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

class Packet:
    # Initialization Packet
    INIT_PACKET = [0xAA, 0x55, 0x61, 0x74, 0x63, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA, 0xFA]

    # Temperature Units
    FAHRENHEIT = [0x61, 0x74]

    # Flags
    FROM_COMPUTER = 0x63  # The packet was sent by the computer.
    FROM_ROASTER = 0x00  # The packet was sent by the roaster.
    CURRENT_SETTINGS = 0xA0  # The current settings on the roaster that had been set manually.
    RECIPE_LINE = 0xAA  # A beginning or middle line of a previously run recipe that had been saved to the roaster.
    LAST_RECIPE_LINE = 0xAF  # Last line of a previously run recipe that had been saved to the roaster.

    # Current States
    IDLE = [0x02, 0x01]  # Idle (Shows current timer and fan speed values)
    ROASTING = [0x04, 0x02]
    COOLING = [0x04, 0x04]
    SLEEPING = [0x08, 0x01]  # Sleeping (Displays “-” in both fan speed and timer fields on the roaster)

    # Heat Settings
    NO_HEAT = 0x00  # Cooling
    LOW_HEAT = 0x01
    MED_HEAT = 0x02
    HIGH_HEAT = 0x03

    def __init__(self):
        self.initPacket = Packet.INIT_PACKET

        self.header = [0xAA, 0xAA]
        self.tempUnit = Packet.FAHRENHEIT
        self.flag = Packet.FROM_COMPUTER
        self.currentState = Packet.ROASTING
        self.fanSpeed = 0x01
        self.timeRemaining = 0x63
        self.heatSetting = Packet.NO_HEAT
        self.currentTemp = [0x00, 0x00]
        self.footer = [0xAA, 0xFA]

    def getPacket(self):
        temp = [self.header, self.tempUnit, self.flag, self.currentState, self.fanSpeed, self.timeRemaining,
                self.heatSetting, self.currentTemp, self.footer]
        temp = Packet.flattenList(temp)
        return temp

    def getHeatSetting(self):
        if self.heatSetting == self.NO_HEAT:
            return "No Heat (Cooling)"

        if self.heatSetting == self.LOW_HEAT:
            return "Low Heat"

        if self.heatSetting == self.MED_HEAT:
            return "Medium Heat"

        if self.heatSetting == self.HIGH_HEAT:
            return "High Heat"

    @staticmethod
    def flattenList(l):
        return Packet.flattenList(l[0]) + (Packet.flattenList(l[1:]) if len(l) > 1 else []) if type(l) is list else [l]