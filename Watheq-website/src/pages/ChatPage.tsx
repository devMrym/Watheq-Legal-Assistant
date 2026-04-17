import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { Send, Scale, Sparkles, Lightbulb, BookOpen, X } from "lucide-react";
import Navbar from "@/components/Navbar";
import { demoSimplification, type ChatMessage } from "@/data/mockData";
import { sendChat } from "@/api"; // ✅ ADD THIS

const ChatPage = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const [simplifyOpen, setSimplifyOpen] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  const handleSend = async () => {
  if (!input.trim()) return;

  const userMessage = input.trim();
  const newId = messages.length + 1;

  setMessages((prev) => [
    ...prev,
    { id: newId, role: "user", content: userMessage },
  ]);

  setInput("");
  setTyping(true);

  try {
    const res = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: userMessage }),
    });

    const data = await res.json();

    setTyping(false);

    setMessages((prev) => [
      ...prev,
      {
        id: newId + 1,
        role: "assistant",
        content: data.answer || "No response",
      },
    ]);
  } catch (err) {
    setTyping(false);

    setMessages((prev) => [
      ...prev,
      {
        id: newId + 1,
        role: "assistant",
        content: "Error connecting to server.",
      },
    ]);
  }
};

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />

      <div className="flex-1 flex flex-col pt-14 max-w-3xl mx-auto w-full">
        <div className="flex-1 overflow-y-auto px-4 md:px-6 py-6 space-y-5">
          {messages.length === 0 && (
            <div className="text-center py-20">
              <div className="w-14 h-14 rounded-2xl bg-primary/8 flex items-center justify-center mx-auto mb-5">
                <Scale className="w-7 h-7 text-primary" />
              </div>
              <h2 className="font-heading text-xl font-bold mb-2">
                مرحباً بك في واثق
              </h2>
              <p className="text-muted-foreground text-sm">
                اسأل أي سؤال متعلق بالأنظمة والقوانين السعودية
              </p>
            </div>
          )}

          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${
                msg.role === "user" ? "justify-start" : "justify-end"
              }`}
            >
              <div className="max-w-[80%]">
                {msg.role === "assistant" && (
                  <div className="flex items-center gap-2 mb-1.5">
                    <div className="w-6 h-6 rounded-md bg-primary flex items-center justify-center">
                      <Sparkles className="w-3.5 h-3.5 text-primary-foreground" />
                    </div>
                    <span className="text-xs font-medium text-muted-foreground">
                      واثق
                    </span>
                  </div>
                )}

                <div
                  className={`p-4 rounded-2xl text-sm leading-relaxed whitespace-pre-line ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground rounded-tr-sm"
                      : "bg-secondary border border-border rounded-tl-sm"
                  }`}
                >
                  {msg.content}
                </div>

                {msg.citation && (
                  <p className="text-xs text-muted-foreground mt-1.5 flex items-center gap-1">
                    <BookOpen className="w-3 h-3" />
                    {msg.citation}
                  </p>
                )}
              </div>
            </motion.div>
          ))}

          {typing && (
            <div className="flex justify-end">
              <div className="bg-secondary border border-border p-4 rounded-2xl rounded-tl-sm flex gap-1.5 mr-2">
                <span className="w-2 h-2 bg-muted-foreground rounded-full typing-dot-1" />
                <span className="w-2 h-2 bg-muted-foreground rounded-full typing-dot-2" />
                <span className="w-2 h-2 bg-muted-foreground rounded-full typing-dot-3" />
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        <div className="px-4 md:px-6 pb-2">
         
        </div>

        <div className="p-4 md:p-6 border-t border-border">
          <div className="flex gap-3">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="اسأل أي سؤال متعلق بالأنظمة والقوانين السعودية..."
              className="flex-1 bg-secondary rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 border border-border transition-shadow"
            />

            <button
              onClick={handleSend}
              className="w-11 h-11 rounded-xl bg-primary flex items-center justify-center hover:bg-primary/90 transition-colors shrink-0"
            >
              <Send className="w-4 h-4 text-primary-foreground" />
            </button>
          </div>
        </div>
      </div>

      {simplifyOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-foreground/10 backdrop-blur-sm"
            onClick={() => setSimplifyOpen(false)}
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            className="relative z-10 w-full max-w-2xl mx-4 bg-card rounded-2xl shadow-lg border border-border overflow-hidden"
          >
            <div className="flex items-center justify-between p-5 border-b border-border">
              <h3 className="font-heading font-bold text-base flex items-center gap-2">
                <Lightbulb className="w-4 h-4 text-primary" />
                تبسيط النص القانوني
              </h3>

              <button
                onClick={() => setSimplifyOpen(false)}
                className="p-1.5 rounded-lg hover:bg-muted transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-5 space-y-4 max-h-[60vh] overflow-y-auto">
              <div className="p-4 rounded-xl bg-secondary border border-border">
                <p className="text-sm leading-relaxed text-foreground/80">
                  {demoSimplification.original}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-primary/5 border border-primary/10">
                <p className="text-sm leading-relaxed text-foreground/80">
                  {demoSimplification.simplified}
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default ChatPage;