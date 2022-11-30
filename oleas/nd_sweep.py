import abc

import numpy as np



class NdSweep(abc.ABC):
    """Utility for performing multidimensional sweeps.

    Implement the ``_run_for_point`` method to run some operation
    at a point.
    """

    def __init__(self, axis_values: list[np.ndarray]):
        """Constructor.

        Args:
            axis_values (list[np.ndarray]): a list of values to use for each axis.
                The order of the axes matters: the first value corresponds to the
                outermost "for loop" while the last value is the innermost "for loop".
        """
        self._axis_values = axis_values
        self._current_index = None
        self._current_point = None

    @property
    def current_index(self) -> tuple:
        return tuple(self._current_index)

    @property
    def current_point(self) -> tuple:
        return tuple(self._current_point)

    @property
    def num_axes(self) -> int:
        return len(self._axis_values)

    def run(self) -> list:
        """Run the sweep.

        Returns:
            list: a list of a list of an etc. containing the values generated at
                each point. The output is ordered according to the axes given.
        """
        self._reset_current_point()
        output = self._recursive_run(axis=0)
        return output

    def _recursive_run(self, axis: int) -> 'list | object':
        """Recursively run the sweep along each axis, starting with the given axis.

        The axis numbering starts at zero and increases from there.

        Args:
            axis (int): starting axis. If this is beyond the last axis,
                the user operation is run.

        Returns:
            list | object: list of list (etc) of values, or single value if
            ``axis`` is the beyond the last axis
        """
        if axis >= self.num_axes:
            return self._run_for_point()
        else:
            result = []
            for i, value in enumerate(self._axis_values[axis]):
                self._set_axis_value(axis, value, i)
                result.append(self._recursive_run(axis + 1))
            return result

    def _set_axis_value(self, axis: int, value: int, index: int):
        """Override to update something when the value along an axis changes.

        Args:
            axis (int): the axis number
            value (int): the value
            index (int): index of this value along the axis
        """
        self._current_index[axis] = index
        self._current_point[axis] = value

    @abc.abstractmethod
    def _run_for_point(self) -> object:
        """Override to run at operation at each point in the sweep.

        Returns:
            object: the result of the operation
        """

    def _reset_current_point(self):
        num_axes = self.num_axes
        self._current_point = [0] * num_axes
        self._current_index = [0] * num_axes
