import dash
from dash.dependencies import Input, Output, State, ALL


outputs = [
    ## CYTOSCAPE FRAME ##
    Output('cytoscape', 'elements'),
    Output('cytoscape', 'stylesheet'),
    Output('cytoscape', 'layout'),
    Output("cytoscape", "className"),


    ## COMPARISON NETWORK ##
    Output('cytoscape-unaltered', 'elements'),
    Output('cytoscape-unaltered', 'stylesheet'),
    Output('cytoscape-unaltered', 'layout'),
    Output("cytoscape-unaltered", "className"),
    Output('unaltered-collapse-button', 'children'),
    Output('element-interaction-container', 'hidden'),
    Output('original_network_button_div', 'hidden'),


    ## WARNING ##
    Output('warning-div', 'children'),

    ## ELEMENT INTERACTION ##
    Output('node-interaction-table', 'children'),
    Output('edge-interaction-table', 'children'),
    Output('label-interaction-table', 'children'),

    ## PROBABILITY SLIDER ##
    Output('edge-prop-slider-div', 'hidden'),

    #####################
    ## SIDEBAR OUTPUTS ##
    #####################

    ## INFO ##
    Output('network-info', 'children'),

    ## NETWORK TAB ##
    Output('choose-entities', 'options'),
    Output('choose-entities', 'value'),

    ## ANALYSIS TAB ##
    Output('analysis-algorithm', 'options'),
    Output('parameter-div', 'children'),

    ####################
    ## DIALOG OUTPUTS ##
    ####################

    ## MODAL STYLE ##
    Output("modal", "style"),

    ## CONFIRM LOAD ##
    Output('modal-confirm-load', 'is_open'),
    Output('modal-load-done', 'is_open'),
    Output('modal-confirm-file-load', 'is_open'),
    Output('modal-file-load-done', 'is_open'),
    Output('hidden-info', 'children'),

    ## ADVANCED SEARCH ##
    Output('modal-search', 'is_open'),
    Output('filter-container', 'children'),
    # It was tried intensively to solve the below dynamically but it seems like this
    # cannot be done beautifully with the current version of Dash
    Output('search-value-dropdown-0', 'options'),
    Output('search-value-dropdown-1', 'options'),
    Output('search-value-dropdown-2', 'options'),
    Output('search-value-dropdown-3', 'options'),
    Output('search-value-dropdown-4', 'options'),
    Output('search-value-dropdown-5', 'options'),
    Output('search-value-dropdown-6', 'options'),
    Output('search-value-dropdown-7', 'options'),
    Output('search-value-dropdown-8', 'options'),
    Output('search-value-dropdown-9', 'options'),
    Output('filter-wrapper-0', 'hidden'),
    Output('filter-wrapper-1', 'hidden'),
    Output('filter-wrapper-2', 'hidden'),
    Output('filter-wrapper-3', 'hidden'),
    Output('filter-wrapper-4', 'hidden'),
    Output('filter-wrapper-5', 'hidden'),
    Output('filter-wrapper-6', 'hidden'),
    Output('filter-wrapper-7', 'hidden'),
    Output('filter-wrapper-8', 'hidden'),
    Output('filter-wrapper-9', 'hidden'),

    ## EDIT DIALOG ##
    Output("modal-edit", "is_open"),
    Output('edit-element-type', 'value'),
    Output('edit-element-type', 'options'),
    Output('edit-element-container', 'children'),
    Output('add-edit-property-label', 'value'),
    Output('add-edit-property-value', 'value'),

    ## ADD DIALOG ##
    Output("modal-add", "is_open"),

    ## ADD NODE DIALOG ##
    Output("modal-addnode", "is_open"),
    Output('addnode-element-type', 'value'),
    Output('addnode-element-type', 'options'),
    Output('addnode-element-container', 'children'),
    Output('add-addnode-property-label', 'value'),
    Output('add-addnode-property-value', 'value'),

    ## ADD EDGE DIALOG ##
    Output("modal-addedge", "is_open"),
    Output('addedge-element-type', 'value'),
    Output('addedge-element-type', 'options'),
    Output('addedge-element-container', 'children'),
    Output('add-addedge-property-label', 'value'),
    Output('add-addedge-property-value', 'value'),
    Output('addedge-source-node', 'options'),
    Output('addedge-target-node', 'options'),

    ## DELETE DIALOG ##
    Output("modal-delete", "is_open"),

    ## MERGE DIALOG ##
    Output("modal-merge", "is_open"),
    Output('merge-elements-type', 'value'),
    Output('merge-elements-type', 'options'),
    Output('merge-element-container', 'children'),
    Output('add-merge-property-label', 'value'),
    Output('add-merge-property-value', 'value'),

    ## EXPORT IMAGE DIALOG ##
    Output("modal-export-image", 'is_open'),
    Output('cytoscape', 'generateImage')
]

