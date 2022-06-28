# *****************************************************************************
# * | File        :	  epd7in5b_V2.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V4.1
# * | Date        :   2020-11-30
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#


import logging

# Display resolution
EPD_WIDTH       = 800
EPD_HEIGHT      = 480

class EPD:
    def __init__(self, driver):
        self.driver = driver
        self.reset_pin = self.driver.RST_PIN
        self.dc_pin = self.driver.DC_PIN
        self.busy_pin = self.driver.BUSY_PIN
        self.cs_pin = self.driver.CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    # Hardware reset
    def reset(self):
        self.driver.digital_write(self.reset_pin, 1)
        self.driver.delay_ms(200) 
        self.driver.digital_write(self.reset_pin, 0)
        self.driver.delay_ms(4)
        self.driver.digital_write(self.reset_pin, 1)
        self.driver.delay_ms(200)

    def send_command(self, command):
        self.driver.digital_write(self.dc_pin, 0)
        self.driver.digital_write(self.cs_pin, 0)
        self.driver.spi_writebyte([command])
        self.driver.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.driver.digital_write(self.dc_pin, 1)
        self.driver.digital_write(self.cs_pin, 0)
        self.driver.spi_writebyte([data])
        self.driver.digital_write(self.cs_pin, 1)
        
    def ReadBusy(self):
        logging.debug("e-Paper busy")
        self.send_command(0x71)
        busy = self.driver.digital_read(self.busy_pin)
        while(busy == 0):
            self.send_command(0x71)
            busy = self.driver.digital_read(self.busy_pin)
        self.driver.delay_ms(200)
            
    def init(self):
        if (self.driver.module_init() != 0):
            return -1
            
        self.reset()
        
        self.send_command(0x01);			#POWER SETTING
        self.send_data(0x07);
        self.send_data(0x07);    #VGH=20V,VGL=-20V
        self.send_data(0x3f);		#VDH=15V
        self.send_data(0x3f);		#VDL=-15V

        self.send_command(0x04); #POWER ON
        self.driver.delay_ms(100);
        self.ReadBusy();

        self.send_command(0X00);			#PANNEL SETTING
        self.send_data(0x0F);   #KW-3f   KWR-2F	BWROTP 0f	BWOTP 1f

        self.send_command(0x61);        	#tres
        self.send_data(0x03);		#source 800
        self.send_data(0x20);
        self.send_data(0x01);		#gate 480
        self.send_data(0xE0);

        self.send_command(0X15);
        self.send_data(0x00);

        self.send_command(0X50);			#VCOM AND DATA INTERVAL SETTING
        self.send_data(0x11);
        self.send_data(0x07);

        self.send_command(0X60);			#TCON SETTING
        self.send_data(0x22);

        self.send_command(0x65);
        self.send_data(0x00);
        self.send_data(0x00);
        self.send_data(0x00);
        self.send_data(0x00);
    
        return 0

    def getbuffer(self, image):
        # logging.debug("bufsiz = ",int(self.width/8) * self.height)
        buf = [0xFF] * (int(self.width/8) * self.height)
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        logging.debug('imwidth = %d  imheight =  %d ',imwidth, imheight)
        if(imwidth == self.width and imheight == self.height):
            logging.debug("Horizontal")
            for y in range(imheight):
                for x in range(imwidth):
                    # Set the bits for the column of pixels at the current position.
                    if pixels[x, y] == 0:
                        buf[int((x + y * self.width) / 8)] &= ~(0x80 >> (x % 8))
        elif(imwidth == self.height and imheight == self.width):
            logging.debug("Vertical")
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if pixels[x, y] == 0:
                        buf[int((newx + newy*self.width) / 8)] &= ~(0x80 >> (y % 8))
        return buf

    def show(self, imageblack, imagered):
        self.send_command(0x10)
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(imageblack[i]);
        
        self.send_command(0x13)
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(~imagered[i]);
        
        self.send_command(0x12)
        self.driver.delay_ms(100)
        self.ReadBusy()

    def clear(self):
        self.send_command(0x10) # Data Stop
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(0xff)
            
        self.send_command(0x13) # Dual SPI
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(0x00)
                
        self.send_command(0x12) # Display Start Transmission
        self.driver.delay_ms(100)
        self.ReadBusy()

    def sleep(self):
        self.send_command(0x02) # POWER_OFF
        self.ReadBusy()
        
        self.send_command(0x07) # DEEP_SLEEP
        self.send_data(0XA5)
        
    def dev_exit(self):
        self.driver.module_exit()

    def alt_get_frame_buffer(self, image):
        buf = [0x00] * (self.width * self.height // 4)
        # Set buffer to value of Python Imaging Library image.
        # Image must be in mode L.
        image_grayscale = image.convert('L')
        imwidth, imheight = image_grayscale.size
        if imwidth != self.width or imheight != self.height:
            raise ValueError('Image must be same dimensions as display \
                ({0}x{1}).' .format(self.width, self.height))

        pixels = image_grayscale.load()
        for y in range(self.height):
            for x in range(self.width):
                # Set the bits for the column of pixels at the current position.
                if pixels[x, y] < 64:           # black
                    buf[(x + y * self.width) // 4] &= ~(0xC0 >> (x % 4 * 2))
                elif pixels[x, y] < 192:     # convert gray to red
                    buf[(x + y * self.width) // 4] &= ~(0xC0 >> (x % 4 * 2))
                    buf[(x + y * self.width) // 4] |= 0x40 >> (x % 4 * 2)
                else:                           # white
                    buf[(x + y * self.width) // 4] |= 0xC0 >> (x % 4 * 2)
        return buf

    def alt_show(self, image):
        frame_buffer = self.alt_get_frame_buffer(image)
        self.send_command(0x10)
        for i in range(0, self.width // 4 * self.height):
            temp1 = frame_buffer[i]
            j = 0
            while (j < 4):
                if ((temp1 & 0xC0) == 0xC0):
                    temp2 = 0x03
                elif ((temp1 & 0xC0) == 0x00):
                    temp2 = 0x00
                else:
                    temp2 = 0x04
                temp2 = (temp2 << 4) & 0xFF
                temp1 = (temp1 << 2) & 0xFF
                j += 1
                if((temp1 & 0xC0) == 0xC0):
                    temp2 |= 0x03
                elif ((temp1 & 0xC0) == 0x00):
                    temp2 |= 0x00
                else:
                    temp2 |= 0x04
                temp1 = (temp1 << 2) & 0xFF
                self.send_data(temp2)
                j += 1
        self.send_command(0x12)
        self.driver.delay_ms(100)
        self.ReadBusy()



