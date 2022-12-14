""" Network construction tasks """
from datetime import datetime, timezone
from falcon import Request, Response, before, HTTP_202
from ..tasks.celery_tasks import perform_parse_wp5_output, perform_parse_wp5_output_for_aegis
from ..hooks.secure_resource import Secure
from ..helpers.validate_schema import validate_schema
from ..schemas.tasks_schemas import network_construction_input
from ..exceptions import ValidationError, FormValidationError, ResourceError
from ..helpers.task_helpers import generate_response, get_bool_field, save_form_file
from ..helpers.log_helpers import log_event
from ..helpers.format_helpers import timestamp_format


@before(Secure("User"))
class NetworkConstructionTasksResource(object):
    """
    summary: Network Construction Tasks Resource
    description: Allows submission of tasks for the network construction
    """

    def parse_form_data(self, context):
        """ Parse form contents """
        filepath = save_form_file(context.form, context.user.get_folder_path())
        threshold = 0
        calibration = get_bool_field(context.form, "calibration")
        directed = get_bool_field(context.form, "directed")
        try:
            threshold = float(context.form["threshold"].value) if "threshold" in context.form else 50
        except ValueError:
            raise FormValidationError("threshold must be a float value", "threshold field")
        return filepath, threshold, calibration, directed

    def handle_parse_wp5_output(self, req: Request, resp: Response):
        """ Create wp5 output parsing task """
        task_result = None
        if hasattr(req.context, "form"):
            filepath, threshold, calibration, directed = self.parse_form_data(req.context)
            task_result = perform_parse_wp5_output.delay(
                threshold,
                calibration,
                directed,
                timestamp_format(datetime.now(timezone.utc)),
                filepath=filepath
            )
            generate_response(resp, task_result.id)
            log_event(
                req.context.request_id,
                "Network constructon task dispatched from uploaded file",
                id=task_result.id,
                file=filepath)
            return
        if req.media.get("network"):
            task_result = perform_parse_wp5_output.delay(
                req.media.get("threshold", 50),
                req.media.get("calibration", False),
                req.media.get("directed", False),
                timestamp_format(datetime.now(timezone.utc)),
                network=req.media["network"]
            )
            generate_response(resp, task_result.id)
            log_event(
                req.context.request_id,
                "Network construction task dispatched from provided network",
                id=task_result.id)
            return
        raise ValidationError("Please provide network to construct with 'network' field", "request body")

    def handle_parse_wp5_output_for_aegis(self, req: Request, resp: Response):
        """ Create wp5 output parsing task for aegis """
        task_result = None
        if hasattr(req.context, "form"):
            filepath, threshold, calibration, directed = self.parse_form_data(req.context)
            task_result = perform_parse_wp5_output_for_aegis.delay(
                threshold,
                calibration,
                directed,
                timestamp_format(datetime.now(timezone.utc)),
                filepath=filepath
            )
            generate_response(resp, task_result.id)
            log_event(
                req.context.request_id,
                "Network constructon task dispatched from uploaded file",
                id=task_result.id,
                file=filepath)
            return
        if req.media.get("network"):
            task_result = perform_parse_wp5_output_for_aegis.delay(
                req.media.get("threshold", 50),
                req.media.get("calibration", False),
                req.media.get("directed", False),
                timestamp_format(datetime.now(timezone.utc)),
                network=req.media["network"]
            )
            generate_response(resp, task_result.id)
            log_event(
                req.context.request_id,
                "Network construction task dispatched from provided network",
                id=task_result.id)
            return
        raise ValidationError("Please provide network to construct with 'network' field", "request body")

    @validate_schema(network_construction_input)
    def on_post_v1_0(self, req: Request, resp: Response, task_name):
        """
        summary: Submit new network construction task
        externalDocs:
            description: Example python code to make network construction tasks
            url: /docs/api_examples.html#network_construction
        parameters:
            -   in: path
                name: task_name
                required: true
                schema:
                    type: string
                description: Name of the network construction algorithm
        requestBody:
            description: Task data
            content:
                application/json:
                    schema: NetworkConstructionInput
                    examples:
                        - TaskPostRequestNetworkConstructionJSONExample
                application/msgpack:
                    schema: NetworkConstructionInput
                    examples:
                        - TaskPostRequestNetworkConstructionJSONExample
                multipart/form-data:
                    schema:
                        type: object
                        properties:
                            file:
                                type: string
                                format: binary
                            threshold:
                                type: number
                            calibration:
                                type: boolean
                            directed:
                                type: boolean
                    encoding:
                        file:
                            contentType: application/json
                    examples:
                        - TaskPostRequestNetworkConstructionMultipartExample
        responses:
            202:
                description: Task submitted
                headers:
                    Operation-Location:
                        description: Relative path to the newly submitted task
                        schema:
                            type: string
        security:
            - jwt:
                - User
        errors:
            - name: FileExistsError
              message: File already exists!
              target: filename
            - name: FormValidationError
              message: "Form key not found: key"
              target: form
            - name: FormValidationError
              message: threshold must be a float value
              target: threshold field
            - name: FormValidationError
              message: file field not found
              target: format
            - name: FormValidationError
              message: calibration must be a boolean value
              target: calibration field
            - name: FormValidationError
              message: directed must be a boolean value
              target: directed field

        examples:
            - ex_name: TaskPostRequestNetworkConstructionJSONExample
              summary: Passing network to construct
              network:
                conversations:
                    - channels:
                        - id: s02e04-Conv10_davidphillips
                          fileName: s02e04-Conv10_davidphillips.wav
                          gender: Male
                          genderConfidence: 0.916986
                          age: 27
                          ageConfidence: 1
                          language: English_American
                          languageConfidence: -1.3236703
                          transcription: bla bla bla
                          entities:
                            PER:
                                - Steve
                voiceprintsMatrix:
                    s02e04-Conv10_davidphillips:
                        s02e04-Conv10_davidphillips: 15.175955
                taskId: 39005885-f8d7-4fa1-9db1-33e8785a37ff
                threshold: 50
                calibration: true
                directed: true
            - ex_name: TaskPostRequestNetworkConstructionMultipartExample
              summary: Construct network from file
              file: {}
              threshold: 50
              calibration: true
              directed: true
        """
        if task_name == "parse_wp5_output":
            self.handle_parse_wp5_output(req, resp)
        elif task_name == "parse_wp5_output_for_aegis":
            self.handle_parse_wp5_output_for_aegis(req, resp)
        else:
            raise ResourceError("No such network construction method", "url")
