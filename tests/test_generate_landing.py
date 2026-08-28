from __future__ import annotations

from pathlib import Path

import pytest
import yaml

import scripts.generate_landing as gl


ROOT = Path(__file__).resolve().parents[1]


def load_instances_fixture() -> dict:
    return yaml.safe_load((ROOT / "data" / "instances.yml").read_text(encoding="utf-8"))


def make_instances(
    *,
    current_slug: str = "2601",
    current_url: str = "./2601/",
    current_registration: str = "https://example.org/register",
    previous_slug: str = "2511",
    previous_visible: bool = True,
    previous_url: str = "./2511/",
) -> dict:
    return {
        "instances": [
            {
                "slug": current_slug,
                "label": "Current run",
                "status": "current",
                "visible": True,
                "instance_url": current_url,
                "registration_url": current_registration,
                "sort_key": 202601,
            },
            {
                "slug": previous_slug,
                "label": "Previous run",
                "status": "previous",
                "visible": previous_visible,
                "instance_url": previous_url,
                "registration_url": "",
                "sort_key": 202511,
            },
        ]
    }


def test_repo_fixture_still_valid() -> None:
    validated = gl.validate_instances_data(load_instances_fixture())
    current = [item for item in validated if item["status"] == "current"]
    assert len(current) == 1
    assert current[0]["visible"] is True
    for item in validated:
        assert {"slug", "label", "status", "visible", "instance_url", "registration_url", "sort_key"} <= set(
            item.keys()
        )


def test_load_yaml_dict_rejects_non_mapping(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yml"
    bad.write_text("- not-a-mapping\n", encoding="utf-8")
    with pytest.raises(gl.ValidationError) as exc:
        gl.load_yaml_dict(bad)
    assert "top-level mapping" in str(exc.value)


def test_load_ui_labels_rejects_unknown_keys(tmp_path: Path) -> None:
    ui = tmp_path / "ui.yml"
    ui.write_text(
        "hero_view_current_lable: Broken typo\n",
        encoding="utf-8",
    )
    with pytest.raises(gl.ValidationError) as exc:
        gl.load_ui_labels(ui)
    assert "unknown key(s)" in str(exc.value)


def test_validate_instances_rejects_multiple_current() -> None:
    data = make_instances()
    data["instances"][1]["status"] = "current"
    data["instances"][1]["visible"] = True
    with pytest.raises(gl.ValidationError) as exc:
        gl.validate_instances_data(data)
    assert "exactly one status='current'" in str(exc.value)


def test_validate_instances_rejects_hidden_current() -> None:
    data = make_instances()
    data["instances"][0]["visible"] = False
    with pytest.raises(gl.ValidationError) as exc:
        gl.validate_instances_data(data)
    assert "current instance must be visible" in str(exc.value)


def test_validate_instances_rejects_invalid_slug_month() -> None:
    data = make_instances(previous_slug="2599", previous_url="./2599/")
    with pytest.raises(gl.ValidationError) as exc:
        gl.validate_instances_data(data)
    assert "month must be between 01 and 12" in str(exc.value)


def test_validate_instances_accepts_absolute_instance_url() -> None:
    data = make_instances(previous_url="https://example.org/2511/")
    validated = gl.validate_instances_data(data)
    assert validated[1]["instance_url"] == "https://example.org/2511/"


def test_validate_instances_rejects_relative_instance_url_slug_mismatch() -> None:
    data = make_instances(previous_slug="2511", previous_url="./2411/")
    with pytest.raises(gl.ValidationError) as exc:
        gl.validate_instances_data(data)
    assert "must match slug for relative links" in str(exc.value)


def test_validate_instances_rejects_protocol_relative_registration_url() -> None:
    data = make_instances(current_registration="//evil.example/path")
    with pytest.raises(gl.ValidationError) as exc:
        gl.validate_instances_data(data)
    assert "must not be protocol-relative" in str(exc.value)


def test_validate_instances_accepts_internal_registration_paths() -> None:
    data = make_instances(current_registration="/registration/form")
    validated = gl.validate_instances_data(data)
    assert validated[0]["registration_url"] == "/registration/form"

    data = make_instances(current_registration="./registration/form")
    validated = gl.validate_instances_data(data)
    assert validated[0]["registration_url"] == "./registration/form"


def test_validate_instances_rejects_bool_sort_key() -> None:
    data = make_instances()
    data["instances"][1]["sort_key"] = True
    with pytest.raises(gl.ValidationError) as exc:
        gl.validate_instances_data(data)
    assert "sort_key must be an integer" in str(exc.value)


def test_build_dynamic_partials_include_visible_previous_only() -> None:
    ui = gl.UI_DEFAULTS.copy()

    visible = gl.validate_instances_data(make_instances(previous_visible=True))
    _, band_visible = gl.build_dynamic_partials(visible, ui)
    assert "Current run" in band_visible
    assert "Previous run" in band_visible
    assert "instance-pill--current" in band_visible

    hidden = gl.validate_instances_data(make_instances(previous_visible=False))
    _, band_hidden = gl.build_dynamic_partials(hidden, ui)
    assert "Current run" in band_hidden
    assert "Previous run" not in band_hidden
    assert "instance-pill--current" in band_hidden


def test_build_dynamic_partials_uses_configurable_labels() -> None:
    validated = gl.validate_instances_data(make_instances())
    ui = gl.UI_DEFAULTS.copy()
    ui["hero_view_current_label"] = "Go to current"
    ui["hero_registration_open_label"] = "Apply now"
    ui["instances_band_title"] = "Earlier runs"
    hero, band = gl.build_dynamic_partials(validated, ui)
    assert "Go to current" in hero
    assert "Apply now" in hero
    assert "Earlier runs" in band

def test_build_dynamic_partials_emit_markdown_links_without_html_url_escaping() -> None:
    validated = gl.validate_instances_data(
        make_instances(
            current_registration="https://example.org/register?course=sci&session=2"
        )
    )
    ui = gl.UI_DEFAULTS.copy()
    hero, _ = gl.build_dynamic_partials(validated, ui)

    assert "[Registration open!]" in hero
    assert "(<https://example.org/register?course=sci&session=2>)" in hero
    assert "&amp;" not in hero


def test_write_generated_partials_writes_expected_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    validated = gl.validate_instances_data(make_instances())
    ui = gl.UI_DEFAULTS.copy()

    generated_dir = tmp_path / "_generated"
    hero_file = generated_dir / "hero-actions.qmd"
    band_file = generated_dir / "instances-band.qmd"

    monkeypatch.setattr(gl, "GENERATED_DIR", generated_dir)
    monkeypatch.setattr(gl, "HERO_ACTIONS_FILE", hero_file)
    monkeypatch.setattr(gl, "INSTANCES_BAND_FILE", band_file)

    gl.write_generated_partials(validated, ui)

    assert hero_file.exists()
    assert band_file.exists()
    assert "./2601/" in hero_file.read_text(encoding="utf-8")
    assert "Previous run" in band_file.read_text(encoding="utf-8")
