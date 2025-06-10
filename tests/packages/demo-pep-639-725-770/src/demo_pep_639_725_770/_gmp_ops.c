#include <Python.h>
#include <gmp.h>


/*
 * C function to compute the sum of two arbitrary-precision integers.
 * It expects two Python string arguments representing the integers (e.g., "12345678901234567890" or "-5").
 * Returns a new Python integer object.
 */
static PyObject *gmp_sum_integers(PyObject *self, PyObject *args) {
    const char *str_a, *str_b;
    mpz_t a, b, sum;
    PyObject *result_py_long = NULL;

    if (!PyArg_ParseTuple(args, "ss", &str_a, &str_b)) {
        return NULL;
    }

    mpz_init(a);
    mpz_init(b);
    mpz_init(sum);

    if (mpz_set_str(a, str_a, 10) != 0) {
        PyErr_SetString(PyExc_ValueError, "Invalid integer string for first argument.");
        goto cleanup;
    }
    if (mpz_set_str(b, str_b, 10) != 0) {
        PyErr_SetString(PyExc_ValueError, "Invalid integer string for second argument.");
        goto cleanup;
    }

    mpz_add(sum, a, b);

    char *sum_str = mpz_get_str(NULL, 10, sum);
    if (sum_str == NULL) {
        PyErr_SetString(PyExc_ValueError, "Failed to convert GMP integer to string.");
        goto cleanup;
    }
    result_py_long = PyLong_FromString(sum_str, NULL, 10);
    free(sum_str);

cleanup:
    mpz_clear(a);
    mpz_clear(b);
    mpz_clear(sum);

    return result_py_long;
}

static PyMethodDef GmpOpsMethods[] = {
    {"sum_gmp_integers_c", gmp_sum_integers, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef gmpopsmodule = {
    PyModuleDef_HEAD_INIT,
    "_gmp_ops",
    NULL,
    -1,
    GmpOpsMethods
};

PyMODINIT_FUNC PyInit__gmp_ops(void) {
    PyObject *m;
    m = PyModule_Create(&gmpopsmodule);
    if (!m) {
        return NULL;
    }

    return m;
}
