import { Link, useNavigate } from 'react-router-dom';
import './Header.css';

function Header() {
  const navigate = useNavigate();

  const handleLogout = () => {
    navigate('/login');
  };

  return (
    <header className="header">
      <div className="header-left">
        <Link to="/" className="header-logo">
          Fund Admin
        </Link>
      </div>
      <nav className="header-nav">
        <Link to="/" className="header-link">Dashboard</Link>
        <Link to="/" className="header-link">Funds</Link>
        <Link to="/" className="header-link">Reports</Link>
      </nav>
      <div className="header-right">
        <span className="header-user">Admin User</span>
        <button className="header-logout-btn" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </header>
  );
}

export default Header;
