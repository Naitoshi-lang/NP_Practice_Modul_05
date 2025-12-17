import tkinter as tk
from tkinter import scrolledtext
import requests
import threading

def download_hamlet():
    def download_task():
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, "Загрузка...\n")
        
        try:
            # ID Гамлета на Project Gutenberg
            book_id = "1524"
            url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
            
            response = requests.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            # Показываем первые 5000 символов
            text = response.text[:5000] + "\n\n... (текст сокращен)"
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, text)
            status_label.config(text=f"Загружено: {len(response.text)} символов")
            
        except Exception as e:
            text_area.insert(tk.END, f"Ошибка: {e}")
            status_label.config(text="Ошибка загрузки")
    
    threading.Thread(target=download_task, daemon=True).start()

# Создаем окно
root = tk.Tk()
root.title("Гамлет - Project Gutenberg")
root.geometry("800x600")

# Кнопка загрузки
btn = tk.Button(root, text="Загрузить Гамлета", command=download_hamlet, font=("Arial", 12))
btn.pack(pady=10)

# Текстовое поле
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=30)
text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Статус
status_label = tk.Label(root, text="Готово к загрузке")
status_label.pack()

root.mainloop()
