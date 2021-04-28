#
# Regular cron jobs for the piccolo3-utils package
#
0 4	* * *	root	[ -x /usr/bin/piccolo3-utils_maintenance ] && /usr/bin/piccolo3-utils_maintenance
