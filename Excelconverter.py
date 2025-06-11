import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import xml.etree.ElementTree as ET

class ConvertExcel:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Excel Converter")

        self.df = None

        # Buttons and UI Elements
        self.load_button = tk.Button(root, text="Load Excel File", command=self.load_excel)
        self.load_button.pack(pady=10)

        self.format_label = tk.Label(root, text="Select Output Format:")
        self.format_label.pack()

        self.format_var = tk.StringVar()
        self.format_var.set("CSV")

        self.format_dropdown = tk.OptionMenu(root, self.format_var, "CSV", "JSON", "XML", "Delimited", "Fixed Width", command=self.on_format_change)
        self.format_dropdown.pack()

        self.delim_label = tk.Label(root, text="Select Delimiter:")
        self.delim_options = ["Comma (,)", "Pipe (|)"]
        self.delim_var = tk.StringVar()
        self.delim_var.set(self.delim_options[0])
        self.delim_dropdown = tk.OptionMenu(root, self.delim_var, *self.delim_options)
        # Don't pack it yet — only when Delimited is selected

        self.convert_button = tk.Button(root, text="Convert and Save", command=self.convert_and_save)
        self.convert_button.pack(pady=10)

        self.status_label = tk.Label(root, text="")
        self.status_label.pack()

    def on_format_change(self, value):
        if value == "Delimited":
            self.delim_label.pack()
            self.delim_dropdown.pack()
        else:
            self.delim_label.pack_forget()
            self.delim_dropdown.pack_forget()

    def load_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if file_path:
            try:
                self.df = pd.read_excel(file_path)
                self.status_label.config(text="Excel file loaded.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def convert_and_save(self):
        if self.df is None:
            messagebox.showerror("Error", "Please load an Excel file first.")
            return

        format_choice = self.format_var.get()
        save_ext = "txt" if format_choice in ["Delimited", "Fixed Width"] else format_choice.lower()
        save_path = filedialog.asksaveasfilename(defaultextension=f".{save_ext}")

        if not save_path:
            return

        try:
            if format_choice == "CSV":
                self.df.to_csv(save_path, index=False)
            elif format_choice == "JSON":
                self.df.to_json(save_path, orient="records", indent=4)
            elif format_choice == "XML":
                self.save_as_xml(save_path)
            elif format_choice == "Delimited":
                self.save_as_delimited(save_path)
            elif format_choice == "Fixed Width":
                self.save_as_fixed_width(save_path)
            else:
                messagebox.showerror("Error", "Unknown format selected.")
                return

            messagebox.showinfo("Success", f"File saved to:\n{save_path}")
            self.status_label.config(text="File saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_as_xml(self, save_path):
        root = ET.Element("Rows")
        for _, row in self.df.iterrows():
            row_elem = ET.SubElement(root, "Row")
            for col in self.df.columns:
                child = ET.SubElement(row_elem, col)
                child.text = str(row[col]) if pd.notnull(row[col]) else ''
        tree_str = ET.tostring(root, encoding="unicode")
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(tree_str)

    def save_as_delimited(self, save_path):
        delimiter = ',' if self.delim_var.get() == "Comma (,)" else '|'
        self.df.to_csv(save_path, index=False, sep=delimiter)

    def save_as_fixed_width(self, save_path):
        # Calculate max width for each column
        col_widths = [max(len(str(x)) for x in [col] + self.df[col].astype(str).tolist()) for col in self.df.columns]

        with open(save_path, "w", encoding="utf-8") as f:
            # Write header
            header = "".join(str(col).ljust(width + 2) for col, width in zip(self.df.columns, col_widths))
            f.write(header + "\n")
            # Write data
            for _, row in self.df.iterrows():
                line = "".join(str(row[col]).ljust(width + 2) for col, width in zip(self.df.columns, col_widths))
                f.write(line + "\n")


# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = ConvertExcel(root)
    root.mainloop()
