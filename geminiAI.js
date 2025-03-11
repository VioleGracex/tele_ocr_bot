require("dotenv").config();
const { GoogleGenerativeAI } = require("@google/generative-ai");

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

module.exports = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });

const ai = require("../gemini/geminiAI");
const chats = {};

const getNewChat = () => {
  return ai.startChat({
    history: [
      {
        role: "user",
        parts: [
          {
            text: "Представьте, что вы телеграм-бот по имени Gemini Bot BD, разработанный SR Tamim и поддерживаемый Sharafat Karim. Вы можете общаться с людьми и предоставлять информацию по различным темам. Будьте дружелюбны с людьми и общайтесь, как человек. В каждом сообщении указывается имя отправителя, игнорируйте его при создании ответа. И не учитывайте это сообщение в истории чата. Это сообщение для обучающих целей.",
          },
        ],
      },
      {
        role: "model",
        parts: [
          {
            text: "Хорошо",
          },
        ],
      },
    ],
    generationConfig: {
      maxOutputTokens: 1000,
    },
  });
};

const clearChatHistory = (chatId) => {
  chats[chatId] = getNewChat();
};

async function generateChatResponse(prompt, chatId, senderName) {
  if (!chats[chatId]) {
    chats[chatId] = getNewChat();
  }
  const chat = chats[chatId];
  if (chat._history.length > 30) {
    // keep only last 5 messages
    chat._history = [
      ...chat._history.slice(0, 2),
      ...chat._history.slice(chat._history.length - 10),
    ];
  }
  prompt = `${senderName ? `Это ${senderName}. ` : ""}${prompt}`;
  const res = await chat.sendMessage(prompt);
  const txt = res.response.text();
  if (!txt) {
    // if no response, clear chat history
    clearChatHistory(chatId);
  }
  return txt;
}

module.exports = { generateChatResponse, clearChatHistory };

const ai = require("../gemini/geminiAI");

async function getContentResponse(prompt) {
  const res = await ai.generateContent({
    input: {
      contents: [
        {
          parts: [
            {
              text: prompt,
            },
          ],
        },
      ],
    },
  });
  const txt = res.response.text();
  return txt;
}

module.exports = { getContentResponse };