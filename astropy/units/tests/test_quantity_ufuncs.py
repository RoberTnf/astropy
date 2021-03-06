# The purpose of these tests are to ensure that calling ufuncs with quantities
# returns quantities with the right units, or raises exceptions.

import warnings

import pytest
import numpy as np
from numpy.testing.utils import assert_allclose

from ... import units as u
from ...tests.helper import raises
from ...utils.compat import NUMPY_LT_1_13


class TestUfuncCoverage:
    """Test that we cover all ufunc's"""

    def test_coverage(self):
        all_np_ufuncs = set([ufunc for ufunc in np.core.umath.__dict__.values()
                             if type(ufunc) == np.ufunc])

        from .. import quantity_helper as qh

        all_q_ufuncs = (qh.UNSUPPORTED_UFUNCS |
                        set(qh.UFUNC_HELPERS.keys()))

        assert all_np_ufuncs - all_q_ufuncs == set([])
        assert all_q_ufuncs - all_np_ufuncs == set([])


class TestQuantityTrigonometricFuncs:
    """
    Test trigonometric functions
    """

    def test_sin_scalar(self):
        q = np.sin(30. * u.degree)
        assert q.unit == u.dimensionless_unscaled
        assert_allclose(q.value, 0.5)

    def test_sin_array(self):
        q = np.sin(np.array([0., np.pi / 4., np.pi / 2.]) * u.radian)
        assert q.unit == u.dimensionless_unscaled
        assert_allclose(q.value,
                        np.array([0., 1. / np.sqrt(2.), 1.]), atol=1.e-15)

    def test_arcsin_scalar(self):
        q1 = 30. * u.degree
        q2 = np.arcsin(np.sin(q1)).to(q1.unit)
        assert_allclose(q1.value, q2.value)

    def test_arcsin_array(self):
        q1 = np.array([0., np.pi / 4., np.pi / 2.]) * u.radian
        q2 = np.arcsin(np.sin(q1)).to(q1.unit)
        assert_allclose(q1.value, q2.value)

    def test_sin_invalid_units(self):
        with pytest.raises(TypeError) as exc:
            np.sin(3. * u.m)
        assert exc.value.args[0] == ("Can only apply 'sin' function "
                                     "to quantities with angle units")

    def test_arcsin_invalid_units(self):
        with pytest.raises(TypeError) as exc:
            np.arcsin(3. * u.m)
        assert exc.value.args[0] == ("Can only apply 'arcsin' function to "
                                     "dimensionless quantities")

    def test_arcsin_no_warning_on_unscaled_quantity(self):
        a = 15 * u.kpc
        b = 27 * u.pc

        with warnings.catch_warnings():
            warnings.filterwarnings('error')
            np.arcsin(b/a)

    def test_cos_scalar(self):
        q = np.cos(np.pi / 3. * u.radian)
        assert q.unit == u.dimensionless_unscaled
        assert_allclose(q.value, 0.5)

    def test_cos_array(self):
        q = np.cos(np.array([0., np.pi / 4., np.pi / 2.]) * u.radian)
        assert q.unit == u.dimensionless_unscaled
        assert_allclose(q.value,
                        np.array([1., 1. / np.sqrt(2.), 0.]), atol=1.e-15)

    def test_arccos_scalar(self):
        q1 = np.pi / 3. * u.radian
        q2 = np.arccos(np.cos(q1)).to(q1.unit)
        assert_allclose(q1.value, q2.value)

    def test_arccos_array(self):
        q1 = np.array([0., np.pi / 4., np.pi / 2.]) * u.radian
        q2 = np.arccos(np.cos(q1)).to(q1.unit)
        assert_allclose(q1.value, q2.value)

    def test_cos_invalid_units(self):
        with pytest.raises(TypeError) as exc:
            np.cos(3. * u.s)
        assert exc.value.args[0] == ("Can only apply 'cos' function "
                                     "to quantities with angle units")

    def test_arccos_invalid_units(self):
        with pytest.raises(TypeError) as exc:
            np.arccos(3. * u.s)
        assert exc.value.args[0] == ("Can only apply 'arccos' function to "
                                     "dimensionless quantities")

    def test_tan_scalar(self):
        q = np.tan(np.pi / 3. * u.radian)
        assert q.unit == u.dimensionless_unscaled
        assert_allclose(q.value, np.sqrt(3.))

    def test_tan_array(self):
        q = np.tan(np.array([0., 45., 135., 180.]) * u.degree)
        assert q.unit == u.dimensionless_unscaled
        assert_allclose(q.value,
                        np.array([0., 1., -1., 0.]), atol=1.e-15)

    def test_arctan_scalar(self):
        q = np.pi / 3. * u.radian
        assert np.arctan(np.tan(q))

    def test_arctan_array(self):
        q = np.array([10., 30., 70., 80.]) * u.degree
        assert_allclose(np.arctan(np.tan(q)).to_value(q.unit), q.value)

    def test_tan_invalid_units(self):
        with pytest.raises(TypeError) as exc:
            np.tan(np.array([1, 2, 3]) * u.N)
        assert exc.value.args[0] == ("Can only apply 'tan' function "
                                     "to quantities with angle units")

    def test_arctan_invalid_units(self):
        with pytest.raises(TypeError) as exc:
            np.arctan(np.array([1, 2, 3]) * u.N)
        assert exc.value.args[0] == ("Can only apply 'arctan' function to "
                                     "dimensionless quantities")

    def test_arctan2_valid(self):
        q1 = np.array([10., 30., 70., 80.]) * u.m
        q2 = 2.0 * u.km
        assert np.arctan2(q1, q2).unit == u.radian
        assert_allclose(np.arctan2(q1, q2).value,
                        np.arctan2(q1.value, q2.to_value(q1.unit)))
        q3 = q1 / q2
        q4 = 1.
        at2 = np.arctan2(q3, q4)
        assert_allclose(at2.value, np.arctan2(q3.to_value(1), q4))

    def test_arctan2_invalid(self):
        with pytest.raises(u.UnitsError) as exc:
            np.arctan2(np.array([1, 2, 3]) * u.N, 1. * u.s)
        assert "compatible dimensions" in exc.value.args[0]
        with pytest.raises(u.UnitsError) as exc:
            np.arctan2(np.array([1, 2, 3]) * u.N, 1.)
        assert "dimensionless quantities when other arg" in exc.value.args[0]

    def test_radians(self):

        q1 = np.deg2rad(180. * u.degree)
        assert_allclose(q1.value, np.pi)
        assert q1.unit == u.radian

        q2 = np.radians(180. * u.degree)
        assert_allclose(q2.value, np.pi)
        assert q2.unit == u.radian

        # the following doesn't make much sense in terms of the name of the
        # routine, but we check it gives the correct result.
        q3 = np.deg2rad(3. * u.radian)
        assert_allclose(q3.value, 3.)
        assert q3.unit == u.radian

        q4 = np.radians(3. * u.radian)
        assert_allclose(q4.value, 3.)
        assert q4.unit == u.radian

        with pytest.raises(TypeError):
            np.deg2rad(3. * u.m)

        with pytest.raises(TypeError):
            np.radians(3. * u.m)

    def test_degrees(self):

        # the following doesn't make much sense in terms of the name of the
        # routine, but we check it gives the correct result.
        q1 = np.rad2deg(60. * u.degree)
        assert_allclose(q1.value, 60.)
        assert q1.unit == u.degree

        q2 = np.degrees(60. * u.degree)
        assert_allclose(q2.value, 60.)
        assert q2.unit == u.degree

        q3 = np.rad2deg(np.pi * u.radian)
        assert_allclose(q3.value, 180.)
        assert q3.unit == u.degree

        q4 = np.degrees(np.pi * u.radian)
        assert_allclose(q4.value, 180.)
        assert q4.unit == u.degree

        with pytest.raises(TypeError):
            np.rad2deg(3. * u.m)

        with pytest.raises(TypeError):
            np.degrees(3. * u.m)


