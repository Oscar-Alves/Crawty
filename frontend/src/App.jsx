import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home';
import DetalhesImovel from './pages/DetalhesImovel';
import Estatisticas from './pages/Estatisticas';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 font-sans selection:bg-blue-100 selection:text-blue-900">
        <Header />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/imovel/:id" element={<DetalhesImovel />} />
          <Route path="/estatisticas" element={<Estatisticas />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;