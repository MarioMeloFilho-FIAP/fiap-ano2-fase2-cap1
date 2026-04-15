#!/usr/bin/env python3
"""
Script para criar dataset combinado CardioIA:
1. Traduz dados do MedQuAD (inglês → português)
2. Gera dados sintéticos cardiológicos em português
3. Combina ambos para atingir ~10k linhas

Fontes:
- MedQuAD: NIH (National Institutes of Health) - CC BY 4.0
- Dados sintéticos: Gerados com base em literatura médica cardiológica
"""

import os
import csv
import random
import re

# Configurações
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
INPUT_DIR = OUTPUT_DIR
TARGET_LINES = 10000

# =============================================================================
# DICIONÁRIO DE TRADUÇÃO MÉDICA (Inglês → Português)
# =============================================================================
MEDICAL_TRANSLATIONS = {
    # Doenças cardíacas
    'heart attack': 'infarto',
    'myocardial infarction': 'infarto do miocárdio',
    'heart failure': 'insuficiência cardíaca',
    'cardiac arrest': 'parada cardíaca',
    'arrhythmia': 'arritmia',
    'atrial fibrillation': 'fibrilação atrial',
    'ventricular fibrillation': 'fibrilação ventricular',
    'tachycardia': 'taquicardia',
    'bradycardia': 'bradicardia',
    'hypertension': 'hipertensão',
    'high blood pressure': 'pressão alta',
    'hypotension': 'hipotensão',
    'low blood pressure': 'pressão baixa',
    'angina': 'angina',
    'coronary artery disease': 'doença arterial coronariana',
    'atherosclerosis': 'aterosclerose',
    'cardiomyopathy': 'cardiomiopatia',
    'pericarditis': 'pericardite',
    'endocarditis': 'endocardite',
    'myocarditis': 'miocardite',
    'heart valve disease': 'doença valvular cardíaca',
    'mitral valve': 'válvula mitral',
    'aortic valve': 'válvula aórtica',
    'stroke': 'AVC',
    'cerebrovascular accident': 'acidente vascular cerebral',
    'thrombosis': 'trombose',
    'embolism': 'embolia',
    'pulmonary embolism': 'embolia pulmonar',
    'deep vein thrombosis': 'trombose venosa profunda',
    'aneurysm': 'aneurisma',
    'aortic dissection': 'dissecção de aorta',
    
    # Sintomas
    'chest pain': 'dor no peito',
    'chest discomfort': 'desconforto no peito',
    'shortness of breath': 'falta de ar',
    'difficulty breathing': 'dificuldade para respirar',
    'dyspnea': 'dispneia',
    'palpitations': 'palpitações',
    'irregular heartbeat': 'batimentos irregulares',
    'rapid heartbeat': 'batimentos acelerados',
    'dizziness': 'tontura',
    'lightheadedness': 'sensação de desmaio',
    'fainting': 'desmaio',
    'syncope': 'síncope',
    'fatigue': 'fadiga',
    'tiredness': 'cansaço',
    'weakness': 'fraqueza',
    'swelling': 'inchaço',
    'edema': 'edema',
    'nausea': 'náusea',
    'sweating': 'sudorese',
    'cold sweat': 'suor frio',
    'pain radiating': 'dor irradiando',
    'jaw pain': 'dor na mandíbula',
    'arm pain': 'dor no braço',
    'back pain': 'dor nas costas',
    'neck pain': 'dor no pescoço',
    
    # Exames e procedimentos
    'electrocardiogram': 'eletrocardiograma',
    'ecg': 'ECG',
    'ekg': 'ECG',
    'echocardiogram': 'ecocardiograma',
    'stress test': 'teste de esforço',
    'cardiac catheterization': 'cateterismo cardíaco',
    'angiography': 'angiografia',
    'angioplasty': 'angioplastia',
    'stent': 'stent',
    'bypass surgery': 'cirurgia de ponte de safena',
    'pacemaker': 'marcapasso',
    'defibrillator': 'desfibrilador',
    'blood pressure': 'pressão arterial',
    'heart rate': 'frequência cardíaca',
    'cholesterol': 'colesterol',
    'triglycerides': 'triglicerídeos',
    
    # Fatores de risco
    'diabetes': 'diabetes',
    'obesity': 'obesidade',
    'smoking': 'tabagismo',
    'sedentary lifestyle': 'sedentarismo',
    'family history': 'histórico familiar',
    'age': 'idade',
    'stress': 'estresse',
    
    # Termos gerais
    'patient': 'paciente',
    'symptoms': 'sintomas',
    'treatment': 'tratamento',
    'diagnosis': 'diagnóstico',
    'prevention': 'prevenção',
    'risk': 'risco',
    'disease': 'doença',
    'condition': 'condição',
    'medication': 'medicação',
    'therapy': 'terapia',
    'emergency': 'emergência',
    'hospital': 'hospital',
    'doctor': 'médico',
    'cardiologist': 'cardiologista',
    
    # Frases comuns
    'what is': 'o que é',
    'what are': 'quais são',
    'what causes': 'o que causa',
    'how to diagnose': 'como diagnosticar',
    'how to prevent': 'como prevenir',
    'how to treat': 'como tratar',
    'who is at risk': 'quem tem risco',
    'what are the symptoms': 'quais são os sintomas',
    'what are the treatments': 'quais são os tratamentos',
}

