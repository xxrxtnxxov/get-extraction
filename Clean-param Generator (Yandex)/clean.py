def create_clean_param(file_in, file_out):
    # Считываем параметры из файла
    with open(file_in, 'r', encoding='utf-8') as file:
        params = [line.strip() for line in file]
    
    # Создаем строки для cleanparam.txt
    lines = []
    current_line = "Clean-param: "
    
    for param in params:
        # Проверяем, вписывается ли новый параметр в текущую строку
        if len(current_line) + len(param) + 1 > 500:  # +1 для символа &
            # Сохраняем текущую строку и начинаем новую
            lines.append(current_line.rstrip('&'))
            current_line = "Clean-param: "
        
        current_line += param + '&'
    
    # Добавляем последнюю строку
    lines.append(current_line.rstrip('&'))
    
    # Записываем строки в выходной файл
    with open(file_out, 'w', encoding='utf-8') as file:
        for line in lines:
            file.write(line + '\n')
    
    print(f"Файл '{file_out}' успешно сохранен.")

# Использование функции
create_clean_param('get.txt', 'cleanparam.txt')