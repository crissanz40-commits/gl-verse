import json
import shutil
import subprocess
from pathlib import Path

import pytest

WEB_ROOT = Path(__file__).parents[1] / "web"


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js no está instalado")
def test_provider_options_follow_other_filters_and_keep_the_selection() -> None:
    module_path = json.dumps((WEB_ROOT / "catalog-filters.js").as_posix())
    script = f"""
const {{ providersForSeries }} = require({module_path});
const assert = require("node:assert/strict");
const providers = [
  {{ id: "", name: "Todas" }},
  {{ id: "youtube", name: "YouTube" }},
  {{ id: "netflix", name: "Netflix" }},
  {{ id: "iqiyi", name: "iQIYI" }},
];
const filteredSeries = [
  {{ availability: [{{ platformId: "youtube" }}, {{ platformId: "iqiyi" }}] }},
];
const ids = providersForSeries(providers, filteredSeries, "netflix").map((item) => item.id);
assert.deepEqual(ids, ["", "youtube", "netflix", "iqiyi"]);
const unselectedIds = providersForSeries(providers, filteredSeries).map((item) => item.id);
assert.deepEqual(unselectedIds, ["", "youtube", "iqiyi"]);
"""

    subprocess.run(["node", "-e", script], check=True)