class TestQuantityMathFuncs:
    """
    Test other mathematical functions
    """

    def test_multiply_scalar(self):
        assert np.multiply(4. * u.m, 2. / u.s) == 8. * u.m / u.s
        assert np.multiply(4. * u.m, 2.) == 8. * u.m
        assert np.multiply(4., 2. / u.s) == 8. / u.s

    def test_multiply_array(self):
        assert np.all(np.multiply(np.arange(3.) * u.m, 2. / u.s) ==
                      np.arange(0, 6., 2.) * u.m / u.s)

    @pytest.mark.parametrize('function', (np.divide, np.true_divide))
    def test_divide_scalar(self, function):
        assert function(4. * u.m, 2. * u.s) == function(4., 2.) * u.m / u.s
        assert function(4. * u.m, 2.) == function(4., 2.) * u.m
        assert function(4., 2. * u.s) == function(4., 2.) / u.s

    @pytest.mark.parametrize('function', (np.divide, np.true_divide))
    def test_divide_array(self, function):
        assert np.all(function(np.arange(3.) * u.m, 2. * u.s) ==
                      function(np.arange(3.), 2.) * u.m / u.s)

    def test_floor_divide_remainder_and_divmod(self):
        inch = u.Unit(0.0254 * u.m)
        dividend = np.array([1., 2., 3.]) * u.m
        divisor = np.array([3., 4., 5.]) * inch
        quotient = dividend // divisor
        remainder = dividend % divisor
        assert_allclose(quotient.value, [13., 19., 23.])
        assert quotient.unit == u.dimensionless_unscaled
        assert_allclose(remainder.value, [0.0094, 0.0696, 0.079])
        assert remainder.unit == dividend.unit
        quotient2 = np.floor_divide(dividend, divisor)
        remainder2 = np.remainder(dividend, divisor)
        assert np.all(quotient2 == quotient)
        assert np.all(remainder2 == remainder)
        quotient3, remainder3 = divmod(dividend, divisor)
        assert np.all(quotient3 == quotient)
        assert np.all(remainder3 == remainder)

        with pytest.raises(TypeError):
            divmod(dividend, u.km)

        with pytest.raises(TypeError):
            dividend // u.km

        with pytest.raises(TypeError):
            dividend % u.km

        if hasattr(np, 'divmod'):  # not NUMPY_LT_1_13
            quotient4, remainder4 = np.divmod(dividend, divisor)
            assert np.all(quotient4 == quotient)
            assert np.all(remainder4 == remainder)
            with pytest.raises(TypeError):
                np.divmod(dividend, u.km)

    def test_sqrt_scalar(self):
        assert np.sqrt(4. * u.m) == 2. * u.m ** 0.5

    def test_sqrt_array(self):
        assert np.all(np.sqrt(np.array([1., 4., 9.]) * u.m)
                      == np.array([1., 2., 3.]) * u.m ** 0.5)

    def test_square_scalar(self):
        assert np.square(4. * u.m) == 16. * u.m ** 2

    def test_square_array(self):
        assert np.all(np.square(np.array([1., 2., 3.]) * u.m)
                      == np.array([1., 4., 9.]) * u.m ** 2)

    def test_reciprocal_scalar(self):
        assert np.reciprocal(4. * u.m) == 0.25 / u.m

    def test_reciprocal_array(self):
        assert np.all(np.reciprocal(np.array([1., 2., 4.]) * u.m)
                      == np.array([1., 0.5, 0.25]) / u.m)

    # heaviside only introduced in numpy 1.13
    @pytest.mark.skipif("not hasattr(np, 'heaviside')")
    def test_heaviside_scalar(self):
        assert np.heaviside(0. * u.m, 0.5) == 0.5 * u.dimensionless_unscaled
        assert np.heaviside(0. * u.s,
                            25 * u.percent) == 0.25 * u.dimensionless_unscaled
        assert np.heaviside(2. * u.J, 0.25) == 1. * u.dimensionless_unscaled

    @pytest.mark.skipif("not hasattr(np, 'heaviside')")
    def test_heaviside_array(self):
        values = np.array([-1., 0., 0., +1.])
        halfway = np.array([0.75, 0.25, 0.75, 0.25]) * u.dimensionless_unscaled
        assert np.all(np.heaviside(values * u.m,
                                   halfway * u.dimensionless_unscaled) ==
                      [0, 0.25, 0.75, +1.] * u.dimensionless_unscaled)

    def test_cbrt_scalar(self):
        assert np.cbrt(8. * u.m**3) == 2. * u.m

    def test_cbrt_array(self):
        # Calculate cbrt on both sides since on Windows the cube root of 64
        # does not exactly equal 4.  See 4388.
        values = np.array([1., 8., 64.])
        assert np.all(np.cbrt(values * u.m**3) ==
                      np.cbrt(values) * u.m)

    def test_power_scalar(self):
        assert np.power(4. * u.m, 2.) == 16. * u.m ** 2
        assert np.power(4., 200. * u.cm / u.m) == \
            u.Quantity(16., u.dimensionless_unscaled)
        # regression check on #1696
        assert np.power(4. * u.m, 0.) == 1. * u.dimensionless_unscaled

    def test_power_array(self):
        assert np.all(np.power(np.array([1., 2., 3.]) * u.m, 3.)
                      == np.array([1., 8., 27.]) * u.m ** 3)
        # regression check on #1696
        assert np.all(np.power(np.arange(4.) * u.m, 0.) ==
                      1. * u.dimensionless_unscaled)

    # float_power only introduced in numpy 1.12
    @pytest.mark.skipif("not hasattr(np, 'float_power')")
    def test_float_power_array(self):
        assert np.all(np.float_power(np.array([1., 2., 3.]) * u.m, 3.)
                      == np.array([1., 8., 27.]) * u.m ** 3)
        # regression check on #1696
        assert np.all(np.float_power(np.arange(4.) * u.m, 0.) ==
                      1. * u.dimensionless_unscaled)

    @raises(ValueError)
    def test_power_array_array(self):
        np.power(4. * u.m, [2., 4.])

    @raises(ValueError)
    def test_power_array_array2(self):
        np.power([2., 4.] * u.m, [2., 4.])

    def test_power_array_array3(self):
        # Identical unit fractions are converted automatically to dimensionless
        # and should be allowed as base for np.power: #4764
        q = [2., 4.] * u.m / u.m
        powers = [2., 4.]
        res = np.power(q, powers)
        assert np.all(res.value == q.value ** powers)
        assert res.unit == u.dimensionless_unscaled
        # The same holds for unit fractions that are scaled dimensionless.
        q2 = [2., 4.] * u.m / u.cm
        # Test also against different types of exponent
        for cls in (list, tuple, np.array, np.ma.array, u.Quantity):
            res2 = np.power(q2, cls(powers))
            assert np.all(res2.value == q2.to_value(1) ** powers)
            assert res2.unit == u.dimensionless_unscaled
        # Though for single powers, we keep the composite unit.
        res3 = q2 ** 2
        assert np.all(res3.value == q2.value ** 2)
        assert res3.unit == q2.unit ** 2
        assert np.all(res3 == q2 ** [2, 2])

    def test_power_invalid(self):
        with pytest.raises(TypeError) as exc:
            np.power(3., 4. * u.m)
        assert "raise something to a dimensionless" in exc.value.args[0]

    def test_copysign_scalar(self):
        assert np.copysign(3 * u.m, 1.) == 3. * u.m
        assert np.copysign(3 * u.m, 1. * u.s) == 3. * u.m
        assert np.copysign(3 * u.m, -1.) == -3. * u.m
        assert np.copysign(3 * u.m, -1. * u.s) == -3. * u.m

    def test_copysign_array(self):
        assert np.all(np.copysign(np.array([1., 2., 3.]) * u.s, -1.) == -np.array([1., 2., 3.]) * u.s)
        assert np.all(np.copysign(np.array([1., 2., 3.]) * u.s, -1. * u.m) == -np.array([1., 2., 3.]) * u.s)
        assert np.all(np.copysign(np.array([1., 2., 3.]) * u.s, np.array([-2., 2., -4.]) * u.m) == np.array([-1., 2., -3.]) * u.s)

        q = np.copysign(np.array([1., 2., 3.]), -3 * u.m)
        assert np.all(q == np.array([-1., -2., -3.]))
        assert not isinstance(q, u.Quantity)

    def test_ldexp_scalar(self):
        assert np.ldexp(4. * u.m, 2) == 16. * u.m

    def test_ldexp_array(self):
        assert np.all(np.ldexp(np.array([1., 2., 3.]) * u.m, [3, 2, 1])
                      == np.array([8., 8., 6.]) * u.m)

    def test_ldexp_invalid(self):
        with pytest.raises(TypeError):
            np.ldexp(3. * u.m, 4.)

        with pytest.raises(TypeError):
            np.ldexp(3., u.Quantity(4, u.m, dtype=int))

    @pytest.mark.parametrize('function', (np.exp, np.expm1, np.exp2,
                                          np.log, np.log2, np.log10, np.log1p))
    def test_exp_scalar(self, function):
        q = function(3. * u.m / (6. * u.m))
        assert q.unit == u.dimensionless_unscaled
        assert q.value == function(0.5)

    @pytest.mark.parametrize('function', (np.exp, np.expm1, np.exp2,
                                          np.log, np.log2, np.log10, np.log1p))
    def test_exp_array(self, function):
        q = function(np.array([2., 3., 6.]) * u.m / (6. * u.m))
        assert q.unit == u.dimensionless_unscaled
        assert np.all(q.value
                      == function(np.array([1. / 3., 1. / 2., 1.])))
        # should also work on quantities that can be made dimensionless
        q2 = function(np.array([2., 3., 6.]) * u.m / (6. * u.cm))
        assert q2.unit == u.dimensionless_unscaled
        assert_allclose(q2.value,
                        function(np.array([100. / 3., 100. / 2., 100.])))

    @pytest.mark.parametrize('function', (np.exp, np.expm1, np.exp2,
                                          np.log, np.log2, np.log10, np.log1p))
    def test_exp_invalid_units(self, function):
        # Can't use exp() with non-dimensionless quantities
        with pytest.raises(TypeError) as exc:
            function(3. * u.m / u.s)
        assert exc.value.args[0] == ("Can only apply '{0}' function to "
                                     "dimensionless quantities"
                                     .format(function.__name__))

    def test_modf_scalar(self):
        q = np.modf(9. * u.m / (600. * u.cm))
        assert q == (0.5 * u.dimensionless_unscaled,
                     1. * u.dimensionless_unscaled)

    def test_modf_array(self):
        v = np.arange(10.) * u.m / (500. * u.cm)
        q = np.modf(v)
        n = np.modf(v.to_value(u.dimensionless_unscaled))
        assert q[0].unit == u.dimensionless_unscaled
        assert q[1].unit == u.dimensionless_unscaled
        assert all(q[0].value == n[0])
        assert all(q[1].value == n[1])

    def test_frexp_scalar(self):
        q = np.frexp(3. * u.m / (6. * u.m))
        assert q == (np.array(0.5), np.array(0.0))

    def test_frexp_array(self):
        q = np.frexp(np.array([2., 3., 6.]) * u.m / (6. * u.m))
        assert all((_q0, _q1) == np.frexp(_d) for _q0, _q1, _d
                   in zip(q[0], q[1], [1. / 3., 1. / 2., 1.]))

    def test_frexp_invalid_units(self):
        # Can't use prod() with non-dimensionless quantities
        with pytest.raises(TypeError) as exc:
            np.frexp(3. * u.m / u.s)
        assert exc.value.args[0] == ("Can only apply 'frexp' function to "
                                     "unscaled dimensionless quantities")

        # also does not work on quantities that can be made dimensionless
        with pytest.raises(TypeError) as exc:
            np.frexp(np.array([2., 3., 6.]) * u.m / (6. * u.cm))
        assert exc.value.args[0] == ("Can only apply 'frexp' function to "
                                     "unscaled dimensionless quantities")

    @pytest.mark.parametrize('function', (np.logaddexp, np.logaddexp2))
    def test_dimensionless_twoarg_array(self, function):
        q = function(np.array([2., 3., 6.]) * u.m / (6. * u.cm), 1.)
        assert q.unit == u.dimensionless_unscaled
        assert_allclose(q.value,
                        function(np.array([100. / 3., 100. / 2., 100.]), 1.))

    @pytest.mark.parametrize('function', (np.logaddexp, np.logaddexp2))
    def test_dimensionless_twoarg_invalid_units(self, function):

        with pytest.raises(TypeError) as exc:
            function(1. * u.km / u.s, 3. * u.m / u.s)
        assert exc.value.args[0] == ("Can only apply '{0}' function to "
                                     "dimensionless quantities"
                                     .format(function.__name__))


