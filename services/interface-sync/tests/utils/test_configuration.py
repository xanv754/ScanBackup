from pathlib import Path

import pytest

from interface_sync.exceptions import InvalidConfigError
from interface_sync.utils.configuration import ConfigurationFile
from interface_sync.utils.logger import ServiceLogger


class RecordingLogger(ServiceLogger):
    def __init__(self) -> None:
        self.records: list[tuple[str, str, str]] = []

    def info(self, message: str, details: str = "") -> None:
        self.records.append(("info", message, details))

    def warning(self, message: str, details: str = "") -> None:
        self.records.append(("warning", message, details))

    def error(self, message: str, details: str = "") -> None:
        self.records.append(("error", message, details))


@pytest.fixture
def recording_logger() -> RecordingLogger:
    return RecordingLogger()


@pytest.fixture
def config_path(tmp_path: Path) -> Path:
    return tmp_path / "config.yml"


def load_causes(
    config_path: Path, content: str | None, recording_logger: RecordingLogger
) -> list[str]:
    if content is not None:
        config_path.write_text(content, encoding="utf-8")
    with pytest.raises(InvalidConfigError) as error_info:
        ConfigurationFile(config_path, recording_logger).load()
    return error_info.value.causes


def test_load_valid_configuration(config_path: Path, recording_logger: RecordingLogger):
    """RF-001: a valid file returns one page per entry, in file order."""
    config_path.write_text(
        'links:\n'
        '  - layer: "borde"\n    url: "https://host/a?X=1"\n    vendor: "huawei"\n'
        '  - layer: "ixp"\n    url: "http://host/b"\n',
        encoding="utf-8",
    )

    pages = ConfigurationFile(config_path, recording_logger).load()

    assert [(p.layer, p.vendor, p.url) for p in pages] == [
        ("BORDE", "HUAWEI", "https://host/a?X=1"),
        ("IXP", "UNDEFINED", "http://host/b"),
    ]
    assert recording_logger.records == [("info", "Configuración cargada", "2 páginas")]


def test_load_standardizes_layer_and_vendor(config_path: Path, recording_logger: RecordingLogger):
    """RF-002: text is stripped and layer and vendor are uppercased; the URL is kept."""
    config_path.write_text(
        'links:\n'
        '  - layer: "  bORDE "\n'
        '    url: "  https://Host/Path  "\n'
        '    vendor: " jUNIPER "\n',
        encoding="utf-8",
    )

    page = ConfigurationFile(config_path, recording_logger).load()[0]

    assert (page.layer, page.vendor, page.url) == ("BORDE", "JUNIPER", "https://Host/Path")


@pytest.mark.parametrize(
    "vendor_line",
    ["", "    vendor:\n", '    vendor: ""\n', '    vendor: "   "\n', "    vendor: UnDefined\n"],
)
def test_load_vendor_defaults_to_undefined(
    config_path: Path, recording_logger: RecordingLogger, vendor_line: str
):
    """RF-002: an omitted, empty or `undefined` vendor becomes `UNDEFINED`."""
    config_path.write_text(
        f"links:\n  - layer: a\n    url: http://h\n{vendor_line}", encoding="utf-8"
    )

    assert ConfigurationFile(config_path, recording_logger).load()[0].vendor == "UNDEFINED"


def test_load_same_layer_with_different_vendor_is_valid(
    config_path: Path, recording_logger: RecordingLogger
):
    """RF-002: the same layer is allowed when the vendors differ."""
    config_path.write_text(
        "links:\n"
        "  - {layer: borde, url: 'http://h/1', vendor: huawei}\n"
        "  - {layer: borde, url: 'http://h/2', vendor: juniper}\n",
        encoding="utf-8",
    )

    assert len(ConfigurationFile(config_path, recording_logger).load()) == 2


def test_load_missing_file(config_path: Path, recording_logger: RecordingLogger):
    """RF-001: a missing file is invalid (cause a)."""
    causes = load_causes(config_path, None, recording_logger)

    assert len(causes) == 1
    assert "No se puede leer" in causes[0]


def test_load_unreadable_file(config_path: Path, recording_logger: RecordingLogger):
    """RF-001: a file that is not valid text is invalid (cause a)."""
    config_path.write_bytes(b"\xff\xfe\x00\xd8")

    causes = load_causes(config_path, None, recording_logger)

    assert "No se puede leer" in causes[0]


def test_load_not_yaml(config_path: Path, recording_logger: RecordingLogger):
    """RF-001: malformed YAML is invalid (cause b)."""
    causes = load_causes(config_path, "links: [", recording_logger)

    assert len(causes) == 1
    assert "no es YAML válido" in causes[0]


