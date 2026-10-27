"""Structural checks on the conformance vectors themselves."""

import kaira_spec


def test_format():
    suite = kaira_spec.load_conformance()
    assert suite["format"] == "kaira.conformance/v1"
    assert set(suite) == {"format", "declarations", "cases", "invalid_declarations"}


def test_case_ids_are_unique():
    suite = kaira_spec.load_conformance()
    ids = [case["id"] for case in suite["cases"]]
    ids += [case["id"] for case in suite["invalid_declarations"]]
    assert len(ids) == len(set(ids))


def test_cases_reference_known_declarations():
    suite = kaira_spec.load_conformance()
    for case in suite["cases"]:
        assert case["declaration"] in suite["declarations"], case["id"]


def test_cases_have_exactly_one_outcome():
    suite = kaira_spec.load_conformance()
    for case in suite["cases"]:
        assert ("ok" in case) != ("error" in case), case["id"]


def test_packaged_files_exist():
    assert kaira_spec.specification_path().is_file()
    assert kaira_spec.schema_path().is_file()
