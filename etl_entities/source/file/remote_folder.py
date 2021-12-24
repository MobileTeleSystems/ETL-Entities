from __future__ import annotations

import os
from pathlib import Path
from typing import Union

from pydantic import validator

from etl_entities.entity import BaseModel, Entity
from etl_entities.instance import AbsolutePath, Cluster, GenericURL

# folder path cannot have delimiters used in qualified_name
PROHIBITED_PATH_SYMBOLS = "@#"


class RemoteFolder(BaseModel, Entity):
    """Remote folder representation

    Parameters
    ----------
    name : :obj:`str` or :obj:`pathlib.PosixPath`

        Folder path

        .. warning::

            Only absolute path without ``..`` are allowed

    instance : :obj:`etl_entities.instance.url.generic_url.GenericURL`

        Instance URL in format ``"protocol://some.domain[:port]"``

    Examples
    ----------

    .. code:: python

        from etl_entities import RemoteFolder

        folder1 = RemoteFolder(name="/absolute/folder", instance="rnd-dwh")
        folder2 = RemoteFolder(name="/absolute/folder", instance="ftp://some.domain:10000")
    """

    name: AbsolutePath
    instance: Union[GenericURL, Cluster]

    class Config:  # noqa: WPS431
        json_encoders = {AbsolutePath: os.fspath}

    @validator("name", pre=True)
    def check_absolute_path(cls, value):  # noqa: N805
        value = AbsolutePath(value)

        for symbol in PROHIBITED_PATH_SYMBOLS:
            if symbol in str(value):
                raise ValueError(f"Folder name cannot contain symbols {' '.join(PROHIBITED_PATH_SYMBOLS)}")

        return value

    def __str__(self):
        """
        Returns name path
        """

        return str(self.name)

    def __truediv__(self, path: Path) -> AbsolutePath:
        """
        Returns absolute path for nested file or folder
        """

        return self.name / path

    @property
    def qualified_name(self) -> str:
        """
        Unique name of remote folder

        Returns
        ----------
        value : str

            Qualified name

        Examples
        ----------

        .. code:: python

            from etl_entities import RemoteFolder

            folder1 = RemoteFolder(name="/absolute/folder", instance="rnd-dwh")
            folder2 = RemoteFolder(name="/absolute/folder", instance="ftp://some.domain:10000")

            assert folder1.qualified_name == "/absolute/folder@rnd-dwh"
            assert folder1.qualified_name == "/absolute/folder@ftp://some.domain:10000"
        """

        return "@".join([str(self), str(self.instance)])
