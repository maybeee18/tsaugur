from tsaugur.models.sarima import Sarima
from tsaugur.models.fourier_sarima import FourierSarima
from tsaugur.models.holt_winters import HoltWinters


MODEL_KEY_SARIMA = "sarima"
MODEL_KEY_FOURIER_SARIMA = "fourier_sarima"
MODEL_KEY_HOLT_WINTERS = "holt_winters"

MODELS = {
    MODEL_KEY_SARIMA: Sarima(),
    MODEL_KEY_FOURIER_SARIMA: FourierSarima(),
    MODEL_KEY_HOLT_WINTERS: HoltWinters(),
}


def create_model(model_key):
    """
    Instantiate the model class.
    :param model_key: Str, a unique identifier of a tsaugur model class for a specific model.
    :return: The tsaugur model class for the requested model.
    """
    return MODELS[model_key]
