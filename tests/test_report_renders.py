from pathlib import Path
from dda.report.render import render_report

def test_report_renders(tmp_path):
    tmpl = tmp_path / "report.md.tmpl"
    tmpl.write_text("# {{ repo.name }}\n{% for c in scorecard.categories %}{{ c.name }}\n{% endfor %}\n")
    out = tmp_path / "out.md"
    render_report(tmpl, out, {"repo": {"name": "x"}, "scorecard": {"categories": [{"name": "A"}]}})
    assert out.read_text().startswith("# x")
