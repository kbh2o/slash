from .parameters import iterate_kwargs_options
from .runnable_test import RunnableTest
from .runnable_test_factory import RunnableTestFactory

class Test(RunnableTest, RunnableTestFactory):
    """
    This is a base class for implementing unittest-style test classes.
    """
    def __init__(self, test_method_name, before_kwargs=None, after_kwargs=None, test_kwargs=None):
        super(Test, self).__init__()
        self._test_method_name = test_method_name
        self._before_kwargs = before_kwargs or {}
        self._after_kwargs = after_kwargs or {}
        self._test_kwargs = test_kwargs or {}
    @classmethod
    def generate_tests(cls):
        if is_abstract_base_class(cls):
            return

        before_kwarg_sets = list(iterate_kwargs_options(cls.before))
        after_kwarg_sets = list(iterate_kwargs_options(cls.after))
        for test_method_name in dir(cls):
            if not test_method_name.startswith("test"):
                continue
            test_method = getattr(cls, test_method_name)
            for before_kwargs in before_kwarg_sets:
                for test_kwargs in iterate_kwargs_options(test_method):
                    for after_kwargs in after_kwarg_sets:
                        yield cls(
                            test_method_name,
                            before_kwargs=before_kwargs,
                            test_kwargs=test_kwargs,
                            after_kwargs=after_kwargs
                            )
    def run(self):
        """
        Not to be overriden
        """
        method = getattr(self, self._test_method_name)
        self.before(**self._before_kwargs)
        try:
            method(**self._test_kwargs)
        finally:
            self.after(**self._after_kwargs)
    def before(self):
        """
        Gets called before each separate case generated from this test class
        """
        pass
    def after(self):
        """
        Gets called after each separate case from this test class executed, assuming :meth:`before` was successful.
        """
        pass
    def get_canonical_name(self):
        return "{0}:{1}".format(super(Test, self).get_canonical_name(), self._test_method_name)


def abstract_test_class(cls):
    """
    Marks a class as **abstract**, thus meaning it is not to be run
    directly, but rather via a subclass.
    """
    assert issubclass(cls, Test), "abstract_test_class only operates on shakedown.Test subclasses"
    cls.__shakedown_abstract__ = True
    return cls

def is_abstract_base_class(cls):
    """
    Checks if a given class is abstract.

    .. seealso:: :func:`abstract_test_class`
    """
    return bool(cls.__dict__.get("__shakedown_abstract__", False))