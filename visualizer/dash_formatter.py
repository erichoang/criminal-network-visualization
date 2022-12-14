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
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from analyzer import request_taker


def dash_network_info(network_info):
    """
    Get a HTML Table with infos regarding th network
    :return: Dash html.Table with infos regarding the network
    """
    return html.Table(children=[
        html.Tbody(children=[
            html.Tr(children=[
                html.Td(className='info-key', children='Network'),
                html.Td(network_info['network_name'])
            ]),
            html.Tr(children=[
                html.Td(className='info-key', children='# Nodes'),
                html.Td(str(network_info['num_nodes']))
            ]),
            html.Tr(children=[
                html.Td(className='info-key', children='# Edges'),
                html.Td(str(network_info['num_edges']))
            ])
        ])
    ])


def dash_message(message, success=True):
    color = '#009900' if success else '#cc3300'
    return [html.Div(id='message', children=message, style={'color': color})]


def dash_dataset_options(external_dataset_list, dataset_list):
    option_list = []
    if external_dataset_list:
        option_list.extend([{'label': data['name'], 'value': data['id']} for data in external_dataset_list])
        option_list.append({'label': '-----------------', 'value': '', 'disabled': True})
    option_list.extend([{'label': data['name'], 'value': data['id']} for data in dataset_list])
    return option_list


def dash_analysis_options():
    """
    :return: The label and name of each analysis function in the format needed for Dash 'options' field.
    """
    info = request_taker.get_info()
    analysis_options = [{'label': info[function]['name'], 'value': function} for function in info]
    enabled = ['community_detection', 'social_influence_analysis', 'link_prediction']
    for option in analysis_options:
        if option['value'] not in enabled:
            option['disabled'] = True
    return analysis_options


def dash_type_options(nodes):
    options = []
    for node in nodes:
        options.append({'label': str(node), 'value': str(node)})
    return options


def dash_entity_options(nodes):
    options = []
    for node in nodes:
        if 'name' in node['properties']:
            options.append({'label': str(node['properties']['name']), 'value': str(node['id'])})
        else:
            options.append({'label': str(node['id']), 'value': str(node['id'])})
    return options


def dash_analysis_method_options(analysis_function, disabled_methods):
    """

    :param analysis_function: A analysis function as a string as defined by the analyzer.
    :return: The label and name for each of the analysis functions defined method in the
    format needed for the Dash 'options' field.
    """
    # TODO Put disabled methods somewhere else (eg. app module)
    info = request_taker.get_info()
    analysis_methods = info[analysis_function]['methods']
    return [{'label': analysis_methods[method]['name'], 'value': method} for method in analysis_methods
            if method not in disabled_methods]


def dash_analysis_parameter(analysis_function, analysis_method):
    """
    Build Dash Dropdowns for parameter selection.
    :param analysis_function: A known analysis function.
    :param analysis_method: A known analysis method of the analysis function.
    :return: A list of html.Divs.
    """
    parameter = request_taker.get_info()[analysis_function]['methods'][analysis_method]['parameter']
    if parameter:
        dropdowns = []
        for i, p in enumerate(parameter):
            options = []
            parameter_name = next(iter(parameter))
            if 'Integer' in parameter[parameter_name]['options']:
                for o in parameter[parameter_name]['options']['Integer']:
                    options.append({'label': str(o), 'value': str(o)})
            else:
                for o in parameter[parameter_name]['options']:
                    options.append({'label': str(parameter[0]['options'][o]), 'value': str(o)})
            d = dcc.Dropdown(className='parameter',
                             id='parameter-' + str(i+1),
                             placeholder=parameter[p]['description'],
                             options=options,
                             multi=False)
            dropdowns.append(d)
        return [html.Div(id='parameter-title', children='PARAMETER'),
                html.Div(id='parameter', children=dropdowns)]
    else:
        return dash_default_parameter()


def dash_default_parameter():
    return [html.Div(id='parameter-title', children='PARAMETER'),
            dcc.Dropdown(className='parameter',
                         id='parameter-1',
                         placeholder='Algorithm has no parameter.',
                         options=[],
                         value=None,
                         multi=False,
                         disabled=True)
            ]

