from playwright.sync_api import sync_playwright
import re


def extract_x_headers():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Enable request interception
        page.on("request", handle_request)

        # Navigate to Booking.com
        page.goto("https://www.booking.com")

        # Perform a search to trigger GraphQL requests
        page.fill('input[name="ss"]', "Tokyo")
        page.press('input[name="ss"]', "Enter")

        # Wait for navigation and GraphQL requests
        page.wait_for_load_state("networkidle")

        browser.close()


def handle_request(request):
    if re.match(r"https://www\.booking\.com/dml/graphql.*", request.url):
        print(f"GraphQL Request URL: {request.url}")
        headers = request.headers
        for key, value in headers.items():
            if key.startswith('x-'):
                print(f"{key}: {value}")
        print("--------------------")


if __name__ == "__main__":
    extract_x_headers()
