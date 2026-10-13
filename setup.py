from setuptools import Extension, setup

try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = lambda *args, **kwargs: []

try:
    import numpy as np
    include_dirs = [np.get_include()]
except ImportError:
    numpy = None
    include_dirs = []

extensions = [
    Extension(
        "app.middleware.fast_verifier",
        sources=["app/middleware/verification.py"],
        include_dirs=include_dirs
    )
]

try:
    setup(
        name="EnterpriseFastVerifier",
        ext_modules=cythonize(extensions, compiler_directives={'language_level': "3"})
    )
except Exception:
    setup(name="EnterpriseFastVerifier")
