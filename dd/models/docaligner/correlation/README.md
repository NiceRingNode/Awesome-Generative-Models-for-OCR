Extracted from https://github.com/sniklaus/pytorch-pwc/tree/master/correlation
This is an adaptation of the FlowNet2 implementation in order to compute cost volumes.
The correlation layer is implemented in CUDA using CuPy, which is why CuPy is a required dependency.
It can be installed using pip install cupy or alternatively using one of the provided binary packages
as outlined in the CuPy repository.