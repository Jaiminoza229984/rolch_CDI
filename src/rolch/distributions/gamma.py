from typing import Tuple

import numpy as np
import scipy.special as spc
import scipy.stats as st

from rolch.base import Distribution, LinkFunction
from rolch.base.scipymixin import ScipyMixin
from rolch.link import LogLink


class DistributionGamma(Distribution, ScipyMixin):
    """The Gamma Distribution for GAMLSS.

    The distribution function is defined as in GAMLSS as:
    $$
    f(y|\mu,\sigma)=\\frac{y^{(1/\sigma^2-1)}\exp[-y/(\sigma^2 \mu)]}{(\sigma^2 \mu)^{(1/\sigma^2)} \Gamma(1/\sigma^2)}
    $$

    with the location and shape parameters $\mu, \sigma > 0$.

    !!! Note
        The function is parameterized as GAMLSS' GA() distribution.

        This parameterization is different to the `scipy.stats.gamma(alpha, loc, scale)` parameterization.

        We can use `DistributionGamma().theta_to_scipy_params(theta)` to map the distribution parameters to scipy.

    The `scipy.stats.gamma()` distribution is defined as:
    $$
    f(x, \\alpha, \\beta) = \\frac{\\beta^\\alpha x^{\\alpha - 1} \exp[-\\beta x]}{\Gamma(\\alpha)}
    $$
    with the paramters $\\alpha, \\beta >0$. The parameters can be mapped as follows:
    $$
    \\alpha = 1/\sigma^2 \Leftrightarrow \sigma = \sqrt{1 / \\alpha}
    $$
    and
    $$
    \\beta = 1/(\sigma^2\mu).
    $$

    Args:
        loc_link (LinkFunction, optional): The link function for $\mu$. Defaults to LogLink().
        scale_link (LinkFunction, optional): The link function for $\sigma$. Defaults to LogLink().
    """

    parameter_names = {0: "mu", 1: "sigma"}
    parameter_support = {
        0: (np.nextafter(0, 1), np.inf),
        1: (np.nextafter(0, 1), np.inf),
    }
    distribution_support = (np.nextafter(0, 1), np.inf)
    # Scipy equivalent and parameter mapping rolch -> scipy
    scipy_dist = st.gamma
    # Theta columns do not map 1:1 to scipy parameters for gamma
    # So we have to overload theta_to_scipy_params
    scipy_names = {}

    def __init__(
        self,
        loc_link: LinkFunction = LogLink(),
        scale_link: LinkFunction = LogLink(),
    ) -> None:
        self.loc_link: LinkFunction = loc_link
        self.scale_link: LinkFunction = scale_link
        self.links: dict[int, LinkFunction] = {0: self.loc_link, 1: self.scale_link}
        self.corresponding_gamlss: str = "GA"
        self._validate_links()

    def theta_to_scipy_params(self, theta: np.ndarray) -> dict:
        """Map GAMLSS Parameters to scipy parameters.

        Args:
            theta (np.ndarray): parameters

        Returns:
            dict: Dict of (a, loc, scale) for scipy.stats.gamma(a, loc, scale)
        """
        mu = theta[:, 0]
        sigma = theta[:, 1]
        beta = 1 / (sigma**2 * mu)
        params = {"a": 1 / sigma**2, "loc": 0, "scale": 1 / beta}
        return params

    def dl1_dp1(self, y: np.ndarray, theta: np.ndarray, param: int = 0) -> np.ndarray:
        self._validate_dln_dpn_inputs(y, theta, param)
        mu, sigma = self.theta_to_params(theta)

        if param == 0:
            return (y - mu) / ((sigma**2) * (mu**2))

        if param == 1:
            return (2 / sigma**3) * (
                (y / mu)
                - np.log(y)
                + np.log(mu)
                + np.log(sigma**2)
                - 1
                + spc.digamma(1 / (sigma**2))
            )

    def dl2_dp2(self, y: np.ndarray, theta: np.ndarray, param: int = 0) -> np.ndarray:
        self._validate_dln_dpn_inputs(y, theta, param)
        mu, sigma = self.theta_to_params(theta)
        if param == 0:
            # MU
            return -1 / ((sigma**2) * (mu**2))

        if param == 1:
            # SIGMA
            return (4 / sigma**4) - (4 / sigma**6) * spc.polygamma(1, (1 / sigma**2))

    def dl2_dpp(
        self, y: np.ndarray, theta: np.ndarray, params: Tuple[int, int] = (0, 1)
    ) -> np.ndarray:
        self._validate_dl2_dpp_inputs(y, theta, params)
        if sorted(params) == [0, 1]:
            return np.zeros_like(y)

    def initial_values(
        self, y: np.ndarray, param: int = 0, axis: int = None
    ) -> np.ndarray:
        if param == 0:
            return np.repeat(np.mean(y, axis=None), y.shape[0])
        if param == 1:
            return np.ones_like(y)
