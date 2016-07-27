"""Forecast given timeseries data."""
from pipeline import *
from sklearn.cross_validation import train_test_split
from statsmodels.tsa import arima_model


class Forecast(object):
    """
    A forecasting model. Given timeseries data, make predictions.

    Input:
    ------
    filename: path for the CSV file containing data.

    Methods:
    --------
    split(test_size): split data for cross validation with a given test_size.
    predict(n): predict whether to buy, sell, or hold at block n.
    """

    def __init__(self, filename, USD=100, ETH=1000):
        """Initialize the model with a filename and asset quantities."""
        self.USD = USD
        self.ETH = ETH
        self.model = None
        self.getData(parse_df(filename))

    def getData(self, filename):
        """Run through the pipeline and load the data."""
        endog, exog, self.end_blocks = pipeline(filename)
        exog_train, exog_test, endog_train, endog_test = train_test_split(
            exog, endog, test_size=0.3
        )
        self.exog_train = exog_train
        self.exog_test = exog_test
        self.endog_train = endog_train
        self.endog_test = endog_test

    def fitARIMA(self, p, d, q, endog, exog):
        """Fit an ARIMA model give a set of parameters. Returns model."""
        model = arima_model.ARIMA(
            endog,
            order=(p, d, q),
            exog=exog).fit(transparams=False)
        return model

    def optimizeARIMA(self, Ap, Ad, Aq, endog, exog):
        """
        Find an optimal ARIMA model given lists of p, d, and q.

        Split the data to test/train sets and then find the best model.

        Optimization criterion is AIC.
        """
        best_model = None
        best_aic = None
        for p in Ap:
            for d in Ad:
                for q in Aq:
                    # Replace the model if AIC is lower
                    _model = self.fitARIMA(p, d, q, endog=endog, exog=exog)
                    if not best_aic:
                        best_model = _model
                        best_aic = _model.aic
                    elif _model.aic < best_aic:
                        best_model = _model
                        best_aic = _model.aic

        # Reset the global model
        self.model = best_model
