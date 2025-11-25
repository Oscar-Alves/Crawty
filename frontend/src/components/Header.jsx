import { Home } from 'lucide-react';
import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-sm backdrop-blur-md bg-opacity-90">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
                <div className="bg-blue-600 p-1.5 rounded-lg">
                    <Home className="text-white" size={20} />
                </div>
                <h1 className="text-xl font-bold text-blue-600 ">Hub<span className="text-gray-900 ">Imóveis</span></h1>
            </Link>
            
            {/* Espaço para menu futuro */}
            <nav className="hidden md:flex gap-6 text-sm font-medium text-gray-600">
                <Link to="/" className="hover:text-blue-600 transition-colors">Início</Link>
                <span className="hover:text-blue-600 cursor-pointer transition-colors">Sobre</span>
            </nav>
        </div>
    </header>
  );
};

export default Header;