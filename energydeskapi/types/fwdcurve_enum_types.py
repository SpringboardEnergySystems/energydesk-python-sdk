from enum import Enum


class FwdCurveInternalEnum(Enum):
    CUBIC_SPLINE = 1   # Key for the most commonly used markets
    FB_PROPHET = 2
    SARIMAX = 3
    EXTERNAL = 4


