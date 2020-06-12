import io
import sys
import unittest
from unittest.mock import patch

import numpy as np
import tensorflow as tf
import tensorflow_probability as tfp
import torch
import wget

import fastestimator as fe
import fastestimator.test.unittest_util as fet


class TestInstanceNorm(unittest.TestCase):
    def test_reflection_padding_2d_10(self):
        n = tfp.distributions.Normal(loc=10, scale=2)
        x = n.sample(sample_shape=(1, 100, 100, 1))
        m = fe.layers.tensorflow.InstanceNormalization()
        y = m(x)
        self.assertLess(tf.reduce_mean(y), 0.1)
        self.assertLess(tf.math.reduce_std(y), 0.1)
