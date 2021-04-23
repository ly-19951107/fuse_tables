# -*- coding: utf-8 -*-
import os
from os import cpu_count

if not os.path.exists('./logs/applog'):
    os.makedirs('./logs/applog')

# The socket to bind.
bind = '0.0.0.0:5000'

# The number of worker processes for handling requests.
# A positive integer generally in the ``2-4*cpu_nums`` range.
workers = 2*cpu_count()

# The number of worker threads for handling requests.
# Run each worker with the specified number of threads.
# A positive integer generally in the ``2-4*cpu_nums`` range.
threads = 2*cpu_count()

# The Access log file to write to.
accesslog = './logs/applog/info.log'
# The Error log file to write to.
errorlog = './logs/applog/error.log'
# The granularity of Error log outputs.
loglevel = 'warning'
# 标准输出重定向至错误日志文件中
capture_output = True

# 正式部署时，改为True
daemon = True
