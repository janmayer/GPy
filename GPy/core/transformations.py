# Copyright (c) 2012, GPy authors (see AUTHORS.txt).
# Licensed under the BSD 3-clause license (see LICENSE.txt)


import numpy as np

class transformation(object):
    def __init__(self):
        # set the domain. Suggest we use 'positive', 'bounded', etc
        self.domain = 'undefined'
    def f(self, x):
        raise NotImplementedError

    def finv(self, x):
        raise NotImplementedError

    def gradfactor(self, f):
        """ df_dx evaluated at self.f(x)=f"""
        raise NotImplementedError
    def initialize(self, f):
        """ produce a sensible initial values for f(x)"""
        raise NotImplementedError
    def __str__(self):
        raise NotImplementedError

class logexp(transformation):
    def __init__(self):
        self.domain = 'positive'
    def f(self, x):
        return np.log(1. + np.exp(x))
    def finv(self, f):
        return np.log(np.exp(f) - 1.)
    def gradfactor(self, f):
        ef = np.exp(f)
        return (ef - 1.) / ef
    def initialize(self, f):
        return np.abs(f)
    def __str__(self):
        return '(+ve)'

class logexp_clipped(transformation):
    max_bound = 1e300
    min_bound = 1e-10
    log_max_bound = np.log(max_bound)
    log_min_bound = np.log(min_bound)
    def __init__(self, lower=1e-6):
        self.domain = 'positive'
        self.lower = lower
    def f(self, x):
        exp = np.exp(np.clip(x, self.log_min_bound, self.log_max_bound))
        f = np.log(1. + exp)
        return f
    def finv(self, f):
        return np.log(np.exp(np.clip(f, self.min_bound, self.max_bound)) - 1.)
    def gradfactor(self, f):
        ef = np.exp(f)
        gf = (ef - 1.) / ef
        return np.where(f < self.lower, 0, gf)
    def initialize(self, f):
        if np.any(f < 0.):
            print "Warning: changing parameters to satisfy constraints"
        return np.abs(f)
    def __str__(self):
        return '(+ve_c)'

class exponent(transformation):
    def __init__(self):
        self.domain = 'positive'
    def f(self, x):
        return np.exp(x)
    def finv(self, x):
        return np.log(x)
    def gradfactor(self, f):
        return f
    def initialize(self, f):
        if np.any(f < 0.):
            print "Warning: changing parameters to satisfy constraints"
        return np.abs(f)
    def __str__(self):
        return '(+ve)'

class negative_exponent(transformation):
    def __init__(self):
        self.domain = 'negative'
    def f(self, x):
        return -np.exp(x)
    def finv(self, x):
        return np.log(-x)
    def gradfactor(self, f):
        return f
    def initialize(self, f):
        if np.any(f > 0.):
            print "Warning: changing parameters to satisfy constraints"
        return -np.abs(f)
    def __str__(self):
        return '(-ve)'

class square(transformation):
    def __init__(self):
        self.domain = 'positive'
    def f(self, x):
        return x ** 2
    def finv(self, x):
        return np.sqrt(x)
    def gradfactor(self, f):
        return 2 * np.sqrt(f)
    def initialize(self, f):
        return np.abs(f)
    def __str__(self):
        return '(+sq)'

class logistic(transformation):
    def __init__(self, lower, upper):
        self.domain = 'bounded'
        assert lower < upper
        self.lower, self.upper = float(lower), float(upper)
        self.difference = self.upper - self.lower
    def f(self, x):
        return self.lower + self.difference / (1. + np.exp(-x))
    def finv(self, f):
        return np.log(np.clip(f - self.lower, 1e-10, np.inf) / np.clip(self.upper - f, 1e-10, np.inf))
    def gradfactor(self, f):
        return (f - self.lower) * (self.upper - f) / self.difference
    def initialize(self, f):
        if np.any(np.logical_or(f < self.lower, f > self.upper)):
            print "Warning: changing parameters to satisfy constraints"
        return np.where(np.logical_or(f < self.lower, f > self.upper), self.f(f * 0.), f)
    def __str__(self):
        return '({},{})'.format(self.lower, self.upper)

