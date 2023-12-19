"""
Request validator for TranscribeAndClip.
"""
# local package imports
from ..ml.clipfind.texttile_config_manager import TextTileClipFinderConfigManager
from ..ml.transcribe.whisperx_config_manager import WhisperXTranscriberConfigManager
from ..utils.pytorch import check_valid_torch_device
from ..request_validator import RequestValidator


class TranscribeAndClipRequestValidator(RequestValidator):
    """
    RequestValidator Class for TranscribeAndClip.
    """

    def __init__(self) -> None:
        """
        Initialize the TranscribeAndClipRequestValidator class.
        """
        super().__init__()

    def check_valid_request_data(self, request_data: dict) -> str or None:
        """
        Checks if the request data is valid. Returns None if so, a descriptive error
        message if not.

        Parameters
        ----------
        request_data: dict
            The request data to be validated.

        Returns
        -------
        str or None
            None if the request data is valid, a descriptive error message if not.
        """
        correct_types = {
            # optional fields from client
            # transcribe
            "mediaFilePath": (str),
            "computeDevice": (str, type(None)),
            "precision": (str, type(None)),
            "languageCode": (str),
            "whisperModelSize": (str, type(None)),
            # clip
            "cutoffPolicy": (str),
            "embeddingAggregationPoolMethod": (str),
            "minClipTime": (float, int),
            "maxClipTime": (float, int),
            "smoothingWidth": (int),
            "windowComparePoolMethod": (str),
        }

        # existence and type check
        error = self.check_request_data_existence_and_types(request_data, correct_types)
        if error is not None:
            return error

        # file extension check
        if not request_data["mediaFilePath"].endswith((".mp3", ".mp4")):
            error = "mediaFilePath must be of type mp3 or mp4. Received: {}".format(
                request_data["mediaFilePath"]
            )
            return error

        # computeDevice
        if request_data["computeDevice"] is not None:
            error = check_valid_torch_device(request_data["computeDevice"])
            if error is not None:
                return error

        # WhisperXTranscriber configuration
        whisperx_config = {
            "language": request_data["languageCode"],
            "model_size": request_data["whisperModelSize"],
            "precision": request_data["precision"],
        }
        whisperx_config_manager = WhisperXTranscriberConfigManager()
        error = whisperx_config_manager.check_valid_config(whisperx_config)
        if error is not None:
            return error

        # TextTiler Configuration
        texttile_config = {
            "cutoff_policy": request_data["cutoffPolicy"],
            "embedding_aggregation_pool_method": request_data[
                "embeddingAggregationPoolMethod"
            ],
            "max_clip_duration_secs": request_data["maxClipTime"],
            "min_clip_duration_secs": request_data["minClipTime"],
            "smoothing_width": request_data["smoothingWidth"],
            "window_compare_pool_method": request_data["windowComparePoolMethod"],
        }
        texttile_config_manager = TextTileClipFinderConfigManager()
        error = texttile_config_manager.check_valid_config(texttile_config)
        if error is not None:
            return error

        return None

    def impute_request_data_defaults(self, request_data: dict) -> dict:
        """
        Populates request data with default values if they are not provided.

        Parameters
        ----------
        request_data: dict
            The request data to be imputed.

        Returns
        -------
        dict
            The imputed request data.
        """
        optional_fields_default_values = {
            "computeDevice": None,
            # transcription
            "precision": None,
            "languageCode": "en",
            "whisperModelSize": None,
            # clip
            "cutoffPolicy": "high",
            "embeddingAggregationPoolMethod": "max",
            "minClipTime": 15,
            "maxClipTime": 900,
            "smoothingWidth": 3,
            "windowComparePoolMethod": "mean",
        }

        for key in optional_fields_default_values.keys():
            if key not in request_data:
                request_data[key] = optional_fields_default_values[key]

        return request_data
