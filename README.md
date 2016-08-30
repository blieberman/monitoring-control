# monitoring-control
Disable and enable monitoring notifications for a particular Nagios host...this is great for deploys in an environment that is sensitive to monitoring.

##Usage:
```
./monitoring_control.py -h
usage: monitoring_control.py [-h] [--target T] --operation O [--duration D]
 
optional arguments:
  -h, --help     show this help message and exit
  --target T     a target hostname to enable/disable notifications;defaults to
                 the run host
  --operation O  a notification operation to execute on a host
  --duration D   a downtime window duration, in minutes
```

####Examples:
Downtime all notifications for services for a given duration in minutes for the host it is run on:
```
# ./monitoring_control.py --operation downtime --duration 10
OK
```

Disable all notifications for the host it is run on:
```
# ./monitoring_control.py --operation disable
OK
```

Enable all notifications for the host it is run on:
```
# ./monitoring_control.py --operation enable
OK
```

Downtime all notifications for services for a given duration in minutes for a target host:
```
# ./monitoring_control.py --operation downtime --duration 10 --target app01.prd.foo.com
OK
```

Disable all notifications for a target host:
```
# ./monitoring_control.py --operation disable --target app01.prd.foo.com
OK
```

Enable all notifications for a target host:
```
# ./monitoring_control.py --operation enable --target app01.prd.foo.com
OK
```

##Credentials
All queries are password protected by a deploy user defined in a htpasswd file for Nagios CGI.

##Error Handling
A successful request will output 'OK' and return code 0, otherwise a Nagios error message should appear and return 1.