inputs = [
    ## CYTOSCAPE FRAME ##
    Input('cytoscape', 'tapNodeData'),
    Input('cytoscape', 'tapEdgeData'),
    Input("unaltered-collapse-button", "n_clicks"),

    ## ELEMENT INTERACTION ##
    Input({'type': 'element-interaction-checkbox', 'id': ALL}, 'value'),
    Input({'type': 'label-display-checkbox', 'id': ALL}, 'value'),

    ## EDGE PROBABILITY SLIDER ##
    Input('edge-prob-slider', 'value'),

    ####################
    ## SIDEBAR INPUTS ##
    ####################

    ## NETWORK TAB ##
    Input('filter-button', 'n_clicks'),  # TODO: Move Line to Element Interaction
    Input('load-network-button', 'n_clicks'),
    Input('load-file-button', 'n_clicks'),
    Input('upload', 'contents'),
    Input('choose-network', 'value'),

    ## ANALYSIS TAB ##
    Input('choose-analysis', 'value'),
    Input('analysis-algorithm', 'value'),
    Input('analysis-button', 'n_clicks'),

    ## ELEMENT INTERACTION ##
    Input("open-edit-element", "n_clicks"),
    Input("open-add-element", "n_clicks"),
    Input("open-delete-element", "n_clicks"),
    Input("open-merge-element", "n_clicks"),
    Input('exclude-button', 'n_clicks'),
    Input('expand-all-button', 'n_clicks'),
    Input('expand-button', 'n_clicks'),

    ###################
    ## DIALOG INPUTS ##
    ###################

    Input("close-dialog", "n_clicks"),
    Input({'type': 'remove-input-field', 'id': ALL}, 'n_clicks'),

    ## CONFIRM LOAD DIALOG ##
    Input('confirm-load-button', 'n_clicks'),
    Input('confirm-load-button2', 'n_clicks'),
    Input('confirm-file-load-button', 'n_clicks'),
    Input('confirm-file-load-button2', 'n_clicks'),
    Input({'type': 'trigger', 'id': ALL}, 'children'),

    ## SEARCH DIALOG ##
    Input({'type': 'search-property-dropdown', 'id': ALL}, 'value'),
    Input({'type': 'remove-search-field', 'id': ALL}, 'n_clicks'),
    Input('add-search-property-button', 'n_clicks'),
    Input('apply-edit-button', 'n_clicks'),

    ## EDIT DIALOG ##
    Input('apply-edit-button', 'n_clicks'),
    Input('add-edit-property-button', 'n_clicks'),

    ## ADD NODE DIALOG ##
    Input('add-node-button', 'n_clicks'),
    Input('add-addnode-property-button', 'n_clicks'),
    Input('apply-addnode-button', 'n_clicks'),

    ## ADD EDGE DIALOG ##
    Input('add-edge-button', 'n_clicks'),
    Input('add-addedge-property-button', 'n_clicks'),
    Input('apply-addedge-button', 'n_clicks'),

    ## DELETE DIALOG ##
    Input('delete-button', 'n_clicks'),

    ## MERGE DIALOG ##
    Input('apply-merge-button', 'n_clicks'),
    Input('add-merge-property-button', 'n_clicks'),

    ## EXPORT IMAGE DIALOG ##
    Input('export-image-button', 'n_clicks'),
    Input('apply-export-image-button', 'n_clicks')
]

states = [

    ## HIGHLIGHT/HIDE INTERACTION ##

    State('node-interaction-table', 'children'),
    State('edge-interaction-table', 'children'),

    ####################
    ## SIDEBAR INPUTS ##
    ####################

    ## NETWORK TAB ##
    State('choose-entities', 'value'),
    State('upload', 'filename'),

    ## ANALYSIS TAB ##
    State('parameter-1', 'value'),

    ###################
    ## DIALOG INPUTS ##
    ###################

    ## SEARCH DIALOG ##
    State('filter-container', 'children'),

    ## EDIT DIALOG ##
    State('edit-element-type', 'value'),
    State('edit-element-container', 'children'),
    State('add-edit-property-label', 'value'),
    State('add-edit-property-value', 'value'),
    State({'type': 'edit-input-field', 'id': ALL}, 'value'),

    ## ADD NODE DIALOG ##
    State('addnode-element-type', 'value'),
    State('addnode-element-name', 'value'),
    State('addnode-element-container', 'children'),
    State('add-addnode-property-label', 'value'),
    State('add-addnode-property-value', 'value'),
    State({'type': 'addnode-input-field', 'id': ALL}, 'value'),

    ## ADD EDGE DIALOG ##
    State('addedge-element-type', 'value'),
    State('addedge-element-name', 'value'),
    State('addedge-source-node', 'value'),
    State('addedge-target-node', 'value'),
    State('addedge-element-container', 'children'),
    State('add-addedge-property-label', 'value'),
    State('add-addedge-property-value', 'value'),
    State({'type': 'addedge-input-field', 'id': ALL}, 'value'),

    ## MERGE DIALOG ##
    State('merge-elements-type', 'value'),
    State('merge-element-container', 'children'),
    State('add-merge-property-label', 'value'),
    State('add-merge-property-value', 'value'),
    State({'type': 'merge-input-field', 'id': ALL}, 'value'),

    ## EXPORT IMAGE DIALOG ##
    State('export-dropdown', 'value')
]

