Why three `requirements-dev-*`?  Because otherwise the `setup()`
arguments `setup_requires` and `tests_require` circumvents `pip`.  This
breaks the [hash-checking mode][2] unless [distutils][1] is configured
to never install anything.

If `distutils` is configured to never install anything, trying to
install packages that use `setup_requires` or `tests_require` breaks
everything unless these dependencies are already installed -- hence this
horrible workaround.

- `requirements-dev-1.txt` installs `setuptools_scm` because
  `pytest-runner` specifies it in `setup_requires`.
- `requirements-dev-2.txt` installs `pytest-runner` because `astroid`
   specifies it in `tests_require`.

Gah!


[1]: https://pip.pypa.io/en/stable/reference/pip_install/#controlling-setup-requires
[2]: https://pip.pypa.io/en/stable/reference/pip_install/#hash-checking-mode
