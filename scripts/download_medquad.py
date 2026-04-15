#!/usr/bin/env python3
"""
Script para baixar e processar o dataset MedQuAD do Hugging Face.
Filtra questões relacionadas a cardiologia e cria datasets para o projeto CardioIA.

Fonte: MedQuAD - Medical Question Answering Dataset
- 47,457 pares de perguntas e respostas médicas
- Criado a partir de 12 websites do NIH (National Institutes of Health)
- Licença: Creative Commons Attribution 4.0 International (CC BY)
- Referência: Ben Abacha & Demner-Fushman, BMC Bioinformatics, 2019

Hugging Face: https://huggingface.co/datasets/keivalya/MedQuad-MedicalQnADataset
GitHub Original: https://github.com/abachaa/MedQuAD
"""

import os
import csv
import random
from datasets import load_dataset

# Configurações
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
MAX_LINES = 10000

# Palavras-chave para filtrar conteúdo cardiovascular
CARDIO_KEYWORDS = [
    # Doenças cardíacas (português e inglês)
    'heart', 'cardiac', 'cardio', 'cardiovascular', 'coronary',
    'arrhythmia', 'arritmia', 'atrial', 'ventricular',
    'infarction', 'infarto', 'myocardial', 'miocárdio',
    'angina', 'hypertension', 'hipertensão', 'blood pressure', 'pressão arterial',
    'heart failure', 'insuficiência cardíaca', 'cardiomyopathy', 'cardiomiopatia',
    'valve', 'válvula', 'aorta', 'aortic', 'mitral', 'tricuspid',
    'pericarditis', 'pericardite', 'endocarditis', 'endocardite',
    'tachycardia', 'taquicardia', 'bradycardia', 'bradicardia',
    'fibrillation', 'fibrilação', 'flutter', 'palpitation', 'palpitação',
    
    # Sintomas cardíacos
    'chest pain', 'dor no peito', 'dor torácica', 'shortness of breath',
    'falta de ar', 'dispneia', 'dyspnea', 'edema', 'inchaço',
    'fatigue', 'fadiga', 'cansaço', 'dizziness', 'tontura', 'syncope', 'síncope',
    
    # Procedimentos e exames
    'ecg', 'ekg', 'electrocardiogram', 'eletrocardiograma',
    'echocardiogram', 'ecocardiograma', 'angiography', 'angiografia',
    'catheterization', 'cateterismo', 'stent', 'bypass', 'pacemaker', 'marcapasso',
    'defibrillator', 'desfibrilador',
    
    # Fatores de risco
    'cholesterol', 'colesterol', 'atherosclerosis', 'aterosclerose',
    'stroke', 'avc', 'derrame', 'thrombosis', 'trombose', 'embolism', 'embolia',
    'diabetes', 'obesity', 'obesidade', 'smoking', 'tabagismo'
]

# Palavras-chave para classificação de risco
HIGH_RISK_KEYWORDS = [
    'emergency', 'emergência', 'urgent', 'urgente', 'severe', 'severo', 'grave',
    'acute', 'agudo', 'sudden', 'súbito', 'immediate', 'imediato',
    'heart attack', 'ataque cardíaco', 'cardiac arrest', 'parada cardíaca',
    'stroke', 'avc', 'derrame', 'infarction', 'infarto',
    'life-threatening', 'risco de vida', 'fatal', 'death', 'morte',
    'intensive care', 'uti', 'icu', 'hospitalization', 'hospitalização',
    'surgery', 'cirurgia', 'transplant', 'transplante',
    'unstable', 'instável', 'critical', 'crítico',
    'chest pain at rest', 'dor em repouso', 'syncope', 'síncope',
    'severe shortness', 'dispneia severa', 'cyanosis', 'cianose'
]

LOW_RISK_KEYWORDS = [
    'mild', 'leve', 'minor', 'menor', 'routine', 'rotina',
    'prevention', 'prevenção', 'lifestyle', 'estilo de vida',
    'diet', 'dieta', 'exercise', 'exercício', 'check-up',
    'monitoring', 'monitoramento', 'follow-up', 'acompanhamento',
    'asymptomatic', 'assintomático', 'stable', 'estável',
    'occasional', 'ocasional', 'temporary', 'temporário',
    'benign', 'benigno', 'functional', 'funcional'
]


def contains_keywords(text, keywords):
    """Verifica se o texto contém alguma das palavras-chave."""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