class TestInvariantUfuncs:

    # np.positive was only added in numpy 1.13.
    @pytest.mark.parametrize(('ufunc'), [np.absolute, np.fabs,
                                         np.conj, np.conjugate,
                                         np.negative, np.spacing, np.rint,
                                         np.floor, np.ceil] +
                             [np.positive] if hasattr(np, 'positive') else [])
    def test_invariant_scalar(self, ufunc):

        q_i = 4.7 * u.m
        q_o = ufunc(q_i)
        assert isinstance(q_o, u.Quantity)
        assert q_o.unit == q_i.unit
        assert q_o.value == ufunc(q_i.value)

    @pytest.mark.parametrize(('ufunc'), [np.absolute, np.conjugate,
                                         np.negative, np.rint,
                                         np.floor, np.ceil])
    def test_invariant_array(self, ufunc):

        q_i = np.array([-3.3, 2.1, 10.2]) * u.kg / u.s
        q_o = ufunc(q_i)
        assert isinstance(q_o, u.Quantity)
        assert q_o.unit == q_i.unit
        assert np.all(q_o.value == ufunc(q_i.value))

    @pytest.mark.parametrize(('ufunc'), [np.add, np.subtract, np.hypot,
                                         np.maximum, np.minimum, np.nextafter,
                                         np.remainder, np.mod, np.fmod])
    def test_invariant_twoarg_scalar(self, ufunc):

        q_i1 = 4.7 * u.m
        q_i2 = 9.4 * u.km
        q_o = ufunc(q_i1, q_i2)
        assert isinstance(q_o, u.Quantity)
        assert q_o.unit == q_i1.unit
        assert_allclose(q_o.value, ufunc(q_i1.value, q_i2.to_value(q_i1.unit)))

    @pytest.mark.parametrize(('ufunc'), [np.add, np.subtract, np.hypot,
                                         np.maximum, np.minimum, np.nextafter,
                                         np.remainder, np.mod, np.fmod])
    def test_invariant_twoarg_array(self, ufunc):

        q_i1 = np.array([-3.3, 2.1, 10.2]) * u.kg / u.s
        q_i2 = np.array([10., -5., 1.e6]) * u.g / u.us
        q_o = ufunc(q_i1, q_i2)
        assert isinstance(q_o, u.Quantity)
        assert q_o.unit == q_i1.unit
        assert_allclose(q_o.value, ufunc(q_i1.value, q_i2.to_value(q_i1.unit)))

    @pytest.mark.parametrize(('ufunc'), [np.add, np.subtract, np.hypot,
                                         np.maximum, np.minimum, np.nextafter,
                                         np.remainder, np.mod, np.fmod])
    def test_invariant_twoarg_one_arbitrary(self, ufunc):

        q_i1 = np.array([-3.3, 2.1, 10.2]) * u.kg / u.s
        arbitrary_unit_value = np.array([0.])
        q_o = ufunc(q_i1, arbitrary_unit_value)
        assert isinstance(q_o, u.Quantity)
        assert q_o.unit == q_i1.unit
        assert_allclose(q_o.value, ufunc(q_i1.value, arbitrary_unit_value))

    @pytest.mark.parametrize(('ufunc'), [np.add, np.subtract, np.hypot,
                                         np.maximum, np.minimum, np.nextafter,
                                         np.remainder, np.mod, np.fmod])
    def test_invariant_twoarg_invalid_units(self, ufunc):

        q_i1 = 4.7 * u.m
        q_i2 = 9.4 * u.s
        with pytest.raises(u.UnitsError) as exc:
            ufunc(q_i1, q_i2)
        assert "compatible dimensions" in exc.value.args[0]


