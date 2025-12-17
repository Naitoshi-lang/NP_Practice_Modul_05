import tkinter as tk
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup
import urllib.parse
import threading

class SearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Поиск книг")
        self.root.geometry("800x500")
        
        # Поисковая строка
        search_frame = tk.Frame(root)
        search_frame.pack(pady=10)
        
        tk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<Return>', lambda e: self.search_books())
        
        self.search_btn = tk.Button(search_frame, text="Найти", command=self.search_books)
        self.search_btn.pack(side=tk.LEFT, padx=5)
        
        # Таблица результатов
        columns = ("ID", "Название", "Автор")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.column("Название", width=300)
        
        scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Кнопка загрузки
        self.download_btn = tk.Button(root, text="Загрузить выбранную", 
                                      command=self.download_selected, state=tk.DISABLED)
        self.download_btn.pack(pady=5)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
    def search_books(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Внимание", "Введите поисковый запрос")
            return
        
        def search_task():
            self.search_btn.config(state=tk.DISABLED)
            
            # Очищаем таблицу
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            try:
                # Кодируем запрос для URL
                encoded_query = urllib.parse.quote(query)
                url = f"https://www.gutenberg.org/ebooks/search/?query={encoded_query}&submit_search=Search"
                
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Ищем результаты
                results = soup.find_all('li', class_='booklink')
                
                for i, result in enumerate(results[:20]):  # Первые 20 результатов
                    # Извлекаем заголовок
                    title_elem = result.find('span', class_='title')
                    title = title_elem.text.strip() if title_elem else "Без названия"
                    
                    # Извлекаем автора
                    author_elem = result.find('span', class_='subtitle')
                    author = author_elem.text.strip() if author_elem else "Неизвестен"
                    
                    # Извлекаем ID
                    link_elem = result.find('a', href=True)
                    if link_elem:
                        href = link_elem['href']
                        if '/ebooks/' in href:
                            book_id = href.split('/')[-1]
                        else:
                            book_id = "N/A"
                    else:
                        book_id = "N/A"
                    
                    self.tree.insert("", tk.END, values=(book_id, title[:80], author[:50]))
                
                self.search_btn.config(state=tk.NORMAL)
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка поиска: {e}")
                self.search_btn.config(state=tk.NORMAL)
        
        threading.Thread(target=search_task, daemon=True).start()
    
    def on_select(self, event):
        selection = self.tree.selection()
        self.download_btn.config(state=tk.NORMAL if selection else tk.DISABLED)
    
    def download_selected(self):
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        book_id = item['values'][0]
        
        if book_id.isdigit():
            self.show_book_text(book_id)
        else:
            messagebox.showwarning("Внимание", "Не удалось определить ID книги")
    
    def show_book_text(self, book_id):
        def download_task():
            try:
                url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
                response = requests.get(url, timeout=15)
                
                # Создаем новое окно для текста
                text_window = tk.Toplevel(self.root)
                text_window.title(f"Книга ID: {book_id}")
                text_window.geometry("700x500")
                
                text_area = scrolledtext.ScrolledText(text_window, wrap=tk.WORD)
                text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                text_area.insert(tk.END, response.text[:5000] + "\n\n... (текст сокращен)")
                text_area.config(state=tk.DISABLED)
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить книгу: {e}")
        
        threading.Thread(target=download_task, daemon=True).start()

# Запуск приложения
root = tk.Tk()
app = SearchApp(root)
root.mainloop()
