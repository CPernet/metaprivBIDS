"""Capture reproducible screenshots of the local browser interface."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "docs" / "_static"
DATASET = ROOT / "Use_Case_Data" / "adult_mini.csv"
HOST = "127.0.0.1"
PORT = 8765
URL = f"http://{HOST}:{PORT}"


def _demo_state():
    sys.path.insert(0, str(ROOT))
    from metaprivBIDS.browser_app import WorkspaceState
    from metaprivBIDS.corelogic import (
        calculate_k_global,
        calculate_privacy_metrics,
        compute_cig,
        compute_suda2,
        load_tabular_data,
    )

    data = load_tabular_data(DATASET)
    quasi_identifiers = [
        "age",
        "education",
        "marital-status",
        "occupation",
        "relationship",
        "sex",
    ]
    state = WorkspaceState(
        filename=DATASET.name,
        data=data,
        original=data.copy(),
        sensitive_attribute="salary-class",
        privacy_quasi_identifiers=quasi_identifiers,
        identifier_column="ID",
    )
    state.privacy_result = calculate_privacy_metrics(
        data, quasi_identifiers, state.sensitive_attribute
    )
    state.k_global_result = calculate_k_global(data, quasi_identifiers)
    state.cig_result = compute_cig(data, quasi_identifiers)
    try:
        state.suda_result = compute_suda2(data, quasi_identifiers, sample_fraction=0.2)
    except RuntimeError:
        # The input view is still useful when the optional R package is absent.
        state.suda_result = None
    return state


def _serve() -> None:
    sys.path.insert(0, str(ROOT))
    from nicegui import ui
    from metaprivBIDS.browser_app import create_page

    @ui.page("/")
    def index() -> None:
        create_page(_demo_state())

    ui.run(
        title="metaprivBIDS documentation",
        host=HOST,
        port=PORT,
        reload=False,
        show=False,
        favicon="🔐",
    )


def _wait_for_server(timeout: float = 30) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urlopen(URL, timeout=1):
                return
        except (OSError, URLError):
            time.sleep(0.25)
    raise TimeoutError(f"The documentation app did not start at {URL}.")


def _capture() -> None:
    from playwright.sync_api import sync_playwright

    STATIC.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment["METAPRIVBIDS_SHOW_BROWSER"] = "0"
    server = subprocess.Popen(
        [sys.executable, str(Path(__file__).resolve()), "--serve"],
        cwd=ROOT,
        env=environment,
    )
    try:
        _wait_for_server()
        with sync_playwright() as playwright:
            launch_options = {"headless": True}
            if sys.platform == "win32":
                launch_options["channel"] = "msedge"
            browser = playwright.chromium.launch(**launch_options)
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            page.goto(URL, wait_until="networkidle")
            page.get_by_text("Data loaded locally").wait_for()

            page.screenshot(path=STATIC / "gui-data.png", full_page=True)

            page.get_by_role("tab", name="Risk").click()
            page.get_by_test_id("contribution-quasi-identifiers-select-all").click()
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(500)
            page.screenshot(path=STATIC / "gui-risk.png", full_page=True)

            page.get_by_role("tab", name="Transform").click()
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(500)
            page.screenshot(path=STATIC / "gui-transform.png", full_page=True)

            page.get_by_role("tab", name="PIF").click()
            page.get_by_test_id("pif-quasi-identifiers-select-all").click()
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(1000)
            page.screenshot(path=STATIC / "gui-pif.png", full_page=True)

            page.get_by_role("tab", name="SUDA2").click()
            page.get_by_test_id("suda-quasi-identifiers-select-all").click()
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(500)
            page.screenshot(path=STATIC / "gui-suda.png", full_page=True)
            browser.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    _serve() if args.serve else _capture()


if __name__ == "__main__":
    main()
