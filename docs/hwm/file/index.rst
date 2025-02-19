.. _file_hwm_classes:

File HWM
========

.. toctree::
    :maxdepth: 2
    :caption: HWM classes

    file_list_hwm
    file_mtime_hwm

What is File HWM?
-----------------

Sometimes it's necessary to read/download only new files from a source folder.

For example, there is a folder with files:

.. code:: bash

    $ hdfs dfs -ls /path

    2MB 2023-09-09 10:13 /path/my/file123
    4Mb 2023-09-09 10:15 /path/my/file234

When new file is being added to this folder:

.. code:: bash

    $ hdfs dfs -ls /path

    2MB 2023-09-09 10:13 /path/my/file123
    4Mb 2023-09-09 10:15 /path/my/file234
    5Mb 2023-09-09 10:20 /path/my/file345  # new one

To download only new files, if is required to somehow track them, and then filter using the information
from a previous run.

This technique is called ``High WaterMark`` or ``HWM`` for short.
It is used by different `strategies <https://onetl.readthedocs.io/en/latest/strategy/index.html#strategy>`_ to implement some complex logic
of filtering source data.

Supported types
---------------

There are a several ways to track HWM value:

    * Save list o file paths, and then select only files not present in this list - :obj:`FileListHWM`
    * Save max modified time of all files, and then select only files with modified time (``file.stat().st_mtime``) - :obj:`FileModifiedTimeHWM`
      higher than this value
    * If file name contains some incrementing value, e.g. id or datetime,
      parse it and save max value of all files, then select only files with higher value - not implemented for now.
