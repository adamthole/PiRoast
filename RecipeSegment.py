# RecipeSegment.py
# Author: Adam Thole

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

class RecipeSegment:

    def __init__(self, startTemp, endTemp, startFanSpeed, endFanSpeed, lengthInSeconds, description, minHeat = 0, maxHeat = 12):
        self.startTemp = startTemp
        self.endTemp = endTemp
        self.startFanSpeed = startFanSpeed
        self.endFanSpeed = endFanSpeed
        self.lengthInSeconds = lengthInSeconds
        self.description = description
        self.minHeatIndex = minHeat
        self.maxHeatIndex = maxHeat
