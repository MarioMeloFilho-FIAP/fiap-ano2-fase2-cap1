// Serviço de agendamentos — dados simulados localmente

const STORAGE_KEY = 'cardioia_agendamentos';

const AGENDAMENTOS_INICIAIS = [
  { id: 1, pacienteId: 1, pacienteNome: 'Leanne Graham',    medico: 'Dr. Carlos Silva',  data: '2026-04-15', hora: '09:00', tipo: 'Consulta',    status: 'confirmado' },
  { id: 2, pacienteId: 2, pacienteNome: 'Ervin Howell',     medico: 'Dra. Ana Oliveira', data: '2026-04-15', hora: '10:30', tipo: 'Retorno',     status: 'confirmado' },
  { id: 3, pacienteId: 3, pacienteNome: 'Clementine Bauch', medico: 'Dr. Carlos Silva',  data: '2026-04-16', hora: '14:00', tipo: 'Exame ECG',   status: 'pendente'   },
  { id: 4, pacienteId: 4, pacienteNome: 'Patricia Lebsack', medico: 'Dra. Ana Oliveira', data: '2026-04-17', hora: '08:30', tipo: 'Consulta',    status: 'confirmado' },
  { id: 5, pacienteId: 5, pacienteNome: 'Chelsey Dietrich', medico: 'Dr. Carlos Silva',  data: '2026-04-18', hora: '11:00', tipo: 'Ecocardiograma', status: 'pendente' },
];

function getAgendamentos() {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored) return JSON.parse(stored);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(AGENDAMENTOS_INICIAIS));
  return AGENDAMENTOS_INICIAIS;
}

function saveAgendamentos(lista) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(lista));
}

export function listarAgendamentos() {
  return Promise.resolve(getAgendamentos());
}

export function criarAgendamento(dados) {
  const lista = getAgendamentos();
  const novo  = { ...dados, id: Date.now(), status: 'pendente' };
  lista.push(novo);
  saveAgendamentos(lista);
  return Promise.resolve(novo);
}

export function cancelarAgendamento(id) {
  const lista = getAgendamentos().map(a =>
    a.id === id ? { ...a, status: 'cancelado' } : a
  );
  saveAgendamentos(lista);
  return Promise.resolve(true);
}
