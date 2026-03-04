import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Landing from './pages/Landing';
import Funds from './pages/Funds';
import Leasing from './pages/Leasing';
import Settings from './pages/Settings';
import Assets from './pages/Assets';
import ProtectedRoute from './components/ProtectedRoute';
import ChatWidget from './components/ChatWidget';

function App() {
  return (
    <>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<ProtectedRoute><Landing /></ProtectedRoute>} />
        <Route path="/funds" element={<ProtectedRoute><Funds /></ProtectedRoute>} />
        <Route path="/leasing" element={<ProtectedRoute><Leasing /></ProtectedRoute>} />
        <Route path="/assets" element={<ProtectedRoute><Assets /></ProtectedRoute>} />
        <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <ChatWidget />
    </>
  );
}

export default App;
