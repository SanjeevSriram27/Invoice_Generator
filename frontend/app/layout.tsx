import './globals.css'

export const metadata = {
  title: 'Invoice Generator - Topmate',
  description: 'GST-compliant invoice generator',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  )
}