def classify_risk(text):
    """Classifica o texto como alto ou baixo risco."""
    text_lower = text.lower()
    
    high_score = sum(1 for kw in HIGH_RISK_KEYWORDS if kw.lower() in text_lower)
    low_score = sum(1 for kw in LOW_RISK_KEYWORDS if kw.lower() in text_lower)
    
    if high_score > low_score:
        return 'alto risco'
    elif low_score > high_score:
        return 'baixo risco'
    else:
        # Se empate, usa heurísticas adicionais
        if any(word in text_lower for word in ['pain', 'dor', 'severe', 'acute']):
            return 'alto risco'
        return 'baixo risco'


def extract_symptoms_from_text(text):
    """Extrai sintomas mencionados no texto."""
    symptom_patterns = {
        'dor no peito': ['chest pain', 'chest discomfort', 'thoracic pain'],
        'falta de ar': ['shortness of breath', 'difficulty breathing', 'dyspnea', 'breathlessness'],
        'palpitações': ['palpitation', 'racing heart', 'heart pounding', 'irregular heartbeat'],
        'tontura': ['dizziness', 'lightheadedness', 'vertigo', 'feeling faint'],
        'cansaço': ['fatigue', 'tiredness', 'exhaustion', 'weakness'],
        'inchaço': ['swelling', 'edema', 'fluid retention'],
        'pressão no peito': ['chest pressure', 'chest tightness', 'squeezing'],
        'náusea': ['nausea', 'feeling sick', 'queasy'],
        'sudorese': ['sweating', 'cold sweat', 'diaphoresis'],
        'desmaio': ['fainting', 'syncope', 'loss of consciousness', 'passing out']
    }
    
    found_symptoms = []
    text_lower = text.lower()
    
    for symptom_pt, patterns_en in symptom_patterns.items():
        if symptom_pt in text_lower or any(p in text_lower for p in patterns_en):
            found_symptoms.append(symptom_pt)
    
    return found_symptoms


