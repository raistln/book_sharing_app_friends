import { Book } from 'lucide-react';

export function BookPlaceholder() {
  return (
    <div className="w-full h-full bg-gradient-to-br from-storybook-leather to-storybook-leather-dark flex items-center justify-center">
      <Book className="h-24 w-24 text-storybook-gold opacity-50" />
    </div>
  );
}
