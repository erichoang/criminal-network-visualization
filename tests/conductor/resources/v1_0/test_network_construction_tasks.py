""" Unit tests for the network construction tasks """
from os.path import isfile
from unittest.mock import patch, MagicMock, ANY
from requests_toolbelt import MultipartEncoder
from falcon.testing import TestClient
from conductor.src.auth_models import User


wp5_data = {
    "network": {
        "conversations": [
            {
                "channels": [
                    {
                        "id": "conv1"
                    }
                ]
            }
        ],
        "voiceprintsMatrix": {
            "conv1": 5.13123123
        }
    },
    "threshold": 100,
    "calibration": True,
    "directed": True
}


def test_network_construction_task_should_call_perform_parse_wp5_output_and_request_is_post_json(client: TestClient, prepared_header):
    """ post request on network construction task resource with parse_wp5_output task name should create perform_parse_wp5_output task """
    result_mock = MagicMock()
    result_mock.id = "super-id"
    with patch("conductor.src.resources.network_construction_tasks.perform_parse_wp5_output") as task_mock:
        task_mock.delay.return_value = result_mock
        result = client.simulate_post("/v1.0/tasks/network_construction/parse_wp5_output", json=wp5_data, headers=prepared_header)
        task_mock.delay.assert_called_once_with(
            wp5_data["threshold"],
            True,
            True,
            ANY,
            network=wp5_data["network"]
        )
        assert result.status_code == 202
        assert result_mock.id in result.headers["Operation-Location"]


def test_network_construction_task_should_call_perform_parse_wp5_output_and_request_is_post_file_form(client: TestClient, prepared_header, prepared_file, prepared_user: User):
    """ post request on task resource with parse_wp5_output task name with multipart form request should create perform_parse_wp5_output task with file path """
    filename = "testfile.json"
    multipart_data = {
        "threshold": "100",
        "calibration": "false",
        "directed": "true",
        "file": (filename, prepared_file, "application/json")
    }
    multipart_file = MultipartEncoder(
        fields=multipart_data
    )
    prepared_header["Content-Type"] = multipart_file.content_type
    result_mock = MagicMock()
    result_mock.id = "super-id"
    with patch("conductor.src.resources.network_construction_tasks.perform_parse_wp5_output") as task_mock:
        task_mock.delay.return_value = result_mock
        response = client.simulate_post("/v1.0/tasks/network_construction/parse_wp5_output", headers=prepared_header, body=multipart_file.to_string())
        print(response)
        task_mock.delay.assert_called_once_with(
            float(multipart_data["threshold"]),
            False,
            True,
            ANY,
            filepath=str(prepared_user.get_folder_path() / filename)
        )
        assert response.status_code == 202
        assert result_mock.id in response.headers["Operation-Location"]


def test_network_construction_task_should_call_perform_parse_wp5_output_for_aegis_and_request_is_post_json(client: TestClient, prepared_header):
    """ post request on network construction task resource with parse_wp5_output_for_aegis task name should create perform_parse_wp5_output_for_aegis task """
    result_mock = MagicMock()
    result_mock.id = "super-id"
    with patch("conductor.src.resources.network_construction_tasks.perform_parse_wp5_output_for_aegis") as task_mock:
        task_mock.delay.return_value = result_mock
        result = client.simulate_post("/v1.0/tasks/network_construction/parse_wp5_output_for_aegis", json=wp5_data, headers=prepared_header)
        task_mock.delay.assert_called_once_with(
            wp5_data["threshold"],
            wp5_data["calibration"],
            wp5_data["directed"],
            ANY,
            network=wp5_data["network"]
        )
        assert result.status_code == 202
        assert result_mock.id in result.headers["Operation-Location"]


def test_network_construction_task_should_call_perform_parse_wp5_output_for_aegis_and_request_is_post_file_form(client: TestClient, prepared_header, prepared_file, prepared_user: User):
    """ post request on task resource with parse_wp5_output_for_aegis task name with multipart form request should create perform_parse_wp5_output_for_aegis task with file path """
    filename = "testfile.json"
    multipart_data = {
        "threshold": "100",
        "calibration": "false",
        "directed": "true",
        "file": (filename, prepared_file, "application/json")
    }
    multipart_file = MultipartEncoder(
        fields=multipart_data
    )
    prepared_header["Content-Type"] = multipart_file.content_type
    result_mock = MagicMock()
    result_mock.id = "super-id"
    with patch("conductor.src.resources.network_construction_tasks.perform_parse_wp5_output_for_aegis") as task_mock:
        task_mock.delay.return_value = result_mock
        response = client.simulate_post("/v1.0/tasks/network_construction/parse_wp5_output_for_aegis", headers=prepared_header, body=multipart_file.to_string())
        print(response)
        task_mock.delay.assert_called_once_with(
            float(multipart_data["threshold"]),
            False,
            True,
            ANY,
            filepath=str(prepared_user.get_folder_path() / filename)
        )
        assert response.status_code == 202
        assert result_mock.id in response.headers["Operation-Location"]


def test_network_construction_task_should_return_error_message_if_network_construction_task_not_found(client: TestClient, prepared_user: User, prepared_header):
    """ post request on network construction task resource with incorrect task name should return ResourceError """
    result = client.simulate_post("/v1.0/tasks/network_construction/randoom", json=wp5_data, headers=prepared_header)
    assert result.status_code == 404
    assert "ResourceError" in str(result.content)