def main():
    print("=" * 60)
    print("CardioIA - Download e Processamento do MedQuAD Dataset")
    print("=" * 60)
    print("\nFonte: MedQuAD (Medical Question Answering Dataset)")
    print("- NIH (National Institutes of Health)")
    print("- Licença: CC BY 4.0")
    print("- Referência: Ben Abacha & Demner-Fushman, BMC Bioinformatics, 2019")
    print()
    
    # Criar diretório de saída
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Carregar dataset do Hugging Face
    print("Carregando dataset do Hugging Face...")
    try:
        dataset = load_dataset("keivalya/MedQuad-MedicalQnADataset", split="train")
        print(f"Dataset carregado: {len(dataset)} registros totais")
    except Exception as e:
        print(f"Erro ao carregar dataset: {e}")
        print("\nTentando método alternativo...")
        dataset = load_dataset("lavita/MedQuAD", split="train")
        print(f"Dataset alternativo carregado: {len(dataset)} registros")
    
    # Filtrar conteúdo cardiovascular
    print("\nFiltrando conteúdo relacionado a cardiologia...")
    cardio_data = []
    
    for item in dataset:
        question = item.get('Question', item.get('question', ''))
        answer = item.get('Answer', item.get('answer', ''))
        combined_text = f"{question} {answer}"
        
        if contains_keywords(combined_text, CARDIO_KEYWORDS):
            cardio_data.append({
                'question': question,
                'answer': answer,
                'risk': classify_risk(combined_text),
                'symptoms': extract_symptoms_from_text(combined_text)
            })
    
    print(f"Registros cardiovasculares encontrados: {len(cardio_data)}")
    
    # Limitar a MAX_LINES
    if len(cardio_data) > MAX_LINES:
        cardio_data = random.sample(cardio_data, MAX_LINES)
        print(f"Limitado a {MAX_LINES} registros")
    
    # Criar dataset de risco (dataset_risco_medquad.csv)
    print("\nCriando dataset de classificação de risco...")
    risk_file = os.path.join(OUTPUT_DIR, 'dataset_risco_medquad.csv')
    
    with open(risk_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(['frase', 'situacao', 'fonte'])
        
        for item in cardio_data:
            # Usar a pergunta como frase de sintoma
            frase = item['question'].strip()
            if len(frase) > 20:  # Filtrar frases muito curtas
                writer.writerow([frase, item['risk'], 'MedQuAD-NIH'])
    
    print(f"Arquivo criado: {risk_file}")
    
    # Criar mapa de conhecimento expandido
    print("\nCriando mapa de conhecimento expandido...")
    knowledge_file = os.path.join(OUTPUT_DIR, 'mapa_conhecimento_medquad.csv')
    
    # Mapa de sintomas para doenças baseado no conteúdo
    symptom_disease_map = {}
    
    for item in cardio_data:
        symptoms = item['symptoms']
        answer_lower = item['answer'].lower()
        
        # Identificar doença mencionada na resposta
        diseases = []
        if 'heart attack' in answer_lower or 'myocardial infarction' in answer_lower:
            diseases.append('Infarto')
        if 'heart failure' in answer_lower:
            diseases.append('Insuficiência Cardíaca')
        if 'arrhythmia' in answer_lower or 'irregular heartbeat' in answer_lower:
            diseases.append('Arritmia')
        if 'angina' in answer_lower:
            diseases.append('Angina')
        if 'hypertension' in answer_lower or 'high blood pressure' in answer_lower:
            diseases.append('Hipertensão')
        if 'cardiomyopathy' in answer_lower:
            diseases.append('Cardiomiopatia')
        if 'valve' in answer_lower:
            diseases.append('Doença Valvular')
        if 'coronary' in answer_lower:
            diseases.append('Doença Coronariana')
        
        # Criar combinações de sintomas e doenças
        if len(symptoms) >= 2 and diseases:
            for i in range(len(symptoms)):
                for j in range(i + 1, len(symptoms)):
                    for disease in diseases:
                        key = (symptoms[i], symptoms[j], disease)
                        symptom_disease_map[key] = symptom_disease_map.get(key, 0) + 1
    
    # Escrever mapa de conhecimento
    with open(knowledge_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Sintoma1', 'Sintoma2', 'Doenca_Associada', 'Frequencia', 'Fonte'])
        
        # Ordenar por frequência
        sorted_map = sorted(symptom_disease_map.items(), key=lambda x: x[1], reverse=True)
        
        for (s1, s2, disease), freq in sorted_map[:500]:  # Top 500 combinações
            writer.writerow([s1, s2, disease, freq, 'MedQuAD-NIH'])
    
    print(f"Arquivo criado: {knowledge_file}")
    
    # Criar arquivo de sintomas de pacientes (simulado a partir das perguntas)
    print("\nCriando arquivo de sintomas de pacientes...")
    symptoms_file = os.path.join(OUTPUT_DIR, 'sintomas_pacientes_medquad.txt')
    
    # Selecionar perguntas que parecem relatos de pacientes
    patient_questions = [
        item['question'] for item in cardio_data
        if any(word in item['question'].lower() for word in 
               ['i have', 'i feel', 'i am experiencing', 'my', 'i\'ve been'])
    ][:100]  # Limitar a 100 frases
    
    with open(symptoms_file, 'w', encoding='utf-8') as f:
        for q in patient_questions:
            f.write(q.strip() + '\n')
    
    print(f"Arquivo criado: {symptoms_file}")
    
    # Estatísticas finais
    print("\n" + "=" * 60)
    print("RESUMO DA EXTRAÇÃO")
    print("=" * 60)
    print(f"Total de registros processados: {len(cardio_data)}")
    
    alto_risco = sum(1 for item in cardio_data if item['risk'] == 'alto risco')
    baixo_risco = len(cardio_data) - alto_risco
    print(f"Alto risco: {alto_risco} ({100*alto_risco/len(cardio_data):.1f}%)")
    print(f"Baixo risco: {baixo_risco} ({100*baixo_risco/len(cardio_data):.1f}%)")
    
    print(f"\nArquivos gerados em: {OUTPUT_DIR}")
    print("- dataset_risco_medquad.csv")
    print("- mapa_conhecimento_medquad.csv")
    print("- sintomas_pacientes_medquad.txt")
    
    print("\n" + "=" * 60)
    print("INFORMAÇÕES DE LICENÇA E ATRIBUIÇÃO")
    print("=" * 60)
    print("Dataset: MedQuAD (Medical Question Answering Dataset)")
    print("Fonte: NIH (National Institutes of Health)")
    print("Licença: Creative Commons Attribution 4.0 International (CC BY)")
    print("Referência: Ben Abacha, A., & Demner-Fushman, D. (2019).")
    print("           A Question-Entailment Approach to Question Answering.")
    print("           BMC Bioinformatics, 20(1), 511.")
    print("URL: https://github.com/abachaa/MedQuAD")


if __name__ == '__main__':
    main()
