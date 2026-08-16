const widget = document.createElement("div");
widget.id = "agentic-copilot-widget";

widget.innerHTML = `
    <div id="cat-mascot">
        <div id="cat-face">😺</div>
        <div id="cat-bubble">Ready!</div>
    </div>

    <div id="copilot-card" class="copilot-hidden">
        <div id="copilot-header">
            <b>Universal Chatbot</b>
            <button id="copilot-minimize">−</button>
        </div>

        <div id="copilot-output">
            Ask me anything about this website.
        </div>

        <div id="copilot-input-row">
            <input
                id="copilot-question"
                placeholder="Ask about this website..."
            >
            <button id="copilot-ask">➤</button>
        </div>

        <button id="copilot-source" style="display:none;">
            📍 Show Source
        </button>
    </div>
`;

document.body.appendChild(widget);

const style = document.createElement("style");

style.textContent = `
#agentic-copilot-widget {
    position: fixed;
    right: 25px;
    bottom: 25px;
    width: 340px;
    z-index: 2147483647;
    font-family: Arial, sans-serif;
}

#cat-mascot {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-left: 15px;
    margin-bottom: -5px;
}

#cat-face {
    font-size: 58px;
    cursor: pointer;
    transform-origin: bottom center;
    filter: drop-shadow(0 5px 8px rgba(0,0,0,.2));
}

#cat-bubble {
    background: white;
    padding: 6px 10px;
    border-radius: 12px;
    font-size: 12px;
    box-shadow: 0 3px 12px rgba(0,0,0,.15);
}
#copilot-card,
#copilot-output,
#copilot-question,
#cat-bubble {
    color: #000000 !important;
}

#copilot-question::placeholder {
    color: #666666 !important;
}

#copilot-output {
    background: #ffffff !important;
    color: #000000 !important;
    user-select: text !important;
    cursor: text !important;
}

#copilot-header {
    color: white !important;
}
#copilot-card {
    background: rgba(255,255,255,.97);
    border-radius: 18px;
    box-shadow: 0 12px 40px rgba(0,0,0,.25);
    overflow: hidden;
    color: #111827;
    user-select: text;
}

#copilot-header {
    background: linear-gradient(135deg,#312e81,#6366f1);
    color: white;
    padding: 12px 14px;
    display: flex;
    align-items: center;
    cursor: move;
}

#copilot-minimize {
    margin-left: auto;
    border: none;
    background: transparent;
    color: white;
    font-size: 20px;
    cursor: pointer;
}

.copilot-hidden {
    display: none !important;
}

#copilot-output {
    padding: 14px;
    max-height: 220px;
    overflow-y: auto;
    line-height: 1.45;
    background: #f8fafc;
}

#copilot-input-row {
    display: flex;
    gap: 7px;
    padding: 12px;
}

#copilot-question {
    flex: 1;
    padding: 10px;
    border-radius: 10px;
    border: 1px solid #d1d5db;
}

#copilot-ask {
    border: none;
    background: #4f46e5;
    color: white;
    border-radius: 10px;
    padding: 0 15px;
    cursor: pointer;
}

#copilot-source {
    margin: 0 12px 12px;
    padding: 8px 12px;
    border: none;
    border-radius: 9px;
    background: #facc15;
    cursor: pointer;
}

.cat-thinking {
    animation: catThinking .35s infinite alternate;
}

@keyframes catThinking {
    from {
        transform: rotate(-8deg) translateY(0);
    }
    to {
        transform: rotate(8deg) translateY(-6px);
    }
}

.cat-happy {
    animation: catHappy .25s 4 alternate;
}

@keyframes catHappy {
    from {
        transform: scale(1);
    }
    to {
        transform: scale(1.25) rotate(6deg);
    }
}
`;

document.head.appendChild(style);


const header = document.getElementById("copilot-header");
const cat = document.getElementById("cat-face");
const catBubble = document.getElementById("cat-bubble");

let dragging = false;
let offsetX = 0;
let offsetY = 0;
let wasDragged = false;

function startDrag(e) {

    // Don't drag while typing or clicking controls
    if (
        e.target.closest("input") ||
        e.target.closest("button")
    ) {
        return;
    }

    dragging = true;
    wasDragged = false;

    const rect = widget.getBoundingClientRect();

    offsetX = e.clientX - rect.left;
    offsetY = e.clientY - rect.top;

    e.preventDefault();
}


document.addEventListener("mousemove", (e) => {
    if (!dragging) return;

    wasDragged = true;

    widget.style.left = `${e.clientX - offsetX}px`;
    widget.style.top = `${e.clientY - offsetY}px`;

    widget.style.right = "auto";
    widget.style.bottom = "auto";
});

document.addEventListener("mouseup", () => {
    dragging = false;
});

// cat.addEventListener("click", () => {
//     meow();
//     const messages = [
//         "Meow! 🐾",
//         "Ask me something 😸",
//         "I'm listening 👀",
//         "Meow meow!",
//         "Need help?"
//     ];

//     catBubble.textContent =
//         messages[Math.floor(Math.random() * messages.length)];

//     cat.classList.add("cat-happy");

