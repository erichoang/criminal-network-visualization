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

 Helpers for formatting data to string """
from collections import OrderedDict
from datetime import datetime
from enum import Enum
from logfmt import format_line


class WeekDay(Enum):
    """ Days of the week """
    Mon = 1
    Tue = 2
    Wed = 3
    Thu = 4
    Fri = 5
    Sat = 6
    Sun = 7


class Month(Enum):
    """ Months of the year """
    Jan = 1
    Feb = 2
    Mar = 3
    Apr = 4
    May = 5
    June = 6
    July = 7
    Aug = 8
    Sept = 9
    Oct = 10
    Nov = 11
    Dec = 12


def timestamp_format(timestamp: datetime):
    """
    Format timestamp according to RFC 5322

    :param timestamp: datetime object
    :returns: formatted string
    """
    weekday = WeekDay(timestamp.isoweekday()).name
    month = Month(timestamp.month).name
    return f"{weekday}, {timestamp.day} {month} {timestamp.year} {timestamp.hour}:{timestamp.minute}:{timestamp.second} GMT"


def log_format(request_id: str, message: str, params: dict):
    """
    Format log message
    :param request_id: ID of the incoming request
    :param message: Log message
    :param params: dict of other data
    :returns: str of log data in logfmt
    """
    return format_line(OrderedDict([("request_id", request_id), ("message", message)] + list(params.items())))
