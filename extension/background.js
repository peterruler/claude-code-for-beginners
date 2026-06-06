// background.js – registers the context‑menu and opens the popup with the selected text

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "summarize-selection",
    title: "Summarize",
    contexts: ["selection"] // only show when something is selected
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId !== "summarize-selection") return;

  // Get the selected text via a temporary content script
  const [{ result: selectedText }] = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => window.getSelection().toString()
  });

  // Store it in session storage (short‑lived, not persisted)
  await chrome.storage.session.set({ selectedText });

  // Open the extension popup (same as clicking the toolbar button)
  chrome.action.openPopup();
});
