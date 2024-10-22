import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import urllib.parse
import os
import logging
import pandas as pd
from datetime import datetime
import time
import threading
import configparser
import webbrowser

# Поддержка Excel
import openpyxl

# Настройка логирования
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(message)s')

# Парсер конфигурации для сохранения настроек пользователя
config = configparser.ConfigParser()
config_file = 'config.ini'

# Функция загрузки настроек пользователя
def load_settings():
    if os.path.exists(config_file):
        config.read(config_file)
        settings = config['Settings']
        language_var.set(settings.get('language', current_language))
        include_values_var.set(settings.getboolean('include_values', False))
        remove_duplicates_var.set(settings.getboolean('remove_duplicates', False))
        output_format_txt_var.set(settings.getboolean('output_txt', True))
        output_format_csv_var.set(settings.getboolean('output_csv', False))
        output_format_xlsx_var.set(settings.getboolean('output_xlsx', False))
        theme_var.set(settings.get('theme', 'darkly'))
        request_type_var.set(settings.get('request_type', 'GET'))
    else:
        pass

def save_settings():
    config['Settings'] = {
        'language': language_var.get(),
        'include_values': include_values_var.get(),
        'remove_duplicates': remove_duplicates_var.get(),
        'output_txt': output_format_txt_var.get(),
        'output_csv': output_format_csv_var.get(),
        'output_xlsx': output_format_xlsx_var.get(),
        'theme': theme_var.get(),
        'request_type': request_type_var.get(),
    }
    with open(config_file, 'w') as configfile:
        config.write(configfile)

# Настройки языков
languages = {
    'ru': {
        'title': "Извлечение GET/POST-параметров",
        'select_input_file': "Выбрать входной файл",
        'input_file_selected': "Выбранный файл:",
        'include_values': "Сохранять значения параметров",
        'remove_duplicates': "Удалять дубликаты параметров",
        'run': "Запустить",
        'language': "Язык",
        'warning': "Предупреждение",
        'input_file_empty': "Пожалуйста, выберите входной файл.",
        'processing_started': "Начало обработки",
        'processing_success': "Обработка завершена успешно",
        'processing_error': "Произошла ошибка",
        'invalid_url': "Некорректный URL",
        'no_params_found': "Параметры не найдены в указанных данных.",
        'success': "Готово",
        'file_saved': "Файлы успешно сохранены в папке 'output'.",
        'input_file_empty_msg': "Входной файл пуст.",
        'select_language': "Выберите язык",
        'result': "Результат",
        'url_column_not_found': "Столбцы с URL не найдены в файле.",
        'unsupported_file_format': "Неподдерживаемый формат файла.",
        'select_output_format': "Выберите формат вывода:",
        'xlsx': "XLSX",
        'theme': "Тема оформления",
        'select_request_type': "Тип параметров для извлечения:",
        'get_parameters': "GET-параметры",
        'post_parameters': "POST-параметры",
        'help': "Помощь",
        'about': "О программе",
        'no_updates': "Обновлений не найдено.",
        'check_updates': "Проверить обновления",
        'processing': "Обработка...",
        'parameters_extracted': "Извлечено параметров: ",
        'urls_processed': "Обработано URL: ",
        'errors_occurred': "Произошли ошибки: ",
        'version': "Версия",
        'author': "Автор",
        'license': "Лицензия",
        'statistics': "Статистика",
    },
    'en': {
        'title': "GET/POST Parameters Extraction",
        'select_input_file': "Select Input File",
        'input_file_selected': "Selected file:",
        'include_values': "Include parameter values",
        'remove_duplicates': "Remove duplicate parameters",
        'run': "Run",
        'language': "Language",
        'warning': "Warning",
        'input_file_empty': "Please select an input file.",
        'processing_started': "Processing started",
        'processing_success': "Processing completed successfully",
        'processing_error': "An error occurred",
        'invalid_url': "Invalid URL",
        'no_params_found': "No parameters found in the provided data.",
        'success': "Success",
        'file_saved': "Files have been saved successfully in 'output' folder.",
        'input_file_empty_msg': "The input file is empty.",
        'select_language': "Select Language",
        'result': "Result",
        'url_column_not_found': "URL columns not found in the file.",
        'unsupported_file_format': "Unsupported file format.",
        'select_output_format': "Select output format:",
        'xlsx': "XLSX",
        'theme': "Theme",
        'select_request_type': "Type of parameters to extract:",
        'get_parameters': "GET parameters",
        'post_parameters': "POST parameters",
        'help': "Help",
        'about': "About",
        'no_updates': "No updates found.",
        'check_updates': "Check for updates",
        'processing': "Processing...",
        'parameters_extracted': "Parameters extracted: ",
        'urls_processed': "URLs processed: ",
        'errors_occurred': "Errors occurred: ",
        'version': "Version",
        'author': "Author",
        'license': "License",
        'statistics': "Statistics",
    }
}

