import Link from "next/link";
import { Book, Sparkles, Users, Search } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-storybook-parchment via-storybook-cream to-storybook-gold-light">
      {/* Header */}
      <header className="bg-storybook-leather text-storybook-cream shadow-book">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Book className="h-8 w-8 text-storybook-gold" />
              <h1 className="font-display text-2xl font-bold">
                Book Sharing App
              </h1>
            </div>
            <nav className="flex gap-4">
              <Link
                href="/login"
                className="px-4 py-2 rounded-lg hover:bg-storybook-leather-dark transition-colors"
              >
                Login
              </Link>
              <Link
                href="/register"
                className="px-4 py-2 bg-storybook-gold text-storybook-ink rounded-lg hover:bg-storybook-gold-light transition-colors font-semibold"
              >
                Register
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="text-center space-y-8 animate-fade-in-up">
          <div className="inline-block">
            <Sparkles className="h-16 w-16 text-storybook-gold animate-float mx-auto mb-4" />
          </div>
          <h2 className="font-display text-5xl md:text-6xl font-bold text-storybook-leather">
            Share the Magic of Reading
          </h2>
          <p className="text-xl md:text-2xl text-storybook-ink-light max-w-2xl mx-auto">
            Build your personal library, share books with friends, and discover
            new stories in our magical reading community.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
            <Link
              href="/register"
              className="px-8 py-4 bg-storybook-leather text-storybook-cream rounded-lg font-display font-semibold text-lg hover:bg-storybook-leather-dark hover:shadow-magical transition-all duration-300 flex items-center justify-center gap-2"
            >
              <Sparkles className="h-5 w-5" />
              Start Your Journey
            </Link>
            <Link
              href="/login"
              className="px-8 py-4 border-2 border-storybook-leather text-storybook-leather rounded-lg font-display font-semibold text-lg hover:bg-storybook-parchment transition-all duration-300"
            >
              I Have an Account
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-3 gap-8">
          {/* Feature 1 */}
          <div className="bg-storybook-cream rounded-lg p-8 shadow-book hover:shadow-book-hover transition-all duration-300 border border-storybook-gold/20">
            <div className="bg-storybook-gold/20 rounded-full w-16 h-16 flex items-center justify-center mb-4">
              <Book className="h-8 w-8 text-storybook-leather" />
            </div>
            <h3 className="font-display text-2xl font-bold text-storybook-leather mb-3">
              Your Library
            </h3>
            <p className="text-storybook-ink-light">
              Organize and manage your personal book collection with ease.
              Add books, track your reading, and share with friends.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="bg-storybook-cream rounded-lg p-8 shadow-book hover:shadow-book-hover transition-all duration-300 border border-storybook-gold/20">
            <div className="bg-storybook-gold/20 rounded-full w-16 h-16 flex items-center justify-center mb-4">
              <Users className="h-8 w-8 text-storybook-leather" />
            </div>
            <h3 className="font-display text-2xl font-bold text-storybook-leather mb-3">
              Community
            </h3>
            <p className="text-storybook-ink-light">
              Connect with fellow readers, join groups, and share your love
              for books in a vibrant community.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="bg-storybook-cream rounded-lg p-8 shadow-book hover:shadow-book-hover transition-all duration-300 border border-storybook-gold/20">
            <div className="bg-storybook-gold/20 rounded-full w-16 h-16 flex items-center justify-center mb-4">
              <Search className="h-8 w-8 text-storybook-leather" />
            </div>
            <h3 className="font-display text-2xl font-bold text-storybook-leather mb-3">
              Discover
            </h3>
            <p className="text-storybook-ink-light">
              Find your next great read with our advanced search and
              personalized recommendations.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-storybook-leather text-storybook-cream mt-20">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <p className="font-script text-xl mb-2">
              "A room without books is like a body without a soul"
            </p>
            <p className="text-storybook-gold-light text-sm">
              - Marcus Tullius Cicero
            </p>
            <div className="mt-6 text-storybook-ink-light">
              <p>&copy; 2025 Book Sharing App. Made with ❤️ for book lovers.</p>
            </div>
          </div>
        </div>
      </footer>
    </main>
  );
}
