// ===============================
// NOVA AI — nova.js (UPGRADED & STABLE)
// Simple | ChatGPT-like | No extra layers
// ===============================

require("dotenv").config();

const express = require("express");
const cors = require("cors");
const Groq = require("groq-sdk");

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static("./public"));

// Check API key
if (!process.env.GROQ_API_KEY) {
  console.error("❌ GROQ_API_KEY missing in .env");
  process.exit(1);
}

// Groq client
const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY,
});

// Short memory (RAM only)
const MAX_MEMORY = 6;
let chatMemory = [];

// Home test
app.get("/", (req, res) => {
  res.send("✅ Nova server running");
});

// Get memory for model
function getMemorySlice() {
  return chatMemory.slice(-MAX_MEMORY).map(m => ({
    role: m.role === "ai" ? "assistant" : "user",
    content: m.content
  }));
}

// Chat API
app.post("/api/chat", async (req, res) => {
  try {
    const userMessage = req.body.message?.trim();
    if (!userMessage) {
      return res.json({ answer: "Please send a message." });
    }

    // Save user message
    chatMemory.push({ role: "user", content: userMessage });

const messages = [
  {
    role: "system",
    content: `
You are Nova AI.

Answer exactly like ChatGPT.

Core behavior:
- Give the MOST DIRECT answer first (1–2 lines)
- If the question is simple, STOP after the direct answer
- Do NOT add background, history, or theory unless asked
- Do NOT use headings for simple questions
- Avoid textbook or formal language
- No repetition
- Keep sentences short and natural
- Sound human, confident, and clear

Formatting:
- Use bullet points ONLY when they genuinely help
- No unnecessary sections or titles

Question handling:
- "who / what / when" → short, direct answer
- "why / how / explain" → brief explanation only
- Never over-explain

Behave like ChatGPT, not a tutorial.
    `.trim()
  },

  // short-term memory
  ...getMemorySlice(),

  // current user message
  {
    role: "user",
    content: userMessage
  }
];

const completion = await groq.chat.completions.create({
  model: "llama-3.1-8b-instant",
  messages,

  // Very focused & confident
  temperature: 0.2,

  // Hard cap to stop essays
  max_tokens: 350,

  // Balanced factual output
  top_p: 0.85,

  // Reduce repetition strongly
  frequency_penalty: 0.45,

  // Slight encouragement for fresh phrasing
  presence_penalty: 0.1,
});

    let answer = "No response from AI.";

    if (completion?.choices?.[0]?.message?.content) {
      answer = completion.choices[0].message.content.trim();
    }

    // Save AI reply
    chatMemory.push({ role: "ai", content: answer });

    res.json({ answer });

  } catch (error) {
    console.error("SERVER ERROR:", error.message);
    res.status(500).json({ answer: "Something went wrong. Try again." });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Nova server running at http://localhost:${PORT}`);
});