class TestComparisonUfuncs:

    @pytest.mark.parametrize(('ufunc'), [np.greater, np.greater_equal,
                                         np.less, np.less_equal,
                                         np.not_equal, np.equal])
    def test_comparison_valid_units(self, ufunc):
        q_i1 = np.array([-3.3, 2.1, 10.2]) * u.kg / u.s
        q_i2 = np.array([10., -5., 1.e6]) * u.g / u.Ms
        q_o = ufunc(q_i1, q_i2)
        assert not isinstance(q_o, u.Quantity)
        assert q_o.dtype == bool
        assert np.all(q_o == ufunc(q_i1.value, q_i2.to_value(q_i1.unit)))
        q_o2 = ufunc(q_i1 / q_i2, 2.)
        assert not isinstance(q_o2, u.Quantity)
        assert q_o2.dtype == bool
        assert np.all(q_o2 == ufunc((q_i1 / q_i2)
                                    .to_value(u.dimensionless_unscaled), 2.))
        # comparison with 0., inf, nan is OK even for dimensional quantities
        for arbitrary_unit_value in (0., np.inf, np.nan):
            ufunc(q_i1, arbitrary_unit_value)
            ufunc(q_i1, arbitrary_unit_value*np.ones(len(q_i1)))
        # and just for completeness
        ufunc(q_i1, np.array([0., np.inf, np.nan]))

    @pytest.mark.parametrize(('ufunc'), [np.greater, np.greater_equal,
                                         np.less, np.less_equal,
                                         np.not_equal, np.equal])
    def test_comparison_invalid_units(self, ufunc):
        q_i1 = 4.7 * u.m
        q_i2 = 9.4 * u.s
        with pytest.raises(u.UnitsError) as exc:
            ufunc(q_i1, q_i2)
        assert "compatible dimensions" in exc.value.args[0]


