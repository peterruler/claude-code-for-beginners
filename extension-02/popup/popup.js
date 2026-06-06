(async () => {
  const { selectedText } = await chrome.storage.session.get('selectedText');
  const summaryEl = document.getElementById('summary');

  if (!selectedText) {
    summaryEl.textContent = "No text selected.";
    return;
  }

  // ----- OpenAI API CALL -----
  const OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions";
  const apiKey = process.env.OPENAI_API_KEY; // will be replaced from .env

  try {
    const response = await fetch(OPENAI_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        messages: [
          { role: "system", content: "Fasse den folgenden Text in genau drei Sätzen zusammen, auf Deutsch, und erhalte die Bedeutung bei." },
          { role: "user",   content: selectedText }
        ],
        max_tokens: 300,
        temperature: 0.5
      })
    });

    if (!response.ok) throw new Error(`OpenAI error ${response.status}`);
    const data = await response.json();
    const summary = data.choices?.[0]?.message?.content?.trim() || "No summary returned.";
    summaryEl.textContent = summary;
  } catch (e) {
    console.error(e);
    summaryEl.textContent = "Error contacting OpenAI – see console for details.";
  }
})();