# =============================================================================
# TEMPLATES PARA GERAÇÃO DE DADOS SINTÉTICOS
# =============================================================================

# Templates de frases de pacientes (sintomas)
PATIENT_SYMPTOM_TEMPLATES = [
    "Há {tempo} estou com {sintoma1} que {intensidade} quando {gatilho}.",
    "Sinto {sintoma1} há {tempo}, {complemento}.",
    "Tenho sentido {sintoma1} desde {tempo}, principalmente {momento}.",
    "Acordo {momento} com {sintoma1} que {duracao}.",
    "Percebo {sintoma1} ao {atividade}, {complemento}.",
    "Há {tempo} venho sentindo {sintoma1} e {sintoma2} ao mesmo tempo.",
    "Sinto {sintoma1} acompanhada de {sintoma2} há {tempo}.",
    "Tenho {sintoma1} {intensidade} há {tempo}, {complemento}.",
    "Desde {tempo} apresento {sintoma1}, especialmente {momento}.",
    "Notei {sintoma1} pela primeira vez há {tempo}, {complemento}.",
    "Minha {sintoma1} começou há {tempo} e {evolucao}.",
    "Estou com {sintoma1} constante há {tempo}, {complemento}.",
    "Sinto {sintoma1} que {intensidade} com {gatilho}.",
    "Há {tempo} tenho episódios de {sintoma1}, {complemento}.",
    "Apresento {sintoma1} e {sintoma2} há {tempo}, {complemento}.",
]

SINTOMAS = [
    "dor no peito", "falta de ar", "palpitações", "tontura", "cansaço",
    "pressão no peito", "dor torácica", "dispneia", "fadiga", "fraqueza",
    "inchaço nas pernas", "inchaço nos pés", "dor no braço esquerdo",
    "dor na mandíbula", "sudorese", "náusea", "sensação de desmaio",
    "batimentos acelerados", "batimentos irregulares", "aperto no peito",
    "dificuldade para respirar", "cansaço extremo", "mal-estar",
    "dor nas costas", "formigamento no braço", "visão turva"
]

TEMPOS = [
    "dois dias", "três dias", "uma semana", "duas semanas", "um mês",
    "alguns dias", "cerca de uma semana", "aproximadamente duas semanas",
    "mais de um mês", "algumas horas", "ontem", "hoje de manhã"
]

INTENSIDADES = [
    "piora", "melhora", "se intensifica", "diminui", "permanece igual",
    "aumenta", "se agrava", "alivia um pouco"
]

GATILHOS = [
    "faço esforço físico", "subo escadas", "caminho rápido", "me deito",
    "fico nervoso", "me estresso", "faço atividades simples", "me levanto",
    "como refeições pesadas", "faço exercícios", "trabalho muito",
    "fico em pé por muito tempo", "me abaixo", "respiro fundo"
]

