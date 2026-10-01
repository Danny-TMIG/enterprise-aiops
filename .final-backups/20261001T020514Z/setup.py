from setuptools import setup, Extension
try:
    try:
    try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = None
except ImportError:
    cythonize = None
except ImportError:
    cythonize = None
import numpy as np

extensions = [
    Extension(
        "app.middleware.fast_verifier",
        sources=["app/middleware/verification.py"],
        include_dirs=[np.get_include()]
    )
]
try:
    setup(name="EnterpriseFastVerifier", ext_modules=cythonize(extensions, compiler_directives={'language_level': "3"}))
except Exception:
    pass
