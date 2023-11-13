from datetime import date, datetime, timedelta

import pytest

from etl_entities.hwm import (
    ColumnDateHWM,
    ColumnDateTimeHWM,
    ColumnIntHWM,
    HWMTypeRegistry,
)


@pytest.mark.parametrize(
    "hwm_class, value",
    [
        (ColumnDateHWM, date.today()),
        (ColumnDateTimeHWM, datetime.now()),
        (ColumnIntHWM, 1),
    ],
)
def test_column_hwm_valid_input(hwm_class, value):
    hwm_instance = hwm_class(name="test", value=value, column="column_name")

    assert hwm_instance.name == "test"
    assert hwm_instance.value == value
    assert hwm_instance.entity == "column_name"


@pytest.mark.parametrize(
    "hwm_class, value, wrong_values",
    [
        (ColumnDateHWM, date.today(), ["abc", "1.1", "1", "2021-01-01T11:22:33", ColumnDateHWM]),
        (ColumnDateTimeHWM, datetime.now(), ["abc", "1.1", "1", ColumnDateTimeHWM]),
        (ColumnIntHWM, 1, ["abc", ColumnIntHWM]),
    ],
)
def test_column_hwm_wrong_input(hwm_class, value, wrong_values):
    column = "column_name"
    table = "table_name"

    with pytest.raises(ValueError):
        hwm_class()

    with pytest.raises(ValueError):
        hwm_class(column=1)

    with pytest.raises(ValueError):
        hwm_class(column=column, name=table, value="abc")

    with pytest.raises(ValueError):
        hwm_class(column=column, name=table, value=[])

    for wrong_value in wrong_values:
        with pytest.raises(ValueError):
            hwm_class(column=column, name=table, value=wrong_value)

    with pytest.raises(ValueError):
        hwm_class(column=column, name=table, value=value, modified_time="unknown")


@pytest.mark.parametrize(
    "hwm_class, value",
    [
        (ColumnDateHWM, date.today()),
        (ColumnDateTimeHWM, datetime.now()),
        (ColumnIntHWM, 1),
    ],
)
def test_column_hwm_set_value(hwm_class, value):
    column = "column_name"
    table = "table_name"
    hwm = hwm_class(column=column, name=table)

    hwm1 = hwm.copy()
    hwm1.set_value(value)
    assert hwm1.value == value
    assert hwm1.modified_time > hwm.modified_time

    hwm2 = hwm1.copy()
    hwm2.set_value(None)
    assert hwm2.value is None
    assert hwm2.modified_time > hwm.modified_time

    with pytest.raises((TypeError, ValueError)):
        hwm.set_value("unknown")

    with pytest.raises(ValueError):
        hwm.set_value(column)

    with pytest.raises(ValueError):
        hwm.set_value(hwm1)


@pytest.mark.parametrize(
    "hwm_class",
    [
        ColumnDateHWM,
        ColumnDateTimeHWM,
        ColumnIntHWM,
    ],
)
def test_column_hwm_frozen(hwm_class):
    column = "column_name"
    table = "table_name"
    hwm = hwm_class(column=column, name=table)
    modified_time = datetime.now() - timedelta(days=5)

    for attr in ("value", "name", "description", "expression", "modified_time"):
        for value in (1, "abc", date.today(), datetime.now(), None, column, table, modified_time):
            with pytest.raises(TypeError):
                setattr(hwm, attr, value)


@pytest.mark.parametrize(  # noqa: WPS210
    "hwm_class, value, delta",
    [
        (ColumnDateHWM, date.today(), timedelta(days=2)),
        (ColumnDateTimeHWM, datetime.now(), timedelta(seconds=2)),
        (ColumnIntHWM, 1, 2),
    ],
)
def test_column_hwm_compare(hwm_class, value, delta):  # noqa: WPS210
    column1 = "column_name_1"
    column2 = "column_name_2"

    table1 = "table_name_1"
    table2 = "table_name_2"

    hwm = hwm_class(column=column1, name=table1, value=value)

    # modified_time is ignored while comparing HWMs
    modified_time = datetime.now() - timedelta(days=5)
    hwm1 = hwm_class(column=column1, name=table1, value=value, modified_time=modified_time)
    hwm2 = hwm_class(column=column2, name=table1, value=value)
    hwm3 = hwm_class(column=column1, name=table2, value=value)
    hwm4 = hwm_class(column=column2, name=table2, value=value)

    next_value = value + delta

    hwm5 = hwm_class(column=column1, name=table1, value=next_value)
    hwm6 = hwm_class(column=column2, name=table1, value=next_value)
    hwm7 = hwm_class(column=column1, name=table2, value=next_value)
    hwm8 = hwm_class(column=column2, name=table2, value=next_value)

    items = (hwm1, hwm2, hwm3, hwm4)
    next_items = (hwm5, hwm6, hwm7, hwm8)
    valid_pairs = list(zip(items, next_items))

    assert hwm == hwm1

    for item in items:
        assert item == value
        assert item != next_value
        assert item < next_value

    for item in next_items:
        assert item == next_value
        assert item != value
        assert item.value > value

    for item1, item2 in valid_pairs:
        assert item1 < item2
        assert item2 > item1

    for item1 in items + next_items:
        for item2 in items:
            if item1 is not item2:
                assert item1 != item2

                if (item1, item2) not in valid_pairs and (item2, item1) not in valid_pairs:
                    with pytest.raises(NotImplementedError):
                        assert item1 > item2

                    with pytest.raises(NotImplementedError):
                        assert item2 < item1


