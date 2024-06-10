import urllib.parse

def extract_get_parameters(file_in, file_out):
    # Считываем URL-адреса из файла
    with open(file_in, 'r', encoding='utf-8') as file:
        urls = file.readlines()
    
    # Множество для хранения уникальных GET-параметров
    get_parameters = set()
    
    # Обрабатываем каждый URL
    for url in urls:
        url = url.strip()
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Добавляем параметры в множество
        for param in query_params.keys():
            get_parameters.add(param)
    
    # Записываем GET-параметры в выходной файл
    with open(file_out, 'w', encoding='utf-8') as file:
        for param in sorted(get_parameters):
            file.write(param + '\n')
    
    # Сообщение об успешном сохранении файла
    print(f"Файл '{file_out}' успешно сохранен.")

# Использование функции
extract_get_parameters('links.txt', 'get.txt')