class TestInplaceUfuncs:

    @pytest.mark.parametrize(('value'), [1., np.arange(10.)])
    def test_one_argument_ufunc_inplace(self, value):
        # without scaling
        s = value * u.rad
        check = s
        np.sin(s, out=s)
        assert check is s
        assert check.unit == u.dimensionless_unscaled
        # with scaling
        s2 = (value * u.rad).to(u.deg)
        check2 = s2
        np.sin(s2, out=s2)
        assert check2 is s2
        assert check2.unit == u.dimensionless_unscaled
        assert_allclose(s.value, s2.value)

    @pytest.mark.parametrize(('value'), [1., np.arange(10.)])
    def test_one_argument_ufunc_inplace_2(self, value):
        """Check inplace works with non-quantity input and quantity output"""
        s = value * u.m
        check = s
        np.absolute(value, out=s)
        assert check is s
        assert np.all(check.value == np.absolute(value))
        assert check.unit is u.dimensionless_unscaled
        np.sqrt(value, out=s)
        assert check is s
        assert np.all(check.value == np.sqrt(value))
        assert check.unit is u.dimensionless_unscaled
        np.exp(value, out=s)
        assert check is s
        assert np.all(check.value == np.exp(value))
        assert check.unit is u.dimensionless_unscaled
        np.arcsin(value/10., out=s)
        assert check is s
        assert np.all(check.value == np.arcsin(value/10.))
        assert check.unit is u.radian

    @pytest.mark.parametrize(('value'), [1., np.arange(10.)])
    def test_one_argument_two_output_ufunc_inplace(self, value):
        v = 100. * value * u.cm / u.m
        v_copy = v.copy()
        tmp = v.copy()
        check = v
        np.modf(v, tmp, v)  # cannot use out1,out2 keywords with numpy 1.7
        assert check is v
        assert check.unit == u.dimensionless_unscaled
        v2 = v_copy.to(u.dimensionless_unscaled)
        check2 = v2
        np.modf(v2, tmp, v2)
        assert check2 is v2
        assert check2.unit == u.dimensionless_unscaled
        # can also replace in last position if no scaling is needed
        v3 = v_copy.to(u.dimensionless_unscaled)
        check3 = v3
        np.modf(v3, v3, tmp)
        assert check3 is v3
        assert check3.unit == u.dimensionless_unscaled
        # in np<1.13, without __array_ufunc__, one cannot replace input with
        # first output when scaling
        v4 = v_copy.copy()
        if NUMPY_LT_1_13:
            with pytest.raises(TypeError):
                np.modf(v4, v4, tmp)
        else:
            check4 = v4
            np.modf(v4, v4, tmp)
            assert check4 is v4
            assert check4.unit == u.dimensionless_unscaled

    @pytest.mark.parametrize(('value'), [1., np.arange(10.)])
    def test_two_argument_ufunc_inplace_1(self, value):
        s = value * u.cycle
        check = s
        s /= 2.
        assert check is s
        assert np.all(check.value == value / 2.)
        s /= u.s
        assert check is s
        assert check.unit == u.cycle / u.s
        s *= 2. * u.s
        assert check is s
        assert np.all(check == value * u.cycle)

    @pytest.mark.parametrize(('value'), [1., np.arange(10.)])
    def test_two_argument_ufunc_inplace_2(self, value):
        s = value * u.cycle
        check = s
        np.arctan2(s, s, out=s)
        assert check is s
        assert check.unit == u.radian
        with pytest.raises(u.UnitsError):
            s += 1. * u.m
        assert check is s
        assert check.unit == u.radian
        np.arctan2(1. * u.deg, s, out=s)
        assert check is s
        assert check.unit == u.radian
        np.add(1. * u.deg, s, out=s)
        assert check is s
        assert check.unit == u.deg
        np.multiply(2. / u.s, s, out=s)
        assert check is s
        assert check.unit == u.deg / u.s

    def test_two_argument_ufunc_inplace_3(self):
        s = np.array([1., 2., 3.]) * u.dimensionless_unscaled
        np.add(np.array([1., 2., 3.]), np.array([1., 2., 3.]) * 2., out=s)
        assert np.all(s.value == np.array([3., 6., 9.]))
        assert s.unit is u.dimensionless_unscaled
        np.arctan2(np.array([1., 2., 3.]), np.array([1., 2., 3.]) * 2., out=s)
        assert_allclose(s.value, np.arctan2(1., 2.))
        assert s.unit is u.radian

    @pytest.mark.skipif(NUMPY_LT_1_13, reason="numpy >=1.13 required.")
    @pytest.mark.parametrize(('value'), [1., np.arange(10.)])
    def test_two_argument_two_output_ufunc_inplace(self, value):
        v = value * u.m
        divisor = 70.*u.cm
        v1 = v.copy()
        tmp = v.copy()
        check = np.divmod(v1, divisor, out=(tmp, v1))
        assert check[0] is tmp and check[1] is v1
        assert tmp.unit == u.dimensionless_unscaled
        assert v1.unit == v.unit
        v2 = v.copy()
        check2 = np.divmod(v2, divisor, out=(v2, tmp))
        assert check2[0] is v2 and check2[1] is tmp
        assert v2.unit == u.dimensionless_unscaled
        assert tmp.unit == v.unit
        v3a = v.copy()
        v3b = v.copy()
        check3 = np.divmod(v3a, divisor, out=(v3a, v3b))
        assert check3[0] is v3a and check3[1] is v3b
        assert v3a.unit == u.dimensionless_unscaled
        assert v3b.unit == v.unit

    def test_ufunc_inplace_non_contiguous_data(self):
        # ensure inplace works also for non-contiguous data (closes #1834)
        s = np.arange(10.) * u.m
        s_copy = s.copy()
        s2 = s[::2]
        s2 += 1. * u.cm
        assert np.all(s[::2] > s_copy[::2])
        assert np.all(s[1::2] == s_copy[1::2])

    def test_ufunc_inplace_non_standard_dtype(self):
        """Check that inplace operations check properly for casting.

        First two tests that check that float32 is kept close #3976.
        """
        a1 = u.Quantity([1, 2, 3, 4], u.m, dtype=np.float32)
        a1 *= np.float32(10)
        assert a1.unit is u.m
        assert a1.dtype == np.float32
        a2 = u.Quantity([1, 2, 3, 4], u.m, dtype=np.float32)
        a2 += (20.*u.km)
        assert a2.unit is u.m
        assert a2.dtype == np.float32
        # For integer, in-place only works if no conversion is done.
        a3 = u.Quantity([1, 2, 3, 4], u.m, dtype=np.int32)
        a3 += u.Quantity(10, u.m, dtype=np.int64)
        assert a3.unit is u.m
        assert a3.dtype == np.int32
        a4 = u.Quantity([1, 2, 3, 4], u.m, dtype=np.int32)
        with pytest.raises(TypeError):
            a4 += u.Quantity(10, u.mm, dtype=np.int64)


