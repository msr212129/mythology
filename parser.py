import json
import re
from urllib.parse import quote

import pandas as pd
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'ru-RU,ru;q=0.9',
}

CULTURE_SYMBOLS = {
    'греческая': '🏛️',
    'скандинавская': '⚔️',
    'славянская': '🌿',
}

GREEK_URL = 'https://ru.wikipedia.org/wiki/Олимпийские_боги'
NORSE_URL = 'https://ru.wikipedia.org/wiki/Асы'
SLAVIC_URL = 'https://ru.wikipedia.org/wiki/Список_славянских_богов'

OUTPUT_FILENAME = 'parsed_mythology_data.csv'
SITE_DATA_JS = 'mythology_data.js'
SITE_DATA_JSON = 'parsed_mythology_data.json'


def export_for_site(df):
    records = df.to_dict(orient='records')

    with open(SITE_DATA_JSON, 'w', encoding='utf-8') as file:
        json.dump(records, file, ensure_ascii=False, indent=2)

    with open(SITE_DATA_JS, 'w', encoding='utf-8') as file:
        file.write('window.mythologyData = ')
        json.dump(records, file, ensure_ascii=False)
        file.write(';\n')


def clean_text(text):
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\[править[^\]]*\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_name(text):
    text = clean_text(text)
    text = re.sub(r'\s*\([^)]*\)', '', text).strip()
    return text


def truncate(text, max_len=150):
    text = clean_text(text)
    if len(text) <= max_len:
        return text
    cut = text[:max_len].rsplit(' ', 1)[0]
    return f'{cut}...'


def fetch_page(url, session):
    response = session.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')


def find_section(soup, heading):
    for tag in soup.find_all(['h2', 'h3', 'h4']):
        if heading in tag.get_text(strip=True):
            return tag.find_parent('section')
    return None


def find_ul_after_heading(soup, heading):
    for tag in soup.find_all(['h2', 'h3', 'h4']):
        if heading not in tag.get_text(strip=True):
            continue

        for element in tag.find_all_next():
            if element.name in ['h2', 'h3', 'h4'] and element is not tag:
                break
            if element.name == 'ul':
                return element
    return None


def split_name_description(text):
    if ') — ' in text:
        index = text.rfind(') — ')
        return text[: index + 1], text[index + 4 :]

    if ' — ' in text:
        name, description = text.rsplit(' — ', 1)
        return name, description

    return None, None


def is_valid_god_name(name):
    if len(name) > 40:
        return False

    skip_patterns = (
        r'^Бог\b',
        r'^Боги\b',
        r'^Богиня\b',
        r'^Богини\b',
        r'^Верховный\b',
        r'Гельмольда',
        r'Ибн\b',
        r'Вальдемара',
        r'Козьмы',
        r'Эббо',
        r'\bи\b',
    )
    return not any(re.search(pattern, name, re.IGNORECASE) for pattern in skip_patterns)


def make_record(culture, name, description, attributes='Спарсено из Википедии'):
    name = parse_name(name)
    description = truncate(description)
    if not name or not description or len(name) < 2 or not is_valid_god_name(name):
        return None
    return {
        'культура': culture,
        'имя_бога': name,
        'функция': description,
        'атрибуты': attributes,
        'символ': CULTURE_SYMBOLS[culture],
    }


def parse_dash_list(section, culture):
    records = []
    seen = set()

    for item in section.find_all('li'):
        text = clean_text(item.get_text(' ', strip=True))
        name, description = split_name_description(text)
        if not name or not description:
            continue

        name = parse_name(name)
        if not name or name in seen:
            continue

        seen.add(name)
        record = make_record(culture, name, description)
        if record:
            records.append(record)

    return records


def parse_wikitable(section, culture):
    records = []
    seen = set()

    for table in section.find_all('table', class_='wikitable'):
        rows = table.find_all('tr')
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue

            name = parse_name(cells[0].get_text(' ', strip=True))
            description = clean_text(cells[1].get_text(' ', strip=True))

            if not name or name in seen or name.lower() in ('имя', 'условное обозначение'):
                continue

            seen.add(name)
            record = make_record(culture, name, description)
            if record:
                records.append(record)

    return records


