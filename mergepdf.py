import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfMerger

class PDFMergerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF Merger Tool")
        self.geometry("600x400")
        self.resizable(False, False)

        self.selected_files = []

        self.create_widgets()
        self.drag_data = {"dragging": False, "start_index": None}

    def create_widgets(self):
        # Frame for input files controls
        input_frame = tk.Frame(self, pady=10)
        input_frame.pack(fill="x")

        tk.Label(input_frame, text="Selected PDFs:", width=12, anchor="w").pack(side="left")
        btn_browse = tk.Button(input_frame, text="Browse PDFs", command=self.browse_input_files)
        btn_browse.pack(side="right", padx=10)

        # Listbox with scrollbar to display selected files
        listbox_frame = tk.Frame(self)
        listbox_frame.pack(fill="both", expand=True, padx=10)

        self.listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE, activestyle='none')
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Bindings for drag and drop reorder
        self.listbox.bind("<ButtonPress-1>", self.on_start_drag)
        self.listbox.bind("<B1-Motion>", self.on_drag_motion)
        self.listbox.bind("<ButtonRelease-1>", self.on_drop)

        # Output file selection frame
        output_frame = tk.Frame(self, pady=10)
        output_frame.pack(fill="x", padx=10)

        tk.Label(output_frame, text="Output File:", width=12, anchor="w").pack(side="left")

        self.output_file_var = tk.StringVar()
        self.output_entry = tk.Entry(output_frame, textvariable=self.output_file_var)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=5)

        btn_browse_output = tk.Button(output_frame, text="Browse", command=self.browse_output_file)
        btn_browse_output.pack(side="right")

        # Merge button frame
        btn_frame = tk.Frame(self, pady=20)
        btn_frame.pack()

        btn_merge = tk.Button(btn_frame, text="Merge PDFs", command=self.merge_button_clicked,
                              width=20, height=2, bg="#4CAF50", fg="white")
        btn_merge.pack()

    def browse_input_files(self):
        files = filedialog.askopenfilenames(
            filetypes=[("PDF files", "*.pdf")],
            title="Select PDFs to Merge"
        )
        if files:
            self.selected_files = list(files)
            self.update_listbox()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for f in self.selected_files:
            # Show only the file name, not full path
            self.listbox.insert(tk.END, os.path.basename(f))

    def browse_output_file(self):
        file = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save Merged PDF As"
        )
        if file:
            self.output_file_var.set(file)

    def merge_button_clicked(self):
        output_pdf = self.output_file_var.get()
        if not self.selected_files:
            messagebox.showwarning("Missing Input", "Please select input files.")
            return
        if not output_pdf:
            messagebox.showwarning("Missing Input", "Please select output file.")
            return

        # Merge in the order of listbox items
        # Because the listbox only shows basenames, we map back to full paths in self.selected_files
        ordered_files = [self.selected_files[idx] for idx in range(len(self.selected_files))]
        # But we need to reorder according to the current listbox order
        # The listbox items order might differ if the user reordered via drag-drop
        # So use the current listbox order to reorder self.selected_files

        # Get the filenames from listbox in current order
        current_order_names = [self.listbox.get(i) for i in range(self.listbox.size())]

        # Create a dict basename -> full path for fast lookup
        basename_to_path = {os.path.basename(path): path for path in self.selected_files}

        # Map current order names to full paths
        ordered_files = [basename_to_path[name] for name in current_order_names]

        self.merge_pdfs(ordered_files, output_pdf)

    def merge_pdfs(self, files, output_pdf):
        merger = PdfMerger()

        for file_path in files:
            if os.path.exists(file_path):
                merger.append(file_path)
            else:
                messagebox.showwarning("Missing File", f"File not found:\n{file_path}")

        try:
            merger.write(output_pdf)
            merger.close()
            messagebox.showinfo("Success", f"PDFs merged successfully into:\n{output_pdf}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write merged PDF:\n{e}")

    # --- Drag and drop handlers ---
    def on_start_drag(self, event):
        self.drag_data["start_index"] = self.listbox.nearest(event.y)
        self.drag_data["dragging"] = True

    def on_drag_motion(self, event):
        if not self.drag_data["dragging"]:
            return
        curr_index = self.listbox.nearest(event.y)
        start_index = self.drag_data["start_index"]
        if curr_index != start_index:
            # Swap items visually
            self.selected_files[start_index], self.selected_files[curr_index] = (
                self.selected_files[curr_index], self.selected_files[start_index]
            )
            self.update_listbox()
            # Keep the dragged item selected
            self.listbox.select_set(curr_index)
            self.drag_data["start_index"] = curr_index

    def on_drop(self, event):
        self.drag_data["dragging"] = False
        self.drag_data["start_index"] = None


if __name__ == "__main__":
    app = PDFMergerGUI()
    app.mainloop()
