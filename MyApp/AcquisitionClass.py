import matplotlib.pyplot as plt
import nidaqmx
import time
import numpy as np
from nidaqmx.constants import AcquisitionType

class Acquisition:
    def __init__(self):