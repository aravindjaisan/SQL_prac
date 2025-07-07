import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import xml.etree.ElementTree as ET
import os
import threading

class ExcelConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel Converter App")
        self.root.geometry("1000x750")
        self.root.configure(bg="lightgrey")

        self.file_path = None
        self.df = None
        self.col_width_entries = []
        self.xml_sample_path = None
        self.xml_sample_type = None

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)

        self.build_file_frame(main_frame)
        self.build_options_frame(main_frame)
        self.build_fixed_width_frame(main_frame)
        self.build_preview_frame(main_frame)
        self.build_dashboard(main_frame)
        self.build_progress_and_buttons(main_frame)
        self.build_status_area(main_frame)

    def build_file_frame(self, parent):
        file_frame = ttk.LabelFrame(parent, text="File Selection", padding=10)
        file_frame.grid(row=0, column=0, sticky="ew", pady=5)
        tk.Button(file_frame, text="Browse Excel File", command=self.load_excel, bg="green", fg="white").grid(row=0, column=0, sticky="w")
        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.grid(row=0, column=1, sticky="w", padx=10)

    def build_options_frame(self, parent):
        options_frame = ttk.LabelFrame(parent, text="Export Options", padding=10)
        options_frame.grid(row=1, column=0, sticky="ew", pady=5)

        ttk.Label(options_frame, text="Format:").grid(row=0, column=0, sticky="e", padx=5)
        self.format_var = tk.StringVar()
        self.format_combo = ttk.Combobox(options_frame, textvariable=self.format_var, state="readonly",
                                         values=["Fixed Width", "Delimited", "JSON", "XML"], width=20)
        self.format_combo.grid(row=0, column=1, sticky="w")
        self.format_combo.bind("<<ComboboxSelected>>", self.on_format_change)

        ttk.Label(options_frame, text="Delimiter:").grid(row=1, column=0, sticky="e", padx=5)
        self.delimiter_var = tk.StringVar()
        self.delimiter_combo = ttk.Combobox(options_frame, textvariable=self.delimiter_var, state="readonly",
                                            values=[",", "Single Pipe (|)", "Triple Pipe (|||)"], width=20)
        self.delimiter_combo.grid(row=1, column=1, sticky="w")

        ttk.Label(options_frame, text="File Extension:").grid(row=2, column=0, sticky="e", padx=5)
        self.ext_var = tk.StringVar()
        self.ext_combo = ttk.Combobox(options_frame, textvariable=self.ext_var, state="readonly",
                                      values=[".txt", ".csv", ".json", ".xml", ".xlsx"], width=20)
        self.ext_combo.grid(row=2, column=1, sticky="w")

        ttk.Label(options_frame, text="Encoding:").grid(row=3, column=0, sticky="e", padx=5)
        self.encoding_var = tk.StringVar(value="utf-8")
        self.encoding_combo = ttk.Combobox(options_frame, textvariable=self.encoding_var, state="readonly",
                                           values=["utf-8", "utf-16", "ascii", "iso-8859-1"], width=20)
        self.encoding_combo.grid(row=3, column=1, sticky="w")

        self.browse_xml_btn = tk.Button(options_frame, text="Browse XML/XSD", command=self.load_xml_sample, bg="orange", fg="white")
        self.browse_xml_btn.grid(row=4, column=0, columnspan=2, pady=5)
        self.browse_xml_btn.grid_remove()

    def build_fixed_width_frame(self, parent):
        self.fixed_frame = ttk.LabelFrame(parent, text="Fixed Width Column Settings", padding=10)
        self.fixed_frame.grid(row=2, column=0, sticky="ew", pady=5)

        self.width_canvas = tk.Canvas(self.fixed_frame, height=150, bg="lightgrey")
        self.width_canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.fixed_frame, orient="vertical", command=self.width_canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.width_canvas.configure(yscrollcommand=scrollbar.set)

        self.width_inner = ttk.Frame(self.width_canvas)
        self.width_canvas.create_window((0, 0), window=self.width_inner, anchor="nw")
        self.width_inner.bind("<Configure>", lambda e: self.width_canvas.configure(scrollregion=self.width_canvas.bbox("all")))

        self.fixed_frame.grid_remove()

    def build_preview_frame(self, parent):
        preview_frame = ttk.LabelFrame(parent, text="Preview Output (first 25 rows)", padding=10)
        preview_frame.grid(row=3, column=0, sticky="nsew", pady=5)
        self.preview_box = tk.Text(preview_frame, height=10, width=110)
        self.preview_box.pack()

    def build_dashboard(self, parent):
        dashboard_frame = ttk.LabelFrame(parent, text="File Stats", padding=10)
        dashboard_frame.grid(row=4, column=0, sticky="ew", pady=5)
        self.dashboard_label = ttk.Label(dashboard_frame, text="No data loaded", justify="left", foreground="green")
        self.dashboard_label.pack()

    def build_progress_and_buttons(self, parent):
        self.progress = ttk.Progressbar(parent, orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=5, column=0, pady=5)

        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=6, column=0, pady=5)

        tk.Button(btn_frame, text="Preview", command=self.preview_output, bg="red", fg="white").grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Convert & Save", command=self.convert_and_save, bg="blue", fg="white").grid(row=0, column=1, padx=5)

    def build_status_area(self, parent):
        self.status_label = ttk.Label(parent, text="", foreground="blue")
        self.status_label.grid(row=7, column=0, sticky="w")
        self.summary_label = ttk.Label(parent, text="", foreground="purple", justify="left")
        self.summary_label.grid(row=8, column=0, sticky="w")

    def load_excel(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if path:
            self.set_status("Loading Excel file...")
            threading.Thread(target=self.read_excel_file, args=(path,), daemon=True).start()

    def read_excel_file(self, path):
        try:
            self.progress.start()
            self.df = pd.read_excel(path)
            self.df = self.df.apply(lambda col: col.str.strip() if col.dtype == 'object' else col)
            self.file_path = path
            self.file_label.config(text=os.path.basename(path))
            self.update_dashboard()
            self.set_status("Excel file loaded successfully.")
            self.root.after(100, self.on_format_change)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Failed to load Excel file.")
        finally:
            self.progress.stop()

    def update_dashboard(self):
        if self.df is not None:
            rows, cols = self.df.shape
            nulls = self.df.isnull().sum()
            null_report = ", ".join([f"{col}: {val}" for col, val in nulls.items() if val > 0]) or "No null values."
            text = f"Rows: {rows} | Columns: {cols}\nNulls: {null_report}"
            self.dashboard_label.config(text=text)

    def update_options_visibility(self):
        fmt = self.format_var.get()
        self.fixed_frame.grid() if fmt == "Fixed Width" else self.fixed_frame.grid_remove()
        self.delimiter_combo.configure(state="readonly" if fmt == "Delimited" else "disabled")
        self.browse_xml_btn.grid() if fmt == "XML" else self.browse_xml_btn.grid_remove()

    def on_format_change(self, event=None):
        self.update_options_visibility()
        for widget in self.width_inner.winfo_children():
            widget.destroy()
        self.col_width_entries.clear()

        if self.df is not None and self.format_var.get() == "Fixed Width":
            for i, col in enumerate(self.df.columns):
                suggested_width = max(10, int(self.df[col].astype(str).str.len().max()))
                ttk.Label(self.width_inner, text=f"{col}:", width=20).grid(row=i, column=0, sticky="e")
                entry = ttk.Entry(self.width_inner, width=10)
                entry.insert(0, str(suggested_width))
                entry.grid(row=i, column=1, sticky="w")
                self.col_width_entries.append((col, entry))

    def load_xml_sample(self):
        path = filedialog.askopenfilename(filetypes=[("XML or XSD files", "*.xml *.xsd")])
        if path:
            ext = os.path.splitext(path)[1].lower()
            self.xml_sample_type = "xsd" if ext == ".xsd" else "xml"
            self.xml_sample_path = path
            msg = "XSD structure-based generation" if self.xml_sample_type == "xsd" else "XML file mapping based generation"
            messagebox.showinfo("XML/XSD Upload", f"Proceeding to preview with {msg}")

    def convert_df_to_sampled_xml(self, df):
        if self.xml_sample_type == "xml":
            tree = ET.parse(self.xml_sample_path)
            root_template = tree.getroot()
            root = ET.Element(root_template.tag)
            for _, row in df.iterrows():
                item = ET.SubElement(root, root_template[0].tag)
                for col in df.columns:
                    child = ET.SubElement(item, col)
                    val = "" if pd.isnull(row[col]) else str(row[col])
                    child.text = val
            return ET.tostring(root, encoding="unicode")
        else:
            return self.convert_df_to_xml(df)

    def convert_df_to_xml(self, df):
        def escape_xml(s):
            return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        root = ET.Element("Root")
        for _, row in df.iterrows():
            item = ET.SubElement(root, "Row")
            for col in df.columns:
                col_elem = ET.SubElement(item, col)
                val = "" if pd.isnull(row[col]) else escape_xml(row[col])
                col_elem.text = val
        return ET.tostring(root, encoding="unicode")

    def preview_output(self):
        if self.df is None:
            messagebox.showerror("Error", "No file loaded.")
            return
        try:
            preview_df = self.df.head(25)
            fmt = self.format_var.get()
            output = ""

            if fmt == "Fixed Width":
                widths = {col: int(entry.get()) for col, entry in self.col_width_entries}
                header = ''.join(col[:widths[col]].ljust(widths[col]) for col in self.df.columns)
                output += header + "\n"
                for _, row in preview_df.iterrows():
                    line = ''.join(str(row[col])[:widths[col]].ljust(widths[col]) if pd.notnull(row[col]) else ''.ljust(widths[col]) for col in self.df.columns)
                    output += line + "\n"
            elif fmt == "Delimited":
                delim_map = {",": ",", "Single Pipe (|)": "|", "Triple Pipe (|||)": "|||"}
                sep = delim_map.get(self.delimiter_var.get(), ",")
                output = preview_df.to_csv(index=False, sep="|")
                if sep == "|||":
                    output = output.replace("|", "|||")
                elif sep != "|":
                    output = preview_df.to_csv(index=False, sep=sep)
            elif fmt == "JSON":
                output = preview_df.to_json(orient="records", lines=True, force_ascii=False)
            elif fmt == "XML" and self.xml_sample_path:
                output = self.convert_df_to_sampled_xml(preview_df)
            else:
                output = self.convert_df_to_xml(preview_df)

            self.preview_box.delete("1.0", tk.END)
            self.preview_box.insert(tk.END, output)
            self.set_status("Preview generated.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Failed to generate preview.")

    def convert_and_save(self):
        if self.df is None:
            messagebox.showerror("Error", "No file loaded.")
            return
        self.set_status("Saving file...")
        threading.Thread(target=self._convert_and_save_thread, daemon=True).start()

    def _convert_and_save_thread(self):
        try:
            fmt = self.format_var.get()
            ext = self.ext_var.get() or ".txt"
            encoding = self.encoding_var.get() or "utf-8"
            save_path = filedialog.asksaveasfilename(defaultextension=ext,
                                                     filetypes=[(f"{ext} files", f"*{ext}"), ("All files", "*.*")],
                                                     initialfile="output" + ext)
            if not save_path:
                self.set_status("Save cancelled.")
                return

            if fmt == "Fixed Width":
                widths = {col: int(entry.get()) for col, entry in self.col_width_entries}
                with open(save_path, "w", encoding=encoding) as f:
                    header = ''.join(col[:widths[col]].ljust(widths[col]) for col in self.df.columns)
                    f.write(header + "\n")
                    for _, row in self.df.iterrows():
                        line = ''.join(str(row[col])[:widths[col]].ljust(widths[col]) if pd.notnull(row[col]) else ''.ljust(widths[col]) for col in self.df.columns)
                        f.write(line + "\n")
            elif fmt == "Delimited":
                sep = {",": ",", "Single Pipe (|)": "|", "Triple Pipe (|||)": "|||"}[self.delimiter_var.get()]
                csv = self.df.to_csv(index=False, sep="|", encoding=encoding)
                if sep == "|||":
                    csv = csv.replace("|", "|||")
                elif sep != "|":
                    csv = self.df.to_csv(index=False, sep=sep, encoding=encoding)
                with open(save_path, "w", encoding=encoding) as f:
                    f.write(csv)
            elif fmt == "JSON":
                self.df.to_json(save_path, orient="records", lines=True, force_ascii=False)
            elif fmt == "XML" and self.xml_sample_path:
                xml_str = self.convert_df_to_sampled_xml(self.df)
                with open(save_path, "w", encoding=encoding) as f:
                    f.write(xml_str)
            else:
                xml_str = self.convert_df_to_xml(self.df)
                with open(save_path, "w", encoding=encoding) as f:
                    f.write(xml_str)

            self.set_status(f"File saved: {save_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Failed to save file.")

    def set_status(self, message):
        self.status_label.config(text=message)

def main():
    root = tk.Tk()
    app = ExcelConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
