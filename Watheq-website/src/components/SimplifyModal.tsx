import { motion, AnimatePresence } from "framer-motion";
import { X, BookOpen, Lightbulb } from "lucide-react";
import { demoSimplification } from "@/data/mockData";

interface Props {
  open: boolean;
  onClose: () => void;
}

const SimplifyModal = ({ open, onClose }: Props) => {
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
            initial={{ opacity: 0, scale: 0.97, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.97, y: 20 }}
            className="fixed inset-4 md:inset-auto md:top-1/2 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2 z-50 w-auto md:w-full md:max-w-2xl bg-card rounded-2xl shadow-lg border border-border overflow-hidden"
          >
            <div className="flex items-center justify-between p-5 border-b border-border">
              <h3 className="font-heading font-bold text-base flex items-center gap-2">
                <Lightbulb className="w-4 h-4 text-primary" />
                تبسيط النص القانوني
              </h3>
              <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-muted transition-colors">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-5 space-y-4 max-h-[70vh] overflow-y-auto">
              <div className="p-4 rounded-xl bg-secondary border border-border">
                <div className="flex items-center gap-2 mb-2">
                  <BookOpen className="w-4 h-4 text-primary" />
                  <h4 className="font-heading font-bold text-sm text-primary">النص الأصلي</h4>
                </div>
                <p className="text-sm leading-relaxed text-foreground/80">{demoSimplification.original}</p>
              </div>

              <div className="p-4 rounded-xl bg-primary/5 border border-primary/10">
                <div className="flex items-center gap-2 mb-2">
                  <Lightbulb className="w-4 h-4 text-primary" />
                  <h4 className="font-heading font-bold text-sm text-primary">التفسير المبسط</h4>
                </div>
                <p className="text-sm leading-relaxed text-foreground/80">{demoSimplification.simplified}</p>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default SimplifyModal;