input_names = [
    #############################################
    ################## INPUTS ###################
    #############################################

    ## 'CYTOSCAPE' 'FRAME' ##
    'clicked_node', 'clicked_edge', 'unaltered_collapse_button_clicks',

    ## 'ELEMENT' 'INTERACTION' ##
    'element_interaction_checkbox', 'label_display_checkbox',

    ## 'EDGE' 'PROBABILITY' 'SLIDER' ##
    'edge_prob_slider_value',

    ################# 'SIDEBAR' 'INPUTS' ############

    ## 'NETWORK' 'TAB' ##
    'advanced_search_clicks', 'load_network_clicks',
    'upload_button_clicks', 'uploaded_file', 'network_selection',

    ## 'ANALYSIS' 'TAB' ##
    'analysis_function', 'analysis_algorithm', 'analysis_button_clicks',

    ## 'ELEMENT' 'INTERACTION' ##
    'edit_clicks', 'add_clicks', 'delete_clicks', 'merge_clicks',
    'exclude_clicks', 'expand_all_clicks', 'expand_button_clicks',

    ############### 'DIALOG' 'INPUTS' ###############

    'close_clicks', 'remove_input_clicks',

    ## 'CONFIRM' 'LOAD' 'DIALOG' ##
    'confirm_load_button', 'confirm_load_button2',
    'confirm_file_load_button', 'confirm_file_load_button2',
    'load_trigger',

    ## 'SEARCH' 'DIALOG' ##
    'search_property_dropdown_input',
    'remove_search_field_clicks',
    'add_search_property_clicks',
    'apply_edit_button_clicks',

    ## 'EDIT' 'DIALOG' ##
    'apply_edit_clicks', 'add_edit_property_clicks',

    ## 'ADD' 'NODE' 'DIALOG' ##
    'add_node_button_clicks', 'add_addnode_property_clicks',
    'apply_addnode_button_clicks',

    ## 'ADD' 'EDGE' 'DIALOG' ##
    'add_edge_button_clicks', 'add_addedge_property_clicks',
    'apply_addedge_button_clicks',

    ## 'DELETE' 'DIALOG' ##
    'delete_button_clicks',

    ## 'MERGE' 'DIALOG' ##
    'apply_merge_clicks', 'add_merge_property_clicks',

    ## 'EXPORT' 'IMAGE' 'DIALOG' ##
    'export_image_clicks', 'apply_export_image_clicks',

    ###############################################
    ################### 'STATES' ####################
    ###############################################

    ## 'HIGHLIGHT'/'HIDE' 'INTERACTION' ##
    'node_interaction_table', 'edge_interaction_table',

    ############### 'SIDEBAR' 'INPUTS' ################

    ## 'NETWORK' 'TAB' ##
    'entities', 'uploaded_filename',

    ## 'ANALYSIS' 'TAB' ##
    'parameter_1',

    ################ 'DIALOG' 'INPUTS' ################

    ## 'SEARCH' 'DIALOG' ##
    'filter_container',


    ## 'EDIT' 'DIALOG' ##
    'edit_element_type', 'edit_element_container',
    'add_edit_property_label', 'add_edit_property_value', 'edit_input_fields',

    ## 'ADD' 'NODE' 'DIALOG' ##
    'addnode_elements_type', 'addnode_element_name', 'addnode_element_container',
    'add_addnode_property_label', 'add_addnode_property_value', 'addnode_input_field',

    ## 'ADD' 'EDGE' 'DIALOG' ##
    'addedge_element_type', 'addedge_element_name',
    'addedge_source_node', 'addedge_target_node',
    'addedge_element_container', 'add_addedge_property_label',
    'add_addedge_property_value', 'addedge_input_field',

    ## 'MERGE' 'DIALOG' ##
    'merge_elements_type', 'merge_element_container',
    'add_merge_property_label', 'add_merge_property_value',
    'merge_input_fields',

    ## 'EXPORT' 'IMAGE' 'DIALOG' ##
    'export_type'
]

