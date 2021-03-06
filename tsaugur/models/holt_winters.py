import itertools
import warnings
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from tsaugur.utils import data_utils, model_utils
from tsaugur.models import base_model
from tsaugur.metrics import get_metric


class HoltWinters(base_model.BaseModel):
    """
    Holt-Winters Exponential Smoothing.
    """

    def _tune(self, y, period, x=None, metric="smape", val_size=None, verbose=False):
        """
        Tune hyperparameters of the model.
        :param y: pd.Series or 1-D np.array, time series to predict.
        :param period: Int or Str, the number of observations per cycle: 1 or "annual" for yearly data, 4 or "quarterly"
        for quarterly data, 7 or "daily" for daily data, 12 or "monthly" for monthly data, 24 or "hourly" for hourly
        data, 52 or "weekly" for weekly data. First-letter abbreviations of strings work as well ("a", "q", "d", "m",
        "h" and "w", respectively). Additional reference: https://robjhyndman.com/hyndsight/seasonal-periods/.
        :param x: not used for Holt-Winters model
        :param metric: Str, the metric used for model selection. One of: "mse", "mae", "mape", "smape", "rmse".
        :param val_size: Int, the number of most recent observations to use as validation set for tuning.
        :param verbose: Boolean, True for printing additional info while tuning.
        :return: None
        """
        self.period = data_utils.period_to_int(period) if type(period) == str else period
        val_size = int(len(y) * .1) if val_size is None else val_size
        y_train, y_val = model_utils.train_val_split(y, val_size=val_size)
        metric_fun = get_metric(metric)

        params_grid = {
            "trend": ["add", "mul"],
            "seasonal": ["add", "mul"],
            "damped": [True, False],
            "use_boxcox": [True, False, "log"],
            "remove_bias": [True, False]
        }
        params_keys, params_values = zip(*params_grid.items())
        params_permutations = [dict(zip(params_keys, v)) for v in itertools.product(*params_values)]

        scores = []
        for permutation in params_permutations:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    model = ExponentialSmoothing(y_train, seasonal_periods=self.period, trend=permutation["trend"],
                                                 seasonal=permutation["seasonal"], damped=permutation["damped"])
                    model = model.fit(use_boxcox=permutation["use_boxcox"], remove_bias=permutation["remove_bias"])
                    y_pred = model.forecast(len(y_val))
                    score = metric_fun(y_val, y_pred)
                    scores.append(score)
            except:
                scores.append(np.inf)

        best_params = params_permutations[np.nanargmin(scores)]
        self.params.update(best_params)
        self.params["tuned"] = True

    def fit(self, y, period, x=None, metric="smape", val_size=None, verbose=False):
        """
        Build the model with using best-tuned hyperparameter values.
        :param y: pd.Series or 1-D np.array, time series to predict.
        :param period: Int or Str, the number of observations per cycle: 1 or "annual" for yearly data, 4 or "quarterly"
        for quarterly data, 7 or "daily" for daily data, 12 or "monthly" for monthly data, 24 or "hourly" for hourly
        data, 52 or "weekly" for weekly data. First-letter abbreviations of strings work as well ("a", "q", "d", "m",
        "h" and "w", respectively). Additional reference: https://robjhyndman.com/hyndsight/seasonal-periods/.
        :param x: not used for Holt-Winters model
        :param metric: Str, the metric used for model selection. One of: "mse", "mae", "mape", "smape", "rmse".
        :param val_size: Int, the number of most recent observations to use as validation set for tuning.
        :param verbose: Boolean, True for printing additional info while tuning.
        :return: None
        """
        self.y = y
        self.name = "Holt-Winters Exponential Smoothing"
        self.key = "holt_winters"
        self._tune(y=y, period=period, x=x, metric=metric, val_size=val_size, verbose=verbose)
        model = ExponentialSmoothing(y, seasonal_periods=self.period, trend=self.params["trend"],
                                     seasonal=self.params["seasonal"], damped=self.params["damped"])
        self.model = model.fit(use_boxcox=self.params["use_boxcox"], remove_bias=self.params["remove_bias"])

    def predict(self, horizon, x=None):
        """
        Predict future values of the time series using the fitted model.
        :param horizon: Int, the number of observations in the future to predict
        :param x: not used for Holt-Winters model
        :return: 1-D np.array with predictions
        """
        return self.model.forecast(horizon).values
