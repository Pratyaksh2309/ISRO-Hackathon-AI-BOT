chrome.action.onClicked.addListener(async (tab) => {
    if (!tab.id) return;

    await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
            const widget = document.getElementById(
                "agentic-copilot-widget"
            );

            if (widget) {
                widget.style.display =
                    widget.style.display === "none"
                        ? "block"
                        : "none";
            }
        }
    });
});