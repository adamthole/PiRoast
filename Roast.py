# Roast.py
# Author: Adam Thole

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from datetime import datetime

class Roast:

    def __init__(self):
        self.name = 'Default'
        self.startTime = datetime.now()
        self.preWeight = 120
        self.postWeight = 100
        time = datetime.now()
        self.firstCrack =  time - time
        self.secondCrack = time - time
        
        self.firstCrackTemp = 0
        self.secondCrackTemp = 0

    def getWeightLoss(self):
        return float(((self.preWeight - self.postWeight) / self.preWeight))
