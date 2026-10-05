"""
Capture GUI Screenshots
=======================
Automated script to capture high-resolution screenshots of the GUI tabs
for project report documentation, submissions, and preview.
"""

import os
import time
from PIL import ImageGrab
import ttkbootstrap as tb
from gui_app import WirelessLinkBudgetApp


def capture_screenshots(output_dir="sample_outputs"):
    os.makedirs(output_dir, exist_ok=True)
    print("Launching GUI for screenshot capture...")

    root = tb.Window(title="Wireless Link Budget GUI", themename="darkly")
    root.geometry("1280x820")
    app = WirelessLinkBudgetApp(root)

    # Force update
    root.update_idletasks()
    root.update()
    time.sleep(0.5)

    def snap(filename):
        x = root.winfo_rootx()
        y = root.winfo_rooty()
        w = root.winfo_width()
        h = root.winfo_height()
        box = (x, y, x + w, y + h)
        try:
            img = ImageGrab.grab(box)
            path = os.path.join(output_dir, filename)
            img.save(path)
            print(f"Captured: {path}")
        except Exception as e:
            print(f"Could not grab window box: {e}")

    # 1. Screenshot Tab 1: Wi-Fi 6 Link Budget Calculator
    root.update()
    snap("gui_screenshot_calculator_tab.png")

    # 2. Screenshot Tab 2: Parametric Sweeps
    app.notebook.select(app.tab_sweeps)
    root.update_idletasks()
    root.update()
    time.sleep(0.3)
    snap("gui_screenshot_sweeps_tab.png")

    # 3. Screenshot Tab 3: Multi-Scenario Comparator
    app.notebook.select(app.tab_compare)
    app._load_all_presets_for_comparison()
    root.update_idletasks()
    root.update()
    time.sleep(0.3)
    snap("gui_screenshot_comparator_tab.png")

    # 4. Screenshot Tab 4: Theory Reference
    app.notebook.select(app.tab_theory)
    root.update_idletasks()
    root.update()
    time.sleep(0.3)
    snap("gui_screenshot_theory_tab.png")

    root.destroy()
    print("Screenshot capture sequence finished.")


if __name__ == "__main__":
    capture_screenshots()
