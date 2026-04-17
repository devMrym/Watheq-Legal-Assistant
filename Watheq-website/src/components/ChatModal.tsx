import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Send, Scale } from "lucide-react";

interface Props {
  open: boolean;
  onClose: () => void;
  prefill?: string;
}

const ChatModal = ({ open, onClose, prefill = "" }: Props) => {
  const [messages, setMessages] = useState<{ role: "user" | "assistant"; text: string }[]>([]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);

  useEffect(() => {
    if (open && prefill) {
      setInput(prefill);
    }
  }, [open, prefill]);

  const handleSend = () => {
    if (!input.trim()) return;
    const userMsg = input.trim();
    setMessages((prev) => [...prev, { role: "user", text: userMsg }]);
    setInput("");
    setTyping(true);

    setTimeout(() => {
      setTyping(false);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "بناءً على تحليل البند المشار إليه، فإن هذا الشرط يتعارض مع النظام لأن الغرامة الجزائية المحددة بنسبة 50% تعد مبالغاً فيها وفقاً للمادة 263 من نظام المعاملات المدنية. يحق للمحكمة تخفيض هذه الغرامة إلى الحد المعقول. نوصي بتعديل النسبة إلى ما لا يتجاوز 10% من قيمة العقد.",
        },
      ]);
    }, 2000);
  };

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-50 bg-foreground/10 backdrop-blur-sm"
          />
          <motion.div
            initial={{ x: "-100%", opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: "-100%", opacity: 0 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed top-0 right-0 bottom-0 z-50 w-full max-w-md bg-card border-l border-border shadow-lg flex flex-col"
          >
            <div className="flex items-center justify-between p-4 border-b border-border">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
                  <Scale className="w-4 h-4 text-primary-foreground" />
                </div>
                <div>
                  <h3 className="font-heading font-bold text-sm">مساعد واثق</h3>
                  <p className="text-xs text-muted-foreground">مساعدك القانوني الذكي</p>
                </div>
              </div>
              <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-muted transition-colors">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {messages.map((msg, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex ${msg.role === "user" ? "justify-start" : "justify-end"}`}
                >
                  <div
                    className={`max-w-[85%] p-3 rounded-xl text-sm leading-relaxed ${
                      msg.role === "user"
                        ? "bg-primary text-primary-foreground rounded-tr-sm"
                        : "bg-secondary border border-border text-foreground rounded-tl-sm"
                    }`}
                  >
                    {msg.text}
                  </div>
                </motion.div>
              ))}
              {typing && (
                <div className="flex justify-end">
                  <div className="bg-secondary border border-border p-3 rounded-xl rounded-tl-sm flex gap-1.5">
                    <span className="w-2 h-2 bg-muted-foreground rounded-full typing-dot-1" />
                    <span className="w-2 h-2 bg-muted-foreground rounded-full typing-dot-2" />
                    <span className="w-2 h-2 bg-muted-foreground rounded-full typing-dot-3" />
                  </div>
                </div>
              )}
            </div>

            <div className="p-4 border-t border-border">
              <div className="flex gap-2">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSend()}
                  placeholder="اكتب سؤالك هنا..."
                  className="flex-1 bg-secondary rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 border border-border"
                />
                <button
                  onClick={handleSend}
                  className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center hover:bg-primary/90 transition-colors shrink-0"
                >
                  <Send className="w-4 h-4 text-primary-foreground" />
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default ChatModal;
