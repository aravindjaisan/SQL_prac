
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import json
import xml.etree.ElementTree as ET
import os
import threading

class ExcelConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel Converter App")
        self.root.configure(bg="lightgrey")

        self.file_path = None
        self.df = None
        self.col_width_entries = []

        # File selection
        tk.Button(root, text="Browse Excel File", command=self.load_excel, bg="red", fg="white").grid(row=0, column=0, padx=10, pady=10)
        self.file_label = tk.Label(root, text="No file selected", bg="lightgrey")
        self.file_label.grid(row=0, column=1, sticky="w")

        # Format selection
        tk.Label(root, text="Format:", bg="lightgrey", fg="blue").grid(row=1, column=0, sticky="e")
        self.format_var = tk.StringVar()
        self.format_combo = ttk.Combobox(root, textvariable=self.format_var, state="readonly")
        self.format_combo['values'] = ("Fixed Width", "Delimited", "JSON", "XML")
        self.format_combo.bind("<<ComboboxSelected>>", self.on_format_change)
        self.format_combo.grid(row=1, column=1, sticky="w")

        # Delimiter options
        self.delimiter_label = tk.Label(root, text="Delimiter:", bg="lightgrey", fg="blue")
        self.delimiter_var = tk.StringVar()
        self.delimiter_combo = ttk.Combobox(root, textvariable=self.delimiter_var, state="readonly")
        self.delimiter_combo['values'] = (",", "Single Pipe (|)", "Triple Pipe (|||)")

        # Delimited file extension dropdown
        self.ext_label = tk.Label(root, text="File Extension:", bg="lightgrey", fg="blue")
        self.ext_var = tk.StringVar()
        self.ext_combo = ttk.Combobox(root, textvariable=self.ext_var, state="readonly")
        self.ext_combo['values'] = (".txt", ".dat", ".csv")

        # Encoding selection
        tk.Label(root, text="Encoding:", bg="lightgrey", fg="blue").grid(row=4, column=0, sticky="e")
        self.encoding_var = tk.StringVar(value="utf-8")
        self.encoding_combo = ttk.Combobox(root, textvariable=self.encoding_var, state="readonly")
        self.encoding_combo['values'] = ("utf-8", "utf-16", "ascii", "iso-8859-1")
        self.encoding_combo.grid(row=4, column=1, sticky="w")

        # Fixed width entry frame
        self.width_frame = tk.Frame(root, bg="lightgrey")
        self.width_frame.grid(row=5, column=0, columnspan=2, sticky="w")

        # Preview area
        tk.Label(root, text="Preview Output (first 25 rows):", bg="lightgrey", fg="red").grid(row=6, column=0, sticky="nw", pady=(10, 0))
        self.preview_box = tk.Text(root, height=15, width=80, wrap="none", bg="white")
        self.preview_box.grid(row=6, column=1, padx=5, pady=(10, 0))

        # Progress bar
        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=8, column=1, pady=5, sticky="w")

        # Buttons
        tk.Button(root, text="Preview", command=self.preview_output, bg="blue", fg="white").grid(row=7, column=0, pady=10)
        tk.Button(root, text="Convert and Save", command=self.convert_and_save, bg="green", fg="white").grid(row=7, column=1, pady=10, sticky="w")

        # Status label
        self.status_label = tk.Label(root, text="", bg="lightgrey", fg="blue")
        self.status_label.grid(row=9, column=0, columnspan=2, sticky="w", padx=10)

    def load_excel(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if path:
            self.set_status("Loading Excel file...")
            threading.Thread(target=self.read_excel_file, args=(path,), daemon=True).start()

    def read_excel_file(self, path):
        self.progress.start()
        try:
            self.file_path = path
            self.df = pd.read_excel(path)
            self.file_label.config(text=os.path.basename(path))
            self.set_status("Excel file loaded successfully.")
            self.root.after(100, self.on_format_change)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Failed to load Excel file.")
        finally:
            self.progress.stop()

    def on_format_change(self, event=None):
        for widget in self.width_frame.winfo_children():
            widget.destroy()
        self.col_width_entries.clear()
        self.delimiter_label.grid_forget()
        self.delimiter_combo.grid_forget()
        self.ext_label.grid_forget()
        self.ext_combo.grid_forget()

        if self.format_var.get() == "Fixed Width" and self.df is not None:
            tk.Label(self.width_frame, text="Column Widths:", bg="lightgrey", fg="blue").grid(row=0, column=0, sticky="w")
            for i, col in enumerate(self.df.columns):
                tk.Label(self.width_frame, text=f"{col}:", bg="lightgrey", fg="blue").grid(row=i + 1, column=0, sticky="e")
                entry = tk.Entry(self.width_frame, width=10)
                entry.insert(0, "10")
                entry.grid(row=i + 1, column=1, sticky="w")
                self.col_width_entries.append((col, entry))

        elif self.format_var.get() == "Delimited":
            self.delimiter_label.grid(row=2, column=0, sticky="e")
            self.delimiter_combo.grid(row=2, column=1, sticky="w")
            self.ext_label.grid(row=3, column=0, sticky="e")
            self.ext_combo.grid(row=3, column=1, sticky="w")

    def format_fixed_width(self, widths):
        lines = []
        for _, row in self.df.iterrows():
            line = ''.join(str(row[col])[:width].ljust(width) if pd.notnull(row[col]) else ''.ljust(width) for col, width in widths.items())
            lines.append(line)
        return "\n".join(lines)

    def format_delimited(self, delimiter):
        delim = {"Single Pipe (|)": "|", "Triple Pipe (|||)": "|||", ",": ","}[delimiter]
        return "\n".join(delim.join(str(cell) if pd.notnull(cell) else '' for cell in row) for _, row in self.df.iterrows())

    def format_json(self):
        return self.df.to_json(orient="records", force_ascii=False, indent=4)

    def format_xml(self):
        root = ET.Element("Rows")
        for _, row in self.df.iterrows():
            row_elem = ET.SubElement(root, "Row")
            for col in self.df.columns:
                child = ET.SubElement(row_elem, col)
                child.text = str(row[col]) if pd.notnull(row[col]) else ''
        return ET.tostring(root, encoding="unicode")

    def validate_fixed_widths(self):
        widths = {}
        for col, entry in self.col_width_entries:
            value = entry.get()
            if not value.isdigit() or int(value) <= 0:
                raise ValueError(f"Invalid width for column '{col}'. Please enter a positive integer.")
            widths[col] = int(value)
        return widths

    def preview_output(self):
        if self.df is None:
            messagebox.showerror("Error", "No Excel file loaded.")
            return

        try:
            preview_df = self.df.head(25)
            format_type = self.format_var.get()
            if format_type == "Fixed Width":
                widths = self.validate_fixed_widths()
                output = "\n".join(
                    ''.join(str(row[col])[:width].ljust(width) if pd.notnull(row[col]) else ''.ljust(width) for col, width in widths.items())
                    for _, row in preview_df.iterrows()
                )
            elif format_type == "Delimited":
                delim = {"Single Pipe (|)": "|", "Triple Pipe (|||)": "|||", ",": ","}[self.delimiter_var.get()]
                output = "\n".join(
                    delim.join(str(cell) if pd.notnull(cell) else '' for cell in row)
                    for _, row in preview_df.iterrows()
                )
            elif format_type == "JSON":
                output = preview_df.to_json(orient="records", force_ascii=False, indent=4)
            elif format_type == "XML":
                root = ET.Element("Rows")
                for _, row in preview_df.iterrows():
                    row_elem = ET.SubElement(root, "Row")
                    for col in preview_df.columns:
                        child = ET.SubElement(row_elem, col)
                        child.text = str(row[col]) if pd.notnull(row[col]) else ''
                output = ET.tostring(root, encoding="unicode")
            else:
                output = ""

            self.preview_box.delete(1.0, tk.END)
            self.preview_box.insert(tk.END, output)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def convert_and_save(self):
        if self.df is None:
            messagebox.showerror("Error", "No file loaded.")
            return

        format_type = self.format_var.get()
        encoding = self.encoding_var.get()
        output = ""

        try:
            if format_type == "Fixed Width":
                widths = self.validate_fixed_widths()
                output = self.format_fixed_width(widths)
                file_ext = ".txt"
            elif format_type == "Delimited":
                output = self.format_delimited(self.delimiter_var.get())
                file_ext = self.ext_var.get() or ".txt"
            elif format_type == "JSON":
                output = self.format_json()
                file_ext = ".json"
            elif format_type == "XML":
                output = self.format_xml()
                file_ext = ".xml"
            else:
                raise ValueError("Unsupported format.")

            save_path = filedialog.asksaveasfilename(defaultextension=file_ext)
            if save_path:
                with open(save_path, "w", encoding=encoding, errors="replace") as f:
                    f.write(output)
                messagebox.showinfo("Success", f"File saved to:\n{save_path}")
                self.set_status("File saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Failed to save file.")

    def set_status(self, message):
        self.status_label.config(text=message)

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelConverterApp(root)
    root.mainloop()
