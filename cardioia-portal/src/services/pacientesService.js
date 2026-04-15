// Serviço de pacientes — usa JSONPlaceholder como API fake
// e enriquece com dados cardiológicos simulados

const BASE_URL = 'https://jsonplaceholder.typicode.com';

const DIAGNOSTICOS = [
  'Hipertensão Arterial', 'Insuficiência Cardíaca', 'Arritmia',
  'Angina Estável', 'Doença Coronariana', 'Fibrilação Atrial',
  'Cardiomiopatia', 'Infarto Prévio', 'Estenose Aórtica',
];

const RISCOS = ['baixo', 'moderado', 'alto'];

function enriquecerPaciente(user, index) {
  const seed = user.id + index;
  return {
    id:          user.id,
    nome:        user.name,
    email:       user.email,
    telefone:    user.phone,
    cidade:      user.address?.city || 'São Paulo',
    diagnostico: DIAGNOSTICOS[seed % DIAGNOSTICOS.length],
    risco:       RISCOS[seed % RISCOS.length],
    ultimaConsulta: new Date(Date.now() - seed * 86400000 * 3).toLocaleDateString('pt-BR'),
    ativo:       seed % 5 !== 0,
  };
}

export async function listarPacientes() {
  const res = await fetch(`${BASE_URL}/users`);
  if (!res.ok) throw new Error('Erro ao buscar pacientes');
  const users = await res.json();
  return users.map((u, i) => enriquecerPaciente(u, i));
}

export async function buscarPaciente(id) {
  const res = await fetch(`${BASE_URL}/users/${id}`);
  if (!res.ok) throw new Error('Paciente não encontrado');
  const user = await res.json();
  return enriquecerPaciente(user, id);
}
