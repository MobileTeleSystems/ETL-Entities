from __future__ import annotations

import os
from pathlib import PosixPath, PurePosixPath
from typing import FrozenSet, Iterable

from pydantic import Field, validator

from etl_entities.hwm.hwm import HWM
from etl_entities.hwm.hwm_type_registry import register_hwm_type
from etl_entities.instance import AbsolutePath, RelativePath
from etl_entities.source import RemoteFolder


@register_hwm_type("files_list")
class FileListHWM(HWM):
    """File List HWM type

    Parameters
    ----------
    source : :obj:`etl_entities.instance.path.remote_folder.RemoteFolder`

        Folder instance

    value : :obj:`frozenset` of :obj:`pathlib.PosixPath`, default: empty set

        HWM value

    modified_time : :obj:`datetime.datetime`, default: current datetime

        HWM value modification time

    process : :obj:`etl_entities.process.process.Process`, default: current process

        Process instance

    Examples
    ----------

    .. code:: python

        from etl_entities import FileListHWM, RemoteFolder

        folder = RemoteFolder(name="/absolute/path", instance="ftp://ftp.server:21")

        hwm = FileListHWM(
            source=folder,
            value=["some/path", "another.file"],
        )
    """

    source: RemoteFolder
    value: FrozenSet[RelativePath] = Field(default_factory=frozenset)

    class Config:  # noqa: WPS431
        json_encoders = {RelativePath: os.fspath, AbsolutePath: os.fspath}

    @validator("value", pre=True)
    def validate_value(cls, value):  # noqa: N805
        if isinstance(value, (str, PosixPath, PurePosixPath)):
            return cls.deserialize_value(os.fspath(value))

        if isinstance(value, Iterable):
            return frozenset(RelativePath(item) for item in value)

        return super().validate_value(value)

    @property
    def name(self) -> str:
        """
        Name of HWM
        """

        return "downloaded_files"

    @property
    def qualified_name(self) -> str:
        """
        Unique name of HWM
        """

        return "#".join([self.name, self.source.qualified_name, self.process.qualified_name])

    def serialize_value(self) -> str:
        r"""Return string representation of HWM value

        Returns
        -------
        result : str

            Serialized value

        Examples
        ----------

        .. code:: python

            from etl_entities import FileListHWM

            hwm = FileListHWM(value=["some/file.py", "another.file"], ...)
            assert hwm.serialize_value() == "some/file.py\nanother.file"

            hwm = FileListHWM(value=[], ...)
            assert hwm.serialize_value() == ""
        """

        return "\n".join(sorted(os.fspath(item) for item in self.value))

    @classmethod
    def deserialize_value(cls, value: str) -> frozenset[RelativePath]:  # noqa: E800
        r"""Parse string representation to get HWM value

        Parameters
        ----------
        value : str

            Serialized value

        Returns
        -------
        result : :obj:`frozenset` of :obj:`etl_entities.instance.path.relative_path.RelativePath`

            Deserialized value

        Examples
        ----------

        .. code:: python

            from etl_entities import FileListHWM

            assert FileListHWM.deserialize_value("some/path.py\nanother.file") == frozenset(
                RelativePath("some/path.py"), RelativePath("another.file")
            )

            assert FileListHWM.deserialize_value([]) == frozenset()
        """

        value = super().deserialize_value(value)

        if value:
            return frozenset(RelativePath(item.strip()) for item in value.split("\n"))

        return frozenset()

    def __bool__(self):
        """Check if HWM value is set

        Returns
        --------
        result : bool

            ``False`` if ``value`` is empty, ``True`` otherwise

        Examples
        ----------

        .. code:: python

            from etl_entities import FileListHWM

            hwm = FileListHWM(value=["some/path.py"], ...)
            assert hwm  # same as bool(hwm.value)

            hwm = FileListHWM(value=[], ...)
            assert not hwm
        """

        return bool(self.value)

    def __add__(self, value: str | os.PathLike | Iterable[str | os.PathLike]):
        """Creates copy of HWM with added value

        Params
        -------
        value : :obj:`str` or :obj:`pathlib.PosixPath` or :obj:`typing.Iterable` of them

            Path or collection of paths to be added to value

        Returns
        --------
        result : HWM

            Copy of HWM with updated value

        Examples
        ----------

        .. code:: python

            from etl_entities import FileListHWM

            hwm1 = FileListHWM(value=["some/path"], ...)
            hwm2 = FileListHWM(value=["some/path", "another.file"], ...)

            assert hwm1 + "another.file" == hwm2
            # same as FileListHWM(value=hwm1.value + "another.file", ...)
        """

        values: Iterable[RelativePath]
        if isinstance(value, Iterable):
            values = {RelativePath(item) for item in value}
        else:
            values = {RelativePath(value)}

        if values:
            return self.with_value(self.value.union(values))

        return self

    def __abs__(self):
        """Returns list of files with absolute paths

        Returns
        --------
        result : :obj:`frosenzet` of :obj:`pathlib.PosixPath`

            Copy of HWM with updated value

        Examples
        ----------

        .. code:: python

            from etl_entities import FileListHWM, Folder, AbsolutePath

            hwm = FileListHWM(value=["some/path"], source=Folder(name="/absolute/path", ...), ...)

            assert abs(hwm) == frozenset(AbsolutePath("/absolute/path/some/path"))
        """

        return frozenset(self.source / item for item in self.value)

    def __contains__(self, item):
        """Checks if path is present in value

        Returns
        --------
        result : bool

            ``True`` if path is present in value, ``False`` otherwise

        Examples
        ----------

        .. code:: python

            from etl_entities import FileListHWM, Folder, AbsolutePath

            hwm = FileListHWM(value=["some/path"], source=Folder(name="/absolute/path", ...), ...)

            assert "some/path" in hwm
            assert "/absolute/path/some/path" in hwm
        """

        if not isinstance(item, os.PathLike):
            item = PurePosixPath(item)

        return item in self.value or item in abs(self)

    def __eq__(self, other):
        """Checks equality of two HWM instances

        Params
        -------
        other : :obj:`hwmlib.hwm.file_list_hwm.FileListHWM`



        Returns
        --------
        result : bool

            ``True`` if both inputs are the same, ``False`` otherwise.

        Examples
        ----------

        .. code:: python

            from etl_entities import FileListHWM

            hwm1 = FileListHWM(value=["some"], ...)
            hwm2 = FileListHWM(value=["another"], ...)

            assert hwm1 == hwm1
            assert hwm1 != hwm2
        """

        self_fields = self.dict(exclude={"modified_time"})
        other_fields = other.dict(exclude={"modified_time"})

        return isinstance(other, FileListHWM) and self_fields == other_fields