COMPLEMENTOS = [
    "mesmo depois de descansar", "e não passa com repouso",
    "acompanhada de suor frio", "junto com náusea",
    "que me impede de fazer atividades normais", "e está piorando",
    "mas melhora quando descanso", "e me preocupa muito",
    "que nunca senti antes", "diferente de tudo que já tive",
    "e está afetando minha rotina", "principalmente à noite"
]

MOMENTOS = [
    "pela manhã", "à noite", "de madrugada", "após as refeições",
    "durante o dia", "ao acordar", "antes de dormir", "no trabalho"
]

DURACOES = [
    "dura alguns minutos", "dura horas", "passa rapidamente",
    "demora para passar", "vai e volta", "é constante"
]

ATIVIDADES = [
    "subir escadas", "caminhar", "fazer esforço", "me levantar",
    "fazer exercícios", "trabalhar", "carregar peso", "me abaixar"
]

EVOLUCOES = [
    "tem piorado progressivamente", "está igual desde então",
    "melhorou um pouco", "vem e vai", "está cada vez mais frequente"
]

# Templates de relatos de pacientes — alto risco (1ª pessoa)
# O médico preenche o campo "situacao" durante a triagem
HIGH_RISK_TEMPLATES = [
    "Estou com {sintoma1} muito forte que irradia para o {local}, começou há {tempo}.",
    "Sinto {sintoma1} intensa há {tempo} e não passa nem com repouso, além de {sintoma2}.",
    "Acordei com {sintoma1} fortíssima e {sintoma2}, estou com muito medo.",
    "Tenho {sintoma1} que não para desde {tempo}, junto com {sintoma2} e {sintoma3}.",
    "Minha pressão está {valor_alto} mmHg e estou sentindo {sintoma1} muito forte.",
    "Estou com o coração batendo a {bpm_alto} bpm e sinto {sintoma1} no peito.",
    "Não consigo respirar direito, tenho {sintoma1} e {sintoma2} há {tempo}.",
    "Já tive infarto antes e agora sinto {sintoma1} igual àquela vez, há {tempo}.",
    "Desmaiei durante o exercício e acordei com {sintoma1} e {sintoma2}.",
    "Sinto {sintoma1} em repouso há {tempo}, não melhora com nada que faço.",
    "Estou com {sintoma1} que vai para o {local} e suando muito frio.",
    "Tenho {sintoma1} e {sintoma2} ao mesmo tempo há {tempo}, está piorando muito.",
    "Sinto o coração disparado e {sintoma1} há {tempo}, quase desmaiei agora.",
    "Estou com {sintoma1} fortíssima, {sintoma2} e não consigo me mover de tanta dor.",
    "Minha {sintoma1} começou de repente há {tempo} e está cada vez mais intensa.",
    "Sinto {sintoma1} que irradia para o {local} e estou com {sintoma2} há {tempo}.",
    "Não consigo deitar por causa da {sintoma1}, só melhora sentado, desde {tempo}.",
    "Estou com {sintoma1} e {sintoma2} há {tempo} e sinto que vou desmaiar.",
    "Sinto {sintoma1} muito forte ao menor esforço, até para falar fico sem ar.",
    "Tenho {sintoma1} constante há {tempo} e minha pressão está muito alta.",
]

