import spidev

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
class Mcp3008():
    
    def __init__(self, ch):
        self.ch = ch
        self.spi = spidev.SpiDev()
        self.spi.open(0,0)
    
    def readadc(self):
        if ((self.ch > 7) or (self.ch < 0)):
            return -1
        r = self.spi.xfer2([1,(8+self.ch)<<4,0])
        adcout = ((r[1]&3) << 8) + r[2]
        return adcout

    def read_pct(self):
        r = self.readadc()
        min = 3
        max = 990
        return int(round(((float(r)-min)/(max-min))*100))

    def read_3v3(self):
        r = self.readadc()
        v = (r/1023.0)*3.3
        return v

    def readadc_avg(self):
        r = []
        for i in range (0,10):
            r.append(self.readadc())
        return sum(r)/10.0
        
    def read_2Y0A02_sensor(self):
        r = []
        for i in range (0,10):
            r.append(self.readadc())
        a = sum(r)/10.0
        v = (a/1023.0)*3.3
        d = 16.2537 * v**4 - 129.893 * v**3 + 382.268 * v**2 - 512.611 * v + 306.439
        cm = int(round(d))
        return cm
