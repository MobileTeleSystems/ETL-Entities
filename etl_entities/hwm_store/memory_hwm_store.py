#  Copyright 2023 MTS (Mobile Telesystems)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import annotations

from typing import Dict

from pydantic import PrivateAttr

from etl_entities.hwm import HWM
from etl_entities.hwm_store.base_hwm_store import BaseHWMStore
from etl_entities.hwm_store.hwm_store_class_registry import register_hwm_store_class


@register_hwm_store_class("memory", "in-memory")
class MemoryHWMStore(BaseHWMStore):
    """In-memory local store for HWM values.

    .. note::

        This class should be used in tests only, because all saved HWM values
        will be deleted after exiting the context

    Examples
    --------

    .. code:: python

        from onetl.connection import Hive, Postgres
        from onetl.db import DBReader
        from onetl.strategy import IncrementalStrategy
        from pyspark.sql import SparkSession

        from etl_entities.hwm_store import MemoryHWMStore

        maven_packages = Postgres.get_packages()
        spark = (
            SparkSession.builder.appName("spark-app-name")
            .config("spark.jars.packages", ",".join(maven_packages))
            .getOrCreate()
        )

        postgres = Postgres(
            host="postgres.domain.com",
            user="myuser",
            password="*****",
            database="target_database",
            spark=spark,
        )

        hive = Hive(cluster="rnd-dwh", spark=spark)

        reader = DBReader(
            connection=postgres,
            source="public.mydata",
            columns=["id", "data"],
            hwm_column="id",
        )

        writer = DBWriter(connection=hive, target="newtable")

        with MemoryHWMStore():
            with IncrementalStrategy():
                df = reader.run()
                writer.run(df)

            # will store HWM value in RAM

        # values are lost after exiting the context
    """

    _data: Dict[str, HWM] = PrivateAttr(default_factory=dict)

    def get(self, name: str) -> HWM | None:
        return self._data.get(name, None)

    def save(self, hwm: HWM) -> None:
        self._data[hwm.name] = hwm

    def clear(self) -> None:
        """
        Clears all stored HWM values.
        """
        self._data.clear()