main_callback_args = [

]

def output(
        ## CYTOSCAPE FRAME ##
        elements=dash.no_update,
        stylesheet=dash.no_update,
        layout=dash.no_update,
        cytoscape_class=dash.no_update,

        ## COMPARISON NETWORK ##
        elements_unaltered=dash.no_update,
        stylesheet_unaltered=dash.no_update,
        layout_unaltered=dash.no_update,
        cytoscape_unaltered_class=dash.no_update,
        collapse_button_text=dash.no_update,
        hide_interaction_checkboxes=dash.no_update,
        hide_original_network_button=dash.no_update,

        ## WARNING ##
        message=dash.no_update,

        # ELEMENT INTERACTION ##
        node_interaction_table=dash.no_update,
        edge_interaction_table=dash.no_update,
        label_interaction_table=dash.no_update,

        # PROB SLIDER #
        hide_prob_slider=dash.no_update,

        #####################
        ## SIDEBAR OUTPUTS ##
        #####################

        ## INFO ##
        network_info=dash.no_update,

        ## NETWORK TAB ##
        entity_options=dash.no_update,
        entity_values=dash.no_update,

        ## ANALYSIS TAB ##
        analysis_algorithms=dash.no_update,
        analysis_parameter=dash.no_update,

        ####################
        ## DIALOG OUTPUTS ##
        ####################

        ## DIALOG STYLE ##
        grey_background=None,

        ## CONFIRM LOAD ##
        show_confirm_load = dash.no_update,
        show_confirm_load2 = dash.no_update,
        show_confirm_file_load=dash.no_update,
        show_confirm_file_load2=dash.no_update,
        hidden_info=dash.no_update,

        ## SEARCH DIALOG ##
        show_search_dialog=dash.no_update,
        filter_container=dash.no_update,
        search_value_options_0=dash.no_update,
        search_value_options_1=dash.no_update,
        search_value_options_2=dash.no_update,
        search_value_options_3=dash.no_update,
        search_value_options_4=dash.no_update,
        search_value_options_5=dash.no_update,
        search_value_options_6=dash.no_update,
        search_value_options_7=dash.no_update,
        search_value_options_8=dash.no_update,
        search_value_options_9=dash.no_update,
        hide_filter_0=dash.no_update,
        hide_filter_1=dash.no_update,
        hide_filter_2=dash.no_update,
        hide_filter_3=dash.no_update,
        hide_filter_4=dash.no_update,
        hide_filter_5=dash.no_update,
        hide_filter_6=dash.no_update,
        hide_filter_7=dash.no_update,
        hide_filter_8=dash.no_update,
        hide_filter_9=dash.no_update,

        ## EDIT DIALOG ##
        show_edit_dialog=dash.no_update,
        edit_element_type=dash.no_update,
        edit_element_type_options=dash.no_update,
        edit_element_container=dash.no_update,
        add_edit_property_label=dash.no_update,
        add_edit_property_value=dash.no_update,

        ## ADD DIALOG ##
        show_add_dialog=dash.no_update,

        ## ADD NODE DIALOG ##
        show_add_node_dialog=dash.no_update,
        addnode_element_typ_value=dash.no_update,
        addnode_element_type_options=dash.no_update,
        addnode_element_container=dash.no_update,
        add_addnode_property_label=dash.no_update,
        add_addnode_property_value=dash.no_update,

        ## ADD EDGE DIALOG ##
        show_add_edge_dialog=dash.no_update,
        addedge_element_type_value=dash.no_update,
        addedge_element_type_option=dash.no_update,
        addedge_element_container=dash.no_update,
        add_addedge_property_label=dash.no_update,
        add_addedge_property_value=dash.no_update,
        addedge_source_node_options=dash.no_update,
        addedge_target_node_options=dash.no_update,

        ## DELETE DIALOG ##
        show_delete_dialog=dash.no_update,

        ## MERGE DIALOG ##
        show_merge_dialog=dash.no_update,
        merge_element_type=dash.no_update,
        merge_element_type_options=dash.no_update,
        merge_element_container=dash.no_update,
        add_merge_property_label=dash.no_update,
        add_merge_property_value=dash.no_update,

        ## EXPORT IMAGE DIALOG ##
        show_export_image_dialog=dash.no_update,
        image_export=dash.no_update
):
    if grey_background:
        grey_background = {"display": "block"}
    if not grey_background:
        grey_background = {"display": "none"}
    return tuple(locals().values())