current_language = 'ru'

def translate(key):
    return languages[current_language].get(key, key)

# Создание основного окна приложения
root = tb.Window(themename="darkly")
root.title(translate('title'))
root.geometry("800x600")  # Размер окна
root.minsize(800, 600)
root.resizable(True, True)

input_file_path = None

# Функция выбора входного файла
def select_input_file():
    file_path = filedialog.askopenfilename(title=translate('select_input_file'), filetypes=[("All Supported", "*.*")])
    if file_path:
        global input_file_path
        input_file_path = file_path
        input_file_label.config(text=f"{translate('input_file_selected')} {os.path.basename(file_path)}")

# Функция обработки перетаскивания файлов
def drop(event):
    files = root.tk.splitlist(event.data)
    if files:
        global input_file_path
        input_file_path = files[0]
        input_file_label.config(text=f"{translate('input_file_selected')} {os.path.basename(input_file_path)}")

# Функция запуска извлечения
def run_extraction():
    if not input_file_path:
        messagebox.showwarning(translate('warning'), translate('input_file_empty'))
        return

    include_values = include_values_var.get()
    remove_duplicates = remove_duplicates_var.get()
    output_formats = []
    if output_format_txt_var.get():
        output_formats.append('txt')
    if output_format_csv_var.get():
        output_formats.append('csv')
    if output_format_xlsx_var.get():
        output_formats.append('xlsx')

    if not output_formats:
        messagebox.showwarning(translate('warning'), "Пожалуйста, выберите хотя бы один формат вывода.")
        return

    request_type = request_type_var.get()
    # Запуск извлечения в новом потоке
    threading.Thread(target=extract_parameters, args=(input_file_path, include_values, remove_duplicates, output_formats, request_type)).start()

