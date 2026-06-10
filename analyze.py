import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

PARSED_DATA_FILE = 'parsed_mythology_data.csv'
FALLBACK_DATA_FILE = 'mythology_data.csv'
GRAPH_FILE = 'mythology_graph.png'


def load_data():
    for filename, encoding in (
        (PARSED_DATA_FILE, 'utf-8-sig'),
        (FALLBACK_DATA_FILE, 'utf-8'),
    ):
        try:
            df = pd.read_csv(filename, encoding=encoding)
            print(f'Загружен файл: {filename} ({len(df)} записей)')
            return df, filename
        except FileNotFoundError:
            continue

    print('Файлы данных не найдены. Сначала запустите parser.py или generate_data.py')
    return None, None


def analyze_and_visualize():
    df, source_file = load_data()
    if df is None:
        return

    grouped = df.groupby('культура')['имя_бога'].apply(list).reset_index()
    print('\n--- Боги по культурам ---')
    for _, row in grouped.iterrows():
        print(f"{row['культура'].capitalize()}: {', '.join(row['имя_бога'])}")

    culture_stats = df['культура'].value_counts().reset_index()
    culture_stats.columns = ['культура', 'количество_богов']
    culture_stats.to_csv('top_archetypes.csv', index=False, encoding='utf-8')

    print('\n--- Статистика по культурам ---')
    print(culture_stats)

    G = nx.Graph()

    for _, row in df.iterrows():
        culture = row['культура'].capitalize()
        god = row['имя_бога']

        G.add_node(culture, type='culture')
        G.add_node(god, type='god')
        G.add_edge(culture, god)

    plt.figure(figsize=(16, 12))

    color_map = []
    for node in G:
        if G.nodes[node].get('type') == 'culture':
            color_map.append('#90ee90')
        else:
            color_map.append('#87ceeb')

    pos = nx.spring_layout(G, k=0.9, iterations=80, seed=42)

    nx.draw_networkx_nodes(G, pos, node_color=color_map, node_size=1200, alpha=0.85)
    nx.draw_networkx_edges(G, pos, width=0.8, alpha=0.4)
    nx.draw_networkx_labels(G, pos, font_size=7, font_family='sans-serif')

    title = 'Древо богов: связи культур и божеств'
    if source_file == PARSED_DATA_FILE:
        title += ' (данные Википедии)'

    plt.title(title, fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(GRAPH_FILE, format='png', dpi=300)
    print(f'\nСетевой граф сохранён в файл: {GRAPH_FILE}')


if __name__ == '__main__':
    analyze_and_visualize()