@pytest.mark.xfail("NUMPY_LT_1_13")
class TestUfuncAt:
    """Test that 'at' method for ufuncs (calculates in-place at given indices)

    For Quantities, since calculations are in-place, it makes sense only
    if the result is still a quantity, and if the unit does not have to change
    """

    def test_one_argument_ufunc_at(self):
        q = np.arange(10.) * u.m
        i = np.array([1, 2])
        qv = q.value.copy()
        np.negative.at(q, i)
        np.negative.at(qv, i)
        assert np.all(q.value == qv)
        assert q.unit is u.m

        # cannot change from quantity to bool array
        with pytest.raises(TypeError):
            np.isfinite.at(q, i)

        # for selective in-place, cannot change the unit
        with pytest.raises(u.UnitsError):
            np.square.at(q, i)

        # except if the unit does not change (i.e., dimensionless)
        d = np.arange(10.) * u.dimensionless_unscaled
        dv = d.value.copy()
        np.square.at(d, i)
        np.square.at(dv, i)
        assert np.all(d.value == dv)
        assert d.unit is u.dimensionless_unscaled

        d = np.arange(10.) * u.dimensionless_unscaled
        dv = d.value.copy()
        np.log.at(d, i)
        np.log.at(dv, i)
        assert np.all(d.value == dv)
        assert d.unit is u.dimensionless_unscaled

        # also for sine it doesn't work, even if given an angle
        a = np.arange(10.) * u.radian
        with pytest.raises(u.UnitsError):
            np.sin.at(a, i)

        # except, for consistency, if we have made radian equivalent to
        # dimensionless (though hopefully it will never be needed)
        av = a.value.copy()
        with u.add_enabled_equivalencies(u.dimensionless_angles()):
            np.sin.at(a, i)
            np.sin.at(av, i)
            assert_allclose(a.value, av)

            # but we won't do double conversion
            ad = np.arange(10.) * u.degree
            with pytest.raises(u.UnitsError):
                np.sin.at(ad, i)

    def test_two_argument_ufunc_at(self):
        s = np.arange(10.) * u.m
        i = np.array([1, 2])
        check = s.value.copy()
        np.add.at(s, i, 1.*u.km)
        np.add.at(check, i, 1000.)
        assert np.all(s.value == check)
        assert s.unit is u.m

        with pytest.raises(u.UnitsError):
            np.add.at(s, i, 1.*u.s)

        # also raise UnitsError if unit would have to be changed
        with pytest.raises(u.UnitsError):
            np.multiply.at(s, i, 1*u.s)

        # but be fine if it does not
        s = np.arange(10.) * u.m
        check = s.value.copy()
        np.multiply.at(s, i, 2.*u.dimensionless_unscaled)
        np.multiply.at(check, i, 2)
        assert np.all(s.value == check)
        s = np.arange(10.) * u.m
        np.multiply.at(s, i, 2.)
        assert np.all(s.value == check)

        # of course cannot change class of data either
        with pytest.raises(TypeError):
            np.greater.at(s, i, 1.*u.km)


