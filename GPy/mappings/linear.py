# Copyright (c) 2013, 2014 GPy authors (see AUTHORS.txt).
# Copyright (c) 2015, James Hensman
# Licensed under the BSD 3-clause license (see LICENSE.txt)

import numpy as np
from ..core.mapping import Mapping
from ..core.parameterization import Param

class Linear(Mapping):
    """
    A Linear mapping.

    .. math::

       F(\\mathbf{x}) = \\mathbf{A} \\mathbf{x})


    :param input_dim: dimension of input.
    :type input_dim: int
    :param output_dim: dimension of output.
    :type output_dim: int
    :param kernel: a GPy kernel, defaults to GPy.kern.RBF
    :type kernel: GPy.kern.kern

    """

    def __init__(self, input_dim, output_dim, name='linmap'):
        super(Linear, self).__init__(input_dim=input_dim, output_dim=output_dim, name=name)
        self.A = Param('A', np.random.randn(self.input_dim, self.output_dim))
        self.link_parameter(self.A)

    def f(self, X):
        return np.dot(X, self.A)

    def update_gradients(self, dL_dF, X):
        self.A.gradient = np.dot(X.T, dL_dF)

    def gradients_X(self, dL_dF, X):
        return np.dot(dL_dF, self.A.T)

    def to_dict(self):
        """
        Convert the object into a json serializable dictionary.

        Note: It uses the private method _save_to_input_dict of the parent.

        :return dict: json serializable dictionary containing the needed information to instantiate the object
        """

        input_dict = super(Linear, self)._save_to_input_dict()
        input_dict["class"] = "GPy.mappings.Linear"
        input_dict["A"] = self.A.values.tolist()
        return input_dict

    @staticmethod
    def _build_from_input_dict(mapping_class, input_dict):
        import copy
        input_dict = copy.deepcopy(input_dict)
        A = np.array(input_dict.pop('A'))
        l = Linear(**input_dict)
        l.unlink_parameter(l.A)
        l.update_model(False)
        l.A = Param('A', A)
        l.link_parameter(l.A)
        return l
