import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import xml.etree.ElementTree as ET
import os
import threading
import json

class ExcelConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel Converter App")
        self.root.configure(bg="lightgrey")

        self.file_path = None
        self.df = None
        self.col_width_entries = []

        # --- File selection ---
        tk.Button(root, text="Browse Excel File", command=self.load_excel, bg="red", fg="white").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.file_label = tk.Label(root, text="No file selected", bg="lightgrey")
        self.file_label.grid(row=0, column=1, sticky="w")

        # --- Format selection ---
        tk.Label(root, text="Format:", bg="lightgrey", fg="blue").grid(row=1, column=0, sticky="e")
        self.format_var = tk.StringVar()
        self.format_combo = ttk.Combobox(root, textvariable=self.format_var, state="readonly")
        self.format_combo['values'] = ("Fixed Width", "Delimited", "JSON", "XML")
        self.format_combo.bind("<<ComboboxSelected>>", self.on_format_change)
        self.format_combo.grid(row=1, column=1, sticky="w")

        # --- Delimiter options ---
        self.delimiter_label = tk.Label(root, text="Delimiter:", bg="lightgrey", fg="blue")
        self.delimiter_var = tk.StringVar()
        self.delimiter_combo = ttk.Combobox(root, textvariable=self.delimiter_var, state="readonly")
        self.delimiter_combo['values'] = (",", "Single Pipe (|)", "Triple Pipe (|||)")

        # --- Delimited file extension ---
        self.ext_label = tk.Label(root, text="File Extension:", bg="lightgrey", fg="blue")
        self.ext_var = tk.StringVar()
        self.ext_combo = ttk.Combobox(root, textvariable=self.ext_var, state="readonly")
        self.ext_combo['values'] = (".txt", ".dat", ".csv")

        # --- Encoding selection ---
        tk.Label(root, text="Encoding:", bg="lightgrey", fg="blue").grid(row=4, column=0, sticky="e")
        self.encoding_var = tk.StringVar(value="utf-8")
        self.encoding_combo = ttk.Combobox(root, textvariable=self.encoding_var, state="readonly")
        self.encoding_combo['values'] = ("utf-8", "utf-16", "ascii", "iso-8859-1")
        self.encoding_combo.grid(row=4, column=1, sticky="w")

        # --- Scrollable fixed-width frame ---
        self.width_canvas = tk.Canvas(root, height=200, bg="lightgrey", highlightthickness=0)
        self.width_canvas.grid(row=5, column=0, columnspan=2, sticky="we", padx=5)

        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.width_canvas.yview)
        self.scrollbar.grid(row=5, column=2, sticky="ns")

        self.width_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.width_inner_frame = tk.Frame(self.width_canvas, bg="lightgrey")
        self.width_canvas.create_window((0, 0), window=self.width_inner_frame, anchor="nw")

        self.width_inner_frame.bind("<Configure>", lambda e: self.width_canvas.configure(scrollregion=self.width_canvas.bbox("all")))

        # --- Preview area ---
        tk.Label(root, text="Preview Output (first 25 rows):", bg="lightgrey", fg="red").grid(row=6, column=0, sticky="nw", pady=(10, 0))
        self.preview_box = tk.Text(root, height=15, width=80, wrap="none", bg="white")
        self.preview_box.grid(row=6, column=1, padx=5, pady=(10, 0))

        # --- Progress bar ---
        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=8, column=1, pady=5, sticky="w")

        # --- Buttons ---
        tk.Button(root, text="Preview", command=self.preview_output, bg="blue", fg="white").grid(row=7, column=0, pady=10, sticky="w")
        tk.Button(root, text="Convert and Save", command=self.convert_and_save, bg="green", fg="white").grid(row=7, column=1, pady=10, sticky="w")

        # --- Status label ---
        self.status_label = tk.Label(root, text="", bg="lightgrey", fg="blue")
        self.status_label.grid(row=9, column=0, columnspan=3, sticky="w", padx=10)

        # --- Output summary and stats ---
        self.summary_label = tk.Label(root, text="", bg="lightgrey", fg="purple", justify="left")
        self.summary_label.grid(row=10, column=0, columnspan=3, sticky="w", padx=10, pady=(5,10))

    # Load Excel file in a thread
    def load_excel(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if path:
            self.set_status("Loading Excel file...")
            threading.Thread(target=self.read_excel_file, args=(path,), daemon=True).start()

    def read_excel_file(self, path):
        try:
            self.progress.start()
            df = pd.read_excel(path)
            self.file_path = path
            self.df = df
            self.file_label.config(text=os.path.basename(path))
            self.set_status("Excel file loaded successfully.")
            self.root.after(100, self.on_format_change)
            self.root.after(100, self.show_data_summary)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Failed to load Excel file.")
        finally:
            self.progress.stop()

    def on_format_change(self, event=None):
        for widget in self.width_inner_frame.winfo_children():
            widget.destroy()
        self.col_width_entries.clear()
        self.delimiter_label.grid_forget()
        self.delimiter_combo.grid_forget()
        self.ext_label.grid_forget()
        self.ext_combo.grid_forget()

        fmt = self.format_var.get()
        if fmt == "Fixed Width" and self.df is not None:
            tk.Label(self.width_inner_frame, text="Column Widths:", bg="lightgrey", fg="blue").grid(row=0, column=0, sticky="w")
            for i, col in enumerate(self.df.columns):
                tk.Label(self.width_inner_frame, text=f"{col}:", bg="lightgrey", fg="blue").grid(row=i + 1, column=0, sticky="e")
                entry = tk.Entry(self.width_inner_frame, width=10)
                entry.insert(0, "10")
                entry.grid(row=i + 1, column=1, sticky="w")
                self.col_width_entries.append((col, entry))

        elif fmt == "Delimited":
            self.delimiter_label.grid(row=2, column=0, sticky="e")
            self.delimiter_combo.grid(row=2, column=1, sticky="w")
            self.ext_label.grid(row=3, column=0, sticky="e")
            self.ext_combo.grid(row=3, column=1, sticky="w")
            # Default selections
            if not self.delimiter_var.get():
                self.delimiter_var.set(",")
            if not self.ext_var.get():
                self.ext_var.set(".csv")

    def validate_fixed_widths(self):
        widths = {}
        for col, entry in self.col_width_entries:
            val = entry.get()
            if not val.isdigit() or int(val) <= 0:
                raise ValueError(f"Invalid width for column '{col}'. Enter positive integer.")
            widths[col] = int(val)
        return widths

    def format_fixed_width(self, widths):
        lines = []
        header = ''.join(col[:widths[col]].ljust(widths[col]) for col in self.df.columns)
        lines.append(header)
        for _, row in self.df.iterrows():
            line = ''.join(
                str(row[col])[:widths[col]].ljust(widths[col]) if pd.notnull(row[col]) else ''.ljust(widths[col])
                for col in self.df.columns
            )
            lines.append(line)
        return "\n".join(lines)

    def format_delimited(self, delimiter_label):
        delimiter_map = {
            "Single Pipe (|)": "|",
            "Triple Pipe (|||)": "|||",
            ",": ","
        }
        delim = delimiter_map[delimiter_label]

        def escape_field(value):
            if pd.isnull(value):
                return ""
            value_str = str(value)
            if delim == ",":
                # Standard CSV quoting for commas and quotes
                if '"' in value_str or ',' in value_str or '\n' in value_str:
                    value_str = value_str.replace('"', '""')
                    return f'"{value_str}"'
                return value_str
            else:
                # For pipe delimiters, just quote all values
                return f'"{value_str}"'

        lines = [delim.join([escape_field(col) for col in self.df.columns])]
        for _, row in self.df.iterrows():
            values = [escape_field(row[col]) for col in self.df.columns]
            lines.append(delim.join(values))
        return "\n".join(lines)

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

    def preview_output(self):
        if self.df is None:
            messagebox.showerror("Error", "No Excel file loaded.")
            return
        try:
            preview_df = self.df.head(25)
            fmt = self.format_var.get()
            output = ""

            if fmt == "Fixed Width":
                widths = self.validate_fixed_widths()
                header = ''.join(col[:widths[col]].ljust(widths[col]) for col in preview_df.columns)
                lines = [header]
                for _, row in preview_df.iterrows():
                    line = ''.join(
                        str(row[col])[:widths[col]].ljust(widths[col]) if pd.notnull(row[col]) else ''.ljust(widths[col])
                        for col in preview_df.columns
                    )
                    lines.append(line)
                output = "\n".join(lines)

            elif fmt == "Delimited":
                delim_map = {
                    "Single Pipe (|)": "|",
                    "Triple Pipe (|||)": "|||",
                    ",": ","
                }
                delim = delim_map[self.delimiter_var.get()]

                def escape_field(value):
                    if pd.isnull(value):
                        return ""
                    value_str = str(value)
                    if delim == ",":
                        if '"' in value_str or ',' in value_str or '\n' in value_str:
                            value_str = value_str.replace('"', '""')
                            return f'"{value_str}"'
                        return value_str
                    else:
                        return f'"{value_str}"'

                lines = [delim.join([escape_field(col) for col in preview_df.columns])]
                for _, row in preview_df.iterrows():
                    values = [escape_field(row[col]) for col in preview_df.columns]
                    lines.append(delim.join(values))
                output = "\n".join(lines)

            elif fmt == "JSON":
                output = preview_df.to_json(orient="records", force_ascii=False, indent=4)

            elif fmt == "XML":
                root = ET.Element("Rows")
                for _, row in preview_df.iterrows():
                    row_elem = ET.SubElement(root, "Row")
                    for col in preview_df.columns:
                        child = ET.SubElement(row_elem, col)
                        child.text = str(row[col]) if pd.notnull(row[col]) else ''
                output = ET.tostring(root, encoding="unicode")

            self.preview_box.delete(1.0, tk.END)
            self.preview_box.insert(tk.END, output)
            self.set_status(f"Preview generated for first 25 rows.")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Preview generation failed.")

    def convert_and_save(self):
        if self.df is None:
            messagebox.showerror("Error", "No file loaded.")
            return
        threading.Thread(target=self._convert_and_save_thread, daemon=True).start()

    def _convert_and_save_thread(self):
        self.progress.start()
        try:
            fmt = self.format_var.get()
            encoding = self.encoding_var.get()
            output = ""
            file_ext = ""

            if fmt == "Fixed Width":
                widths = self.validate_fixed_widths()
                output = self.format_fixed_width(widths)
                file_ext = ".txt"
            elif fmt == "Delimited":
                delim = self.delimiter_var.get()
                output = self.format_delimited(delim)
                file_ext = self.ext_var.get() or ".txt"
            elif fmt == "JSON":
                output = self.format_json()
                file_ext = ".json"
            elif fmt == "XML":
                output = self.format_xml()
                file_ext = ".xml"
            else:
                raise ValueError("Unsupported format.")

            save_path = filedialog.asksaveasfilename(defaultextension=file_ext)
            if not save_path:
                self.set_status("Save cancelled.")
                self.progress.stop()
                return

            with open(save_path, "w", encoding=encoding, errors="replace") as f:
                f.write(output)

            # Show file size and output stats
            size_bytes = os.path.getsize(save_path)
            size_kb = size_bytes / 1024

            lines_count = output.count('\n') + 1
            encoding_used = encoding

            summary = (f"Saved file: {save_path}\n"
                       f"Size: {size_kb:.2f} KB ({size_bytes} bytes)\n"
                       f"Lines: {lines_count}\n"
                       f"Encoding: {encoding_used}")

            self.show_summary(summary)
            messagebox.showinfo("Success", f"File saved successfully.\n\n{summary}")
            self.set_status("File saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Failed to save file.")
        finally:
            self.progress.stop()

    def set_status(self, message):
        self.status_label.config(text=message)

    def show_summary(self, summary_text):
        self.summary_label.config(text=summary_text)

    def show_data_summary(self):
        if self.df is None:
            self.summary_label.config(text="")
            return
        try:
            rows, cols = self.df.shape
            null_counts = self.df.isnull().sum()
            null_str = ", ".join(f"{col}: {cnt}" for col, cnt in null_counts.items() if cnt > 0)
            if not null_str:
                null_str = "No null values."
            summary = (f"Data summary:\nRows: {rows}\nColumns: {cols}\nNull counts per column:\n{null_str}")
            self.summary_label.config(text=summary)
        except Exception as e:
            self.summary_label.config(text="Error generating data summary.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelConverterApp(root)
    root.mainloop()
