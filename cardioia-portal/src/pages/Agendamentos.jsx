import { useState, useEffect, useReducer } from 'react';
import { listarAgendamentos, criarAgendamento, cancelarAgendamento } from '../services/agendamentosService';
import styles from './Agendamentos.module.css';

// Estado inicial do formulário
const FORM_INICIAL = {
  pacienteNome: '',
  medico: '',
  data: '',
  hora: '',
  tipo: 'Consulta',
};

// Reducer para gerenciar o estado do formulário
function formReducer(state, action) {
  switch (action.type) {
    case 'SET_FIELD':
      return { ...state, [action.field]: action.value };
    case 'RESET':
      return FORM_INICIAL;
    default:
      return state;
  }
}

const MEDICOS = ['Dr. Carlos Silva', 'Dra. Ana Oliveira'];
const TIPOS   = ['Consulta', 'Retorno', 'Exame ECG', 'Ecocardiograma', 'Teste de Esforço'];

export default function Agendamentos() {
  const [agendamentos, setAgendamentos] = useState([]);
  const [loading,      setLoading]      = useState(true);
  const [showForm,     setShowForm]     = useState(false);
  const [salvando,     setSalvando]     = useState(false);
  const [sucesso,      setSucesso]      = useState('');

  const [form, dispatch] = useReducer(formReducer, FORM_INICIAL);

  useEffect(() => {
    listarAgendamentos()
      .then(setAgendamentos)
      .finally(() => setLoading(false));
  }, []);

  function handleChange(field, value) {
    dispatch({ type: 'SET_FIELD', field, value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSalvando(true);
    try {
      const novo = await criarAgendamento(form);
      setAgendamentos(prev => [...prev, novo]);
      dispatch({ type: 'RESET' });
      setShowForm(false);
      setSucesso('Agendamento criado com sucesso!');
      setTimeout(() => setSucesso(''), 3000);
    } finally {
      setSalvando(false);
    }
  }

  async function handleCancelar(id) {
    if (!confirm('Cancelar este agendamento?')) return;
    await cancelarAgendamento(id);
    setAgendamentos(prev => prev.map(a => a.id === id ? { ...a, status: 'cancelado' } : a));
  }

  if (loading) return <div className={styles.loading}>Carregando agendamentos...</div>;

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1>Agendamentos</h1>
        <button className={styles.btnNovo} onClick={() => setShowForm(!showForm)}>
          {showForm ? '✕ Fechar' : '+ Novo Agendamento'}
        </button>
      </header>

      {sucesso && <div className={styles.sucesso} role="status">{sucesso}</div>}

      {/* Formulário de novo agendamento */}
      {showForm && (
        <form onSubmit={handleSubmit} className={styles.form}>
          <h2>Novo Agendamento</h2>
          <div className={styles.formGrid}>
            <div className={styles.field}>
              <label>Nome do Paciente</label>
              <input
                type="text"
                value={form.pacienteNome}
                onChange={e => handleChange('pacienteNome', e.target.value)}
                placeholder="Nome completo"
                required
              />
            </div>
            <div className={styles.field}>
              <label>Médico</label>
              <select value={form.medico} onChange={e => handleChange('medico', e.target.value)} required>
                <option value="">Selecione...</option>
                {MEDICOS.map(m => <option key={m} value={m}>{m}</option>)}
              </select>
            </div>
            <div className={styles.field}>
              <label>Data</label>
              <input
                type="date"
                value={form.data}
                onChange={e => handleChange('data', e.target.value)}
                min={new Date().toISOString().split('T')[0]}
                required
              />
            </div>
            <div className={styles.field}>
              <label>Hora</label>
              <input
                type="time"
                value={form.hora}
                onChange={e => handleChange('hora', e.target.value)}
                required
              />
            </div>
            <div className={styles.field}>
              <label>Tipo</label>
              <select value={form.tipo} onChange={e => handleChange('tipo', e.target.value)}>
                {TIPOS.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
          </div>
          <div className={styles.formActions}>
            <button type="button" className={styles.btnCancelar} onClick={() => { setShowForm(false); dispatch({ type: 'RESET' }); }}>
              Cancelar
            </button>
            <button type="submit" className={styles.btnSalvar} disabled={salvando}>
              {salvando ? 'Salvando...' : 'Salvar Agendamento'}
            </button>
          </div>
        </form>
      )}

      {/* Lista de agendamentos */}
      <div className={styles.lista}>
        {agendamentos.map(a => (
          <div key={a.id} className={`${styles.item} ${styles[a.status]}`}>
            <div className={styles.itemInfo}>
              <strong>{a.pacienteNome}</strong>
              <span>{a.tipo} com {a.medico}</span>
            </div>
            <div className={styles.itemMeta}>
              <span className={styles.dataHora}>📅 {a.data} às {a.hora}</span>
              <span className={`${styles.badge} ${styles['badge_' + a.status]}`}>{a.status}</span>
            </div>
            {a.status !== 'cancelado' && (
              <button
                className={styles.btnCancelarItem}
                onClick={() => handleCancelar(a.id)}
                aria-label={`Cancelar agendamento de ${a.pacienteNome}`}
              >
                ✕
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
