import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Thesis Experiment Platform",
  description: "SLM/LLM experiment runner and results dashboard",
};

const navItems = [
  { href: "/", label: "Dashboard" },
  { href: "/experiments", label: "Experiments" },
  { href: "/results", label: "Results" },
  { href: "/infrastructure", label: "Infrastructure" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-zinc-50 text-zinc-900`}>
        <Providers>
          <div className="flex min-h-screen">
            <aside className="w-56 border-r border-zinc-200 bg-white px-4 py-6">
              <h1 className="mb-8 text-xl font-bold">Thesis Platform</h1>
              <nav className="space-y-1">
                {navItems.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="block rounded-md px-3 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-100 hover:text-zinc-900"
                  >
                    {item.label}
                  </Link>
                ))}
              </nav>
            </aside>
            <main className="flex-1 overflow-auto p-8">{children}</main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