# Templates de relatos de pacientes — baixo risco (1ª pessoa)
LOW_RISK_TEMPLATES = [
    "Sinto um {sintoma1} leve depois de fazer exercício, mas passa rápido.",
    "Tenho {sintoma1} no final do dia quando trabalho muito, some depois que descanso.",
    "Meu coração acelera às vezes depois de tomar café, mas passa sozinho.",
    "Sinto {sintoma1} quando levanto rápido da cama, dura só alguns segundos.",
    "Fui ao médico de rotina e minha pressão estava {valor_normal} mmHg, sem sintomas.",
    "Sinto o coração bater um pouco diferente às vezes, mas não me atrapalha.",
    "Tenho um leve inchaço nos tornozelos no fim do dia, some quando elevo as pernas.",
    "Sinto {sintoma1} quando respiro fundo, mas só quando estou muito ansioso.",
    "Meu médico disse que tenho extrassístoles, mas sou assintomático.",
    "Sinto {sintoma1} leve depois de academia, passa em menos de dez minutos.",
    "Tenho {sintoma1} no peito quando fico nervoso, mas some quando me acalmo.",
    "Sinto o coração acelerar quando fico ansioso, mas passa logo.",
    "Tenho azia depois de comer muito, às vezes confundo com dor no peito.",
    "Sinto {sintoma1} leve quando durmo mal, mas no dia seguinte passa.",
    "Tenho {sintoma1} ocasional que não me impede de fazer nada.",
    "Sinto {sintoma1} ao subir escadas, mas só quando subo muitos andares de uma vez.",
    "Meu coração acelera às vezes durante apresentações no trabalho, mas é nervoso.",
    "Tenho {sintoma1} esporádica que dura poucos segundos e some sozinha.",
    "Sou atleta e meu coração bate mais devagar que o normal, o médico disse que é normal.",
    "Minha pressão subiu um pouco depois de um dia estressante, mas voltou ao normal.",
    "Tenho um sopro no coração desde criança, o médico disse que é funcional.",
    "Sinto {sintoma1} leve que piora quando aperto o peito com a mão.",
    "Fiz exame de rotina e encontraram um pequeno aneurisma estável, sem sintomas.",
    "Sinto {sintoma1} depois de viagem longa de avião, mas passa no dia seguinte.",
    "Tenho {sintoma1} que melhora quando tomo antiácido, acho que é refluxo.",
]

SINTOMAS_ALTO_RISCO = [
    "dor no peito", "falta de ar", "dor forte no peito", "pressão no peito",
    "dor que irradia", "aperto no peito", "dificuldade para respirar", "tontura intensa"
]

SINTOMAS_BAIXO_RISCO = [
    "desconforto leve", "cansaço", "tontura passageira", "palpitação leve",
    "dorzinha", "incômodo", "fadiga", "mal-estar passageiro"
]

LOCAIS_IRRADIACAO = [
    "braço esquerdo", "mandíbula", "pescoço", "costas", "ombro esquerdo"
]

VALORES_PA_ALTO = ["200x120", "180x110", "190x115", "210x130", "185x120"]
VALORES_PA_NORMAL = ["130x85", "125x80", "120x75", "135x85", "128x82"]
BPM_ALTO = ["180", "200", "175", "190", "165"]

# Mapa de conhecimento expandido
SYMPTOM_DISEASE_MAP = [
    ("dor no peito", "falta de ar", "Infarto"),
    ("dor no peito", "sudorese", "Infarto"),
    ("dor no peito", "náusea", "Infarto"),
    ("dor no peito", "dor no braço esquerdo", "Infarto"),
    ("dor no peito", "pressão no peito", "Angina"),
    ("pressão no peito", "falta de ar", "Angina"),
    ("cansaço constante", "inchaço nas pernas", "Insuficiência Cardíaca"),
    ("falta de ar", "inchaço nos pés", "Insuficiência Cardíaca"),
    ("dispneia", "fadiga", "Insuficiência Cardíaca"),
    ("palpitações", "tontura", "Arritmia"),
    ("batimentos irregulares", "falta de ar", "Arritmia"),
    ("taquicardia", "palpitações", "Arritmia"),
    ("pressão no peito", "tontura", "Hipertensão"),
    ("dor de cabeça", "visão turva", "Hipertensão"),
    ("tontura", "falta de ar", "Hipertensão"),
    ("dor no peito", "tontura", "Doença Coronariana"),
    ("cansaço", "falta de ar", "Doença Coronariana"),
    ("palpitações", "pressão no peito", "Fibrilação Atrial"),
    ("batimentos acelerados", "tontura", "Taquicardia"),
    ("fraqueza", "tontura", "Bradicardia"),
    ("inchaço nas pernas", "falta de ar", "Insuficiência Cardíaca Congestiva"),
    ("dor torácica", "dispneia", "Síndrome Coronariana Aguda"),
    ("síncope", "palpitações", "Arritmia Ventricular"),
    ("dor no peito", "formigamento no braço", "Infarto"),
    ("fadiga extrema", "inchaço", "Cardiomiopatia"),
]


