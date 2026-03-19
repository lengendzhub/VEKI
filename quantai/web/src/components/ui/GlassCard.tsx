// web/src/components/ui/GlassCard.tsx
import type { PropsWithChildren } from "react";

interface GlassCardProps {
  className?: string;
}

export function GlassCard({ className = "", children }: PropsWithChildren<GlassCardProps>) {
  return (
    <section
      className={`liquid-glass ${className}`}
      style={{
        padding: "1rem",
        position: "relative",
        overflow: "hidden"
      }}
    >
      <div
        aria-hidden
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: 1,
          background: "linear-gradient(90deg, transparent, rgba(255,255,255,.35), transparent)"
        }}
      />
      {children}
    </section>
  );
}