def fetch_wiki_summary(title, session):
    page_title = quote(title.replace(' ', '_'), safe='')
    url = f'https://ru.wikipedia.org/api/rest_v1/page/summary/{page_title}'

    try:
        response = session.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return clean_text(response.json().get('extract', ''))
    except requests.RequestException:
        pass

    return ''


def parse_slavic_names(list_element, session, existing_names):
    records = []

    if not list_element:
        return records

    for item in list_element.find_all('li', recursive=False):
            link = item.find('a', href=re.compile(r'^/wiki/[^:]+$'))
            name = parse_name(link.get_text(' ', strip=True) if link else item.get_text(' ', strip=True))

            if not name or name in existing_names:
                continue

            description = fetch_wiki_summary(name, session)
            if not description:
                description = 'божество славянской мифологии'

            record = make_record('славянская', name, description)
            if record:
                records.append(record)
                existing_names.add(name)

    return records


def parse_greek(session):
    print('Парсим древнегреческих богов...')
    soup = fetch_page(GREEK_URL, session)
    section = find_section(soup, 'Список')
    if not section:
        print('  Предупреждение: раздел «Список» не найден.')
        return []

    records = parse_dash_list(section, 'греческая')
    print(f'  Найдено: {len(records)}')
    return records


def parse_norse(session):
    print('Парсим скандинавских богов...')
    soup = fetch_page(NORSE_URL, session)
    section = find_section(soup, 'Список асов')
    if not section:
        print('  Предупреждение: раздел «Список асов» не найден.')
        return []

    records = parse_dash_list(section, 'скандинавская')
    print(f'  Найдено: {len(records)}')
    return records


def parse_slavic(session):
    print('Парсим славянских богов...')
    soup = fetch_page(SLAVIC_URL, session)
    records = []
    existing_names = set()

    for heading in ('Божества с известными именами',):
        section = find_section(soup, heading)
        if section:
            table_records = parse_wikitable(section, 'славянская')
            for record in table_records:
                if record['имя_бога'] not in existing_names:
                    records.append(record)
                    existing_names.add(record['имя_бога'])

    accepted_list = find_ul_after_heading(soup, 'Общепризнанная божественность')
    if accepted_list:
        name_records = parse_slavic_names(accepted_list, session, existing_names)
        records.extend(name_records)
        print(f'  Из списка общепризнанных божеств: {len(name_records)}')
    else:
        print('  Предупреждение: раздел «Общепризнанная божественность» не найден.')

    print(f'  Всего славянских записей: {len(records)}')
    return records


def parse_wikipedia():
    print('Начинаем парсинг Википедии...')
    data = []

    with requests.Session() as session:
        try:
            data.extend(parse_greek(session))
        except requests.RequestException as error:
            print(f'Ошибка при парсинге греческих богов: {error}')

        try:
            data.extend(parse_norse(session))
        except requests.RequestException as error:
            print(f'Ошибка при парсинге скандинавских богов: {error}')

        try:
            data.extend(parse_slavic(session))
        except requests.RequestException as error:
            print(f'Ошибка при парсинге славянских богов: {error}')

    if not data:
        print('Не удалось получить данные. Проверьте подключение к интернету.')
        return

    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset=['культура', 'имя_бога'])

    df.to_csv(OUTPUT_FILENAME, index=False, encoding='utf-8-sig')
    export_for_site(df)

    print(f'\nУспешно! Спарсено {len(df)} богов.')
    for culture in CULTURE_SYMBOLS:
        count = len(df[df['культура'] == culture])
        print(f'  {culture}: {count}')
    print(f'Сырые данные сохранены в файл: {OUTPUT_FILENAME}')
    print(f'Данные для сайта: {SITE_DATA_JS}, {SITE_DATA_JSON}')


if __name__ == '__main__':
    parse_wikipedia()