@pytest.mark.xfail("NUMPY_LT_1_13")
class TestUfuncReduceReduceatAccumulate:
    """Test 'reduce', 'reduceat' and 'accumulate' methods for ufuncs

    For Quantities, it makes sense only if the unit does not have to change
    """

    def test_one_argument_ufunc_reduce_accumulate(self):
        # one argument cannot be used
        s = np.arange(10.) * u.radian
        i = np.array([0, 5, 1, 6])
        with pytest.raises(ValueError):
            np.sin.reduce(s)
        with pytest.raises(ValueError):
            np.sin.accumulate(s)
        with pytest.raises(ValueError):
            np.sin.reduceat(s, i)

    def test_two_argument_ufunc_reduce_accumulate(self):
        s = np.arange(10.) * u.m
        i = np.array([0, 5, 1, 6])
        check = s.value.copy()
        s_add_reduce = np.add.reduce(s)
        check_add_reduce = np.add.reduce(check)
        assert s_add_reduce.value == check_add_reduce
        assert s_add_reduce.unit is u.m

        s_add_accumulate = np.add.accumulate(s)
        check_add_accumulate = np.add.accumulate(check)
        assert np.all(s_add_accumulate.value == check_add_accumulate)
        assert s_add_accumulate.unit is u.m

        s_add_reduceat = np.add.reduceat(s, i)
        check_add_reduceat = np.add.reduceat(check, i)
        assert np.all(s_add_reduceat.value == check_add_reduceat)
        assert s_add_reduceat.unit is u.m

        # reduce(at) or accumulate on comparisons makes no sense,
        # as intermediate result is not even a Quantity
        with pytest.raises(TypeError):
            np.greater.reduce(s)

        with pytest.raises(TypeError):
            np.greater.accumulate(s)

        with pytest.raises(TypeError):
            np.greater.reduceat(s, i)

        # raise UnitsError if unit would have to be changed
        with pytest.raises(u.UnitsError):
            np.multiply.reduce(s)

        with pytest.raises(u.UnitsError):
            np.multiply.accumulate(s)

        with pytest.raises(u.UnitsError):
            np.multiply.reduceat(s, i)

        # but be fine if it does not
        s = np.arange(10.) * u.dimensionless_unscaled
        check = s.value.copy()
        s_multiply_reduce = np.multiply.reduce(s)
        check_multiply_reduce = np.multiply.reduce(check)
        assert s_multiply_reduce.value == check_multiply_reduce
        assert s_multiply_reduce.unit is u.dimensionless_unscaled
        s_multiply_accumulate = np.multiply.accumulate(s)
        check_multiply_accumulate = np.multiply.accumulate(check)
        assert np.all(s_multiply_accumulate.value == check_multiply_accumulate)
        assert s_multiply_accumulate.unit is u.dimensionless_unscaled
        s_multiply_reduceat = np.multiply.reduceat(s, i)
        check_multiply_reduceat = np.multiply.reduceat(check, i)
        assert np.all(s_multiply_reduceat.value == check_multiply_reduceat)
        assert s_multiply_reduceat.unit is u.dimensionless_unscaled