def get_label(info_name):
    return dbc.Label(info_name)

def get_text_field(info_name, default_value, type):
    new_input = html.Div(className='text-field-div', children=[
        dbc.Input(
            id={
                'type': type + '-input-field',
                'id': info_name
            },
            className='text-input', value=default_value, type='text'),
        html.Button('-', id={
                'type': 'remove-input-field',
                'id': 'field:' + info_name + ';container:' + type + '-element-container'
            }, className='remove-property-button')
    ])
    return new_input


def get_element_interaction_row(element_type, element_class):
    row = html.Tr(children=[
        html.Td(element_type, className='element-interaction-type-name'),
        html.Td(
            dcc.Checklist(id={
                'type': 'element-interaction-checkbox',
                'id': 'show-' + element_type + '-' + element_class + '-checkbox'
                },
                className='show-' + element_class + '-checkbox element-interaction-checkbox',
                options=[{'label': '',
                          'value': 'show-' + element_type + '-' + element_class,
                          }],
                value=['show-' + element_type + '-' + element_class]
                )
        ),
        html.Td(
            dcc.Checklist(id={
                'type': 'element-interaction-checkbox',
                'id': 'highlight-' + element_type + '-' + element_class + '-checkbox'
                },
                          className='highlight-' + element_class + '-checkbox element-interaction-checkbox',
                          options=[{'label': '',
                                    'value': 'highlight-' + element_type + '-' + element_class,
                                    }]
                          )
        )
    ])
    return row


def get_node_interaction_table():
    return [{'props': {'children': [{'props': {'children': 'TYPE'}, 'type': 'Th', 'namespace': 'dash_html_components'},
                             {'props': {'children': 'SHOW'}, 'type': 'Th', 'namespace': 'dash_html_components'},
                             {'props': {'children': 'HIGHLIGHT'}, 'type': 'Th', 'namespace': 'dash_html_components'}]},
      'type': 'Tr', 'namespace': 'dash_html_components'}]


def get_edge_interaction_table():
    return [{'props': {'children': [{'props': {'children': 'TYPE'}, 'type': 'Th', 'namespace': 'dash_html_components'},
                                    {'props': {'children': 'SHOW'}, 'type': 'Th', 'namespace': 'dash_html_components'},
                                    {'props': {'children': 'HIGHLIGHT'}, 'type': 'Th', 'namespace': 'dash_html_components'}]},
             'type': 'Tr', 'namespace': 'dash_html_components'}]

def get_info_table():
    return [{'props': {'children': [{'props': {'children': 'VARIABLE'}, 'type': 'Th', 'namespace': 'dash_html_components'},
                                    {'props': {'children': 'VALUE'}, 'type': 'Th', 'namespace': 'dash_html_components'}]},
             'type': 'Tr', 'namespace': 'dash_html_components'}]

def get_label_table():
    return [{'props': {'children': [{'props': {'children': 'VARIABLE'}, 'type': 'Th', 'namespace': 'dash_html_components'},
                                    {'props': {'children': 'DISPLAY'}, 'type': 'Th', 'namespace': 'dash_html_components', "class": "label-variable"}]},
             'type': 'Tr', 'namespace': 'dash_html_components'}]


def get_label_table_row(variable, value):
    # if/else block ist not a very clean solution.
    # However, seems like their is no real straight forward alternative in this case.
    if value:
        row = html.Tr(children=[
            html.Td(variable, className='element-interaction-type-name label-variable'),
            html.Td(
                dcc.Checklist(id={
                    'type': 'label-display-checkbox',
                    'id': 'display-' + variable + '-checkbox'
                },
                    className='element-interaction-checkbox',
                    options=[{'label': '',
                              'value': 'display-' + variable
                              }],
                    value=['display-' + variable]
                )),
        ])
    else:
        row = html.Tr(children=[
            html.Td(variable, className='element-interaction-type-name label-variable'),
            html.Td(
                dcc.Checklist(id={
                    'type': 'label-display-checkbox',
                    'id': 'display-' + variable + '-checkbox'
                },
                    className='element-interaction-checkbox',
                    options=[{'label': '',
                              'value': 'display-' + variable
                              }],
                )),

        ])
    return row