def extract_parameters(file_in, include_values=False, remove_duplicates=False, output_formats=None, request_type='GET'):
    try:
        logging.info(translate('processing_started'))
        save_settings()
        # Обновление интерфейса
        run_button.config(state='disabled')
        progress['value'] = 0
        progress_label.config(text=translate('processing'))
        error_count = 0

        start_time = time.time()

        # Чтение данных из входного файла
        _, file_extension = os.path.splitext(file_in)
        if file_extension.lower() in ['.txt']:
            with open(file_in, 'r', encoding='utf-8') as file:
                data = [line.strip() for line in file if line.strip()]
        elif file_extension.lower() in ['.csv']:
            df = pd.read_csv(file_in)
            # Собираем все столбцы с URL
            data = []
            for column in df.columns:
                sample_values = df[column].dropna().astype(str).head(10)
                if sample_values.str.contains(r'(http[s]?://|/|\?).+', regex=True).any():
                    data.extend(df[column].dropna().astype(str).tolist())
            if not data:
                messagebox.showerror(translate('processing_error'), translate('url_column_not_found'))
                run_button.config(state='normal')
                return
        elif file_extension.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(file_in)
            # Собираем все столбцы с URL
            data = []
            for column in df.columns:
                sample_values = df[column].dropna().astype(str).head(10)
                if sample_values.str.contains(r'(http[s]?://|/|\?).+', regex=True).any():
                    data.extend(df[column].dropna().astype(str).tolist())
            if not data:
                messagebox.showerror(translate('processing_error'), translate('url_column_not_found'))
                run_button.config(state='normal')
                return
        else:
            messagebox.showerror(translate('processing_error'), translate('unsupported_file_format'))
            run_button.config(state='normal')
            return

        if not data:
            messagebox.showwarning(translate('warning'), translate('input_file_empty_msg'))
            run_button.config(state='normal')
            return

        total_items = len(data)
        progress['maximum'] = total_items
        root.update_idletasks()

        # Хранилище для параметров
        parameters = {}
        parameters_with_values = []
        errors = []
        url_count = 0

        for idx, item in enumerate(data):
            try:
                item = item.strip()
                if not item:
                    continue

                # Обработка GET параметров
                if request_type == 'GET':
                    url = item
                    parsed_url = urllib.parse.urlparse(url)
                    if not parsed_url.scheme:
                        url = 'http://example.com' + url if url.startswith('/') else 'http://example.com/' + url
                        parsed_url = urllib.parse.urlparse(url)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                # Обработка POST параметров (предполагаем, что item - тело запроса)
                else:
                    query_params = urllib.parse.parse_qs(item)

                for param, values in query_params.items():
                    if include_values:
                        parameters_with_values.append({'Parameter': param, 'Value': ', '.join(values)})
                    parameters[param] = parameters.get(param, 0) + 1

                url_count += 1

            except Exception as e:
                errors.append(str(e))
                error_count += 1
                logging.error(f"Error processing item: {item} - {str(e)}")

            # Обновление прогресса
            progress['value'] = idx + 1
            percent = int((idx + 1) / total_items * 100)
            elapsed_time = time.time() - start_time
            estimated_total_time = elapsed_time / (idx + 1) * total_items
            remaining_time = estimated_total_time - elapsed_time
            remaining_time_str = time.strftime("%H:%M:%S", time.gmtime(remaining_time))
            progress_label.config(text=f"{percent}% - {remaining_time_str} осталось")
            root.update_idletasks()

        if not parameters:
            messagebox.showinfo(translate('result'), translate('no_params_found'))
            run_button.config(state='normal')
            return

        # Удаление дубликатов, если необходимо
        if remove_duplicates:
            if include_values:
                parameters_with_values = [dict(t) for t in {tuple(d.items()) for d in parameters_with_values}]

        # Создание папки output, если не существует
        output_folder = os.path.join(os.getcwd(), 'output')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Сохранение результатов в выбранных форматах
        if 'txt' in output_formats:
            output_filename_txt = f"parameters_{timestamp}.txt"
            file_out_txt = os.path.join(output_folder, output_filename_txt)
            with open(file_out_txt, 'w', encoding='utf-8') as file:
                for param in sorted(parameters):
                    if include_values:
                        values = ', '.join(set([item['Value'] for item in parameters_with_values if item['Parameter'] == param]))
                        file.write(f"{param}: {values}\n")
                    else:
                        file.write(param + '\n')

        if 'csv' in output_formats:
            output_filename_csv = f"parameters_{timestamp}.csv"
            file_out_csv = os.path.join(output_folder, output_filename_csv)
            if include_values:
                df_output = pd.DataFrame(parameters_with_values)
                df_output.to_csv(file_out_csv, index=False, encoding='utf-8-sig')
            else:
                df_output = pd.DataFrame({'Parameter': list(parameters.keys())})
                df_output.to_csv(file_out_csv, index=False, encoding='utf-8-sig')

        if 'xlsx' in output_formats:
            output_filename_xlsx = f"parameters_{timestamp}.xlsx"
            file_out_xlsx = os.path.join(output_folder, output_filename_xlsx)
            if include_values:
                df_output = pd.DataFrame(parameters_with_values)
                df_output.to_excel(file_out_xlsx, index=False)
            else:
                df_output = pd.DataFrame({'Parameter': list(parameters.keys())})
                df_output.to_excel(file_out_xlsx, index=False)

        # Показ сообщения об успехе
        messagebox.showinfo(translate('success'), translate('file_saved'))
        logging.info(translate('processing_success'))

        # Обновление статистики
        total_params = len(parameters)
        parameters_extracted_label.config(text=f"{translate('parameters_extracted')} {total_params}")
        urls_processed_label.config(text=f"{translate('urls_processed')} {url_count}")
        errors_occurred_label.config(text=f"{translate('errors_occurred')} {error_count}")

        run_button.config(state='normal')

    except Exception as e:
        messagebox.showerror(translate('processing_error'), f"{translate('processing_error')}: {str(e)}")
        logging.error(f"{translate('processing_error')}: {str(e)}")
        run_button.config(state='normal')

