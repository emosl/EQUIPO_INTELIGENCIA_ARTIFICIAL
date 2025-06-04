import type React from "react";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import MenuBar from "../components/MenuBar";
import { PatientProvider } from "../components/PatientContext";
import { AuthProvider } from "../components/AuthContext";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Dashboard App",
  description: "A modern dashboard application built with Next.js",
  generator: "v0.dev",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          <PatientProvider>
            <MenuBar />
            <main className="page-container">{children}</main>
          </PatientProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
