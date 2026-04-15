import { useState, useEffect } from 'react';
import { listarPacientes } from '../services/pacientesService';
import styles from './Pacientes.module.css';

const CORES_RISCO = { baixo: '#2ecc71', moderado: '#f39c12', alto: '#e74c3c' };

export default function Pacientes() {
  const [pacientes, setPacientes] = useState([]);
  const [loading,   setLoading]   = useState(true);
  const [busca,     setBusca]     = useState('');
  const [filtroRisco, setFiltroRisco] = useState('todos');

  useEffect(() => {
    listarPacientes()
      .then(setPacientes)
      .finally(() => setLoading(false));
  }, []);

  const filtrados = pacientes.filter(p => {
    const matchBusca = p.nome.toLowerCase().includes(busca.toLowerCase()) ||
                       p.diagnostico.toLowerCase().includes(busca.toLowerCase());
    const matchRisco = filtroRisco === 'todos' || p.risco === filtroRisco;
    return matchBusca && matchRisco;
  });

  if (loading) return <div className={styles.loading}>Carregando pacientes...</div>;

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1>Pacientes</h1>
        <span className={styles.total}>{filtrados.length} de {pacientes.length}</span>
      </header>

      <div className={styles.filtros}>
        <input
          type="search"
          placeholder="Buscar por nome ou diagnóstico..."
          value={busca}
          onChange={e => setBusca(e.target.value)}
          className={styles.busca}
          aria-label="Buscar pacientes"
        />
        <div className={styles.filtroRisco}>
          {['todos', 'baixo', 'moderado', 'alto'].map(r => (
            <button
              key={r}
              className={`${styles.filtroBtn} ${filtroRisco === r ? styles.ativo : ''}`}
              onClick={() => setFiltroRisco(r)}
              style={filtroRisco === r && r !== 'todos' ? { background: CORES_RISCO[r], borderColor: CORES_RISCO[r] } : {}}
            >
              {r.charAt(0).toUpperCase() + r.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className={styles.tabela}>
        <table>
          <thead>
            <tr>
              <th>Paciente</th>
              <th>Diagnóstico</th>
              <th>Risco</th>
              <th>Última Consulta</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {filtrados.map(p => (
              <tr key={p.id}>
                <td>
                  <div className={styles.pacienteInfo}>
                    <div className={styles.avatar}>{p.nome.charAt(0)}</div>
                    <div>
                      <strong>{p.nome}</strong>
                      <span>{p.email}</span>
                    </div>
                  </div>
                </td>
                <td>{p.diagnostico}</td>
                <td>
                  <span
                    className={styles.riscoBadge}
                    style={{ background: CORES_RISCO[p.risco] + '22', color: CORES_RISCO[p.risco], borderColor: CORES_RISCO[p.risco] }}
                  >
                    {p.risco}
                  </span>
                </td>
                <td>{p.ultimaConsulta}</td>
                <td>
                  <span className={`${styles.statusBadge} ${p.ativo ? styles.ativo : styles.inativo}`}>
                    {p.ativo ? 'Ativo' : 'Inativo'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtrados.length === 0 && (
          <p className={styles.vazio}>Nenhum paciente encontrado.</p>
        )}
      </div>
    </div>
  );
}