# Функция смены языка
def change_language(*args):
    global current_language
    current_language = language_var.get()
    update_interface_texts()

# Функция смены темы
def change_theme(*args):
    selected_theme = theme_var.get()
    style = tb.Style()
    style.theme_use(selected_theme)

# Функция обновления текстов интерфейса
def update_interface_texts():
    root.title(translate('title'))
    select_input_button.config(text=translate('select_input_file'))
    include_values_check.config(text=translate('include_values'))
    remove_duplicates_check.config(text=translate('remove_duplicates'))
    run_button.config(text=translate('run'))
    language_label.config(text=translate('language'))
    output_format_label.config(text=translate('select_output_format'))
    output_format_txt_check.config(text="TXT")
    output_format_csv_check.config(text="CSV")
    output_format_xlsx_check.config(text=translate('xlsx'))
    theme_label.config(text=translate('theme'))
    request_type_label.config(text=translate('select_request_type'))
    get_radio.config(text=translate('get_parameters'))
    post_radio.config(text=translate('post_parameters'))
    help_button.config(text=translate('help'))
    about_button.config(text=translate('about'))
    parameters_extracted_label.config(text="")
    urls_processed_label.config(text="")
    errors_occurred_label.config(text="")
    stats_label.config(text=translate('statistics'))  # Добавлено обновление текста метки
    if input_file_path:
        input_file_label.config(text=f"{translate('input_file_selected')} {os.path.basename(input_file_path)}")
    else:
        input_file_label.config(text=translate('input_file_selected'))
    # Обновление меню языков
    menu = language_menu['menu']
    menu.delete(0, 'end')
    for code, name in language_options:
        menu.add_radiobutton(label=name, command=tk._setit(language_var, code))
    language_menu.config(text=code_to_display_name[current_language])

    theme_menu['menu'].delete(0, 'end')
    for theme in available_themes:
        theme_menu['menu'].add_radiobutton(label=theme, command=tk._setit(theme_var, theme))

# Функция показа помощи
def show_help():
    messagebox.showinfo(translate('help'), "Ждите в будущих обновлениях!")

# Функция показа информации о программе
def show_about():
    info = f"{translate('version')}: 3.0\n{translate('author')}: xxrxtnxxov\n{translate('license')}: MIT License"
    messagebox.showinfo(translate('about'), info)

# Настройка языковых опций
language_options = [('ru', 'Русский'), ('en', 'English')]
code_to_display_name = dict(language_options)

# Переменная для текущей темы
theme_var = tk.StringVar(value='darkly')
theme_var.trace('w', change_theme)

# Переменная для текущего языка
language_var = tk.StringVar(value=current_language)
language_var.trace('w', change_language)

# Переменная для типа параметров
request_type_var = tk.StringVar(value='GET')

# Создание основных фреймов
main_frame = tb.Frame(root)
main_frame.pack(expand=True, fill='both')

# Фрейм для выбора входного файла
input_frame = tb.Frame(main_frame)
input_frame.pack(pady=10)

select_input_button = tb.Button(input_frame, text=translate('select_input_file'), command=select_input_file)
select_input_button.pack()

input_file_label = tb.Label(input_frame, text=translate('input_file_selected'))
input_file_label.pack()

# Чекбокс для включения значений параметров
include_values_var = tk.BooleanVar()
include_values_check = tb.Checkbutton(main_frame, text=translate('include_values'), variable=include_values_var)
include_values_check.pack(pady=5)

# Чекбокс для удаления дубликатов
remove_duplicates_var = tk.BooleanVar()
remove_duplicates_check = tb.Checkbutton(main_frame, text=translate('remove_duplicates'), variable=remove_duplicates_var)
remove_duplicates_check.pack(pady=5)

