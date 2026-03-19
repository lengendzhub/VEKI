import type { PropsWithChildren } from "react";

interface SectionGridProps {
  columns?: string;
}

export function SectionGrid({ columns = "repeat(auto-fit, minmax(280px, 1fr))", children }: PropsWithChildren<SectionGridProps>) {
  return <section style={{ display: "grid", gap: "1rem", gridTemplateColumns: columns }}>{children}</section>;
}
