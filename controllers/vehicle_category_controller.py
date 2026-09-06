import csv
import sqlite3
from datetime import datetime
import pandas as pd
from tkinter import filedialog, messagebox
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from factories import ModelFactory
#from models.vehicle_category_model import VehicleCategoryModel


class VehicleCategoryController:
    def __init__(self, db):
        self.db = db
        self.model = ModelFactory.create_model("vehicle_category", db=db)

    # ---------- READ ----------

    def get_all_categories(self):
        return self.model.get_all()

    def get_category_by_id(self, category_id):
        return self.model.get_by_id(category_id)

    def search_categories(self, term):
        if not term:
            return self.get_all_categories()
        return self.model.search(term)

    # ---------- VALIDATION HELPER ----------

    def _validate(self, data):
        name = data.get('name', '').strip()
        base_rate = data.get('base_rate', '').strip()
        late_fee = data.get('late_fee_rate', '').strip()

        if not name:
            return None, 'Category name is required'

        try:
            base_rate = float(base_rate)
            if base_rate < 0:
                return None, 'Base rate cannot be negative'
        except ValueError:
            return None, 'Base rate must be a number'

        try:
            late_fee = float(late_fee) if late_fee else 0
            if late_fee < 0:
                return None, 'Late fee rate cannot be negative'
        except ValueError:
            return None, 'Late fee rate must be a number'

        status = 1 if data.get('status', '1') == '1' else 0
        description = data.get('description', '').strip()

        return {
            'name': name,
            'description': description,
            'base_rate': base_rate,
            'late_fee_rate': late_fee,
            'status': status
        }, None

    # ---------- CREATE ----------

    def add_category(self, data):
        clean, error = self._validate(data)
        if error:
            return {'success': False, 'message': error}

        result = self.model.insert(
            clean['name'], clean['description'],
            clean['base_rate'], clean['late_fee_rate'], clean['status']
        )
        if result is None:
            return {'success': False, 'message': 'Category name already exists or failed to add'}
        return {'success': True, 'message': 'Category added successfully'}

    # ---------- UPDATE ----------

    def update_category(self, category_id, data):
        clean, error = self._validate(data)
        if error:
            return {'success': False, 'message': error}

        result = self.model.update(
            category_id, clean['name'], clean['description'],
            clean['base_rate'], clean['late_fee_rate'], clean['status']
        )
        if result is None:
            return {'success': False, 'message': 'Failed to update category'}
        return {'success': True, 'message': 'Category updated successfully'}

    # ---------- DELETE ----------

    def delete_category(self, category_id):
        result = self.model.delete(category_id)
        if result is None:
            return {'success': False, 'message': 'Failed to delete category'}
        return {'success': True, 'message': 'Category deleted successfully'}

    # ---------- TOGGLE ----------

    def toggle_status(self, category_id, current_status):
        new_status = 0 if current_status == 1 else 1
        result = self.model.toggle_status(category_id, new_status)
        if result is None:
            return {'success': False, 'message': 'Failed to toggle status'}
        action = 'activated' if new_status == 1 else 'deactivated'
        return {'success': True, 'message': f'Category {action} successfully'}

    # ---------- EXPORT: CSV ----------

    def export_to_csv(self, categories):
        filename = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv')],
            initialfile=f'vehicle_categories_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Name', 'Description', 'Base Rate', 'Late Fee Rate', 'Status', 'Created At'])
                for row in categories:
                    status = 'Active' if row['category_status'] == 1 else 'Inactive'
                    writer.writerow([
                        row['id'], 
                        row['name'], 
                        row['description'] or '',
                        f"${row['base_rate']:.2f}", 
                        f"${row['late_fee_rate']:.2f}",
                        status,
                        row['created_at'] or ''
                    ])
            messagebox.showinfo('Success', f'Exported to CSV:\n{filename}')
        except Exception as e:
            messagebox.showerror('Error', f'CSV export failed: {e}')

    # ---------- EXPORT: EXCEL ----------

    def export_to_excel(self, categories):
        filename = filedialog.asksaveasfilename(
            defaultextension='.xlsx',
            filetypes=[('Excel files', '*.xlsx')],
            initialfile=f'vehicle_categories_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
        if not filename:
            return

        try:
            data = []
            for row in categories:
                status = 'Active' if row['category_status'] == 1 else 'Inactive'
                data.append({
                    'ID': row['id'],
                    'Name': row['name'],
                    'Description': row['description'] or '',
                    'Base Rate': f"${row['base_rate']:.2f}",
                    'Late Fee Rate': f"${row['late_fee_rate']:.2f}",
                    'Status': status,
                    'Created At': row['created_at'] or ''
                })
            pd.DataFrame(data).to_excel(filename, index=False, engine='openpyxl')
            messagebox.showinfo('Success', f'Exported to Excel:\n{filename}')
        except Exception as e:
            messagebox.showerror('Error', f'Excel export failed: {e}')

    # ---------- EXPORT: PDF ----------

    def export_to_pdf(self, categories):
        filename = filedialog.asksaveasfilename(
            defaultextension='.pdf',
            filetypes=[('PDF files', '*.pdf')],
            initialfile=f'vehicle_categories_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
        if not filename:
            return

        try:
            doc = SimpleDocTemplate(filename, pagesize=landscape(letter))
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('Title', parent=styles['Title'], alignment=TA_CENTER)

            elements = [
                Paragraph("Vehicle Categories Report", title_style),
                Spacer(1, 20)
            ]

            table_data = [['ID', 'Name', 'Description', 'Base Rate', 'Late Fee', 'Status']]
            for row in categories:
                status = 'Active' if row['category_status'] == 1 else 'Inactive'
                table_data.append([
                    str(row['id']), 
                    row['name'], 
                    (row['description'] or '')[:40],
                    f"${row['base_rate']:.2f}", 
                    f"${row['late_fee_rate']:.2f}",
                    status
                ])

            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            elements.append(table)
            doc.build(elements)
            messagebox.showinfo('Success', f'Exported to PDF:\n{filename}')
        except Exception as e:
            messagebox.showerror('Error', f'PDF export failed: {e}')