LPD8806.Ledstrip
================

Control RGB ledstrips based on the LPD8806 chip via SPI


Setup
-----

Edit the 'config' file to specify default values.
You probably want to check the 'spidevice' settings.

    On a Beaglebone, /dev/spidev2.0 corresonds to pin 30 and pin 31,
    where pin 30 on P9 is SPI1_D0 (connect to DI on the LED strip)
    and pin 31 in P9 is SPI_SCLK (connect to CL on the LED strip).

    On a Raspberry PI, /dev/spidev0.0 is probably disabled by default.
    To enable, make sure the module 'spi-bcm2708' is not blacklisted
    in '/etc/modprobe.d/raspi-blacklist.conf'.
    Connect pin 19 (SPI MOSI) to DI in the LED strip
    and pin 23 (SPI SCLK) to CL on the LED strip.

The LED strip and the controlling board needs common ground, but the board
will most likely not be able to power all the LEDs at once, so you should
connect +5V from a more powerfull supply.
NOTE: Do not attach the LPD8806 to more than +5V, as that will destroy it.

You may also power the board from the same power supply directly to the
header pins. This can be a bit  more convenient than using a USB cable or a
separate power connector.
If you choose this, connect ground (0V) to pin 1 or 2 on the Beaglebone P9
header, or pin 6 on the Raspberry Pi expansion header. Then connect +5V to
pin 5 or 6 on the Beaglebone P9 header, or pin 2 on the Raspberry Pi
expansion header.


