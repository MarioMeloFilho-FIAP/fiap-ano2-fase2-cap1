import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import styles from './Navbar.module.css';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate('/login');
  }

  return (
    <nav className={styles.navbar}>
      <div className={styles.brand}>
        <span className={styles.heart}>♥</span>
        <span className={styles.brandName}>CardioIA</span>
      </div>

      <ul className={styles.links}>
        <li><Link to="/dashboard">Dashboard</Link></li>
        <li><Link to="/pacientes">Pacientes</Link></li>
        <li><Link to="/agendamentos">Agendamentos</Link></li>
      </ul>

      <div className={styles.user}>
        <span className={styles.userName}>{user?.name}</span>
        <span className={styles.userRole}>{user?.role}</span>
        <button className={styles.logoutBtn} onClick={handleLogout}>Sair</button>
      </div>
    </nav>
  );
}
