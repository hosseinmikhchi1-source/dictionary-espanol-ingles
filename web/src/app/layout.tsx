import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Diccionario — English ↔ Spanish Dictionary",
  description: "A bilingual English ↔ Spanish dictionary for learners, translators, and travelers.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
