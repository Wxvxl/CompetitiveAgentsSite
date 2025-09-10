import "./globals.css";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <header>
          <h1>Competitive Agents Dashboard</h1>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