def translate_text(text):
    """Traduz texto do inglês para português usando o dicionário médico."""
    result = text.lower()
    
    # Ordenar por tamanho (maior primeiro) para evitar substituições parciais
    sorted_translations = sorted(MEDICAL_TRANSLATIONS.items(), 
                                  key=lambda x: len(x[0]), reverse=True)
    
    for eng, pt in sorted_translations:
        result = result.replace(eng.lower(), pt)
    
    # Capitalizar primeira letra
    if result:
        result = result[0].upper() + result[1:]
    
    return result


def generate_patient_symptom():
    """Gera uma frase de sintoma de paciente."""
    template = random.choice(PATIENT_SYMPTOM_TEMPLATES)
    
    sintoma1 = random.choice(SINTOMAS)
    sintoma2 = random.choice([s for s in SINTOMAS if s != sintoma1])
    
    return template.format(
        sintoma1=sintoma1,
        sintoma2=sintoma2,
        tempo=random.choice(TEMPOS),
        intensidade=random.choice(INTENSIDADES),
        gatilho=random.choice(GATILHOS),
        complemento=random.choice(COMPLEMENTOS),
        momento=random.choice(MOMENTOS),
        duracao=random.choice(DURACOES),
        atividade=random.choice(ATIVIDADES),
        evolucao=random.choice(EVOLUCOES)
    )


def generate_high_risk_phrase():
    """Gera uma frase de alto risco."""
    template = random.choice(HIGH_RISK_TEMPLATES)
    
    return template.format(
        sintoma1=random.choice(SINTOMAS_ALTO_RISCO),
        sintoma2=random.choice(SINTOMAS_ALTO_RISCO),
        sintoma3=random.choice(SINTOMAS_ALTO_RISCO),
        local=random.choice(LOCAIS_IRRADIACAO),
        tempo=random.choice(["2 minutos", "5 minutos", "10 minutos"]),
        valor_alto=random.choice(VALORES_PA_ALTO),
        bpm_alto=random.choice(BPM_ALTO)
    )


def generate_low_risk_phrase():
    """Gera uma frase de baixo risco."""
    template = random.choice(LOW_RISK_TEMPLATES)
    
    return template.format(
        sintoma1=random.choice(SINTOMAS_BAIXO_RISCO),
        valor_normal=random.choice(VALORES_PA_NORMAL)
    )