//     setTimeout(() => {
//         cat.classList.remove("cat-happy");
//     }, 800);
// });



const askBtn = document.getElementById("copilot-ask");
const questionInput = document.getElementById("copilot-question");
const output = document.getElementById("copilot-output");
const sourceBtn = document.getElementById("copilot-source");


const card = document.getElementById("copilot-card");
const minimizeBtn = document.getElementById("copilot-minimize");

cat.addEventListener("mousedown", startDrag);

header.addEventListener("mousedown", startDrag);


cat.addEventListener("click", () => {
    meow();

    if (wasDragged) {
        wasDragged = false;
        return;
    }

    card.classList.toggle("copilot-hidden");

    if (card.classList.contains("copilot-hidden")) {
        catBubble.textContent = "Meow! 🐾";
    } else {
        catBubble.textContent = "Ask me 😸";

        setTimeout(() => {
            questionInput.focus();
        }, 100);
    }

    cat.classList.add("cat-happy");

    setTimeout(() => {
        cat.classList.remove("cat-happy");
    }, 800);
});

minimizeBtn.addEventListener("click", (e) => {
    e.stopPropagation();

    card.classList.add("copilot-hidden");
    catBubble.textContent = "I'm here 🐾";
});

async function ingestCurrentPage() {
    const page = {
        url: window.location.href,
        title: document.title,
        text: document.body.innerText,
        links: Array.from(document.querySelectorAll("a"))
            .map(a => ({
                text: (a.innerText || "").trim(),
                href: a.href
            }))
            .filter(x => x.href)
    };

    const response = await fetch(
        "http://127.0.0.1:8000/ingest",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(page)
        }
    );

    return await response.json();
}

askBtn.addEventListener("click", async () => {
    const question = questionInput.value.trim();

    if (!question) return;

    // UI while thinking
    output.textContent = "Thinking...";
    sourceBtn.style.display = "none";

    catBubble.textContent = "Thinking... 🐾";
    cat.classList.add("cat-thinking");

    try {
        catBubble.textContent = "Reading page... 🐾";

        await ingestCurrentPage();

        catBubble.textContent = "Thinking... 🐾";
        const response = await fetch("http://127.0.0.1:8000/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question,
                current_url: window.location.href
            })
        });

        const data = await response.json();

        output.textContent = data.answer;
        meow();
        // cat reaction
        cat.classList.remove("cat-thinking");
        cat.classList.add("cat-happy");
        catBubble.textContent = "Found it! 😸";

        setTimeout(() => {
            cat.classList.remove("cat-happy");
        }, 1000);

        // source button
        if (data.source_url) {
            sourceBtn.style.display = "block";

            sourceBtn.onclick = () => {
                const answerText = data.answer.split(".")[0].trim();

                // store highlight text temporarily
                sessionStorage.setItem(
                    "copilot_highlight_text",
                    answerText
                );

                window.location.href = data.source_url;
            };
        }

        // navigation command
        if (data.navigate_url) {
            window.location.href = data.navigate_url;
        }

    } catch (error) {
        console.error(error);

        cat.classList.remove("cat-thinking");
        catBubble.textContent = "Oops 😿";

        output.textContent =
            "Could not connect to the local AI backend.";
    }
});

questionInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        askBtn.click();
    }
});

function meow() {
    const audio = new Audio(
        chrome.runtime.getURL("assets/meow.mp3")
    );

    audio.volume = 0.25;
    audio.play().catch(() => {});
}

window.addEventListener("load", () => {
    const savedText = sessionStorage.getItem(
        "copilot_highlight_text"
    );

    if (!savedText) return;

    sessionStorage.removeItem(
        "copilot_highlight_text"
    );

    setTimeout(() => {
        const words = savedText
            .toLowerCase()
            .split(/\s+/)
            .map(w => w.replace(/[^a-z0-9-]/g, ""))
            .filter(w => w.length > 4)
            .slice(0, 8);

        const elements = [
            ...document.querySelectorAll(
                "p, li, h1, h2, h3, h4, div"
            )
        ];

        let bestElement = null;
        let bestScore = 0;

        for (const el of elements) {
            const content =
                (el.innerText || "").toLowerCase();

            if (!content || content.length < 20) {
                continue;
            }

            const score = words.filter(
                word => content.includes(word)
            ).length;

            if (score > bestScore) {
                bestScore = score;
                bestElement = el;
            }
        }

        if (bestElement && bestScore >= 2) {
            bestElement.scrollIntoView({
                behavior: "smooth",
                block: "center"
            });

            bestElement.style.setProperty(
                "background-color",
                "#ffeb3b",
                "important"
            );

            bestElement.style.setProperty(
                "outline",
                "5px solid #ff9800",
                "important"
            );

            bestElement.style.setProperty(
                "box-shadow",
                "0 0 18px 8px rgba(255,193,7,0.9)",
                "important"
            );

            bestElement.style.setProperty(
                "padding",
                "10px",
                "important"
            );

            bestElement.style.setProperty(
                "border-radius",
                "8px",
                "important"
            );
        }
    }, 1000);
});