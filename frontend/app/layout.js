import './globals.css'

export const metadata = {
  title: 'Invoice Generator - Topmate',
  description: 'Professional GST-compliant invoice generator',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
