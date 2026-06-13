from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 1000})

    console_errors = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda exc: console_errors.append(f"PAGEERROR: {exc}"))

    page.goto("http://localhost:8501", timeout=60000)

    # Wait for the header to render
    page.wait_for_selector(".main-header", timeout=120000)
    print("MAIN HEADER FOUND:", page.locator(".main-header").inner_text())

    subtitle = page.locator(".sub-header").inner_text()
    print("SUBTITLE:", subtitle)

    # Wait for sidebar radio group
    page.wait_for_selector('div[role="radiogroup"] label', timeout=120000)
    radio_labels = page.locator('div[role="radiogroup"] label').all_inner_texts()
    print("RADIO OPTIONS:", radio_labels)

    # Check which one is checked
    radio_inputs = page.locator('div[role="radiogroup"] input')
    for i in range(radio_inputs.count()):
        checked = radio_inputs.nth(i).is_checked()
        print(f"RADIO {i} ({radio_labels[i] if i < len(radio_labels) else '?'}) checked:", checked)

    # Wait for chat input
    page.wait_for_selector('[data-testid="stChatInput"] textarea', timeout=120000)
    chat_input = page.locator('[data-testid="stChatInput"] textarea')
    print("CHAT INPUT COUNT:", chat_input.count())
    print("CHAT INPUT PLACEHOLDER:", chat_input.first.get_attribute("placeholder"))

    time.sleep(1)
    page.screenshot(path=".claude/_screenshot_1_initial.png", full_page=True)

    # Type a question and submit
    chat_input.first.click()
    chat_input.first.fill("What tables exist in the database?")
    page.screenshot(path=".claude/_screenshot_2_typed.png", full_page=True)
    chat_input.first.press("Enter")

    # Wait for the user's chat message to appear
    page.wait_for_selector('[data-testid="stChatMessage"]', timeout=30000)
    print("CHAT MESSAGE COUNT AFTER SEND:", page.locator('[data-testid="stChatMessage"]').count())

    # Check input cleared
    time.sleep(1)
    input_value = chat_input.first.input_value()
    print("CHAT INPUT VALUE AFTER SUBMIT:", repr(input_value))
    page.screenshot(path=".claude/_screenshot_3_after_submit.png", full_page=True)

    # Wait for the assistant response (second chat message), up to 3 minutes
    for i in range(36):
        time.sleep(5)
        count = page.locator('[data-testid="stChatMessage"]').count()
        print(f"--- after {(i+1)*5}s, chat message count = {count} ---", flush=True)
        if count >= 2:
            break

    time.sleep(1)
    page.screenshot(path=".claude/_screenshot_4_response.png", full_page=True)
    messages = page.locator('[data-testid="stChatMessage"]').all_inner_texts()
    for i, m in enumerate(messages):
        print(f"MESSAGE {i}:", m[:500])

    input_value = chat_input.first.input_value()
    print("FINAL CHAT INPUT VALUE:", repr(input_value))

    print("CONSOLE ERRORS:", console_errors[:20])

    browser.close()
