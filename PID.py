# PID.py
# Modified by PiRoast, starting from PID.py from OpenRoast.  Original header below.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# -*- coding: utf-8 -*-
# Author: cnr437@gmail.com
# Code URL: http://code.activestate.com/recipes/577231-discrete-pid-controller/
# License: MIT
# Modified by Openroast.
# Modified again by PiRoast


class PID(object):
    """Discrete PID control."""
    def __init__(self, P, I, D, Derivator=0, Integrator=0, Integrator_max=1500,
                 Integrator_min=-1500):

        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.Derivator1 = Derivator
        self.Derivator2 = Derivator
        self.Derivator3 = Derivator
        self.Derivator4 = Derivator
        self.Integrator = Integrator
        self.Integrator_max = Integrator_max
        self.Integrator_min = Integrator_min

        self.P_value = 0
        self.I_value = 0
        self.D_value = 0

        self.targetTemp = 0
        self.error = 0.0

    def update(self, currentTemp, targetTemp):
        """Calculate PID output value for given reference input and feedback."""
        self.targetTemp = targetTemp
        self.error = targetTemp - currentTemp

        self.P_value = self.Kp * self.error
        self.D_value = self.Kd * (self.error - self.Derivator4)

        self.Derivator4 = self.Derivator3
        self.Derivator3 = self.Derivator2
        self.Derivator2 = self.Derivator1
        self.Derivator1 = self.error

        self.Integrator = self.Integrator + self.error

        if self.Integrator > self.Integrator_max:
            self.Integrator = self.Integrator_max
        elif self.Integrator < self.Integrator_min:
            self.Integrator = self.Integrator_min

        self.I_value = self.Integrator * self.Ki

        output = self.P_value + self.I_value + self.D_value

        return(output)

    def setPoint(self, targetTemp):
        """Initilize the setpoint of PID."""
        self.targetTemp = targetTemp
        self.Integrator = 0
        self.Derivator1 = 0
        self.Derivator2 = 0
        self.Derivator3 = 0
        self.Derivator4 = 0

    def setIntegrator(self, Integrator):
        self.Integrator = Integrator

    def setDerivator(self, Derivator):
        self.Derivator1 = Derivator
        self.Derivator2 = Derivator
        self.Derivator3 = Derivator
        self.Derivator4 = Derivator

    def setKp(self, P):
        self.Kp = P

    def setKi(self, I):
        self.Ki = I

    def setKd(self, D):
        self.Kd = D

    def getPoint(self):
        return self.targetTemp

    def getError(self):
        return self.error

    def getIntegrator(self):
        return self.Integrator

    def getDerivator(self):
        return self.Derivator4

    def update_p(self, p):
        self.Kp = p

    def update_i(self, i):
        self.Ki = i

    def update_d(self, d):
        self.Kd = d
