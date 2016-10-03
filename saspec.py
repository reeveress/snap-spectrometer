#!/usr/bin/python
import corr,time,struct,sys,logging,pylab
import matplotlib.pyplot as plt
import os
import sys
import numpy as np
katcp_port=7147


def get_data():
    pol0 = np.array(struct.unpack('>2048Q', fpga.read('pol0',2048*8,0)))
    pol1 = np.array(struct.unpack('>2048Q', fpga.read('pol1',2048*8,0)))
    
   

    

    
    real = np.array(struct.unpack('>2048q', fpga.read('real',2048*8,0)))
    imaginary = np.array(struct.unpack('>2048q', fpga.read('imaginary',2048*8,0)))
    print(len(pol0))
    
    return pol0,pol1,real+1j*imaginary

def plot_spectrum():
    
    pol0, pol1, crossmult = get_data()
    freq = np.arange(0,250,.1220703125)
    plt.subplot(311)
    plt.plot(freq,pol0,'r')
    plt.xticks(np.arange(min(freq), max(freq)+1, 10))
    plt.subplots_adjust(hspace = 1.2)
    plt.xlabel('frequency(MHz)')
    plt.ylabel('Power')
    plt.title('Power Spectra of pol0')
    plt.subplot(312)
    plt.plot(freq,pol1,'k')
    plt.xticks(np.arange(min(freq), max(freq)+1, 10))
    plt.title('Power Spectra of pol1')
    plt.xlabel('frequency(MHz)')
    plt.ylabel('Power')
    plt.subplot(313)
    plt.plot(freq,np.angle(crossmult),'b')
    plt.title('Crossmult angle signal')
    plt.ylabel('Phase(radians)')
    plt.xlabel('frequency(MHz)')
    plt.show()
if __name__ == '__main__':
    from optparse import OptionParser
    

    p = OptionParser()
    p.set_usage('saspec.py <SNAP_HOSTNAME_or_IP> [options]')
    p.set_description(__doc__)
    p.add_option('-l', '--acc_len', dest='acc_len', type='int',default=2*(2**28)/2048,
        help='Set the number of vectors to accumulate between dumps. default is 2((2^28)/2048, or just under 2 seconds.')
    p.add_option('-s', '--skip', dest='skip', action='store_true',
        help='Skip reprogramming the FPGA and configuring EQ.')
    p.add_option('-b', '--bof', dest='boffile',type='str', default='',
        help='Specify the bof file to load')
    opts, args = p.parse_args(sys.argv[1:])

    if args==[]:
        print 'Please specify a SNAP board. Run with the -h flag to see all options.\nExiting.'
        exit()
    else:
        snap = args[0]
    if opts.boffile != '':
        bitstream = opts.boffile


logger = []
lh = corr.log_handlers.DebugLogHandler()
logger = logging.getLogger(snap)
logger.addHandler(lh)
logger.setLevel(10)

print('Connecting to server %s on port %i... '%(snap,katcp_port)),
fpga = corr.katcp_wrapper.FpgaClient(snap, katcp_port, timeout=10, logger=logger)
time.sleep(1)

if fpga.is_connected():
    print 'ok\n'
else:
    print 'ERROR connecting to server %s on port %i. \n' %(roach,katcp_port)
    exit_fail()



print '-------------------'

if not opts.skip:
    fpga.progdev(bitstream)
    print('done')
else:
    print 'Skipped'


time.sleep(2)


print 'Configuring registers...'
fpga.write_int('acc_len', opts.acc_len)
fpga.write_int('fft_shift', 0xFFFFFFFF)
fpga.write_int('antenna',2)
fpga.write_int('c_rst',0)
fpga.write_int('c_rst',1)
fpga.write_int('c_rst',0)
print 'Done!'

#adc_0 = np.array(struct.unpack('>2048b', fpga.read('adc_data', 2048, 0)))
#adc_fft = abs(np.fft.fft(adc_0))
#t = np.linspace(0,250,2048)
#plt.plot(t,adc_0)
#plt.plot(t,adc_fft)
#plt.show()
plot_spectrum()

