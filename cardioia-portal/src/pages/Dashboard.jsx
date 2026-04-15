import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { listarPacientes } from '../services/pacientesService';
import { listarAgendamentos } from '../services/agendamentosService';
import styles from './Dashboard.module.css';

function MetricCard({ titulo, valor, subtitulo, cor, icone }) {
  return (
    <div className={styles.card} style={{ borderTopColor: cor }}>
      <div className={styles.cardIcon} style={{ color: cor }}>{icone}</div>
      <div className={styles.cardInfo}>
        <span className={styles.cardValor}>{valor}</span>
        <span className={styles.cardTitulo}>{titulo}</span>
        {subtitulo && <span className={styles.cardSub}>{subtitulo}</span>}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { user } = useAuth();
  const [pacientes,     setPacientes]     = useState([]);
  const [agendamentos,  setAgendamentos]  = useState([]);
  const [loading,       setLoading]       = useState(true);

  useEffect(() => {
    Promise.all([listarPacientes(), listarAgendamentos()])
      .then(([p, a]) => { setPacientes(p); setAgendamentos(a); })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className={styles.loading}>Carregando métricas...</div>;

  const totalPacientes   = pacientes.length;
  const pacientesAtivos  = pacientes.filter(p => p.ativo).length;
  const altoRisco        = pacientes.filter(p => p.risco === 'alto').length;
  const consultasHoje    = agendamentos.filter(a => a.data === new Date().toISOString().split('T')[0]).length;
  const pendentes        = agendamentos.filter(a => a.status === 'pendente').length;
  const confirmados      = agendamentos.filter(a => a.status === 'confirmado').length;

  const distribuicaoRisco = ['baixo', 'moderado', 'alto'].map(r => ({
    risco: r,
    qtd: pacientes.filter(p => p.risco === r).length,
    pct: Math.round(100 * pacientes.filter(p => p.risco === r).length / totalPacientes),
  }));

  const coresRisco = { baixo: '#2ecc71', moderado: '#f39c12', alto: '#e74c3c' };

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div>
          <h1>Dashboard</h1>
          <p>Bem-vindo, <strong>{user?.name}</strong></p>
        </div>
        <span className={styles.date}>
          {new Date().toLocaleDateString('pt-BR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
        </span>
      </header>

      {/* Métricas principais */}
      <section className={styles.metrics}>
        <MetricCard titulo="Total de Pacientes"  valor={totalPacientes}  subtitulo={`${pacientesAtivos} ativos`}    cor="#3498db" icone="👥" />
        <MetricCard titulo="Alto Risco"          valor={altoRisco}       subtitulo="requerem atenção"               cor="#e74c3c" icone="⚠️" />
        <MetricCard titulo="Consultas Hoje"      valor={consultasHoje}   subtitulo="agendadas"                      cor="#9b59b6" icone="📅" />
        <MetricCard titulo="Agendamentos"        valor={agendamentos.length} subtitulo={`${pendentes} pendentes`}   cor="#f39c12" icone="🗓️" />
      </section>

      <div className={styles.grid}>
        {/* Distribuição de risco */}
        <section className={styles.section}>
          <h2>Distribuição de Risco</h2>
          <div className={styles.riskList}>
            {distribuicaoRisco.map(({ risco, qtd, pct }) => (
              <div key={risco} className={styles.riskItem}>
                <div className={styles.riskLabel}>
                  <span className={styles.riskDot} style={{ background: coresRisco[risco] }} />
                  <span className={styles.riskName}>{risco.charAt(0).toUpperCase() + risco.slice(1)} Risco</span>
                  <span className={styles.riskQtd}>{qtd} pacientes</span>
                </div>
                <div className={styles.riskBar}>
                  <div className={styles.riskFill} style={{ width: `${pct}%`, background: coresRisco[risco] }} />
                </div>
                <span className={styles.riskPct}>{pct}%</span>
              </div>
            ))}
          </div>
        </section>

        {/* Próximos agendamentos */}
        <section className={styles.section}>
          <h2>Próximos Agendamentos</h2>
          <div className={styles.agendList}>
            {agendamentos.slice(0, 5).map(a => (
              <div key={a.id} className={styles.agendItem}>
                <div className={styles.agendInfo}>
                  <strong>{a.pacienteNome}</strong>
                  <span>{a.tipo} — {a.medico}</span>
                </div>
                <div className={styles.agendMeta}>
                  <span className={styles.agendData}>{a.data} {a.hora}</span>
                  <span className={`${styles.badge} ${styles[a.status]}`}>{a.status}</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* Status dos agendamentos */}
      <section className={styles.section}>
        <h2>Status dos Agendamentos</h2>
        <div className={styles.statusGrid}>
          {[
            { label: 'Confirmados', val: confirmados, cor: '#2ecc71' },
            { label: 'Pendentes',   val: pendentes,   cor: '#f39c12' },
            { label: 'Cancelados',  val: agendamentos.filter(a => a.status === 'cancelado').length, cor: '#e74c3c' },
          ].map(({ label, val, cor }) => (
            <div key={label} className={styles.statusCard} style={{ borderLeftColor: cor }}>
              <span className={styles.statusVal} style={{ color: cor }}>{val}</span>
              <span className={styles.statusLabel}>{label}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
