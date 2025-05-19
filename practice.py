import tkinter as tk
from tkinter import Label, Entry, ttk, Tk, Button, messagebox


class CustomerForm:
    def __init__(self, cform):
        self.cform = cform
        self.cform.title("Customer Form")
        self.cform.geometry("400x500")

        Label(cform, text="Customer ID").place(x=20, y=20)
        self.ent_cid = Entry()
        self.ent_cid.place(x=60, y=20)

        Label(cform, text="Customer Name").place(x=20, y=60)
        self.ent_name = Entry()
        self.ent_name.place(x=60, y=60)

        Label(cform, text="Customer Address").place(x=20, y=100)
        self.ent_cadd = Entry()
        self.ent_cadd.place(x=60, y=100)

        Button(cform, text="Search").place(x=20, y=140)
        self.search_btn = Entry()
        self.search_btn.place(x=60, y=140)

        self.tbl = ttk.Treeview(cform, columns=("cid", "cname", "cadd"))
        self.tbl.heading("cid", text="Customer ID")
        self.tbl.heading("cname", text="Customer Name")
        self.tbl.heading("cadd", text="Customer Address")
        self.tbl.bind("ButtonRelease=1>", self.tbl_event)

        Button(cform, text="Add").place(x=100, y=180)
        Button(cform, text="Edit").place(x=100, y=220)
        Button(cform, text="Delete").place(x=100, y=260)

    def tbl_event(self, event):
        sr = self.tbl.focus()
        values = self.tbl.item(sr, 'values')

        if values:
            self.ent_cid.delete(0, tk.END)
        self.ent_cname.delete(0, tk.END)
        self.ent_cadd.delete(0, tk.END)
        self.ent_cid.insert(0, values[0])
        self.ent_cname.insert(0, values[1])
        self.ent_cadd.insert(0, values[2])

    def tbl_insert(self):
        cid = self.ent_cid.get()
        cname = self.ent_cname.get()
        cadd = self.ent_cadd.get()

        if cid and cname and cadd:
            self.tbl.insert("", "end", values=(cid, cname, cadd))
        else:
            messagebox.showwarning("WARNING", "All fields are required!")

    def tbl_update(self):
        sr = self.tbl.focus()
        if sr:
            self.tbl.item(sr, values=(self.ent_cid.get(), self.ent_cname.get(), self.ent_cadd.get()))
        else:
            messagebox.showwarning("WARNING", "Select a Record!")

    def tbl_remove(self):
        sr = self.tbl.focus()
        if sr:
            self.tbl.delete(sr)
        else:
            messagebox.showwarning("WARNING", "Select a Record!")

    def clear_field(self):
        self.ent_cid.delete(0, tk.END)
        self.ent_cname.delete(0, tk.END)
        self.ent_cadd.delete(0, tk.END)


if __name__ == "__main__":
    cform = Tk()
    CustomerForm(cform)
    cform.mainloop()















