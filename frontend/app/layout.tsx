import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Film Trivia RAG",
  description: "Domain-specific RAG system for movie questions",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
