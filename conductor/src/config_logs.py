"""
=================================== LICENSE ==================================
Copyright (c) 2021, Consortium Board ROXANNE
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

Neither the name of the ROXANNE nor the
names of its contributors may be used to endorse or promote products
derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY CONSORTIUM BOARD ROXANNE ``AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL CONSORTIUM BOARD TENCOMPETENCE BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
==============================================================================

 Configure logging """
import logging
import atexit
from logging.handlers import QueueHandler, QueueListener
from sys import stdout, stderr
from queue import Queue
from .config import config


class SpecificLevelFilter(object):
    def __init__(self, level):
        self.__level = level

    def filter(self, logRecord):
        return logRecord.levelno == self.__level


logging.basicConfig(format=config["LOG_FORMAT"])
api_logger = logging.getLogger("api")
api_logger.setLevel(getattr(logging, config["LOG_LEVEL"]))

log_queue = Queue(-1)
queue_handler = QueueHandler(log_queue)
event_handler = logging.StreamHandler(stdout)
error_handler = logging.StreamHandler(stderr)
event_handler.setLevel(logging.INFO)
error_handler.setLevel(logging.ERROR)
event_handler.addFilter(SpecificLevelFilter(logging.INFO))
queue_listener = QueueListener(log_queue, event_handler, error_handler, respect_handler_level=True)
api_logger.addHandler(queue_handler)

queue_listener.start()

atexit.register(lambda: queue_listener.stop())
