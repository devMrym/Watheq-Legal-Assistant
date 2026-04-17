import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileText, Shield, AlertTriangle, ChevronDown, ChevronUp, RotateCcw } from "lucide-react";
import Navbar from "@/components/Navbar";
import ChatModal from "@/components/ChatModal";
import SimplifyModal from "@/components/SimplifyModal";

type Stage = "upload" | "analyzing" | "results" | "error";
type RiskLevel = "عالية" | "متوسطة" | "منخفضة";

type Issue = {
  id: number;
  title: string;
  riskLevel: RiskLevel;
  reason: string;
  recommendation: string;
  legalReference: string;
  articleText: string;
};

type AnalysisData = {
  contractTitle?: string;
  complianceScore: number;
  summary: { high: number; medium: number; low: number };
  issues: Issue[];
};

const RISK_STYLES: Record<RiskLevel, { badge: string; border: string }> = {
  عالية: {
    badge: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
    border: "border-l-red-400",
  },
  متوسطة: {
    badge: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
    border: "border-l-amber-400",
  },
  منخفضة: {
    badge: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
    border: "border-l-green-400",
  },
};

// --- Helper to handle potentially flipped/broken Arabic text ---
function formatArabicText(text: string) {
  if (!text) return "";
  
  // This helps browsers handle the bidirectional nature of the text
  // even if the character order is slightly mangled by the PDF extractor.
  return text; 
}

function getScoreColor(score: number) {
  if (score >= 70) return "text-green-600";
  if (score >= 40) return "text-amber-500";
  return "text-red-500";
}

function getProgressColor(score: number) {
  if (score >= 70) return "bg-green-500";
  if (score >= 40) return "bg-amber-400";
  return "bg-red-500";
}

