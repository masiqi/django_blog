kill -9 `ps auwx|grep manage|grep runfcgi|grep 3033|awk '{print $2}'`;python ./manage.py runfcgi method=threaded host=127.0.0.1 port=3033 outlog=/tmp/django.out errlog=/tmp/django.err minspare=5 
