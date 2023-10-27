import pytest

from etl_entities.hwm_store import (
    HWMStoreStackManager,
    MemoryHWMStore,
    detect_hwm_store,
)


@pytest.mark.parametrize(
    "hwm_store_class, input_config, key",
    [
        (
            MemoryHWMStore,
            {"hwm_store": "memory"},
            "hwm_store",
        ),
        (
            MemoryHWMStore,
            {"some_store": "memory"},
            "some_store",
        ),
        (
            MemoryHWMStore,
            {"hwm_store": {"memory": None}},
            "hwm_store",
        ),
        (
            MemoryHWMStore,
            {"hwm_store": {"memory": []}},
            "hwm_store",
        ),
        (
            MemoryHWMStore,
            {"hwm_store": {"memory": {}}},
            "hwm_store",
        ),
    ],
)
@pytest.mark.parametrize("config_constructor", [dict])
def test_hwm_store_unit_detect(hwm_store_class, input_config, config_constructor, key):
    @detect_hwm_store(key)
    def main(config):
        assert isinstance(HWMStoreStackManager.get_current(), hwm_store_class)

    conf = config_constructor(input_config)
    main(conf)


@pytest.mark.parametrize(
    "input_config",
    [
        {"hwm_store": 1},
        {"hwm_store": "unknown"},
        {"hwm_store": {"unknown": None}},
    ],
)
@pytest.mark.parametrize("config_constructor", [dict])
def test_hwm_store_unit_detect_failure(input_config, config_constructor):
    @detect_hwm_store("hwm_store")
    def main(config):  # NOSONAR
        pass

    conf = config_constructor(input_config)
    with pytest.raises((KeyError, ValueError)):
        main(conf)

    conf = config_constructor({"nested": input_config})
    with pytest.raises((KeyError, ValueError)):
        main(conf)

    conf = config_constructor({"even": {"more": {"nested": input_config}}})
    with pytest.raises((KeyError, ValueError)):
        main(conf)


@pytest.mark.parametrize(
    "input_config",
    [
        {"hwm_store": {"memory": 1}},
        {"hwm_store": {"memory": {"unknown": "arg"}}},
        {"hwm_store": {"memory": ["too_many_arg"]}},
    ],
)
@pytest.mark.parametrize("config_constructor", [dict])
def test_hwm_store_unit_wrong_options(input_config, config_constructor):
    @detect_hwm_store("hwm_store")
    def main(config):  # NOSONAR
        pass

    conf = config_constructor(input_config)

    with pytest.raises((TypeError, ValueError)):
        main(conf)

    conf = config_constructor({"nested": input_config})
    with pytest.raises((TypeError, ValueError)):
        main(conf)

    conf = config_constructor({"even": {"more": {"nested": input_config}}})
    with pytest.raises((TypeError, ValueError)):
        main(conf)


@pytest.mark.parametrize(
    "config, key",
    [
        ({"some": "yml"}, "unknown"),
        ({"some": "yml"}, "some.unknown"),
        ({"some": "yml"}, "some.yaml.unknown"),
        ({"var": {"hwm_store": "yml"}}, "var.hwm_store."),
        ({"var": {"hwm_store": "yml"}}, "var..hwm_store"),
        ({"some": "yml"}, 12),
        ({}, "var.hwm_store"),
        ({"var": {"hwm_store": "yml"}}, ""),
        ({}, ""),
    ],
)
@pytest.mark.parametrize("config_constructor", [dict])
def test_hwm_store_wrong_config_and_key_value_error(config_constructor, config, key):
    with pytest.raises(ValueError):

        @detect_hwm_store(key)
        def main(config):
            ...  # noqa:  WPS428

        conf = config_constructor(config)
        main(conf)