function IssueCard({ issue }: { issue: Issue }) {
  const [open, setOpen] = useState(false);
  const styles = RISK_STYLES[issue.riskLevel] ?? RISK_STYLES["منخفضة"];

  return (
    <div
      className={`border border-border rounded-xl bg-card border-l-4 ${styles.border} overflow-hidden`}
      dir="rtl"
    >
      <button
        className="w-full flex items-start justify-between gap-3 p-4 text-right"
        onClick={() => setOpen((v) => !v)}
      >
        <div className="flex items-start gap-3 flex-1 min-w-0">
          <span className={`shrink-0 text-xs px-2.5 py-1 rounded-full font-medium ${styles.badge}`}>
            {issue.riskLevel}
          </span>
          <p className="text-sm font-medium text-foreground leading-snug">
            {issue.title}
          </p>
        </div>
        {open ? (
          <ChevronUp className="shrink-0 w-4 h-4 text-muted-foreground mt-0.5" />
        ) : (
          <ChevronDown className="shrink-0 w-4 h-4 text-muted-foreground mt-0.5" />
        )}
      </button>

      {open && (
        <div className="px-4 pb-4 space-y-3 text-sm border-t border-border pt-3">
          <p className="text-muted-foreground leading-relaxed">{issue.reason}</p>
          <div className="rounded-lg bg-muted/50 p-3 space-y-1">
            <p className="font-medium text-foreground">التوصية</p>
            <p className="text-muted-foreground leading-relaxed">{issue.recommendation}</p>
          </div>
          {issue.legalReference && (
            <p className="text-primary text-xs font-medium">📌 {issue.legalReference}</p>
          )}
          {issue.articleText && (
            <div className="bg-muted rounded-lg p-3 text-xs text-muted-foreground leading-relaxed border-r-2 border-primary/40">
              {issue.articleText}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

const AnalyzerPage = () => {
  const [stage, setStage] = useState<Stage>("upload");
  const [dragOver, setDragOver] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [contractText, setContractText] = useState("");
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);

  const reset = () => {
    setStage("upload");
    setContractText("");
    setAnalysisData(null);
    setErrorMsg("");
  };

  const handleUpload = async (file: File) => {
    if (file.type !== "application/pdf") {
      setErrorMsg("الرجاء رفع ملف PDF فقط.");
      setStage("error");
      return;
    }

    setStage("analyzing");
    setErrorMsg("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch("http://127.0.0.1:8000/upload-contract", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error(`خطأ في الخادم: ${res.status}`);

      const raw = await res.json();
      const text = raw?.data?.question ?? raw?.question ?? "";
      setContractText(text);

      const answerRaw = raw?.data?.answer ?? raw?.answer ?? "";
      const cleaned = answerRaw.replace(/```json|```/g, "").trim();

      let parsed: AnalysisData;
      try {
        parsed = JSON.parse(cleaned);
      } catch {
        throw new Error("لم يتمكن الخادم من إرجاع بيانات صالحة.");
      }

      setAnalysisData(parsed);
      setStage("results");
    } catch (err: any) {
      setErrorMsg(err.message ?? "حدث خطأ غير متوقع.");
      setStage("error");
    }
  };

  const score = analysisData?.complianceScore ?? 0;
  const issues = analysisData?.issues ?? [];
  const summary = analysisData?.summary ?? { high: 0, medium: 0, low: 0 };

  return (
    <div className="min-h-screen bg-background" dir="rtl">
      <Navbar />

      <div className="pt-20 px-4 pb-10">
        <div className="max-w-7xl mx-auto">
          <AnimatePresence mode="wait">
            
            {(stage === "upload" || stage === "error") && (
              <motion.div
                key="upload"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -16 }}
                className="flex flex-col items-center justify-center min-h-[70vh] gap-6"
              >
                <div className="text-center space-y-2">
                  <h1 className="text-3xl font-bold tracking-tight">تحليل العقود القانونية</h1>
                  <p className="text-muted-foreground text-sm">ارفع عقدك بصيغة PDF وسيتم تحليله وفق الأنظمة السعودية</p>
                </div>

                {stage === "error" && errorMsg && (
                  <div className="flex items-center gap-2 bg-destructive/10 border border-destructive/30 text-destructive rounded-xl px-4 py-3 text-sm max-w-md w-full">
                    <AlertTriangle className="w-4 h-4 shrink-0" />
                    <span>{errorMsg}</span>
                  </div>
                )}

                <div
                  onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                  onDragLeave={() => setDragOver(false)}
                  onDrop={(e) => {
                    e.preventDefault();
                    setDragOver(false);
                    const file = e.dataTransfer.files?.[0];
                    if (file) handleUpload(file);
                  }}
                  onClick={() => {
                    const input = document.createElement("input");
                    input.type = "file";
                    input.accept = "application/pdf";
                    input.onchange = (e: any) => {
                      const file = e.target.files?.[0];
                      if (file) handleUpload(file);
                    };
                    input.click();
                  }}
                  className={`w-full max-w-md border-2 border-dashed rounded-2xl p-14 text-center cursor-pointer transition-all duration-200 select-none ${dragOver ? "border-primary bg-primary/5 scale-[1.01]" : "border-border hover:border-primary/50 hover:bg-muted/30"}`}
                >
                  <div className="flex flex-col items-center gap-4">
                    <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center">
                      <Upload className="w-7 h-7 text-primary" />
                    </div>
                    <div className="space-y-1">
                      <p className="font-semibold text-foreground">اسحب الملف هنا أو انقر للاختيار</p>
                      <p className="text-sm text-muted-foreground">يدعم ملفات PDF فقط</p>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {stage === "analyzing" && (
              <motion.div
                key="analyzing"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center justify-center min-h-[70vh] gap-5"
              >
                <div className="relative">
                  <div className="w-16 h-16 rounded-full border-4 border-primary/20 border-t-primary animate-spin" />
                  <FileText className="w-6 h-6 text-primary absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
                </div>
                <div className="text-center space-y-1">
                  <h2 className="font-semibold text-lg">جارٍ تحليل العقد</h2>
                  <p className="text-sm text-muted-foreground">يتم مراجعة البنود وفق الأنظمة السعودية...</p>
                </div>
              </motion.div>
            )}

            {stage === "results" && analysisData && (
              <motion.div
                key="results"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="space-y-5"
              >
                <div className="bg-card border border-border rounded-2xl p-5">
                  <div className="flex flex-wrap items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                        <Shield className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <h2 className="font-bold text-lg leading-tight">{analysisData.contractTitle || "نتائج التحليل"}</h2>
                        <div className="flex items-center gap-2 mt-1 flex-wrap">
                          {summary.high > 0 && <span className="text-xs px-2.5 py-0.5 rounded-full bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 font-medium">عالية: {summary.high}</span>}
                          {summary.medium > 0 && <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 font-medium">متوسطة: {summary.medium}</span>}
                          {summary.low > 0 && <span className="text-xs px-2.5 py-0.5 rounded-full bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 font-medium">منخفضة: {summary.low}</span>}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-5">
                      <div className="text-center">
                        <p className="text-xs text-muted-foreground mb-1">نسبة الامتثال</p>
                        <p className={`text-3xl font-bold ${getScoreColor(score)}`}>{score}%</p>
                        <div className="mt-1.5 h-1.5 w-24 bg-muted rounded-full overflow-hidden">
                          <div className={`h-full rounded-full transition-all duration-700 ${getProgressColor(score)}`} style={{ width: `${score}%` }} />
                        </div>
                      </div>
                      <button onClick={reset} className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors">
                        <RotateCcw className="w-4 h-4" />
                        عقد جديد
                      </button>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
                  {/* --- FIXED CONTRACT TEXT SECTION --- */}
                  <div className="bg-card border border-border rounded-2xl p-5 max-h-[72vh] overflow-y-auto overflow-x-hidden">
                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4 pb-3 border-b border-border">
                      📄 نص العقد الأصلي
                    </p>
                    {/* The fix: direction: rtl and unicodeBidi: plaintext ensures the browser renders the string logically for Arabic */}
                    <pre 
                      className="whitespace-pre-wrap text-sm leading-loose text-foreground font-sans text-right"
                      style={{ 
                        direction: 'rtl', 
                        unicodeBidi: 'plaintext',
                        textAlign: 'right' 
                      }}
                    >
                      {contractText || "لم يُستخرج نص من الملف."}
                    </pre>
                  </div>

                  <div className="max-h-[72vh] overflow-y-auto space-y-3">
                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">
                      ⚖️ التحليل القانوني ({issues.length} بند)
                    </p>
                    {issues.length === 0 ? (
                      <div className="bg-card border border-border rounded-2xl p-10 text-center text-muted-foreground text-sm">
                        لم يتم رصد أي مشاكل قانونية في هذا العقد.
                      </div>
                    ) : (
                      issues.map((issue) => <IssueCard key={issue.id} issue={issue} />)
                    )}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      <ChatModal open={false} onClose={() => {}} prefill="" />
      <SimplifyModal open={false} onClose={() => {}} />
    </div>
  );
};

export default AnalyzerPage;