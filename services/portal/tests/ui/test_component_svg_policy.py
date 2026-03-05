from __future__ import annotations

from pathlib import Path

from django.template import Context, Template
from django.test import SimpleTestCase

REPO_ROOT = Path(__file__).resolve().parents[4]
COMPONENTS_DIR = REPO_ROOT / "services" / "portal" / "templates" / "components"
ALLOWLIST_FILE = REPO_ROOT / ".component-svg-allowlist"


def _load_svg_allowlist() -> set[str]:
    allowed: set[str] = set()
    for raw in ALLOWLIST_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        allowed.add(line.split("|", 1)[0].strip())
    return allowed


class ComponentSvgPolicyTests(SimpleTestCase):
    def test_only_allowlisted_components_contain_raw_svg(self) -> None:
        allowlisted = _load_svg_allowlist()
        found_raw_svg: set[str] = set()

        for component_file in sorted(COMPONENTS_DIR.glob("*.html")):
            content = component_file.read_text(encoding="utf-8")
            if "<svg" in content:
                found_raw_svg.add(component_file.relative_to(REPO_ROOT).as_posix())

        self.assertSetEqual(found_raw_svg, allowlisted)

    def test_migrated_components_use_icon_tag(self) -> None:
        migrated_components = [
            "account_status_banner.html",
            "alert.html",
            "badge.html",
            "cookie_consent_banner.html",
            "customer_selector.html",
            "list_page_filters.html",
            "list_page_header.html",
            "mobile_header.html",
            "mobile_nav_item.html",
            "modal.html",
            "nav_dropdown.html",
            "pagination.html",
            "step_navigation.html",
            "table.html",
        ]

        for filename in migrated_components:
            content = (COMPONENTS_DIR / filename).read_text(encoding="utf-8")
            self.assertIn("{% icon ", content, msg=f"{filename} should render icons via {{% icon %}}")

    def test_account_status_banner_renders_icon_svg(self) -> None:
        rendered = Template(
            '{% include "components/account_status_banner.html" with banner=banner %}'
        ).render(
            Context(
                {
                    "banner": {
                        "severity": "critical",
                        "message": "Payment overdue",
                        "cta_url": "/billing/",
                        "cta_text": "Pay now",
                    }
                }
            )
        )

        self.assertIn("<svg", rendered)
        self.assertIn("M10 14l2-2m0 0l2-2", rendered)  # x-circle
        self.assertIn("M9 5l7 7-7 7", rendered)  # chevron-right

    def test_list_page_header_renders_configured_icon_svg(self) -> None:
        rendered = Template(
            '{% include "components/list_page_header.html" with '
            'list_icon_bg="bg-blue-600" '
            'list_icon_name="menu" '
            'list_title="Title" '
            'list_subtitle="Subtitle" %}'
        ).render(Context({}))

        self.assertIn("<svg", rendered)
        self.assertIn("M4 6h16M4 12h16M4 18h16", rendered)  # menu icon
