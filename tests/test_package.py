def test_package_version_is_public_v01() -> None:
    from cyber_junshi import __version__

    assert __version__ == "0.1.0"
