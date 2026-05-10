import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Assignment Checker | Intelligent Grading System",
  description: "Automate the grading of handwritten student assignments using advanced OCR and Large Language Models. Get accurate extraction and expert evaluation.",
  keywords: ["OCR", "AI Grading", "Assignment Checker", "Handwriting Recognition", "Education Technology"]
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
