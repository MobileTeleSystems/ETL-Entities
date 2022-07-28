from __future__ import annotations

from functools import total_ordering
from typing import Generic, Optional, TypeVar

from etl_entities.entity import GenericModel
from etl_entities.hwm.hwm import HWM
from etl_entities.source import Column, Table

ColumnValueType = TypeVar("ColumnValueType")


@total_ordering
class ColumnHWM(HWM[Optional[ColumnValueType]], GenericModel, Generic[ColumnValueType]):
    """Base column HWM type

    Parameters
    ----------
    column : :obj:`etl_entities.source.db.column.Column`

        Column instance

    source : :obj:`etl_entities.source.db.table.Table`

        Table instance

    value : ``ColumnValueType`` or ``None``, default: ``None``

        HWM value

    modified_time : :obj:`datetime.datetime`, default: current datetime

        HWM value modification time

    process : :obj:`etl_entities.process.process.Process`, default: current process

        Process instance
    """

    column: Column
    source: Table
    value: Optional[ColumnValueType] = None

    @property
    def name(self) -> str:
        """
        HWM column name

        Returns
        ----------
        value : str

            Column name

        Examples
        ----------

        .. code:: python

            column = Column(name="id")
            table = Table(name="mytable", db="mydb", instance="postgres://db.host:5432")

            hwm = ColumnHWM(column=column, source=table, value=val)

            assert hwm.name == "id"
        """

        return self.column.name

    def __str__(self) -> str:
        """
        Returns full HWM name
        """

        return f"{self.name}#{self.source.full_name}"

    @property
    def qualified_name(self) -> str:
        """
        Unique name of HWM

        Returns
        ----------
        value : str

            Qualified name

        Examples
        ----------

        .. code:: python

            column = Column(name="id")
            table = Table(name="mytable", db="mydb", instance="postgres://db.host:5432")

            hwm = ColumnHWM(column=column, source=table, value=1)

            assert (
                hwm.qualified_name
                == "id#mydb.mytable@postgres://db.host:5432#currentprocess@currenthost"
            )
        """

        return "#".join([self.column.qualified_name, self.source.qualified_name, self.process.qualified_name])

    def with_value(self, value: ColumnValueType | None):
        if value is not None:
            return super().with_value(value)

        return self

    def serialize_value(self) -> str:
        """Return string representation of HWM value

        Returns
        -------
        result : str

            Serialized value
        """

        if self.value is None:
            return "null"

        return super().serialize_value()

    def __bool__(self):
        """Check if HWM value is set

        Returns
        --------
        result : bool

            ``False`` if ``value`` is ``None``, ``True`` otherwise

        Examples
        ----------

        .. code:: python

            from etl_entities import ColumnHWM

            hwm = ColumnHWM(value=1, ...)
            assert hwm  # same as hwm.value is not None

            hwm = ColumnHWM(value=None, ...)
            assert not hwm
        """

        return self.value is not None

    def __add__(self, value):
        """Creates copy of HWM with increased value

        Params
        -------
        value : ``Any`` or ``None``

            Should be compatible with ``value`` attribute type.

            For example, you cannot add ``str`` to ``int`` value, but you can add ``int`` to ``int``.

            ``None`` input does not change the value.

        Returns
        --------
        result : HWM

            Copy of HWM with updated value

        Examples
        ----------

        .. code:: python

            # assume val2 == val1 + inc

            hwm1 = ColumnHWM(value=val1, ...)
            hwm2 = ColumnHWM(value=val2, ...)

            # same as ColumnHWM(value=hwm1.value + inc, ...)
            assert hwm1 + inc == hwm2
        """

        if self.value is not None and value is not None:
            return self.with_value(self.value + value)

        return self

    def __sub__(self, value):
        """Creates copy of HWM with decreased value

        Params
        -------
        value : ``Any`` or ``None``

            Should be compatible with ``value`` attribute type.

            For example, you cannot subtract ``str`` from ``int`` value, but you can subtract ``int`` from ``int``.

            ``None`` input does not change the value.

        Returns
        --------
        result : HWM

            Copy of HWM with updated value

        Examples
        ----------

        .. code:: python

            # assume val2 == val1 - dec

            hwm1 = ColumnHWM(value=val1, ...)
            hwm2 = ColumnHWM(value=val2, ...)

            # same as ColumnHWM(value=hwm1.value - dec, ...)
            assert hwm1 - dec == hwm2
        """

        if self.value is not None and value is not None:
            return self.with_value(self.value - value)

        return self

    def __eq__(self, other):
        """Checks equality of two HWM instances

        Params
        -------
        other : :obj:`etl_entities.hwm.column_hwm.ColumnHWM` or any :obj:`object`

            You can compare two :obj:`hwmlib.hwm.column_hwm.ColumnHWM` instances,
            obj:`hwmlib.hwm.column_hwm.ColumnHWM` with an :obj:`object`,
            if its value is comparable with the ``value`` attribute of HWM

        Returns
        --------
        result : bool

            ``True`` if both inputs are the same, ``False`` otherwise.
        """

        if isinstance(other, HWM):
            self_fields = self.dict(exclude={"modified_time"})
            other_fields = other.dict(exclude={"modified_time"})
            return isinstance(other, ColumnHWM) and self_fields == other_fields

        return self.value == other

    def __lt__(self, other):
        """Checks current HWM value is less than another one

        Params
        -------
        other : :obj:`etl_entities.hwm.column_hwm.ColumnHWM` or any :obj:`object`

            You can compare two :obj:`hwmlib.hwm.column_hwm.ColumnHWM` instances,
            obj:`hwmlib.hwm.column_hwm.ColumnHWM` with an :obj:`object`,
            if its value is comparable with the ``value`` attribute of HWM

            .. warning::

                You cannot compare HWMs if one of them has None value

        Returns
        --------
        result : bool

            ``True`` if current HWM value is less than provided value, ``False`` otherwise.
        """

        if isinstance(other, HWM):
            if isinstance(other, ColumnHWM):
                self_fields = self.dict(exclude={"value", "modified_time"})
                other_fields = other.dict(exclude={"value", "modified_time"})
                if self_fields == other_fields:
                    return self.value < other.value

                raise NotImplementedError(  # NOSONAR
                    "Cannot compare ColumnHWM with different column, source or process",
                )

            return NotImplemented

        return self.value < other
