#!/usr/bin/python

import Image, time, sys, argparse, os, signal

# Config file parser:
COMMENT_CHAR = '#'
OPTION_CHAR =  '='
def parse_config(filename):
    options = {}
    f = open(filename)
    for line in f:
        # First, remove comments:
        if COMMENT_CHAR in line:
            # split on comment char, keep only the part before
            line, comment = line.split(COMMENT_CHAR, 1)
        # Second, find lines with an option=value:
        if OPTION_CHAR in line:
            # split on option char:
            option, value = line.split(OPTION_CHAR, 1)
            # strip spaces:
            option = option.strip()
            value = value.strip()
            # store in dictionary:
            options[option] = value
    f.close()
    return options

# Parse config file and force some defaults for missing values:
options = parse_config('config')
if "options['spidevice']" not in locals():
    options['spidevice']="/dev/spidev2.0"
if "options['numleds']" not in locals():
    options['numleds']="52"
if "options['columndelay']" not in locals():
    options['columndelay']="0.03"
if "options['repeatdelay']" not in locals():
    options['repeatdelay']="1.0"

# Get and parse arguments:
parser = argparse.ArgumentParser(description="Use an image to program a LPD8806 LED strip sequence.")
parser.add_argument("filename", metavar="Image", type=str, help="Image file name")
parser.add_argument("-r", "--repeats", metavar="Repeats", dest="repeats", default=0, type=int, help="Limit the number of times the sequence is repeated (default 0 (infinite)).")
parser.add_argument("-d", "--delay", metavar="Repeatdelay", dest="repeatdelay", default=float(options['repeatdelay']), type=float, help="Delay (seconds) between each repeated sequence (default "+str(float(options['repeatdelay']))+").")
parser.add_argument("-c", "--coldelay", metavar="Columndelay", dest="coldelay", default=float(options['columndelay']), type=float, help="Delay (seconds) between each column (default "+str(float(options['columndelay']))+").")
parser.add_argument("-b", "--blank", dest="blank", help="Turn LEDs off between repeats.", action="store_true")
parser.add_argument("-s", "--silent", dest="silent", help="Silent operation.", action="store_true")
parser.add_argument("-q", "--quiet", dest="quiet", help="Silent operation and suppress error messages.", action="store_true")
parser.add_argument("--leds", metavar="Leds", dest="numleds", default=int(options['numleds']), type=int, help="Number of available leds (default "+str(int(options['numleds']))+").")
parser.add_argument("--spi", metavar="SPI device", dest="spidevice", default=options['spidevice'], type=str, help="The SPI device to use (default "+options['spidevice']+").")
args = parser.parse_args()
if(args.quiet):
    args.silent=True

# Check that we can write to SPI-device:
if os.path.exists(args.spidevice):
    if os.path.isdir(args.spidevice):
        if(not(args.quiet)):
            print "Unable to open output SPI device "+args.spidevice
        sys.exit(1)
    elif os.access(args.spidevice, os.W_OK):
        spidev   = file(args.spidevice,"wb")
    else:
        if(not(args.quiet)):
            print "No permission to write to SPI device "+args.spidevice+" (not root?)"
else:
    if(not(args.quiet)):
        print "Unable to open output SPI device "+args.spidevice
        sys.exit(1)

# Check that image file exists and open it:
if os.path.isfile(args.filename):
    if(not(args.silent)):
        print "Loading "+args.filename+"..."
    img      = Image.open(args.filename).convert("RGB")
    pixels   = img.load()
    width    = img.size[0]
    height   = img.size[1]
    #print "%dx%d pixels" % img.size
    if height > args.numleds:
        if(not(args.quiet)):
            print "Image max height is %d pixels. This image is %d pixels." % (args.numleds, height)
        sys.exit(1)
else:
    if(not(args.quiet)):
        print "Unable to open image file "+args.filename
    sys.exit(1)

# To turn off the LEDs when done or when stopped:
off = [0]
off[0] = bytearray(args.numleds*3+3)
for y in range(args.numleds*3+3):
    off[0][y]=128

# Trap signals:
def signal_handler(signal, frame):
    spidev.write(off[0])
    spidev.flush()
    if(not(args.quiet)):
        print "Exit on signal %d" % signal
    exit(0)
signal.signal(signal.SIGINT,signal_handler)
signal.signal(signal.SIGTERM,signal_handler)
signal.signal(signal.SIGSEGV,signal_handler)
signal.signal(signal.SIGHUP,signal_handler)

# Definne the gamma curve for LED output:
gamma = bytearray(256)
for i in range(256):
    gamma[i] = 0x80 | int(pow(float(i) / 255.0, 2.5) * 127.0 + 0.5)

# Define the "image":
if(not(args.silent)):
    print "Allocating %d columns..." % width
column = [0 for x in range(width)]
for x in range(width):
    column[x] = bytearray(height*3+1)

# Convert the image to useful data and apply gamma curve:
if(not(args.silent)):
    print "Converting..."
for x in range(width):
    for y in range(height):
        value=pixels[x,y]
        y3=y*3
        column[x][y3+0] = gamma[value[2]] # Led 1: blue
        column[x][y3+1] = gamma[value[0]] # Led 2: red
        column[x][y3+2] = gamma[value[1]] # Led 3: green

if(not(args.silent)):
    if args.repeats == 1:
        print "Displaying..."
    elif args.repeats > 1:
        print "Displaying %d times..." % args.repeats
    else:
        print "Displaying (continous)..."

if args.repeats < 1:
    while True:
        for x in range(width):
            spidev.write(column[x])
            spidev.flush()
            time.sleep(args.coldelay)
        if(args.blank):
            time.sleep(args.repeatdelay)
else:
    for loop in range(args.repeats):
        for x in range(width):
            spidev.write(column[x])
            spidev.flush()
            time.sleep(args.coldelay)
        if(args.blank):
            time.sleep(args.repeatdelay)

# Blank LED when done:
spidev.write(off[0])
spidev.flush()
exit(0)

