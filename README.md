# ROLCH: Regularized Online Learning for Conditional Heteroskedasticity

[![Open Source Love](https://badges.frapsoft.com/os/v2/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/) 
[![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](https://opensource.org/licenses/MIT) 
![GitHub Release](https://img.shields.io/github/v/release/simon-hirsch/rolch?display_name=release&label=Release)
[![Downloads](https://static.pepy.tech/badge/rolch)](https://pepy.tech/project/rolch) 
[![Tests](https://github.com/simon-hirsch/rolch/actions/workflows/ci_run_tests.yml/badge.svg?branch=main)](https://github.com/simon-hirsch/rolch/actions/workflows/ci_run_tests.yml)
[![Docs](https://github.com/simon-hirsch/rolch/actions/workflows/ci_build_docs.yml/badge.svg?branch=main)](https://github.com/simon-hirsch/rolch/actions/workflows/ci_build_docs.yml)

## Introduction

This package provides an online estimation of models for distributional regression, respectively, models for conditional heteroskedastic data. The main contribution is an online/incremental implementation of the generalized additive models for location, shape and scale (GAMLSS, see [Rigby & Stasinopoulos, 2005](https://academic.oup.com/jrsssc/article-abstract/54/3/507/7113027)) developed in [Hirsch, Berrisch & Ziel, 2024](https://arxiv.org/abs/2407.08750).

Please have a look at the [documentation](https://simon-hirsch.github.io/rolch/) or the [example notebook](https://github.com/simon-hirsch/rolch/blob/main/example.ipynb).

We're actively working on the package and welcome contributions from the community. Have a look at the [Release Notes](https://github.com/simon-hirsch/rolch/releases) and the [Issue Tracker](https://github.com/simon-hirsch/rolch/issues).

## Distributional Regression

The main idea of distributional regression (or regression beyond the mean, multiparameter regression) is that the response variable $Y$ is distributed according to a specified distribution $\mathcal{F}(\theta)$, where $\theta$ is the parameter vector for the distribution. In the Gaussian case, we have $\theta = (\theta_1, \theta_2) = (\mu, \sigma)$. We then specify an individual regression model for all parameters of the distribution of the form 

$$g_k(\theta_k) = \eta_k = X_k\beta_k$$

where $g_k(\cdot)$ is a link function, which ensures that the predicted distribution parameters are in a sensible range (we don't want, e.g. negative standard deviations), and $\eta_k$ is the predictor. For the Gaussian case, this would imply that we have two regression equations, one for the mean (location) and one for the standard deviation (scale) parameters. Distributions other than the normal distribution are possible, and we have already implemented them, e.g., Student's $ t$ distribution and Johnson's $S_U$ distribution. If you are interested in another distribution, please open an Issue.

This allows us to specify very flexible models that consider the conditional behaviour of the variable's volatility, skewness and tail behaviour. A simple example for electricity markets is wind forecasts, which are skewed depending on the production level - intuitively, there is a higher risk of having lower production if the production level is already high since it cannot go much higher than "full load" and if, the turbines might cut-off. Modelling these conditional probabilistic behaviours is the key strength of distributional regression models.

## Example

Basic estimation and updating procedure:

```python
import rolch
import numpy as np
from sklearn.datasets import load_diabetes

X, y = load_diabetes(return_X_y=True)

# Model coefficients 
equation = {
    0 : "all", # Can also use "intercept" or np.ndarray of integers / booleans
    1 : "all", 
    2 : "all", 
}

# Create the estimator
online_gamlss_lasso = rolch.OnlineGamlss(
    distribution=rolch.DistributionT(),
    method="lasso",
    equation=equation,
    fit_intercept=True,
    estimation_kwargs={"ic": {i: "bic" for i in range(dist.n_params)}},
)

# Initial Fit
online_gamlss_lasso.fit(
    X=X[:-11, :], 
    y=y[:-11], 
)
print("Coefficients for the first N-11 observations \n")
print(online_gamlss_lasso.betas)

# Update call
online_gamlss_lasso.update(
    X=X[[-11], :], 
    y=y[[-11]]
)
print("\nCoefficients after update call \n")
print(online_gamlss_lasso.betas)

# Prediction for the last 10 observations
prediction = online_gamlss_lasso.predict(
    X=X[-10:, :]
)

print("\n Predictions for the last 10 observations")
# Location, scale and shape (degrees of freedom)
print(prediction)
```

## Installation & Dependencies

The package is available from [pypi](https://pypi.org/project/rolch/) - do `pip install rolch` and enjoy.

`ROLCH` is designed to have minimal dependencies. We rely on `python>=3.10`, `numpy`, `numba` and `scipy` in a reasonably up-to-date versions.


## Authors

- Simon Hirsch, University of Duisburg-Essen & Statkraft
- Jonathan Berrisch, University of Duisburg-Essen
- Florian Ziel, University of Duisburg-Essen

## Acknowledgements & Disclosure

Simon is employed at Statkraft and gratefully acknowledges support received from Statkraft for his PhD studies. This work contains the author's opinion and not necessarily reflects Statkraft's position.

## Contributing 

We welcome every contribution from the community. Feel free to open an issue if you find bugs or want to propose changes. 

We're still in an early phase and welcome feedback, especially on the usability and "look and feel" of the package. Secondly, we're working to port distributions from the `R`-GAMLSS package and welcome according PRs.

To get started, just create a fork and get going. We will modularize the code over the next versions and increase our testing coverage. We use `ruff` and `black` as formatters.

## Install from source:

1) Clone this repo.
2) Install the necessary dependencies from the `requirements.txt` using `conda create --name <env> --file requirements.txt`. 
3) Run `python3 -m build` to build the wheel.
4) Run `pip install dist/rolch-0.1.0-py3-none-any.whl` with the accurate version. If necessary, append `--force-reinstall`
5) Enjoy.O