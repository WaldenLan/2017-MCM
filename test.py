import numpy as np

from sympy import *

x, y, z = symbols('x y z')
# >>> init_printing(use_unicode=True)
# a = integrate(cos(x), x)
y = x**2
a = integrate(y, (x, 0, 2))
# print(type(a))
# print(b)
print(a)