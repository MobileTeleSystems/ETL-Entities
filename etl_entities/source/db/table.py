from __future__ import annotations

import re
from typing import Union

from pydantic import ConstrainedStr, root_validator

from etl_entities.entity import BaseModel, Entity
from etl_entities.instance import Cluster, GenericURL


# table or db name cannot have delimiters used in qualified_name
class TableDBName(ConstrainedStr):
    regex = re.compile("^[^.@#]+$")


class Table(BaseModel, Entity):
    """DB table representation

    Parameters
    ----------
    name : str

        Table name

        .. warning::

            Cannot contain ``.``, ``@`` and ``#``

    db : str

        Database (schema) name

        .. warning::

            Cannot contain dot symbol ``.``, ``@`` and ``#``

    instance : :obj:`etl_entities.instance.url.generic_url.GenericURL`
                or :obj:`etl_entities.instance.cluster.cluster.Cluster`

        Cluster name in format ``my-cluster`` or instance URL in format ``"protocol://some.domain[:port]"``

    Examples
    ----------

    .. code:: python

        from etl_entities import Table

        table1 = Table(name="mytable", db="mydb", instance="postgres://db.host:5432")
        table2 = Table(name="mytable", db="mydb", instance="rnd-dwh")
    """

    name: TableDBName
    db: TableDBName
    instance: Union[GenericURL, Cluster]

    @property
    def full_name(self) -> str:
        return f"{self.db}.{self.name}"

    def __str__(self):
        """
        Returns table name
        """

        return self.full_name

    @root_validator(pre=True)
    def parse_name(cls, value: dict) -> dict:  # noqa: N805
        name: str | None = value.get("name")
        db: str | None = value.get("db")

        if name and not db and "." in name:
            if name.count(".") != 1:
                raise ValueError(f"Table name should be passed in `schema.name` format, got '{name}'")

            db, name = name.split(".")
            value["name"] = name
            value["db"] = db

        return value

    @property
    def qualified_name(self) -> str:
        """
        Unique name of table

        Returns
        ----------
        value : str

            Qualified name

        Examples
        ----------

        .. code:: python

            from etl_entities import Table

            table1 = Table(name="mytable", db="mydb", instance="postgres://db.host:5432")
            table2 = Table(name="mytable", db="mydb", instance="rnd-dwh")

            assert table1.qualified_name == "mydb.mytable@postgres://db.host:5432"
            assert table2.qualified_name == "mydb.mytable@rnd-dwh"
        """

        return "@".join([str(self), str(self.instance)])