def test_load_root_is_not_a_mapping(config_path: Path, recording_logger: RecordingLogger):
    """RF-001: a YAML root that is not a mapping is invalid (cause b)."""
    causes = load_causes(config_path, "- layer: a\n", recording_logger)

    assert "debe ser un mapeo" in causes[0]


@pytest.mark.parametrize("content", ["", "# only a comment\n"])
def test_load_without_content(config_path: Path, recording_logger: RecordingLogger, content: str):
    """RF-001: an empty file or one with only comments is invalid (cause c)."""
    causes = load_causes(config_path, content, recording_logger)

    assert "no tiene contenido" in causes[0]


@pytest.mark.parametrize("content", ["links:\n", "links: []\n"])
def test_load_empty_links(config_path: Path, recording_logger: RecordingLogger, content: str):
    """RF-001: an empty `links` is invalid (cause c)."""
    causes = load_causes(config_path, content, recording_logger)

    assert causes == ["La clave 'links' no existe o está vacía"]


def test_load_links_is_not_a_list(config_path: Path, recording_logger: RecordingLogger):
    """RF-001: `links` must be a list."""
    causes = load_causes(config_path, "links: {layer: a}\n", recording_logger)

    assert causes == ["La clave 'links' debe ser una lista"]


@pytest.mark.parametrize(
    ("entry", "expected_cause"),
    [
        ("{url: 'http://h'}", "Página 1: layer: campo obligatorio ausente"),
        ("{layer: a}", "Página 1: url: campo obligatorio ausente"),
        ("{layer: '  ', url: 'http://h'}", "Página 1: layer: campo obligatorio vacío"),
        ("{layer: a, url: ''}", "Página 1: url: campo obligatorio vacío"),
        ("{layer: a, url: 'http://h', extra: 1}", "Página 1: extra: clave no reconocida"),
        ("{layer: a, url: 'ftp://h/x'}", "Página 1: url: la URL debe usar el esquema http o https"),
        ("{layer: a, url: 'h/x'}", "Página 1: url: la URL debe usar el esquema http o https"),
        ("{layer: a, url: 'https:///x'}", "Página 1: url: la URL no tiene host"),
        ("just text", "Página 1: entrada: cada entrada debe ser un mapeo"),
    ],
)
def test_load_invalid_entry(
    config_path: Path, recording_logger: RecordingLogger, entry: str, expected_cause: str
):
    """RF-001: each invalid entry cause (d, e, g) is reported with its position."""
    causes = load_causes(config_path, f"links:\n  - {entry}\n", recording_logger)

    assert len(causes) == 1
    assert causes[0].startswith(expected_cause)


def test_load_duplicate_layer_and_vendor_after_standardizing(
    config_path: Path, recording_logger: RecordingLogger
):
    """RF-001: pages equal after standardization are duplicates (cause f)."""
    content = (
        "links:\n"
        "  - {layer: borde, url: 'http://h/1', vendor: huawei}\n"
        "  - {layer: ixp, url: 'http://h/2'}\n"
        "  - {layer: ' BORDE ', url: 'http://h/3', vendor: HUAWEI}\n"
    )

    causes = load_causes(config_path, content, recording_logger)

    assert causes == ["Capa 'BORDE' y proveedor 'HUAWEI' repetidos entre las páginas 1 y 3"]


def test_load_accumulates_all_causes(config_path: Path, recording_logger: RecordingLogger):
    """RF-001: causes are not cut at the first one and are all logged as errors."""
    content = (
        "unknown: 1\n"
        "links:\n"
        "  - {layer: a, url: 'ftp://h'}\n"
        "  - {url: 'http://h'}\n"
        "  - {layer: b, url: 'http://h/1'}\n"
        "  - {layer: b, url: 'http://h/2'}\n"
    )

    causes = load_causes(config_path, content, recording_logger)

    assert len(causes) == 4
    assert recording_logger.records == [
        ("error", "Configuración inválida", cause) for cause in causes
    ]


def test_load_invalid_entry_is_not_reported_as_duplicate(
    config_path: Path, recording_logger: RecordingLogger
):
    """RF-001: duplicate detection only compares entries that are valid on their own."""
    content = (
        "links:\n"
        "  - {layer: a, url: 'http://h/1'}\n"
        "  - {layer: a, url: 'ftp://h/2'}\n"
    )

    causes = load_causes(config_path, content, recording_logger)

    assert len(causes) == 1
    assert "repetidos" not in causes[0]
