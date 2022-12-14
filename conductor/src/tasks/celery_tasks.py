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

 Long running analysis tasks """
import os
from datetime import datetime, timezone
import ujson
from ..celery import celery
from ..exceptions import TaskError
from ..helpers.format_helpers import timestamp_format
from storage.fft_helpers import parse_wp5_output, parse_wp5_output_for_aegis
from storage.builtin_datasets import BuiltinDataset
from analyzer.request_taker import InMemoryAnalyzer


def hanlde_task_result(result, started_at):
    """ Return different results, based on  """
    if not result["success"]:
        raise TaskError(result["message"], "Task")
    analysis_result = {k: result[k] for k in result if not (k == "success" or k == "message")}
    return {
        "createdDateTime": started_at,
        "lastActionDateTime": timestamp_format(datetime.now(timezone.utc)),
        "status": "SUCCESS",
        "description": "Analysis resulted successfully",
        "result": analysis_result
    }


@celery.task(bind=True, name="conductor.src.tasks.celery_tasks.perform_analysis_file")
def perform_analysis_file(self, filepath, task_id, options, started_at, params=None):
    """
    Create dataset from file and perform analysis on it

    :param filepath: Path to the network file
    :param task_id: Task name
    :param options: Task options
    :param started_at: Time, when task was dispatched
    :param params: Task parameters
    :returns: Analyzer result
    """
    self.update_state(state="STARTED", meta={
        "progress": 0,
        "status": "STARTED",
        "description": "Reading the dataset",
        "createdDateTime": started_at,
        "lastActionDateTime": timestamp_format(datetime.now(timezone.utc))})
    if not os.path.isfile(filepath):
        raise RuntimeError(f"File {filepath} not found!")
    dataset = BuiltinDataset(filepath)
    os.remove(filepath)
    analyzer = InMemoryAnalyzer()
    self.update_state(state="PROGRESS", meta={
        "progress": 5,
        "status": "PROGRESS",
        "description": "Performing the analysis",
        "createdDateTime": started_at,
        "lastActionDateTime": timestamp_format(datetime.now(timezone.utc))})
    result = analyzer.perform_analysis({
        "task_id": task_id,
        "network": dataset.get_network(),
        "options": options
    }, params=params)
    show_result = hanlde_task_result(result, started_at)
    return show_result


@celery.task(bind=True, name="conductor.src.tasks.celery_tasks.perform_analysis_network")
def perform_analysis_network(self, task, started_at, params=None):
    """
    Recieve network and analyse it
    :param task: Task data for InMemoryAnalyzer
    :param started_at: When task was dispatched
    :param params: Parameters for analysis function
    :returns: Analyzer result
    """
    self.update_state(state="STARTED", meta={
        "progress": 0,
        "status": "STARTED",
        "description": "Initializing the analyzer",
        "createdDateTime": started_at,
        "lastActionDateTime": timestamp_format(datetime.now(timezone.utc))})
    analyzer = InMemoryAnalyzer()
    self.update_state(state="PROGRESS", meta={
        "progress": 5,
        "status": "PROGRESS",
        "description": "Performing the analysis",
        "createdDateTime": started_at,
        "lastActionDateTime": timestamp_format(datetime.now(timezone.utc))})
    result = analyzer.perform_analysis(task, params=params)
    show_result = hanlde_task_result(result, started_at)
    return show_result


@celery.task(bind=True, name="conductor.src.tasks.celery_tasks.perform_parse_wp5_output")
def perform_parse_wp5_output(self, threshold, calibration, directed, started_at, network=None, filepath=None):
    """
    Construct network from wp5
    :param threshold: Parsing threshold
    :param calibration: Calibration value
    :param directed: Tells if the network is directed
    :param network: wp5 network as dictonary
    :param filepath: Path to a wp5 network
    :param started_at: Time, when task was started
    :returns: Constructed network
    """
    self.update_state(state="STARTED", meta={
        "progress": 0,
        "status": "STARTED",
        "description": "Initializing network parsing",
        "createdDateTime": started_at,
        "lastActionDateTime": timestamp_format(datetime.now(timezone.utc))})
    if filepath:
        self.update_state(state="PROGRESS", meta={
            "progress": 1,
            "status": "PROGRESS",
            "description": "Reading network file",
            "createdDateTime": started_at,
            "lastActionDateTime": timestamp_format(datetime.now(timezone.utc))})
        with open(filepath, "r") as network_file:
            network = ujson.load(network_file)
        os.remove(filepath)
    self.update_state(state="PROGRESS", meta={
        "progress": 5,
        "status": "PROGRESS",
        "description": "Parsing the wp5 network",
        "createdDateTime": started_at,
        "lastActionDateTime": timestamp_format(datetime.now(timezone.utc))})
    result = None
    try:
        result = parse_wp5_output(network, threshold, calibration, directed)
    except Exception as ex:
        raise TaskError(str(ex), "Task")
    return {
        "createdDateTime": started_at,
        "lastActionDateTime": timestamp_format(datetime.now(timezone.utc)),
        "status": "SUCCESS",
        "description": "Network parsed successfully",
        "result": result
    }


@celery.task(bind=True, name="conductor.src.tasks.celery_tasks.perform_parse_wp5_output_for_aegis")
def perform_parse_wp5_output_for_aegis(self, threshold, calibration, directed, started_at, network=None, filepath=None):
    """
    Construct network from wp5
    :param directed: Tells if the network is directed
    :param network: wp5 network as dictonary
    :param filepath: Path to a wp5 network
    :param started_at: Time, when task was started
    :returns: Constructed network
    """
    self.update_state(state="STARTED", meta={
        "progress": 0,
        "status": "STARTED",
        "description": "Initializing network parsing",
        "createdDateTime": started_at,
        "lastActionDateTime": timestamp_format(datetime.now(timezone.utc))})
    if filepath:
        self.update_state(state="PROGRESS", meta={
            "progress": 1,
            "status": "PROGRESS",
            "description": "Reading network file",
            "createdDateTime": started_at,
            "lastActionDateTime": timestamp_format(datetime.now(timezone.utc))})
        with open(filepath, "r") as network_file:
            network = ujson.load(network_file)
        os.remove(filepath)
    self.update_state(state="PROGRESS", meta={
        "progress": 5,
        "status": "PROGRESS",
        "description": "Parsing the wp5 network",
        "createdDateTime": started_at,
        "lastActionDateTime": timestamp_format(datetime.now(timezone.utc))})
    result = None
    try:
        result = parse_wp5_output_for_aegis(network, threshold, calibration, directed)
    except Exception as ex:
        raise TaskError(str(ex), "Task")
    return {
        "createdDateTime": started_at,
        "lastActionDateTime": timestamp_format(datetime.now(timezone.utc)),
        "status": "SUCCESS",
        "description": "Network parsed successfully",
        "result": result
    }
