import { AlertTriangle, CheckCircle2, Info, X } from "lucide-react";
import { useEffect } from "react";

export default function Toast({ toast, onClose }) {
  useEffect(() => {
    if (!toast) return undefined;
    const timer = setTimeout(onClose, 5000);
    return () => clearTimeout(timer);
  }, [toast, onClose]);

  if (!toast) return null;

  const styles = {
    success: {
      icon: CheckCircle2,
      cls: "border-emerald-500/30 bg-emerald-500/10 text-emerald-200",
    },
    error: {
      icon: AlertTriangle,
      cls: "border-rose-500/30 bg-rose-500/10 text-rose-200",
    },
    info: {
      icon: Info,
      cls: "border-indigo-500/30 bg-indigo-500/10 text-indigo-200",
    },
  };
  const meta = styles[toast.type] || styles.info;
  const Icon = meta.icon;

  return (
    <div className="fixed bottom-5 right-5 z-50 max-w-sm animate-fade-in">
      <div
        className={`flex items-start gap-3 rounded-xl border px-4 py-3 text-sm shadow-2xl backdrop-blur-xl ${meta.cls}`}
      >
        <Icon className="mt-0.5 h-4 w-4 shrink-0" />
        <p className="leading-relaxed">{toast.message}</p>
        <button
          onClick={onClose}
          className="ml-2 opacity-60 transition hover:opacity-100"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
