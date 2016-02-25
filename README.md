# monitoring-control
Disable and enable monitoring notifications for a particular Nagios host

##Usage:
```
./monitoring_control.py -h
usage: monitoring_control.py [-h] [--target T] --operation O

optional arguments:
  -h, --help     show this help message and exit
  --target T     a target hostname to enable/disable notifications;defaults to
                 the run host
  --operation O  a notification operation to execute on a host
```

####Examples:
Disable all notifications for the host it is run on:
```
[root@locs01 ~]# /srv/systems/scripts/bin/monitoring_control.py --operation disable
OK
```

Enable all notifications for the host it is run on:
```
[root@locs01 ~]# /srv/systems/scripts/bin/monitoring_control.py --operation enable
OK
```

Disable all notifications for a target host:
```
[root@locs01 ~]# /srv/systems/scripts/bin/monitoring_control.py --operation disable --target locs01.prd.nj1.smartertravel.net
OK
```

Enable all notifications for a target host:
```
[root@locs01 ~]# /srv/systems/scripts/bin/monitoring_control.py --operation enable --target locs01.prd.nj1.smartertravel.net
OK
```

##Credentials
All queries are password protected by a deploy user defined in a htpasswd file for Nagios CGI.

##Error Handling
A successful request will output 'OK' and return code 0, otherwise a Nagios error message should appear and return 1.
