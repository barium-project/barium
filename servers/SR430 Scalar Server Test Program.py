import labrad
from labrad.units import WithUnit as U
from time import sleep


if __name__ == "__main__":
    cxn = labrad.connect()
    sr = cxn.sr430_scalar_server
    sr.select_device(0L)
    print "Begin Test..."
    print "\n"

    print "output_gpib..."
    sr.output_gpib()
    sr.clear_status()
    sleep(1.0)
    print "\n"

    print "idn..."
    print sr.idn()
    sr.clear_status()
    sleep(1.0)
    print "\n"
    
    print "bin_width..."
    print "List Supported arguments"
    print sr.bin_width()
    print "Query"
    print sr.bin_width(0)
    print "Testing all supported arguments"
    supported_arguments=[5,40,80,160,320,640,1280,2560,5120,
                               10240,20480,40960,81920,163840,327680,
                               655360,1310700,2621400,5242900,1048600]
    for x in supported_arguments:
        print sr.bin_width(x)
        print sr.bin_width(0)
        sleep(0.1)
    print "Testing unsupported arguments"
    try:
        print sr.bin_width(2)
    except:
        print "Failed as expected"
    print sr.bin_width(0)
    try:
        print sr.bin_width(-5.1)
    except:
        print "Failed as expected"
    print sr.bin_width(0)
    sr.clear_status()
    sleep(1.0)
    print "\n"

    print "bins_per_record..."
    print "List Supported arguments"
    print sr.bins_per_record()
    print "Query"
    print sr.bins_per_record(0)
    supported_arguments=[(i+1)*1024 for i in range(16)]
    print "Testing all supported arguments"
    for x in supported_arguments:
        print sr.bins_per_record(x)
        print sr.bins_per_record(0)
        sleep(0.1)
    print "Testing unsupported arguments"
    try:
        print sr.bins_per_record(1025)
    except:
        print "Failed as expected"
    print sr.bins_per_record(0)
    try:
        print sr.bins_per_record(-5.1)
    except:
        print "Failed as expected"
    print sr.bins_per_record(0)
    sr.clear_status()
    sleep(1.0)
    print "\n"

    print "records_per_scan..."
    print "Query"
    print sr.records_per_scan()
    print "Testing supported arguments"
    print sr.records_per_scan(10000)
    print sr.records_per_scan()
    sleep(0.0001)
    print sr.records_per_scan(30000)
    print sr.records_per_scan()
    sleep(0.0001)
    print sr.records_per_scan(50000)
    print sr.records_per_scan()
    sleep(0.0001)
    print sr.records_per_scan()
    print "Testing unsupported arguments"
    try:
        print sr.records_per_scan(80000)
    except:
        pass
    print sr.records_per_scan()
    try:
        print sr.records_per_scan(0.5)
    except:
        print "Failed as expected"
    print sr.records_per_scan()
    sr.clear_status()
    sleep(1.0)
    print "\n"

    print "trigger_level..."
    print "Query"
    print sr.trigger_level()
    print "Testing supported arguments"
    print sr.trigger_level(U(1,'V'))
    print sr.trigger_level()
    print sr.trigger_level(U(-1,'V'))
    print sr.trigger_level()
    print "Testing unsupported arguments"
    try:
        print sr.trigger_level(5)
    except:
        print "Failed as expected"
    print sr.trigger_level()
    try:
        print sr.trigger_level(U(900,'V'))
    except:
        print "Failed as expected"
    print sr.trigger_level()
    sr.clear_status()
    sleep(1.0)
    print "\n"

    print "discriminator_level..."
    print "Query"
    print sr.discriminator_level()
    print "Testing supported arguments"
    print sr.discriminator_level(U(0.100,'V'))
    print sr.discriminator_level()
    print sr.discriminator_level(U(-0.100,'V'))
    print sr.discriminator_level()
    print "Testing unsupported arguments"
    try:
        print sr.discriminator_level(5)
    except:
        print "Failed as expected"
    print sr.discriminator_level()
    try:
        print sr.discriminator_level(U(900,'V'))
    except:
        print "Failed as expected"
    print sr.discriminator_level()
    sr.clear_status()
    sleep(1.0)
    print "\n"

    print "start_new_scan..."
    print sr.records_per_scan(10)
    print sr.bin_width(5)
    print sr.bins_per_record(1024)
    print sr.start_new_scan(U(3.0,'s'))
    try:
        print sr.start_new_scan(3.0)
    except:
        print "Failed as expected"
    try:
        print sr.start_new_scan()
    except:
        print "Failed as expected"
    sr.clear_status()
    sleep(1.0)
    print "\n"

    print "get_counts..."
    print sr.get_counts()
    sr.clear_status()
    sleep(1.0)
    print "\n"

    print "clear_scan..."
    print "Before clearing"
    print sr.get_counts()
    sr.clear_scan()
    print "After clearing"
    print sr.get_counts()
    sr.clear_status()
    sleep(1.0)
    print "\n"

    print "stop_scan..."
    print sr.records_per_scan(25)
    print sr.bin_width(1048600)
    print sr.bins_per_record(16*1024)
    print "Starting"
    sr.start_scan()
    sleep(2.0)
    print "Stopping"
    sr.stop_scan()
    print "Scan should have stopped."
    sr.clear_status()
    sleep(1.0)
    print "\n"
    
