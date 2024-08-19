import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from googletrans import Translator
from langdetect import detect, DetectorFactory
import time
import logging

# برای نتایج پایدار در تشخیص زبان
DetectorFactory.seed = 0

# تنظیمات لاگ
logging.basicConfig(filename='translator.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_srt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return lines

def detect_language(text):
    try:
        lang = detect(text)
        return lang
    except Exception as e:
        messagebox.showerror("Error", f"Language detection failed: {str(e)}")
        return 'en'  # پیش‌فرض به انگلیسی برمی‌گردد در صورت بروز خطا

def translate_subtitles(lines, dest_lang, progress_bar, progress_label):
    translator = Translator()
    translated_lines = []
    src_lang = detect_language(' '.join([line for line in lines if not line.strip().isdigit() and '-->' not in line]))

    max_retries = 3
    retry_delay = 5  # ثانیه
    request_timeout = 10  # ثانیه

    total_lines = len(lines)
    progress_bar['maximum'] = total_lines

    for idx, line in enumerate(lines):
        if line.strip().isdigit() or '-->' in line or line.strip() == '':
            translated_lines.append(line)
        else:
            success = False
            for attempt in range(max_retries):
                try:
                    start_time = time.time()
                    translation = translator.translate(line, src=src_lang, dest=dest_lang, timeout=request_timeout)
                    duration = time.time() - start_time
                    logging.info(f"Translation successful in {duration:.2f} seconds for line: {line.strip()}")
                    translated_lines.append(translation.text + '\n')
                    success = True
                    break
                except Exception as e:
                    logging.error(f"Attempt {attempt+1} failed: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                    else:
                        translated_lines.append(line)
                        logging.error(f"Final attempt failed for line: {line.strip()}")
        # به‌روزرسانی نوار پیشرفت
        progress_bar['value'] = idx + 1
        progress_label.config(text=f'Processing: {idx + 1}/{total_lines} lines')
        root.update_idletasks()
    return translated_lines

def save_srt(file_path, lines):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)

def select_input_file():
    input_file.set(filedialog.askopenfilename(filetypes=[("SRT files", "*.srt")]))

def select_output_path():
    output_file.set(filedialog.asksaveasfilename(defaultextension=".srt", filetypes=[("SRT files", "*.srt")]))

def start_translation():
    if not input_file.get():
        messagebox.showwarning("Warning", "Please select an input file.")
        return
    
    if not output_file.get():
        messagebox.showwarning("Warning", "Please select an output file path.")
        return
    
    dest_lang_code = 'en' if dest_language.get() == 'انگلیسی' else 'fa' if dest_language.get() == 'فارسی' else 'de'
    
    try:
        lines = read_srt(input_file.get())
        translate_subtitles(lines, dest_lang_code, progress_bar, progress_label)
        save_srt(output_file.get(), lines)
        messagebox.showinfo("Success", f"Translation completed successfully and saved to {output_file.get()}.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# رابط کاربری
root = tk.Tk()
root.title("Subtitle Translator")

input_file = tk.StringVar()
output_file = tk.StringVar()
dest_language = tk.StringVar(value='فارسی')

tk.Label(root, text="Select SRT file:").grid(row=0, column=0, padx=10, pady=5)
tk.Entry(root, textvariable=input_file, width=50).grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Browse...", command=select_input_file).grid(row=0, column=2, padx=10, pady=5)

tk.Label(root, text="Output file path:").grid(row=1, column=0, padx=10, pady=5)
tk.Entry(root, textvariable=output_file, width=50).grid(row=1, column=1, padx=10, pady=5)
tk.Button(root, text="Save As...", command=select_output_path).grid(row=1, column=2, padx=10, pady=5)

tk.Label(root, text="Select destination language:").grid(row=2, column=0, padx=10, pady=5)
tk.OptionMenu(root, dest_language, "انگلیسی", "فارسی", "آلمانی").grid(row=2, column=1, padx=10, pady=5)

tk.Button(root, text="Translate", command=start_translation).grid(row=3, column=0, columnspan=3, pady=20)

# نوار پیشرفت و برچسب مربوطه
progress_bar = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate')
progress_bar.grid(row=4, column=0, columnspan=3, padx=10, pady=10)
progress_label = tk.Label(root, text='Processing: 0/0 lines')
progress_label.grid(row=5, column=0, columnspan=3)

root.mainloop()