def get_info_table_row(variable, value):
    row = html.Tr(children=[
        html.Td(variable, className='element-interaction-type-name'),
        html.Td(value, className='element-interaction-type-name'),
    ])
    return row


def get_search_criteria(property, values, and_or):
    text = property + '  IS '
    text += ' ' + values[0]
    values = values[1:]
    for value in values:
        text = text + '  ' + str(and_or) + '  ' + value
    new_input = html.Div(className='search-criteria-wrapper', children=[
        html.Div(
            children=[text],
            className='search-criteria'),
        html.Button('-', id={
                'type': 'remove-search-criteria',
                'id': 'field: ;container:-element-container' # TODO: Adjust IDs dynamically ...
            }, className='remove-property-button')
    ])
    return new_input


def get_new_search_criteria(id, search_properties):
    return [html.Div(className='add-search-property-div', children=[
        html.Div(id='search-property-wrapper', children=[
            dcc.Dropdown(className='search-property', id={
                "type": "search-property-dropdown",
                'id': id
            },
                placeholder='Select property ...',
                options=search_properties
            )
        ]),
        html.Div(id='search-value-wrapper', children=[
            dcc.Dropdown(
                className='search-value',
                id={
                    "type": "search-value-dropdown",
                    'id': id
                },
                placeholder='Select property value...',
                multi=True
            )
        ]),
        html.Div(id='radio-wrapper', children=[
            dcc.RadioItems(
                id={
                    "type": "and-or-radio",
                    'id': id
                },
                options=[
                    {'label': 'AND', 'value': 'AND'},
                    {'label': 'OR', 'value': 'OR'}
                ],
                value='AND'
            ),
        ],
                 className='radio-wrapper',
        ),
        html.Button('-',
                id={
                    'type': 'remove-input-field',
                    'id': 'field:0;container:filter-container'
                },
                className='remove-filter-property-button')
    ]),
    html.Hr()]

def init_filters(property_options):
    filter = []
    for idx in range(10):

        div = html.Div(id='filter-wrapper-{}'.format(str(idx)), children=[
            html.Div(className='search-property-wrapper',
                     children=[
                         dcc.Dropdown(
                             className='search-property',
                             id={
                                 "type": "search-property-dropdown",
                                 'id': str(idx)
                             },
                             placeholder='Select property ...',
                             options=property_options
                         )
                     ]
                     ),
            html.Div(className='search-value-wrapper',
                     children=[
                         dcc.Dropdown(
                             className='search-value',
                             id="search-value-dropdown-{}".format(str(idx)),
                             placeholder='Select property value...',
                             multi=True,
                             options=[],
                         )
                     ]
                     ),
            html.Div(className='radio-wrapper',
                     children=[
                         dcc.RadioItems(
                             className='and-or-radio',
                             id={
                                 "type": "and-or-radio",
                                 'id': str(idx)
                             },
                             options=[
                                 {'label': 'AND', 'value': 'AND'},
                                 {'label': 'OR', 'value': 'OR'}
                             ],
                             value='AND'
                         )
                     ]
                     ),
            html.Button('-',
                        className='remove-filter-property-button',
                        id={
                            'type': 'remove-search-field',
                            'id': str(idx)
                        },
                        )
        ],
                 hidden=False if idx == 0 else True
                 )
        filter.append(div)
    return filter


def get_load_trigger():
    return html.Div(
            id={
                'type': 'trigger',
                'id': "load-trigger"
            },
            children=[
                dcc.Dropdown(
                    id="dummy",
                    # random input, just used for triggering
                    options=[
                        {'label': 'New York City', 'value': 'NYC'},
                        {'label': 'Montreal', 'value': 'MTL'},
                        {'label': 'San Francisco', 'value': 'SF'}
                    ]
                )
            ]
        )