import json
import tkinter as tk
from tkinter import ttk, messagebox

# Caminho para o arquivo JSON com os casos existentes
json_file_path = 'JsonCasos.json'

# Função para carregar os casos existentes do arquivo JSON
def load_cases_from_json():
    try:
        with open(json_file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Função para salvar casos no arquivo JSON
def save_cases_to_json(cases):
    with open(json_file_path, 'w') as file:
        json.dump(cases, file, indent=4)
    # Exibir mensagem de sucesso após salvar o caso
    messagebox.showinfo("Sucesso", "Novo caso salvo com sucesso!")

# Função para comparar dois casos com base em suas características e retornar a porcentagem de similaridade
def compare_cases(case1, case2, weights):
    score = 0
    total_weight = sum(weights.values())
    
    # Comparando atributos
    if case1['DescDoenca'] == case2['DescDoenca']:
        score += weights['DescDoenca']
    if case1['area-damaged'] == case2['area-damaged']:
        score += weights['area-damaged']
    
    # Comparando atributos numéricos
    severity_diff = abs(case1['severity'] - case2['severity'])
    max_severity = 5  # Supondo que a gravidade tenha um valor máximo de 5
    score += weights['severity'] * (1 - severity_diff / max_severity)

    # Retornar porcentagem de similaridade
    return (score / total_weight) * 100

# Função para recuperar os casos com similaridade acima da porcentagem mínima definida pelo usuário
def find_similar_cases(new_case, cases_db, weights, min_similarity):
    similarities = [(case, compare_cases(new_case, case, weights)) for case in cases_db]
    # Filtrar os casos com porcentagem de similaridade acima do limite definido pelo usuário
    return [case for case, similarity in similarities if similarity >= min_similarity]

# Função para adicionar novo caso e exibir solução sugerida
def add_new_case():
    # Coleta os dados do formulário
    new_case = {
        'DescDoenca': combo_desc_doenca.get(),
        'area-damaged': combo_area_damaged.get(),
        'severity': int(combo_severity.get()),
        'solution': 'Solução a ser definida'  # Placeholder para solução
    }
    
    # Adiciona o novo caso na base de dados
    cases_db.append(new_case)
    save_cases_to_json(cases_db)  # Salvar o novo caso no arquivo JSON
    
    # Exibe o novo caso 
    result_label.config(text=f"Novo caso adicionado: {new_case}")
    
    # Define a porcentagem mínima de similaridade escolhida pelo usuário
    min_similarity = similarity_scale.get()
    
    # Encontra os casos semelhantes com base na porcentagem de similaridade
    similar_cases = find_similar_cases(new_case, cases_db, weights, min_similarity)
    
    # Limpa a tabela antes de mostrar os casos recuperados
    for item in tree.get_children():
        tree.delete(item)
    
    # Adiciona os casos recuperados à tabela
    for case in similar_cases:
        similarity = compare_cases(new_case, case, weights)
        tree.insert("", "end", values=(case['DescDoenca'], case['area-damaged'], case['severity'], f"{similarity:.2f}%"))
    
    # Sugere a solução com base no caso mais semelhante
    if similar_cases:
        most_similar_case = similar_cases[0]  # Caso mais semelhante
        suggested_solution.set(f"Solução sugerida: {most_similar_case['solution']}")
    else:
        suggested_solution.set("Nenhuma solução encontrada.")

# Função para visualizar todos os casos salvos no JSON
def view_saved_cases():
    cases = load_cases_from_json()
    
    # Janela para mostrar os casos salvos
    view_window = tk.Toplevel(root)
    view_window.title("Casos Salvos")
    view_window.geometry("600x400")
    
    # Tabela para mostrar casos
    columns = ("DescDoenca", "Area Danificada", "Gravidade", "Solução")
    saved_cases_tree = ttk.Treeview(view_window, columns=columns, show='headings')
    saved_cases_tree.heading("DescDoenca", text="Descrição da Doença")
    saved_cases_tree.heading("Area Danificada", text="Área Danificada")
    saved_cases_tree.heading("Gravidade", text="Gravidade")
    saved_cases_tree.heading("Solução", text="Solução")
    saved_cases_tree.pack(fill="both", expand=True)
    
    # Adicionar os casos à tabela
    for case in cases:
        saved_cases_tree.insert("", "end", values=(case['DescDoenca'], case['area-damaged'], case['severity'], case['solution']))

# Pesos para as comparações
weights = {'DescDoenca': 0.4, 'area-damaged': 0.3, 'severity': 0.3}

# Carregar a base de casos do arquivo JSON
cases_db = load_cases_from_json()

# Inicializa a janela principal
root = tk.Tk()
root.title("Sistema RBC- Tabela De Casos ")
root.geometry("600x600")

# Entrada de novo caso
label_new_case = tk.Label(root, text="Entrada de Novo Caso:")
label_new_case.pack(pady=10)

# Definir opções predefinidas
desc_doenca_options = ['cancro do caule', 'mancha alvo', 'fungo de solo', 'ferrugem asiática']
area_damaged_options = ['espalhado', 'áreas baixas', 'localizada']

# Descrição da doença
tk.Label(root, text="Descrição da Doença:").pack(pady=5)
combo_desc_doenca = ttk.Combobox(root, values=desc_doenca_options)
combo_desc_doenca.pack(pady=5)

# Área danificada
tk.Label(root, text="Área Danificada:").pack(pady=5)
combo_area_damaged = ttk.Combobox(root, values=area_damaged_options)
combo_area_damaged.pack(pady=5)

# Gravidade
tk.Label(root, text="Gravidade (1-5):").pack(pady=5)
severity_options = [1, 2, 3, 4, 5]
combo_severity = ttk.Combobox(root, values=severity_options)
combo_severity.pack(pady=5)

# Escala para escolher a porcentagem mínima de similaridade
tk.Label(root, text="Porcentagem mínima de similaridade:").pack(pady=5)

# Ajuste na escala para evitar sobreposição de números
similarity_scale = tk.Scale(root, from_=0, to=100, orient='horizontal', length=400)  # Aumenta o comprimento da escala
similarity_scale.set(70)  # Define o valor padrão em 70%
similarity_scale.pack(pady=5)

# Botão para adicionar o novo caso
btn_add_case = tk.Button(root, text="Adicionar Caso", command=add_new_case)
btn_add_case.pack(pady=10)

# Botão para visualizar os casos salvos no JSON
btn_view_cases = tk.Button(root, text="Ver Casos Salvos", command=view_saved_cases)
btn_view_cases.pack(pady=10)

# Exibição de resultados após adicionar o novo caso
result_label = tk.Label(root, text="")
result_label.pack(pady=10)

# Tabela para mostrar casos semelhantes recuperados
label_similar_cases = tk.Label(root, text="Casos Semelhantes Recuperados:")
label_similar_cases.pack(pady=10)

# Configurando a tabela
columns = ("DescDoenca", "Area Danificada", "Gravidade", "Similaridade (%)")
tree = ttk.Treeview(root, columns=columns, show='headings')
tree.heading("DescDoenca", text="Descrição da Doença")
tree.heading("Area Danificada", text="Área Danificada")
tree.heading("Gravidade", text="Gravidade")
tree.heading("Similaridade (%)", text="Porcentagem de Similaridade (%)")
tree.pack(pady=10, fill="x")

# Label para mostrar a solução sugerida
suggested_solution = tk.StringVar()
suggestion_label = tk.Label(root, textvariable=suggested_solution, font=("Arial", 12, "bold"))
suggestion_label.pack(pady=10)

# Inicia a interface gráfica
root.mainloop()
