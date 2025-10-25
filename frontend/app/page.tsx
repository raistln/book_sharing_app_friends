import Link from "next/link";
import { Book, Sparkles, Users, Search } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-storybook-parchment via-storybook-cream to-storybook-gold-light">
      {/* Cabecera */}
      <header className="bg-storybook-leather text-storybook-cream shadow-book">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Book className="h-8 w-8 text-storybook-gold" />
              <h1 className="font-display text-2xl font-bold">
                App para Compartir Libros
              </h1>
            </div>
            <nav className="flex gap-4">
              <Link
                href="/login"
                className="px-4 py-2 rounded-lg hover:bg-storybook-leather-dark transition-colors"
              >
                Iniciar sesión
              </Link>
              <Link
                href="/register"
                className="px-4 py-2 bg-storybook-gold text-storybook-ink rounded-lg hover:bg-storybook-gold-light transition-colors font-semibold"
              >
                Registrarse
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Sección hero */}
      <section className="container mx-auto px-4 py-20">
        <div className="text-center space-y-8 animate-fade-in-up">
          <div className="inline-block">
            <Sparkles className="h-16 w-16 text-storybook-gold animate-float mx-auto mb-4" />
          </div>
          <h2 className="font-display text-5xl md:text-6xl font-bold text-storybook-leather">
            Comparte la magia de la lectura
          </h2>
          <p className="text-xl md:text-2xl text-storybook-ink-light max-w-2xl mx-auto">
            Crea tu biblioteca personal, comparte libros con tus amigos y descubre
            nuevas historias en nuestra comunidad lectora.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
            <Link
              href="/register"
              className="px-8 py-4 bg-storybook-leather text-storybook-cream rounded-lg font-display font-semibold text-lg hover:bg-storybook-leather-dark hover:shadow-magical transition-all duration-300 flex items-center justify-center gap-2"
            >
              <Sparkles className="h-5 w-5" />
              Comienza tu aventura
            </Link>
            <Link
              href="/login"
              className="px-8 py-4 border-2 border-storybook-leather text-storybook-leather rounded-lg font-display font-semibold text-lg hover:bg-storybook-parchment transition-all duration-300"
            >
              Ya tengo cuenta
            </Link>
          </div>
        </div>
      </section>

      {/* Sección de características */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-3 gap-8">
          {/* Feature 1 */}
          <div className="bg-storybook-cream rounded-lg p-8 shadow-book hover:shadow-book-hover transition-all duration-300 border border-storybook-gold/20">
            <div className="bg-storybook-gold/20 rounded-full w-16 h-16 flex items-center justify-center mb-4">
              <Book className="h-8 w-8 text-storybook-leather" />
            </div>
            <h3 className="font-display text-2xl font-bold text-storybook-leather mb-3">
              Tu biblioteca
            </h3>
            <p className="text-storybook-ink-light">
              Organiza y gestiona tu colección personal de libros con facilidad.
              Añade títulos, sigue tus lecturas y compártelas con tus amistades.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="bg-storybook-cream rounded-lg p-8 shadow-book hover:shadow-book-hover transition-all duration-300 border border-storybook-gold/20">
            <div className="bg-storybook-gold/20 rounded-full w-16 h-16 flex items-center justify-center mb-4">
              <Users className="h-8 w-8 text-storybook-leather" />
            </div>
            <h3 className="font-display text-2xl font-bold text-storybook-leather mb-3">
              Comunidad
            </h3>
            <p className="text-storybook-ink-light">
              Conecta con otras personas lectoras, únete a grupos y comparte tu amor
              por los libros en una comunidad vibrante.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="bg-storybook-cream rounded-lg p-8 shadow-book hover:shadow-book-hover transition-all duration-300 border border-storybook-gold/20">
            <div className="bg-storybook-gold/20 rounded-full w-16 h-16 flex items-center justify-center mb-4">
              <Search className="h-8 w-8 text-storybook-leather" />
            </div>
            <h3 className="font-display text-2xl font-bold text-storybook-leather mb-3">
              Descubre
            </h3>
            <p className="text-storybook-ink-light">
              Encuentra tu próxima gran lectura con nuestra búsqueda avanzada y
              recomendaciones personalizadas.
            </p>
          </div>
        </div>
      </section>

      {/* Pie de página */}
      <footer className="bg-storybook-leather text-storybook-cream mt-20">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <p className="font-script text-xl mb-2">
              «Una habitación sin libros es como un cuerpo sin alma»
            </p>
            <p className="text-storybook-gold-light text-sm">
              - Marco Tulio Cicerón
            </p>
            <div className="mt-6 text-storybook-ink-light">
              <p>&copy; 2025 App para Compartir Libros. Hecho con ❤️ para amantes de la lectura.</p>
            </div>
          </div>
        </div>
      </footer>
    </main>
  );
}
