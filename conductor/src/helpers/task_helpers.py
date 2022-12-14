""" Helpers for processing API tasks """
from ..exceptions import FormValidationError
from falcon import HTTP_202
from werkzeug.utils import secure_filename
from ..helpers.file_helpers import save_file


def get_bool_field(form, field_name, default=None) -> False:
    """
    Get value from boolean form field
    :param form: Input form
    :param field_name: Name of the field
    :param default: Default field value
    """
    if field_name in form:
        if form[field_name].value == "true":
            return True
        elif form[field_name].value == "false":
            return False
        elif default is None:
            raise FormValidationError(f"{field_name} must be a boolean value", f"{field_name} field")
        return default
    raise FormValidationError(f"no such field {field_name} in form", "form")


def generate_response(resp, task_id):
    """ Generate task creation response """
    resp.status = HTTP_202
    resp.append_header("Operation-Location", "/v1.0/operations/" + str(task_id))


def save_form_file(form, user_folder, field_name="file"):
    """
    Save form file and return its path
    :param form: Data form
    :param user_folder: folder of the user data
    :param field_name: name of the file field
    :returns: path to the file
    """
    try:
        filename = secure_filename(form[field_name].filename)
        filepath = str(user_folder / filename)
        return save_file(form[field_name].file, filepath)
    except KeyError:
        raise FormValidationError("file field not found", "form")
