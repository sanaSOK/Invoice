import os
from tkinter import Tk, StringVar, IntVar, Label, Entry, Button, messagebox
from tkinter import ttk
import tkinter.font as tkfont
from db import init_db, add_product, get_products, add_invoice, update_product
from pdf_invoice import generate_invoice_pdf


DB_PATH = os.path.join(os.path.dirname(__file__), 'bank_db.db')


class App:
    def __init__(self, root):
        self.root = root
        self.root.title('Invoice / POS Mini System')
        self.root.geometry('1000x600')

        init_db(DB_PATH)

        # Layout frames
        self.font_title = tkfont.Font(size=11, weight='bold')
        left = ttk.Frame(root, padding=(10, 10))
        left.grid(row=0, column=0, rowspan=10, sticky='n')
        right = ttk.Frame(root, padding=(10, 10))
        right.grid(row=0, column=3, rowspan=10, columnspan=3, sticky='n')

        # Product form (left)
        Label(left, text='Products', font=self.font_title).grid(row=0, column=0, columnspan=3, sticky='w')
        Label(left, text='Product name').grid(row=1, column=0, sticky='w')
        self.p_name = StringVar()
        Entry(left, textvariable=self.p_name, width=25).grid(row=1, column=1, columnspan=2, pady=2)

        Label(left, text='Price').grid(row=2, column=0, sticky='w')
        self.p_price = StringVar()
        Entry(left, textvariable=self.p_price, width=10).grid(row=2, column=1, pady=2, sticky='w')

        Button(left, text='Add Product', command=self.handle_add_product).grid(row=3, column=0, pady=6)

        # Search
        Label(left, text='Search').grid(row=4, column=0, sticky='w')
        self.search_var = StringVar()
        Entry(left, textvariable=self.search_var, width=20).grid(row=4, column=1)
        Button(left, text='Find', command=self.search_products).grid(row=4, column=2)

        self.products_tv = ttk.Treeview(left, columns=('id', 'name', 'price'), show='headings', height=8)
        self.products_tv.heading('id', text='ID')
        self.products_tv.heading('name', text='Name')
        self.products_tv.heading('price', text='Price')
        self.products_tv.column('id', width=40)
        self.products_tv.grid(row=5, column=0, columnspan=3, pady=8)
        self.products_tv.bind('<<TreeviewSelect>>', self.on_product_select)

        # Invoice area
        # Invoice area (right)
        Label(right, text='Invoice', font=self.font_title).grid(row=0, column=0, columnspan=3, sticky='w')
        Label(right, text='Customer').grid(row=1, column=0, sticky='w')
        self.cust = StringVar()
        Entry(right, textvariable=self.cust, width=30).grid(row=1, column=1, columnspan=2, pady=2)

        Label(right, text='Select Product ID').grid(row=2, column=0, sticky='w')
        self.sel_pid = StringVar()
        Entry(right, textvariable=self.sel_pid, width=8).grid(row=2, column=1, sticky='w')

        Label(right, text='Quantity').grid(row=3, column=0, sticky='w')
        self.qty = IntVar(value=1)
        Entry(right, textvariable=self.qty, width=6).grid(row=3, column=1, sticky='w')

        Button(right, text='Add to Invoice', command=self.add_line_item).grid(row=4, column=0, columnspan=2, pady=6)

        # Product edit buttons (left)
        Button(left, text='Load Selected for Edit', command=self.load_selected_for_edit).grid(row=6, column=0, pady=4)
        Button(left, text='Update Product', command=self.handle_update_product).grid(row=6, column=1, pady=4)

        self.items_tv = ttk.Treeview(right, columns=('name', 'price', 'qty', 'total'), show='headings', height=10)
        for col, title in [('name', 'Name'), ('price', 'Price'), ('qty', 'Qty'), ('total', 'Total')]:
            self.items_tv.heading(col, text=title)
        self.items_tv.grid(row=5, column=0, columnspan=3, pady=8)

        self.total_var = StringVar(value='0.00')
        Label(root, text='Total:').grid(row=5, column=3, sticky='e')
        Label(root, textvariable=self.total_var).grid(row=5, column=4, sticky='w')

        Button(right, text='Save Invoice (PDF)', command=self.save_invoice).grid(row=6, column=0, columnspan=2, pady=8)

        self.line_items = []
        self.refresh_products()

    def handle_add_product(self):
        name = self.p_name.get().strip()
        try:
            price = float(self.p_price.get())
        except Exception:
            messagebox.showerror('Invalid price', 'Enter a numeric price')
            return
        if not name:
            messagebox.showerror('Invalid name', 'Enter a product name')
            return
        add_product(DB_PATH, name, price)
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
            messagebox.showwarning('Select', 'Select a product to edit')
            return
        vals = self.products_tv.item(sel[0], 'values')
        pid, name, price = vals
        self.p_name.set(name)
        self.p_price.set(str(price))
        self.sel_pid.set(str(pid))

    def handle_update_product(self):
        pid = self.sel_pid.get().strip()
        if not pid.isdigit():
            messagebox.showerror('Invalid', 'No product selected or invalid ID')
            return
        pid = int(pid)
        name = self.p_name.get().strip()
        try:
            price = float(self.p_price.get())
        except Exception:
            messagebox.showerror('Invalid price', 'Enter a numeric price')
            return
        if not name:
            messagebox.showerror('Invalid name', 'Enter a product name')
            return
        # update DB
        update_product(DB_PATH, pid, name, price)
        self.refresh_products()

    def refresh_products(self):
        for i in self.products_tv.get_children():
            self.products_tv.delete(i)
        for row in get_products(DB_PATH):
            self.products_tv.insert('', 'end', values=row)

    def add_line_item(self):
        pid = self.sel_pid.get().strip()
        if not pid.isdigit():
            messagebox.showerror('Invalid ID', 'Enter a valid product ID')
            return
        pid = int(pid)
        qty = max(1, int(self.qty.get()))
        products = {p[0]: (p[1], p[2]) for p in get_products(DB_PATH)}
        if pid not in products:
            messagebox.showerror('Not found', 'Product ID not found')
            return
        name, price = products[pid]
        total = price * qty
        self.line_items.append({'pid': pid, 'name': name, 'price': price, 'qty': qty, 'total': total})
        self.items_tv.insert('', 'end', values=(name, f'{price:.2f}', qty, f'{total:.2f}'))
        self.update_total()

    def update_total(self):
        total = sum(item['total'] for item in self.line_items)
        self.total_var.set(f'{total:.2f}')

    def save_invoice(self):
        if not self.line_items:
            messagebox.showwarning('Empty', 'Add items to invoice first')
            return
        customer = self.cust.get().strip() or 'Customer'
        invoice_id = add_invoice(DB_PATH, customer, self.line_items)
        invoices_dir = os.path.join(os.path.dirname(__file__), 'invoices')
        os.makedirs(invoices_dir, exist_ok=True)
        pdf_path = os.path.join(invoices_dir, f'invoice_{invoice_id}.pdf')
        generate_invoice_pdf(pdf_path, invoice_id, customer, self.line_items)
        messagebox.showinfo('Saved', f'Invoice saved as {pdf_path}')
        # reset
        self.line_items = []
        for i in self.items_tv.get_children():
            self.items_tv.delete(i)
        self.update_total()


if __name__ == '__main__':
    root = Tk()
    app = App(root)
    root.mainloop()
