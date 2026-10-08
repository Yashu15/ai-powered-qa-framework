"""Standalone Playwright smoke test for Booking.com's destination input."""

from playwright.sync_api import Page, expect


def test_booking_search(page: Page):
    page.goto("https://www.booking.com", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(2000)

    # Dismiss common overlays if they appear.
    dismiss_targets = [
        page.get_by_label("Dismiss sign-in info."),
        page.get_by_role("button", name="Dismiss"),
        page.get_by_role("button", name="Accept"),
    ]
    for target in dismiss_targets:
        try:
            if target.is_visible(timeout=2000):
                target.click(timeout=3000)
                break
        except Exception:
            pass

    destination = page.locator(
        "input[name='ss'], input[placeholder*='Where are you going?'], "
        "input[aria-label*='Where are you going?'], input[aria-label='Enter destination'], "
        "input[aria-label*='Enter destination']"
    ).first
    expect(destination).to_be_visible(timeout=30000)
    destination.fill("Perth")
    expect(destination).to_have_value("Perth", timeout=15000)