""" Helpers for the task resources """
import pytest
from pathlib import Path
from falcon import HTTP_202
from ....conductor.src.helpers.task_helpers import get_bool_field, generate_response, save_form_file
from ....conductor.src.exceptions import FormValidationError
from unittest.mock import MagicMock, patch


def test_get_bool_field_should_return_true_if_form_value_is_string_with_true():
    """ get_bool_field should return True if field value is 'true' """
    form_field = MagicMock()
    form_field.value = "true"
    form = {"field": form_field}
    assert get_bool_field(form, "field")


def test_get_bool_field_should_return_false_if_form_value_is_string_with_false():
    """ get_bool_field should return False if field value is 'false' """
    form_field = MagicMock()
    form_field.value = "false"
    form = {"field": form_field}
    assert not get_bool_field(form, "field")


def test_get_bool_field_should_raise_FormValidationError_if_field_is_not_boolean():
    """
    get_bool_field should raise FormValidationError if
    form fields value is neither 'true' or 'false'
    """
    form_field = MagicMock()
    form_field.value = "random"
    form = {"wrong": form_field}
    with pytest.raises(FormValidationError):
        get_bool_field(form, "field")


def test_get_bool_field_should_return_default_when_set_and_value_is_not_boolean():
    """
    get_bool_field should return the default value if default is set and value is not a boolean
    """
    form_field = MagicMock()
    form_field.value = "pepe"
    default = True
    form = {"field": form_field}
    assert default == get_bool_field(form, "field", default)


def test_generate_response_should_set_http_code_to_202_and_set_operation_location_header():
    """
    generate_response should set the http response code to 202 accepted and
    set the Operation-Location header to the address of the operation results
    """
    response_mock = MagicMock()
    task_id = "some-task-id"
    generate_response(response_mock, task_id)
    assert response_mock.status == HTTP_202
    response_mock.append_header.assert_called_once_with("Operation-Location", "/v1.0/operations/" + str(task_id))


def test_save_form_file_should_save_file_in_user_directory_and_return_filepath():
    """
    save_form_file should sanitize the filename, add it to the user directory, save the file
    and return the filepath
    """
    form_field = MagicMock()
    form_field.filename = "path/to/file.json"
    file_mock = MagicMock()
    form_field.file = file_mock
    user_folder = Path("/some/user/path/")
    form = {"file": form_field}
    with patch("sna.conductor.src.helpers.task_helpers.save_file") as save_mock:
        save_form_file(form, user_folder, "file")
        save_args = save_mock.call_args[0]
        assert save_args[0] is file_mock
        assert str(user_folder / "path_to_file.json") == save_args[1]


def test_save_form_file_should_raise_FormValidationError_if_field_not_found():
    """
    save_form_file_should raise FormValidationError if the field is not found
    on the form
    """
    user_folder = Path("/some/user/path/")
    form = {}
    with pytest.raises(FormValidationError):
        save_form_file(form, user_folder, "file")