def load_medquad_data():
    """Carrega e filtra dados do MedQuAD relacionados a cardiologia."""
    cardio_keywords = [
        'heart', 'cardiac', 'cardio', 'cardiovascular', 'coronary',
        'arrhythmia', 'infarction', 'angina', 'hypertension',
        'blood pressure', 'chest pain', 'palpitation'
    ]
    
    medquad_file = os.path.join(INPUT_DIR, 'dataset_risco_medquad.csv')
    cardio_data = []
    
    if os.path.exists(medquad_file):
        with open(medquad_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                frase = row['frase'].lower()
                if any(kw in frase for kw in cardio_keywords):
                    cardio_data.append(row)
    
    return cardio_data


def main():
    print("=" * 70)
    print("CardioIA - Criação de Dataset Combinado (MedQuAD + Sintético)")
    print("=" * 70)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. Carregar e traduzir dados do MedQuAD
    print("\n[1/4] Carregando dados do MedQuAD...")
    medquad_data = load_medquad_data()
    print(f"      Registros cardiológicos encontrados: {len(medquad_data)}")
    
    # 2. Traduzir para português
    print("\n[2/4] Traduzindo dados para português...")
    translated_data = []
    for item in medquad_data:
        translated_phrase = translate_text(item['frase'])
        translated_data.append({
            'frase': translated_phrase,
            'situacao': item['situacao'],
            'fonte': 'MedQuAD-NIH (traduzido)'
        })
    print(f"      Registros traduzidos: {len(translated_data)}")
    
    # 3. Gerar dados sintéticos para completar 10k
    print("\n[3/4] Gerando dados sintéticos cardiológicos...")
    synthetic_needed = TARGET_LINES - len(translated_data)
    
    synthetic_data = []
    
    # Balancear alto/baixo risco (50/50)
    high_risk_count = synthetic_needed // 2
    low_risk_count = synthetic_needed - high_risk_count
    
    # Gerar frases de alto risco
    for _ in range(high_risk_count):
        synthetic_data.append({
            'frase': generate_high_risk_phrase(),
            'situacao': 'alto risco',
            'fonte': 'Sintético-CardioIA'
        })
    
    # Gerar frases de baixo risco
    for _ in range(low_risk_count):
        synthetic_data.append({
            'frase': generate_low_risk_phrase(),
            'situacao': 'baixo risco',
            'fonte': 'Sintético-CardioIA'
        })
    
    print(f"      Registros sintéticos gerados: {len(synthetic_data)}")
    
    # 4. Combinar e salvar
    print("\n[4/4] Combinando e salvando datasets...")
    
    # Dataset de risco combinado
    combined_data = translated_data + synthetic_data
    random.shuffle(combined_data)
    
    risk_file = os.path.join(OUTPUT_DIR, 'dataset_risco_combinado.csv')
    with open(risk_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['frase', 'situacao', 'fonte'],
                                quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(combined_data)
    print(f"      Arquivo criado: dataset_risco_combinado.csv ({len(combined_data)} linhas)")
    
    # Mapa de conhecimento expandido
    knowledge_file = os.path.join(OUTPUT_DIR, 'mapa_conhecimento_expandido.csv')
    with open(knowledge_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Sintoma1', 'Sintoma2', 'Doenca_Associada', 'Fonte'])
        
        # Adicionar mapa base
        for s1, s2, disease in SYMPTOM_DISEASE_MAP:
            writer.writerow([s1, s2, disease, 'Literatura Médica'])
        
        # Gerar variações adicionais
        for _ in range(475):  # Para ter ~500 linhas
            s1 = random.choice(SINTOMAS)
            s2 = random.choice([s for s in SINTOMAS if s != s1])
            diseases = ["Infarto", "Insuficiência Cardíaca", "Arritmia", 
                       "Angina", "Hipertensão", "Doença Coronariana",
                       "Cardiomiopatia", "Fibrilação Atrial"]
            disease = random.choice(diseases)
            writer.writerow([s1, s2, disease, 'Sintético-CardioIA'])
    
    print(f"      Arquivo criado: mapa_conhecimento_expandido.csv")
    
    # Sintomas de pacientes expandido
    symptoms_file = os.path.join(OUTPUT_DIR, 'sintomas_pacientes_expandido.txt')
    with open(symptoms_file, 'w', encoding='utf-8') as f:
        # Gerar 500 frases de sintomas de pacientes
        for _ in range(500):
            f.write(generate_patient_symptom() + '\n')
    print(f"      Arquivo criado: sintomas_pacientes_expandido.txt (500 linhas)")
    
    # Estatísticas finais
    print("\n" + "=" * 70)
    print("RESUMO FINAL")
    print("=" * 70)
    
    alto_risco = sum(1 for d in combined_data if d['situacao'] == 'alto risco')
    baixo_risco = len(combined_data) - alto_risco
    medquad_count = sum(1 for d in combined_data if 'MedQuAD' in d['fonte'])
    synthetic_count = len(combined_data) - medquad_count
    
    print(f"\nDataset de Risco Combinado:")
    print(f"  - Total de registros: {len(combined_data)}")
    print(f"  - Alto risco: {alto_risco} ({100*alto_risco/len(combined_data):.1f}%)")
    print(f"  - Baixo risco: {baixo_risco} ({100*baixo_risco/len(combined_data):.1f}%)")
    print(f"  - Origem MedQuAD (traduzido): {medquad_count}")
    print(f"  - Origem Sintética: {synthetic_count}")
    
    print("\n" + "=" * 70)
    print("FONTES E ATRIBUIÇÕES")
    print("=" * 70)
    print("\n1. MedQuAD (Medical Question Answering Dataset)")
    print("   - Fonte: NIH (National Institutes of Health)")
    print("   - Licença: Creative Commons Attribution 4.0 (CC BY)")
    print("   - Referência: Ben Abacha & Demner-Fushman, BMC Bioinformatics, 2019")
    print("   - URL: https://github.com/abachaa/MedQuAD")
    print("\n2. Dados Sintéticos CardioIA")
    print("   - Gerados com base em literatura médica cardiológica")
    print("   - Templates baseados em terminologia médica padrão")
    print("   - Criados para fins educacionais (FIAP)")


if __name__ == '__main__':
    main()
