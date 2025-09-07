
import "./globals.css";

export const metadata = {
  title: "PayNow + Agent Assist",
  description: "Mini feature frontend for decision + agent trace",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
