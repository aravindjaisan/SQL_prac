import tkinter as tk
from tkinter import filedialog, ttk, messagebox, simpledialog
import pandas as pd
import xml.etree.ElementTree as ET
import os
import threading
import re
import json
import xmlschema
from io import StringIO

# ---------------------------
# Helper Classes for Validation
# ---------------------------

class ValidationRule:
    def __init__(self, col_name, rule_type, param=None):
        self.col_name = col_name
        self.rule_type = rule_type  # e.g. 'not_null', 'date', 'regex'
        self.param = param          # e.g. regex pattern

    def validate(self, series: pd.Series):
        errors = []
        if self.rule_type == "not_null":
            invalid_rows = series[series.isnull()]
            for idx in invalid_rows.index:
                errors.append((idx, f"Null value in column '{self.col_name}'"))
        elif self.rule_type == "date":
            # Attempt to convert to datetime, errors if fail
            invalid_rows = []
            for idx, val in series.items():
                if pd.isnull(val):
                    continue
                try:
                    pd.to_datetime(val)
                except Exception:
                    invalid_rows.append(idx)
            for idx in invalid_rows:
                errors.append((idx, f"Invalid date in column '{self.col_name}': {series[idx]}"))
        elif self.rule_type == "regex":
            pattern = re.compile(self.param)
            invalid_rows = series[~series.fillna("").astype(str).apply(lambda x: bool(pattern.fullmatch(x)))]
            for idx in invalid_rows.index:
                errors.append((idx, f"Regex mismatch in '{self.col_name}': {series[idx]}"))
        return errors

# ---------------------------
# Main App Class
# ---------------------------

class ExcelConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel Converter & Validator App")
        self.root.geometry("1100x850")
        self.root.configure(bg="lightgrey")

        # Data and states
        self.file_path = None
        self.df = None
        self.col_width_entries = []
        self.xml_sample_path = None
        self.xml_sample_type = None  # 'xml' or 'xsd'
        self.validation_rules = []  # List[ValidationRule]
        self.validation_enabled = tk.BooleanVar(value=False)
        self.reverse_mode = tk.BooleanVar(value=False)
        self.reverse_file_path = None
        self.reverse_df = None
        self.fixed_width_entries_reverse = []

        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # Forward Conversion Tab (Excel to Other)
        self.tab_forward = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_forward, text="Excel → Other")

        # Reverse Conversion Tab (Other to Excel)
        self.tab_reverse = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_reverse, text="Other → Excel")

        # Validation Editor Tab
        self.tab_validation = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_validation, text="Validation Editor")

        self.build_forward_tab(self.tab_forward)
        self.build_reverse_tab(self.tab_reverse)
        self.build_validation_tab(self.tab_validation)

    # ------------- Forward Tab --------------

    def build_forward_tab(self, parent):
        # File selection frame
        file_frame = ttk.LabelFrame(parent, text="Excel File Selection", padding=10)
        file_frame.pack(fill="x", pady=5)
        tk.Button(file_frame, text="Browse Excel File", command=self.load_excel, bg="green", fg="white").pack(side="left")
        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.pack(side="left", padx=10)

        # Format options frame
        options_frame = ttk.LabelFrame(parent, text="Export Options", padding=10)
        options_frame.pack(fill="x", pady=5)

        ttk.Label(options_frame, text="Format:").grid(row=0, column=0, sticky="e", padx=5)
        self.format_var = tk.StringVar(value="Fixed Width")
        self.format_combo = ttk.Combobox(options_frame, textvariable=self.format_var, state="readonly",
                                         values=["Fixed Width", "Delimited", "JSON", "XML"], width=20)
        self.format_combo.grid(row=0, column=1, sticky="w")
        self.format_combo.bind("<<ComboboxSelected>>", self.on_format_change)

        ttk.Label(options_frame, text="Delimiter:").grid(row=1, column=0, sticky="e", padx=5)
        self.delimiter_var = tk.StringVar(value=",")
        self.delimiter_combo = ttk.Combobox(options_frame, textvariable=self.delimiter_var, state="readonly",
                                            values=[",", "Single Pipe (|)", "Triple Pipe (|||)"], width=20)
        self.delimiter_combo.grid(row=1, column=1, sticky="w")

        ttk.Label(options_frame, text="File Extension:").grid(row=2, column=0, sticky="e", padx=5)
        self.ext_var = tk.StringVar(value=".txt")
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

        # Validation toggle
        self.schema_check_cb = ttk.Checkbutton(options_frame, text="Enable schema/XSD conformity check before save",
                                               variable=self.validation_enabled)
        self.schema_check_cb.grid(row=5, column=0, columnspan=2, pady=5)

        # Fixed width frame
        self.fixed_frame = ttk.LabelFrame(parent, text="Fixed Width Column Settings", padding=10)
        self.fixed_frame.pack(fill="x", pady=5)

        self.width_canvas = tk.Canvas(self.fixed_frame, height=150, bg="lightgrey")
        self.width_canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.fixed_frame, orient="vertical", command=self.width_canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.width_canvas.configure(yscrollcommand=scrollbar.set)

        self.width_inner = ttk.Frame(self.width_canvas)
        self.width_canvas.create_window((0, 0), window=self.width_inner, anchor="nw")
        self.width_inner.bind("<Configure>", lambda e: self.width_canvas.configure(scrollregion=self.width_canvas.bbox("all")))

        self.fixed_frame.pack_forget()

        # Preview frame
        preview_frame = ttk.LabelFrame(parent, text="Preview Output (first 25 rows)", padding=10)
        preview_frame.pack(fill="both", expand=True, pady=5)
        self.preview_box = tk.Text(preview_frame, height=15, width=120)
        self.preview_box.pack(expand=True, fill="both")

        # Validation summary below preview
        self.validation_summary_label = ttk.Label(preview_frame, text="", foreground="red", justify="left")
        self.validation_summary_label.pack(fill="x")

        # Dashboard frame
        dashboard_frame = ttk.LabelFrame(parent, text="File Stats", padding=10)
        dashboard_frame.pack(fill="x", pady=5)
        self.dashboard_label = ttk.Label(dashboard_frame, text="No data loaded", justify="left", foreground="green")
        self.dashboard_label.pack()

        # Progress and buttons
        self.progress = ttk.Progressbar(parent, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=5)

        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Preview", command=self.preview_output, bg="red", fg="white").grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Convert & Save", command=self.convert_and_save, bg="blue", fg="white").grid(row=0, column=1, padx=5)

        # Status area
        self.status_label = ttk.Label(parent, text="", foreground="blue")
        self.status_label.pack(anchor="w", padx=10)
        self.summary_label = ttk.Label(parent, text="", foreground="purple", justify="left")
        self.summary_label.pack(anchor="w", padx=10)

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

    def update_options_visibility(self):
        fmt = self.format_var.get()
        if fmt == "Fixed Width":
            self.fixed_frame.pack(fill="x", pady=5)
        else:
            self.fixed_frame.pack_forget()

        if fmt == "Delimited":
            self.delimiter_combo.configure(state="readonly")
        else:
            self.delimiter_combo.configure(state="disabled")

        if fmt == "XML":
            self.browse_xml_btn.grid()
        else:
            self.browse_xml_btn.grid_remove()

    def load_excel(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if path:
            self.set_status("Loading Excel file...")
            threading.Thread(target=self.read_excel_file, args=(path,), daemon=True).start()

    def read_excel_file(self, path):
        try:
            self.progress.start()
            self.df = pd.read_excel(path)
            # Strip strings
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
        elif self.xml_sample_type == "xsd":
            # Generate XML using XSD structure is complex;
            # Here just call generic XML converter for demo
            return self.convert_df_to_xml(df)
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
                widths = []
                for col, entry in self.col_width_entries:
                    try:
                        w = int(entry.get())
                        widths.append(w)
                    except:
                        messagebox.showerror("Error", f"Invalid width for column '{col}'")
                        return
                lines = []
                for _, row in preview_df.iterrows():
                    line = ""
                    for col, width in zip(preview_df.columns, widths):
                        val = "" if pd.isnull(row[col]) else str(row[col])
                        val = val[:width].ljust(width)
                        line += val
                    lines.append(line)
                output = "\n".join(lines)
            elif fmt == "Delimited":
                delim_map = {",": ",", "Single Pipe (|)": "|", "Triple Pipe (|||)": "|||"}
                delim = delim_map.get(self.delimiter_var.get(), ",")
                output = preview_df.to_csv(sep=delim, index=False)
            elif fmt == "JSON":
                output = preview_df.to_json(orient="records", indent=2)
            elif fmt == "XML":
                output = self.convert_df_to_sampled_xml(preview_df)
            else:
                output = "Unsupported format."

            self.preview_box.delete("1.0", tk.END)
            self.preview_box.insert(tk.END, output)

            # Perform validation if enabled
            if self.validation_enabled.get():
                self.perform_validation(preview_df)
            else:
                self.validation_summary_label.config(text="")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview: {e}")

    def perform_validation(self, df_for_validation):
        errors = []
        for rule in self.validation_rules:
            errors.extend(rule.validate(df_for_validation[rule.col_name]))

        # Schema/XSD validation if enabled and XSD uploaded
        schema_errors = []
        if self.validation_enabled.get() and self.xml_sample_type == "xsd" and self.xml_sample_path:
            try:
                schema = xmlschema.XMLSchema(self.xml_sample_path)
                xml_str = self.convert_df_to_sampled_xml(df_for_validation)
                schema.validate(xml_str)
            except xmlschema.validators.exceptions.XMLSchemaValidationError as e:
                schema_errors.append(str(e))
            except Exception as e:
                schema_errors.append(f"Schema validation failed: {e}")

        summary = ""
        if errors or schema_errors:
            summary += f"Validation errors: {len(errors)} column rule errors, {len(schema_errors)} schema errors.\n"
            for idx, msg in errors[:10]:
                summary += f"Row {idx + 1}: {msg}\n"
            for err in schema_errors:
                summary += f"Schema Error: {err}\n"
        else:
            summary = "No validation errors found."

        self.validation_summary_label.config(text=summary)

    def convert_and_save(self):
        if self.df is None:
            messagebox.showerror("Error", "No file loaded.")
            return
        if self.validation_enabled.get():
            # Validate full df before save
            self.perform_validation(self.df)
            if "Validation errors" in self.validation_summary_label.cget("text"):
                res = messagebox.askyesno("Validation Errors",
                                          "Validation errors detected. Save anyway?")
                if not res:
                    return

        save_path = filedialog.asksaveasfilename(defaultextension=self.ext_var.get(),
                                                 filetypes=[("All files", "*.*")])
        if not save_path:
            return

        fmt = self.format_var.get()
        try:
            if fmt == "Fixed Width":
                widths = []
                for col, entry in self.col_width_entries:
                    widths.append(int(entry.get()))
                lines = []
                for _, row in self.df.iterrows():
                    line = ""
                    for col, width in zip(self.df.columns, widths):
                        val = "" if pd.isnull(row[col]) else str(row[col])
                        val = val[:width].ljust(width)
                        line += val
                    lines.append(line)
                with open(save_path, "w", encoding=self.encoding_var.get()) as f:
                    f.write("\n".join(lines))
            elif fmt == "Delimited":
                delim_map = {",": ",", "Single Pipe (|)": "|", "Triple Pipe (|||)": "|||"}
                delim = delim_map.get(self.delimiter_var.get(), ",")
                self.df.to_csv(save_path, sep=delim, index=False, encoding=self.encoding_var.get())
            elif fmt == "JSON":
                self.df.to_json(save_path, orient="records", indent=2)
            elif fmt == "XML":
                xml_str = self.convert_df_to_sampled_xml(self.df)
                with open(save_path, "w", encoding=self.encoding_var.get()) as f:
                    f.write(xml_str)
            else:
                messagebox.showerror("Error", "Unsupported format for saving.")
                return
            self.set_status(f"File saved successfully to {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def set_status(self, msg):
        self.status_label.config(text=msg)
        self.root.after(5000, lambda: self.status_label.config(text=""))

    # ------------- Validation Tab --------------

    def build_validation_tab(self, parent):
        instructions = ("Define validation rules per column.\n"
                        "Supported rules:\n"
                        "- Not Null\n"
                        "- Date\n"
                        "- Regex (provide pattern)\n\n"
                        "Select column, choose rule, set parameter if needed, then add.\n"
                        "You can save/load validation config as JSON.")
        ttk.Label(parent, text=instructions, justify="left").pack(anchor="w", pady=5, padx=5)

        # Dropdown to select column
        self.val_col_var = tk.StringVar()
        self.val_rule_var = tk.StringVar()
        self.val_param_var = tk.StringVar()

        frm = ttk.Frame(parent)
        frm.pack(pady=10, padx=10, fill="x")

        ttk.Label(frm, text="Column:").grid(row=0, column=0, sticky="e")
        self.val_col_combo = ttk.Combobox(frm, textvariable=self.val_col_var, state="readonly")
        self.val_col_combo.grid(row=0, column=1, sticky="w", padx=5)

        ttk.Label(frm, text="Rule:").grid(row=1, column=0, sticky="e")
        self.val_rule_combo = ttk.Combobox(frm, textvariable=self.val_rule_var, state="readonly",
                                           values=["not_null", "date", "regex"])
        self.val_rule_combo.grid(row=1, column=1, sticky="w", padx=5)
        self.val_rule_combo.bind("<<ComboboxSelected>>", self.on_rule_change)

        ttk.Label(frm, text="Parameter:").grid(row=2, column=0, sticky="e")
        self.val_param_entry = ttk.Entry(frm, textvariable=self.val_param_var, state="disabled")
        self.val_param_entry.grid(row=2, column=1, sticky="w", padx=5)

        ttk.Button(frm, text="Add Rule", command=self.add_validation_rule).grid(row=3, column=0, columnspan=2, pady=5)

        # Validation rules display
        self.rules_listbox = tk.Listbox(parent, height=10)
        self.rules_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.rules_listbox.bind("<Delete>", self.remove_selected_rule)

        # Save/Load buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Save Validation Config", command=self.save_validation_config).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Load Validation Config", command=self.load_validation_config).pack(side="left", padx=5)

        self.update_validation_columns()

    def update_validation_columns(self):
        if self.df is not None:
            self.val_col_combo["values"] = list(self.df.columns)
        else:
            self.val_col_combo["values"] = []

    def on_rule_change(self, event=None):
        rule = self.val_rule_var.get()
        if rule == "regex":
            self.val_param_entry.configure(state="normal")
        else:
            self.val_param_var.set("")
            self.val_param_entry.configure(state="disabled")

    def add_validation_rule(self):
        col = self.val_col_var.get()
        rule = self.val_rule_var.get()
        param = self.val_param_var.get().strip()

        if not col or not rule:
            messagebox.showerror("Error", "Please select column and rule.")
            return
        if rule == "regex" and not param:
            messagebox.showerror("Error", "Please provide regex pattern parameter.")
            return

        new_rule = ValidationRule(col, rule, param if rule == "regex" else None)
        self.validation_rules.append(new_rule)
        self.rules_listbox.insert(tk.END, f"{col} - {rule} {param}")
        self.set_status(f"Added validation rule for {col}")

    def remove_selected_rule(self, event=None):
        sel = self.rules_listbox.curselection()
        if sel:
            idx = sel[0]
            self.rules_listbox.delete(idx)
            self.validation_rules.pop(idx)
            self.set_status("Removed selected validation rule")

    def save_validation_config(self):
        if not self.validation_rules:
            messagebox.showinfo("Info", "No validation rules to save.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("JSON files", "*.json")])
        if not path:
            return
        try:
            to_save = []
            for rule in self.validation_rules:
                to_save.append({
                    "col_name": rule.col_name,
                    "rule_type": rule.rule_type,
                    "param": rule.param
                })
            with open(path, "w") as f:
                json.dump(to_save, f, indent=2)
            self.set_status(f"Validation config saved to {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save validation config: {e}")

    def load_validation_config(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path:
            return
        try:
            with open(path) as f:
                loaded = json.load(f)
            self.validation_rules.clear()
            self.rules_listbox.delete(0, tk.END)
            for r in loaded:
                rule = ValidationRule(r["col_name"], r["rule_type"], r.get("param"))
                self.validation_rules.append(rule)
                display_param = rule.param if rule.param else ""
                self.rules_listbox.insert(tk.END, f"{rule.col_name} - {rule.rule_type} {display_param}")
            self.set_status(f"Loaded validation config from {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load validation config: {e}")

    # ------------- Reverse Tab --------------

    def build_reverse_tab(self, parent):
        file_frame = ttk.LabelFrame(parent, text="Input File Selection (XML, JSON, CSV, Fixed Width)", padding=10)
        file_frame.pack(fill="x", pady=5)

        tk.Button(file_frame, text="Browse Input File", command=self.load_reverse_file, bg="green", fg="white").pack(side="left")
        self.rev_file_label = ttk.Label(file_frame, text="No file selected")
        self.rev_file_label.pack(side="left", padx=10)

        options_frame = ttk.LabelFrame(parent, text="Input Format Options", padding=10)
        options_frame.pack(fill="x", pady=5)

        ttk.Label(options_frame, text="Input Format:").grid(row=0, column=0, sticky="e", padx=5)
        self.rev_format_var = tk.StringVar(value="Auto Detect")
        self.rev_format_combo = ttk.Combobox(options_frame, textvariable=self.rev_format_var, state="readonly",
                                            values=["Auto Detect", "XML", "JSON", "CSV", "Fixed Width"], width=20)
        self.rev_format_combo.grid(row=0, column=1, sticky="w")
        self.rev_format_combo.bind("<<ComboboxSelected>>", self.on_reverse_format_change)

        ttk.Label(options_frame, text="Delimiter (for CSV):").grid(row=1, column=0, sticky="e", padx=5)
        self.rev_delimiter_var = tk.StringVar(value=",")
        self.rev_delimiter_combo = ttk.Combobox(options_frame, textvariable=self.rev_delimiter_var, state="readonly",
                                                values=[",", "|", "|||"], width=20)
        self.rev_delimiter_combo.grid(row=1, column=1, sticky="w")

        self.rev_fixed_width_frame = ttk.LabelFrame(parent, text="Fixed Width Column Widths", padding=10)
        self.rev_fixed_width_frame.pack(fill="x", pady=5)
        self.rev_fixed_width_inner = ttk.Frame(self.rev_fixed_width_frame)
        self.rev_fixed_width_inner.pack(fill="x")

        preview_frame = ttk.LabelFrame(parent, text="Preview Parsed Excel Table (first 25 rows)", padding=10)
        preview_frame.pack(fill="both", expand=True, pady=5)
        self.rev_preview_box = tk.Text(preview_frame, height=15, width=120)
        self.rev_preview_box.pack(expand=True, fill="both")

        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Preview Parsed Table", command=self.reverse_preview, bg="red", fg="white").grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Save as Excel", command=self.reverse_save_excel, bg="blue", fg="white").grid(row=0, column=1, padx=5)

        self.rev_fixed_width_frame.pack_forget()

    def load_reverse_file(self):
        path = filedialog.askopenfilename(filetypes=[("All supported", "*.xml *.json *.csv *.txt *.dat *.fwf")])
        if path:
            self.reverse_file_path = path
            self.rev_file_label.config(text=os.path.basename(path))
            self.auto_detect_reverse_format()

    def auto_detect_reverse_format(self):
        if not self.reverse_file_path:
            return
        ext = os.path.splitext(self.reverse_file_path)[1].lower()
        detected_format = "Auto Detect"
        if ext == ".xml":
            detected_format = "XML"
        elif ext == ".json":
            detected_format = "JSON"
        elif ext in [".csv", ".txt"]:
            detected_format = "CSV"
        elif ext in [".fwf", ".dat"]:
            detected_format = "Fixed Width"
        self.rev_format_var.set(detected_format)
        self.on_reverse_format_change()

    def on_reverse_format_change(self, event=None):
        fmt = self.rev_format_var.get()
        if fmt == "Fixed Width":
            self.rev_fixed_width_frame.pack(fill="x", pady=5)
            # Try to populate widths if df available
            for widget in self.rev_fixed_width_inner.winfo_children():
                widget.destroy()
            self.fixed_width_entries_reverse.clear()
            # No df yet, so just placeholder widths for now
            ttk.Label(self.rev_fixed_width_inner, text="Define column widths separated by commas (e.g. 10,5,20)").pack(anchor="w")
            self.rev_fixed_width_entry = ttk.Entry(self.rev_fixed_width_inner, width=50)
            self.rev_fixed_width_entry.pack(anchor="w", pady=2)
        else:
            self.rev_fixed_width_frame.pack_forget()

    def reverse_preview(self):
        if not self.reverse_file_path:
            messagebox.showerror("Error", "No input file selected.")
            return
        fmt = self.rev_format_var.get()
        if fmt == "Auto Detect":
            self.auto_detect_reverse_format()
            fmt = self.rev_format_var.get()
        try:
            if fmt == "XML":
                tree = ET.parse(self.reverse_file_path)
                root = tree.getroot()
                data = []
                cols = set()
                for child in root:
                    row_dict = {}
                    for elem in child:
                        row_dict[elem.tag] = elem.text
                        cols.add(elem.tag)
                    data.append(row_dict)
                cols = list(cols)
                df = pd.DataFrame(data, columns=cols)
            elif fmt == "JSON":
                df = pd.read_json(self.reverse_file_path)
            elif fmt == "CSV":
                delim = self.rev_delimiter_var.get()
                df = pd.read_csv(self.reverse_file_path, sep=delim)
            elif fmt == "Fixed Width":
                if not hasattr(self, "rev_fixed_width_entry"):
                    messagebox.showerror("Error", "Please define fixed width column widths.")
                    return
                widths_text = self.rev_fixed_width_entry.get()
                try:
                    widths = [int(w.strip()) for w in widths_text.split(",")]
                except:
                    messagebox.showerror("Error", "Invalid fixed width column widths.")
                    return
                df = pd.read_fwf(self.reverse_file_path, widths=widths)
            else:
                messagebox.showerror("Error", "Unsupported input format.")
                return

            preview_text = df.head(25).to_string(index=False)
            self.rev_preview_box.delete("1.0", tk.END)
            self.rev_preview_box.insert(tk.END, preview_text)
            self.reverse_df = df
            self.set_status("Preview loaded for reverse conversion.")

            # Update validation columns on main tab as well if applicable
            if fmt in ["CSV", "Fixed Width"]:
                self.df = df
                self.update_validation_columns()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse file: {e}")

    def reverse_save_excel(self):
        if not hasattr(self, "reverse_df"):
            messagebox.showerror("Error", "No preview available to save.")
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                 filetypes=[("Excel files", "*.xlsx")])
        if not save_path:
            return
        try:
            self.reverse_df.to_excel(save_path, index=False)
            self.set_status(f"Reverse converted file saved as {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save Excel file: {e}")

# ------------- ValidationRule class -------------

class ValidationRule:
    def __init__(self, col_name, rule_type, param=None):
        self.col_name = col_name
        self.rule_type = rule_type
        self.param = param

    def validate(self, series):
        errors = []
        if self.rule_type == "not_null":
            for idx, val in series.items():
                if pd.isnull(val) or (isinstance(val, str) and val.strip() == ""):
                    errors.append((idx, "Value cannot be null or empty"))
        elif self.rule_type == "date":
            for idx, val in series.items():
                if pd.isnull(val):
                    continue
                try:
                    pd.to_datetime(val)
                except:
                    errors.append((idx, f"Invalid date: {val}"))
        elif self.rule_type == "regex":
            pattern = self.param
            import re
            for idx, val in series.items():
                if pd.isnull(val):
                    continue
                if not re.match(pattern, str(val)):
                    errors.append((idx, f"Value does not match pattern: {pattern}"))
        return errors

# ------------- Main program --------------

if __name__ == "__main__":
    import pandas as pd
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    import os
    import json
    import xml.etree.ElementTree as ET
    import xmlschema

    root = tk.Tk()
    app = ExcelConverterApp(root)
    root.mainloop()