@pytest.mark.xfail("NUMPY_LT_1_13")
class TestUfuncOuter:
    """Test 'outer' methods for ufuncs

    Just a few spot checks, since it uses the same code as the regular
    ufunc call
    """

    def test_one_argument_ufunc_outer(self):
        # one argument cannot be used
        s = np.arange(10.) * u.radian
        with pytest.raises(ValueError):
            np.sin.outer(s)

    def test_two_argument_ufunc_outer(self):
        s1 = np.arange(10.) * u.m
        s2 = np.arange(2.) * u.s
        check1 = s1.value
        check2 = s2.value
        s12_multiply_outer = np.multiply.outer(s1, s2)
        check12_multiply_outer = np.multiply.outer(check1, check2)
        assert np.all(s12_multiply_outer.value == check12_multiply_outer)
        assert s12_multiply_outer.unit == s1.unit * s2.unit

        # raise UnitsError if appropriate
        with pytest.raises(u.UnitsError):
            np.add.outer(s1, s2)

        # but be fine if it does not
        s3 = np.arange(2.) * s1.unit
        check3 = s3.value
        s13_add_outer = np.add.outer(s1, s3)
        check13_add_outer = np.add.outer(check1, check3)
        assert np.all(s13_add_outer.value == check13_add_outer)
        assert s13_add_outer.unit is s1.unit

        s13_greater_outer = np.greater.outer(s1, s3)
        check13_greater_outer = np.greater.outer(check1, check3)
        assert type(s13_greater_outer) is np.ndarray
        assert np.all(s13_greater_outer == check13_greater_outer)
