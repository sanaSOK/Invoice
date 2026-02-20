import os
from tkinter import Tk, StringVar, IntVar, Label, Entry, Button, messagebox, Frame
from tkinter import ttk
import tkinter.font as tkfont
from db import init_db, add_product, get_products, add_invoice, update_product
from pdf_invoice import generate_invoice_pdf


DB_PATH = os.path.join(os.path.dirname(__file__), 'bank_db.db')

# Color scheme
BG_COLOR = '#f0f0f0'
PRIMARY_COLOR = '#2c3e50'
ACCENT_COLOR = '#3498db'
SUCCESS_COLOR = '#27ae60'
BUTTON_HOVER = '#2980b9'
TEXT_COLOR = '#2c3e50'
LIGHT_BG = '#ecf0f1'
BORDER_COLOR = '#bdc3c7'


class App:
    def __init__(self, root):
        self.root = root
        self.root.title('💰 Invoice / POS Mini System')
        self.root.geometry('1400x750')
        self.root.configure(bg=BG_COLOR)

        init_db(DB_PATH)

        # Define fonts
        self.font_title = tkfont.Font(family='Segoe UI', size=14, weight='bold')
        self.font_subtitle = tkfont.Font(family='Segoe UI', size=10, weight='bold')
        self.font_normal = tkfont.Font(family='Segoe UI', size=10)
        self.font_label = tkfont.Font(family='Segoe UI', size=9)

        # Main container
        main_container = Frame(root, bg=BG_COLOR)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Left panel - Products Management
        left_panel = Frame(main_container, bg='white', relief='flat', highlightthickness=1, highlightbackground=BORDER_COLOR)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 5))

        self._create_product_section(left_panel)

        # Right panel - Invoice Creation
        right_panel = Frame(main_container, bg='white', relief='flat', highlightthickness=1, highlightbackground=BORDER_COLOR)
        right_panel.pack(side='right', fill='both', expand=True, padx=(5, 0))

        self._create_invoice_section(right_panel)

        self.line_items = []
        self.refresh_products()

    def _create_product_section(self, parent):
        """Create the product management section"""
        # Header
        header = Frame(parent, bg=PRIMARY_COLOR, height=50)
        header.pack(fill='x')
        header.pack_propagate(False)

        Label(header, text='📦 Products Management', font=self.font_title, bg=PRIMARY_COLOR, fg='white').pack(side='left', padx=15, pady=10)

        # Content area
        content = Frame(parent, bg='white')
        content.pack(fill='both', expand=True, padx=15, pady=15)

        # Add Product Form
        form_frame = Frame(content, bg='white')
        form_frame.pack(fill='x', pady=(0, 15))

        Label(form_frame, text='Add New Product', font=self.font_subtitle, bg='white', fg=TEXT_COLOR).pack(anchor='w', pady=(0, 10))

        # Product name
        Label(form_frame, text='Product Name', font=self.font_label, bg='white', fg=TEXT_COLOR).pack(anchor='w')
        self.p_name = StringVar()
        name_entry = Entry(form_frame, textvariable=self.p_name, font=self.font_normal, relief='solid', borderwidth=1)
        name_entry.pack(fill='x', pady=(0, 8))
        name_entry.config(highlightbackground=BORDER_COLOR, highlightthickness=1)

        # Price
        price_frame = Frame(form_frame, bg='white')
        price_frame.pack(fill='x', pady=(0, 8))
        Label(price_frame, text='Price ($)', font=self.font_label, bg='white', fg=TEXT_COLOR).pack(side='left', anchor='w')
        self.p_price = StringVar()
        price_entry = Entry(price_frame, textvariable=self.p_price, font=self.font_normal, width=15, relief='solid', borderwidth=1)
        price_entry.pack(side='left', anchor='w', pady=(0, 0))
        price_entry.config(highlightbackground=BORDER_COLOR, highlightthickness=1)

        # Buttons
        button_frame = Frame(form_frame, bg='white')
        button_frame.pack(fill='x', pady=(0, 15))

        add_btn = Button(button_frame, text='➕ Add Product', command=self.handle_add_product,
                        bg=SUCCESS_COLOR, fg='white', font=self.font_normal,
                        relief='flat', padx=15, pady=8, cursor='hand2')
        add_btn.pack(side='left', padx=(0, 8))
        self._hover_effect(add_btn, SUCCESS_COLOR, '#229954')

        update_btn = Button(button_frame, text='✏️ Update Selected', command=self.handle_update_product,
                           bg=ACCENT_COLOR, fg='white', font=self.font_normal,
                           relief='flat', padx=15, pady=8, cursor='hand2')
        update_btn.pack(side='left')
        self._hover_effect(update_btn, ACCENT_COLOR, BUTTON_HOVER)

        # Separator
        ttk.Separator(content, orient='horizontal').pack(fill='x', pady=10)

        # Search section
        search_frame = Frame(content, bg='white')
        search_frame.pack(fill='x', pady=(0, 10))

        Label(search_frame, text='🔍 Search Products', font=self.font_subtitle, bg='white', fg=TEXT_COLOR).pack(anchor='w', pady=(0, 8))

        search_input_frame = Frame(search_frame, bg='white')
        search_input_frame.pack(fill='x')

        self.search_var = StringVar()
        search_entry = Entry(search_input_frame, textvariable=self.search_var, font=self.font_normal, relief='solid', borderwidth=1)
        search_entry.pack(side='left', fill='x', expand=True, padx=(0, 8))
        search_entry.config(highlightbackground=BORDER_COLOR, highlightthickness=1)

        search_btn = Button(search_input_frame, text='Search', command=self.search_products,
                           bg=ACCENT_COLOR, fg='white', font=self.font_normal,
                           relief='flat', padx=15, pady=6, cursor='hand2')
        search_btn.pack(side='left')
        self._hover_effect(search_btn, ACCENT_COLOR, BUTTON_HOVER)

        # Separator
        ttk.Separator(content, orient='horizontal').pack(fill='x', pady=10)

        # Products Treeview
        tree_label = Label(content, text='Product Inventory', font=self.font_subtitle, bg='white', fg=TEXT_COLOR)
        tree_label.pack(anchor='w', pady=(0, 8))

        # Style the treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', font=self.font_normal, rowheight=25, background='white', foreground=TEXT_COLOR)
        style.configure('Treeview.Heading', font=self.font_label, background=LIGHT_BG, foreground=TEXT_COLOR)
        style.map('Treeview', background=[('selected', ACCENT_COLOR)], foreground=[('selected', 'white')])

        self.products_tv = ttk.Treeview(content, columns=('id', 'name', 'price'), show='headings', height=12)
        self.products_tv.heading('id', text='ID')
        self.products_tv.heading('name', text='Product Name')
        self.products_tv.heading('price', text='Price')
        self.products_tv.column('id', width=50, anchor='center')
        self.products_tv.column('name', width=150, anchor='w')
        self.products_tv.column('price', width=80, anchor='e')
        self.products_tv.pack(fill='both', expand=True)
        self.products_tv.bind('<<TreeviewSelect>>', self.on_product_select)

        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(content, orient='vertical', command=self.products_tv.yview)
        self.products_tv.configure(yscrollcommand=scrollbar.set)

    def _create_invoice_section(self, parent):
        """Create the invoice creation section"""
        # Header
        header = Frame(parent, bg=PRIMARY_COLOR, height=50)
        header.pack(fill='x')
        header.pack_propagate(False)

        Label(header, text='📋 Create Invoice', font=self.font_title, bg=PRIMARY_COLOR, fg='white').pack(side='left', padx=15, pady=10)

        # Content area
        content = Frame(parent, bg='white')
        content.pack(fill='both', expand=True, padx=15, pady=15)

        # Customer section
        customer_frame = Frame(content, bg='white')
        customer_frame.pack(fill='x', pady=(0, 15))

        Label(customer_frame, text='Customer Information', font=self.font_subtitle, bg='white', fg=TEXT_COLOR).pack(anchor='w', pady=(0, 8))

        Label(customer_frame, text='Customer Name', font=self.font_label, bg='white', fg=TEXT_COLOR).pack(anchor='w')
        self.cust = StringVar()
        cust_entry = Entry(customer_frame, textvariable=self.cust, font=self.font_normal, relief='solid', borderwidth=1)
        cust_entry.pack(fill='x', pady=(0, 8))
        cust_entry.config(highlightbackground=BORDER_COLOR, highlightthickness=1)

        # Separator
        ttk.Separator(content, orient='horizontal').pack(fill='x', pady=10)

        # Add items section
        items_frame = Frame(content, bg='white')
        items_frame.pack(fill='x', pady=(0, 15))

        Label(items_frame, text='Add Items to Invoice', font=self.font_subtitle, bg='white', fg=TEXT_COLOR).pack(anchor='w', pady=(0, 8))

        # Product selection
        product_frame = Frame(items_frame, bg='white')
        product_frame.pack(fill='x', pady=(0, 8))

        Label(product_frame, text='Product ID', font=self.font_label, bg='white', fg=TEXT_COLOR).pack(side='left', padx=(0, 10))
        self.sel_pid = StringVar()
        pid_entry = Entry(product_frame, textvariable=self.sel_pid, font=self.font_normal, width=12, relief='solid', borderwidth=1)
        pid_entry.pack(side='left', padx=(0, 15))
        pid_entry.config(highlightbackground=BORDER_COLOR, highlightthickness=1)

        Label(product_frame, text='Quantity', font=self.font_label, bg='white', fg=TEXT_COLOR).pack(side='left', padx=(0, 10))
        self.qty = IntVar(value=1)
        qty_entry = Entry(product_frame, textvariable=self.qty, font=self.font_normal, width=8, relief='solid', borderwidth=1)
        qty_entry.pack(side='left')
        qty_entry.config(highlightbackground=BORDER_COLOR, highlightthickness=1)

        # Add button
        add_item_btn = Button(items_frame, text='✅ Add to Invoice', command=self.add_line_item,
                             bg=SUCCESS_COLOR, fg='white', font=self.font_normal,
                             relief='flat', padx=15, pady=8, cursor='hand2')
        add_item_btn.pack(fill='x', pady=(0, 15))
        self._hover_effect(add_item_btn, SUCCESS_COLOR, '#229954')

        # Separator
        ttk.Separator(content, orient='horizontal').pack(fill='x', pady=10)

        # Items treeview
        tree_label = Label(content, text='Invoice Items', font=self.font_subtitle, bg='white', fg=TEXT_COLOR)
        tree_label.pack(anchor='w', pady=(0, 8))

        self.items_tv = ttk.Treeview(content, columns=('name', 'price', 'qty', 'total'), show='headings', height=10)
        for col, title in [('name', 'Product'), ('price', 'Price'), ('qty', 'Qty'), ('total', 'Total')]:
            self.items_tv.heading(col, text=title)
        self.items_tv.column('name', width=150, anchor='w')
        self.items_tv.column('price', width=70, anchor='e')
        self.items_tv.column('qty', width=50, anchor='center')
        self.items_tv.column('total', width=80, anchor='e')
        self.items_tv.pack(fill='both', expand=True, pady=(0, 15))

        # Total section
        total_frame = Frame(content, bg=LIGHT_BG, relief='solid', borderwidth=1)
        total_frame.pack(fill='x', pady=(0, 15), padx=10, ipady=10)

        self.total_var = StringVar(value='$0.00')
        total_label = Label(total_frame, text='Grand Total:', font=tkfont.Font(family='Segoe UI', size=12, weight='bold'),
                           bg=LIGHT_BG, fg=TEXT_COLOR)
        total_label.pack(side='left', padx=10)

        total_value = Label(total_frame, textvariable=self.total_var, font=tkfont.Font(family='Segoe UI', size=14, weight='bold'),
                           bg=LIGHT_BG, fg=SUCCESS_COLOR)
        total_value.pack(side='left', padx=10)

        # Save button
        save_btn = Button(content, text='💾 Save Invoice (PDF)', command=self.save_invoice,
                         bg=PRIMARY_COLOR, fg='white', font=self.font_normal,
                         relief='flat', padx=20, pady=12, cursor='hand2')
        save_btn.pack(fill='x')
        self._hover_effect(save_btn, PRIMARY_COLOR, '#34495e')

    def _hover_effect(self, button, normal_color, hover_color):
        """Add hover effect to buttons"""
        def on_enter(event):
            button.config(bg=hover_color)

        def on_leave(event):
            button.config(bg=normal_color)

        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)

    def handle_add_product(self):
        name = self.p_name.get().strip()
        try:
            price = float(self.p_price.get())
        except Exception:
            messagebox.showerror('❌ Invalid Price', 'Please enter a valid numeric price')
            return
        if not name:
            messagebox.showerror('❌ Invalid Name', 'Please enter a product name')
            return
        if price < 0:
            messagebox.showerror('❌ Invalid Price', 'Price cannot be negative')
            return
        add_product(DB_PATH, name, price)
        messagebox.showinfo('✅ Success', f'Product "{name}" added successfully!')
        self.p_name.set('')
        self.p_price.set('')
        self.refresh_products()

    def search_products(self):
        q = self.search_var.get().strip().lower()
        rows = get_products(DB_PATH)
        if q:
            rows = [r for r in rows if q in r[1].lower() or q == str(r[0])]
        for i in self.products_tv.get_children():
            self.products_tv.delete(i)
        for row in rows:
            self.products_tv.insert('', 'end', values=row)
        if not rows and q:
            messagebox.showinfo('🔍 Search', f'No products found matching "{q}"')

    def on_product_select(self, event):
        sel = self.products_tv.selection()
        if not sel:
            return
        vals = self.products_tv.item(sel[0], 'values')
        if vals:
            pid, name, price = vals
            self.p_name.set(name)
            self.p_price.set(str(price))
            self.sel_pid.set(str(pid))

    def load_selected_for_edit(self):
        sel = self.products_tv.selection()
        if not sel:
            messagebox.showwarning('⚠️ Select Product', 'Please select a product to edit')
            return
        vals = self.products_tv.item(sel[0], 'values')
        pid, name, price = vals
        self.p_name.set(name)
        self.p_price.set(str(price))
        self.sel_pid.set(str(pid))

    def handle_update_product(self):
        pid = self.sel_pid.get().strip()
        if not pid.isdigit():
            messagebox.showerror('❌ Invalid', 'Please select a product or enter valid ID')
            return
        pid = int(pid)
        name = self.p_name.get().strip()
        try:
            price = float(self.p_price.get())
        except Exception:
            messagebox.showerror('❌ Invalid Price', 'Please enter a valid numeric price')
            return
        if not name:
            messagebox.showerror('❌ Invalid Name', 'Please enter a product name')
            return
        if price < 0:
            messagebox.showerror('❌ Invalid Price', 'Price cannot be negative')
            return
        update_product(DB_PATH, pid, name, price)
        messagebox.showinfo('✅ Success', f'Product updated successfully!')
        self.refresh_products()
        self.p_name.set('')
        self.p_price.set('')
        self.sel_pid.set('')

    def refresh_products(self):
        for i in self.products_tv.get_children():
            self.products_tv.delete(i)
        for row in get_products(DB_PATH):
            self.products_tv.insert('', 'end', values=row)

    def add_line_item(self):
        pid = self.sel_pid.get().strip()
        if not pid.isdigit():
            messagebox.showerror('❌ Invalid ID', 'Please enter a valid product ID')
            return
        pid = int(pid)
        try:
            qty = int(self.qty.get())
            if qty <= 0:
                messagebox.showerror('❌ Invalid Quantity', 'Quantity must be greater than 0')
                return
        except ValueError:
            messagebox.showerror('❌ Invalid Quantity', 'Please enter a valid number for quantity')
            return

        products = {p[0]: (p[1], p[2]) for p in get_products(DB_PATH)}
        if pid not in products:
            messagebox.showerror('❌ Not Found', f'Product ID {pid} not found')
            return
        name, price = products[pid]
        total = price * qty
        self.line_items.append({'pid': pid, 'name': name, 'price': price, 'qty': qty, 'total': total})
        self.items_tv.insert('', 'end', values=(name, f'${price:.2f}', qty, f'${total:.2f}'))
        self.update_total()
        self.sel_pid.set('')
        self.qty.set(1)
        messagebox.showinfo('✅ Added', f'{name} x{qty} added to invoice')

    def update_total(self):
        total = sum(item['total'] for item in self.line_items)
        self.total_var.set(f'${total:.2f}')

    def save_invoice(self):
        if not self.line_items:
            messagebox.showwarning('⚠️ Empty Invoice', 'Please add items to invoice first')
            return
        customer = self.cust.get().strip() or 'Walk-in Customer'
        invoice_id = add_invoice(DB_PATH, customer, self.line_items)
        invoices_dir = os.path.join(os.path.dirname(__file__), 'invoices')
        os.makedirs(invoices_dir, exist_ok=True)
        pdf_path = os.path.join(invoices_dir, f'invoice_{invoice_id}.pdf')
        generate_invoice_pdf(pdf_path, invoice_id, customer, self.line_items)
        messagebox.showinfo('✅ Saved', f'Invoice #{invoice_id} saved as PDF!\n{pdf_path}')
        # reset
        self.line_items = []
        for i in self.items_tv.get_children():
            self.items_tv.delete(i)
        self.update_total()
        self.cust.set('')


if __name__ == '__main__':
    root = Tk()
    app = App(root)
    root.mainloop()
