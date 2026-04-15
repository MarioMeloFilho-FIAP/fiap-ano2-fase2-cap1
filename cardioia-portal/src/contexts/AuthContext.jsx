import { createContext, useContext, useState, useEffect } from 'react';

// Simula geração de JWT fake
function generateFakeJWT(user) {
  const header  = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const payload = btoa(JSON.stringify({ sub: user.id, name: user.name, role: user.role, iat: Date.now() }));
  const sig     = btoa('fake-signature-cardioia');
  return `${header}.${payload}.${sig}`;
}

const AuthContext = createContext(null);

// Usuários simulados
const USERS = [
  { id: 1, name: 'Dr. Carlos Silva',   email: 'carlos@cardioia.com', password: '123456', role: 'medico' },
  { id: 2, name: 'Dra. Ana Oliveira',  email: 'ana@cardioia.com',    password: '123456', role: 'medico' },
  { id: 3, name: 'Admin CardioIA',     email: 'admin@cardioia.com',  password: 'admin',  role: 'admin'  },
];

export function AuthProvider({ children }) {
  const [user,  setUser]  = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Restaurar sessão do localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem('cardioia_token');
    const storedUser  = localStorage.getItem('cardioia_user');
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  function login(email, password) {
    const found = USERS.find(u => u.email === email && u.password === password);
    if (!found) throw new Error('Credenciais inválidas');

    const { password: _, ...safeUser } = found;
    const jwt = generateFakeJWT(safeUser);

    localStorage.setItem('cardioia_token', jwt);
    localStorage.setItem('cardioia_user',  JSON.stringify(safeUser));
    setToken(jwt);
    setUser(safeUser);
    return safeUser;
  }

  function logout() {
    localStorage.removeItem('cardioia_token');
    localStorage.removeItem('cardioia_user');
    setToken(null);
    setUser(null);
  }

  const isAuthenticated = !!token && !!user;

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth deve ser usado dentro de AuthProvider');
  return ctx;
}
