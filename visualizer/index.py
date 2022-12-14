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
"""
import warnings
import os
import sys

# suppress warning caused by panda
# once this is dealt with in the analyzer module, remove following
warnings.simplefilter(action='ignore', category=FutureWarning)

# APPEND PATH TO ROOT TO ENSURE INTERNAL IMPORTS
tokens = os.path.abspath(__file__).split('/')
path2root = '/'.join(tokens[:-2])
if path2root not in sys.path:
    sys.path.append(path2root)

import logging
from logging.handlers import RotatingFileHandler

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from storage.builtin_datasets import ActiveNetwork
from visualizer import app


# ------------------------------------------------------------------------------------ #


# SET UP LOGGER
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = RotatingFileHandler('visualizer.log', backupCount=1)
handler.setFormatter(formatter)
handler.setLevel('DEBUG')
logger.addHandler(handler)


# INITIAL LAYOUT
app.visualizer_app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


# CALLBACK ROUTING '/'
@app.visualizer_app.callback(Output('page-content', 'children'),
                             [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        app.active_network = ActiveNetwork(path_2_data=None, from_file=False)
        return app.layout
    else:
        return '404'


# ------------------------------------------------------------------------------------ #


# PARSE ARGUMENTS, ADD EXTERNAL DATASETS AND LOGGER, RUN SERVER
if __name__ == '__main__':
    app.visualizer_app.server.logger.addHandler(handler)
    app_host='0.0.0.0'
    if app.args.host:
        app_host=str(app.args.host)
    if app.args.debug:
        app.visualizer_app.run_server(host=app_host, debug=True)
    else:
        app.visualizer_app.run_server(host=app_host, debug=False)
