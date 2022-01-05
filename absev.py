# absolute exposure value
from fractions import Fraction
import math

time = float(Fraction(input('time: ')))
iris = float(Fraction(input('iris: ')))
iso  = int(input('iso:  '))
exp  = iris**-2*(time*iso)
print(f'exp: {math.log(exp,2):.0f}')