@pytest.mark.parametrize(  # noqa: WPS210
    "hwm_class, value, delta",
    [
        (ColumnDateHWM, date.today(), timedelta(days=2)),
        (ColumnDateTimeHWM, datetime.now(), timedelta(seconds=2)),
        (ColumnIntHWM, 1, 2),
    ],
)
def test_column_hwm_covers(hwm_class, value, delta):  # noqa: WPS210
    column = "column_name"
    table = "table_name"

    empty_hwm = hwm_class(column=column, name=table)

    assert not empty_hwm.covers(value)
    assert not empty_hwm.covers(value - delta)
    assert not empty_hwm.covers(value + delta)

    hwm = hwm_class(column=column, name=table, value=value)

    assert hwm.covers(value)
    assert hwm.covers(value - delta)
    assert not hwm.covers(value + delta)


@pytest.mark.parametrize(
    "hwm_class, value",
    [
        (ColumnDateHWM, date.today()),
        (ColumnDateTimeHWM, datetime.now()),
        (ColumnIntHWM, 1),
    ],
)
def test_column_hwm_compare_other_type(hwm_class, value):  # noqa: WPS210
    other_types = {ColumnDateHWM, ColumnDateTimeHWM, ColumnIntHWM} - {hwm_class}

    column = "column_name"
    table = "table_name"

    hwm = hwm_class(column=column, name=table, value=value)

    for other_type in other_types:
        other_hwm = other_type(column=column, name=table)

        assert hwm != other_hwm

        with pytest.raises(TypeError):
            assert hwm > other_hwm

        with pytest.raises(TypeError):
            assert hwm < other_hwm


@pytest.mark.parametrize(
    "hwm_class, value, delta",
    [
        (ColumnDateHWM, date.today(), timedelta(days=2)),
        (ColumnDateTimeHWM, datetime.now(), timedelta(seconds=2)),
        (ColumnIntHWM, 1, 2),
    ],
)
def test_column_hwm_add(hwm_class, value, delta):
    column = "column_name"
    table = "table_name"
    hwm = hwm_class(column=column, name=table)

    # if something has been changed, update modified_time
    hwm1 = hwm.copy(update={"value": value})
    hwm2 = hwm.copy(update={"value": value + delta})

    hwm3 = hwm1 + delta

    assert hwm3 == hwm2
    assert hwm3.value == hwm2.value == value + delta
    assert hwm3 is not hwm1  # a copy is returned
    assert hwm3.modified_time > hwm.modified_time

    # not allowed
    with pytest.raises(TypeError):
        _ = hwm3 + None

    with pytest.raises(TypeError):
        _ = hwm + None

    with pytest.raises(TypeError):
        _ = hwm + delta


@pytest.mark.parametrize(
    "hwm_class, value, delta",
    [
        (ColumnDateHWM, date.today(), timedelta(days=2)),
        (ColumnDateTimeHWM, datetime.now(), timedelta(seconds=2)),
        (ColumnIntHWM, 1, 2),
    ],
)
def test_column_hwm_sub(hwm_class, value, delta):
    column = "column_name"
    table = "table_name"
    hwm = hwm_class(column=column, name=table)

    hwm1 = hwm.copy(update={"value": value})
    hwm2 = hwm.copy(update={"value": value - delta})
    hwm3 = hwm1 - delta

    assert hwm3 == hwm2
    assert hwm3.value == hwm2.value == value - delta
    assert hwm3 is not hwm1  # a copy is returned
    assert hwm3.modified_time > hwm.modified_time

    # not allowed
    with pytest.raises(TypeError):
        _ = hwm3 - None

    with pytest.raises(TypeError):
        _ = hwm - None

    with pytest.raises(TypeError):
        _ = hwm - delta


@pytest.mark.parametrize(
    "hwm_class, hwm_type, value, serialized_value",
    [
        (
            ColumnDateHWM,
            "column_date",
            date(year=2021, month=12, day=1),
            "2021-12-01",
        ),
        (
            ColumnDateTimeHWM,
            "column_datetime",
            datetime(year=2021, month=12, day=1, hour=4, minute=20, second=33),
            "2021-12-01T04:20:33",
        ),
        (ColumnIntHWM, "column_int", 1, 1),
    ],
)
def test_column_hwm_serialization(hwm_class, hwm_type, value, serialized_value):
    column = "column_name"
    table = "table_name"
    modified_time = datetime.now()

    serialized1 = {
        "value": serialized_value,
        "type": hwm_type,
        "entity": column,
        "name": table,
        "description": "",
        "expression": None,
        "modified_time": modified_time.isoformat(),
    }
    hwm1 = hwm_class(column=column, name=table, value=value, modified_time=modified_time)

    assert hwm1.serialize() == serialized1
    assert hwm_class.deserialize(serialized1) == hwm1

    serialized2 = serialized1.copy()
    serialized2["value"] = None
    hwm2 = hwm_class(column=column, name=table, modified_time=modified_time)

    assert hwm2.serialize() == serialized2
    assert hwm_class.deserialize(serialized2) == hwm2


@pytest.mark.parametrize(
    "hwm_class",
    [
        ColumnDateHWM,
        ColumnDateTimeHWM,
        ColumnIntHWM,
    ],
)
def test_column_hwm_unregistered_type(hwm_class):
    class UnregisteredHWM(hwm_class):
        pass  # noqa: WPS604

    err_msg = r"You should registered <class \'.*'> class using @register_hwm_type decorator"

    with pytest.raises(KeyError, match=err_msg):
        HWMTypeRegistry.get_key(UnregisteredHWM)
