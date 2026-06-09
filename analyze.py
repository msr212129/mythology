import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def analyze_and_visualize():
    # 1. Загрузка данных
    try:
        df = pd.read_csv('mythology_data.csv', encoding='utf-8')
    except FileNotFoundError:
        print("Файл mythology_data.csv не найден. Сначала запустите generate_data.py")
        return

    # 2. Группировка богов по функциям
    # Группируем имена богов по функциям
    grouped = df.groupby('функция')['имя_бога'].apply(list).reset_index()
    print("\n--- Группировка богов по функциям ---")
    for index, row in grouped.iterrows():
        print(f"{row['функция'].capitalize()}: {', '.join(row['имя_бога'])}")

    # 3. Расчет «коэффициента совпадения» (насколько функция представлена во всех трёх культурах)
    total_cultures = df['культура'].nunique()
    
    # Считаем, в скольких уникальных культурах представлена каждая функция
    culture_counts = df.groupby('функция')['культура'].nunique().reset_index()
    culture_counts.columns = ['функция', 'количество_культур']
    
    # Коэффициент = количество культур / общее количество культур
    culture_counts['коэффициент_совпадения'] = culture_counts['количество_культур'] / total_cultures
    
    # 4. Формирование таблицы «Топ общечеловеческих архетипов»
    top_archetypes = culture_counts.sort_values(by='коэффициент_совпадения', ascending=False)
    
    print("\n--- Топ общечеловеческих архетипов ---")
    print(top_archetypes[['функция', 'коэффициент_совпадения']])
    
    # Сохраняем статистику
    top_archetypes.to_csv('top_archetypes.csv', index=False, encoding='utf-8')

    # 5. Построение сетевого графа
    G = nx.Graph()

    # Добавляем узлы и рёбра
    # Будем связывать каждую Культуру с Функция, и Функцию с Богом
    
    cultures = df['культура'].unique()
    functions = df['функция'].unique()
    
    # Добавляем узлы с атрибутом типа для раскраски
    for culture in cultures:
        G.add_node(culture.capitalize(), type='culture')
        
    for func in functions:
        G.add_node(func, type='function')
        
    for index, row in df.iterrows():
        god = row['имя_бога']
        G.add_node(god, type='god')
        
        # Связь: Культура -> Бог
        G.add_edge(row['культура'].capitalize(), god)
        # Связь: Бог -> Функция (общая функция)
        G.add_edge(god, row['функция'])

    # Настройки для отрисовки графа
    plt.figure(figsize=(14, 10))
    
    # Определяем цвета для узлов
    color_map = []
    for node in G:
        if G.nodes[node].get('type') == 'culture':
            color_map.append('lightgreen')
        elif G.nodes[node].get('type') == 'function':
            color_map.append('lightcoral')
        else:
            color_map.append('lightblue')
            
    # Используем spring_layout для красивого распределения узлов
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    
    # Рисуем граф
    nx.draw_networkx_nodes(G, pos, node_color=color_map, node_size=2000, alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
    
    # Добавляем подписи
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif', font_weight='bold')
    
    plt.title("Древо богов: Сетевой граф мифологических соответствий", fontsize=16)
    plt.axis('off') # Отключаем оси
    
    # Сохраняем граф как картинку
    plt.tight_layout()
    plt.savefig('mythology_graph.png', format='png', dpi=300)
    print("\nСетевой граф успешно сохранен в файл: mythology_graph.png")
    
if __name__ == "__main__":
    analyze_and_visualize()