# Выбор типа параметров
request_type_label = tb.Label(main_frame, text=translate('select_request_type'))
request_type_label.pack(pady=5)
request_type_frame = tb.Frame(main_frame)
request_type_frame.pack()
get_radio = tb.Radiobutton(request_type_frame, text=translate('get_parameters'), variable=request_type_var, value='GET')
get_radio.pack(side='left', padx=5)
post_radio = tb.Radiobutton(request_type_frame, text=translate('post_parameters'), variable=request_type_var, value='POST')
post_radio.pack(side='left', padx=5)

# Выбор формата вывода
output_format_frame = tb.Frame(main_frame)
output_format_frame.pack(pady=5)
output_format_label = tb.Label(output_format_frame, text=translate('select_output_format'))
output_format_label.pack()

output_format_txt_var = tk.BooleanVar(value=True)
output_format_txt_check = tb.Checkbutton(output_format_frame, text="TXT", variable=output_format_txt_var)
output_format_txt_check.pack(side='left', padx=5)

output_format_csv_var = tk.BooleanVar()
output_format_csv_check = tb.Checkbutton(output_format_frame, text="CSV", variable=output_format_csv_var)
output_format_csv_check.pack(side='left', padx=5)

output_format_xlsx_var = tk.BooleanVar()
output_format_xlsx_check = tb.Checkbutton(output_format_frame, text=translate('xlsx'), variable=output_format_xlsx_var)
output_format_xlsx_check.pack(side='left', padx=5)

# Кнопка запуска
run_button = tb.Button(main_frame, text=translate('run'), width=20, command=run_extraction)
run_button.pack(pady=10)

# Прогресс-бар и метка
progress = tb.Progressbar(main_frame, orient='horizontal', mode='determinate')
progress.pack(pady=5, fill='x')
progress_label = tb.Label(main_frame, text="0%")
progress_label.pack()

# Метка статистики
stats_label = tb.Label(main_frame, text=translate('statistics'))
stats_label.pack(pady=5)

parameters_extracted_label = tb.Label(main_frame, text="")
parameters_extracted_label.pack()
urls_processed_label = tb.Label(main_frame, text="")
urls_processed_label.pack()
errors_occurred_label = tb.Label(main_frame, text="")
errors_occurred_label.pack()

# Выбор языка и темы
options_frame = tb.Frame(main_frame)
options_frame.pack(pady=5)

# Выбор языка
language_frame = tb.Frame(options_frame)
language_frame.pack(side='left', padx=10)
language_label = tb.Label(language_frame, text=translate('language'))
language_label.pack(side='left', padx=5)
language_menu = tb.OptionMenu(language_frame, language_var)
language_menu.pack(side='left')

# Выбор темы
theme_frame = tb.Frame(options_frame)
theme_frame.pack(side='left', padx=10)
theme_label = tb.Label(theme_frame, text=translate('theme'))
theme_label.pack(side='left', padx=5)
available_themes = tb.Style().theme_names()
theme_menu = tb.OptionMenu(theme_frame, theme_var, *available_themes)
theme_menu.pack(side='left')

# Кнопки помощи и информации
help_frame = tb.Frame(main_frame)
help_frame.pack(pady=5)

help_button = tb.Button(help_frame, text=translate('help'), command=show_help)
help_button.pack(side='left', padx=5)

about_button = tb.Button(help_frame, text=translate('about'), command=show_about)
about_button.pack(side='left', padx=5)

# Инициализация меню языков
def init_language_menu():
    menu = language_menu['menu']
    menu.delete(0, 'end')
    for code, name in language_options:
        menu.add_radiobutton(label=name, command=tk._setit(language_var, code))
    language_menu.config(text=code_to_display_name[current_language])

init_language_menu()

# Инициализация меню тем
def init_theme_menu():
    menu = theme_menu['menu']
    menu.delete(0, 'end')
    for theme in available_themes:
        menu.add_radiobutton(label=theme, command=tk._setit(theme_var, theme))

init_theme_menu()

# Поддержка перетаскивания файлов
try:
    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', drop)
except:
    pass  # Перетаскивание не поддерживается на этой платформе

# Загрузка настроек пользователя
load_settings()
update_interface_texts()

# Запуск приложения
root.mainloop()
