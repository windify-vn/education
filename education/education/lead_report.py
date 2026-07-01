# Copyright (c) 2026, Windify Technologies Pvt. Ltd.
# Lead Sales Report Exporter
#
# Generates an Excel "Bảng theo dõi doanh số" from Lead records.

import io
from datetime import date

import frappe
from frappe import _
from frappe.utils import flt, getdate


@frappe.whitelist()
def export_lead_sales_report(month=None, year=None):
	"""Generate and stream the sales tracking Excel report.

	Args:
		month: int 1-12, defaults to current month
		year:  int e.g. 2026, defaults to current year
	"""
	frappe.has_permission("Lead", "export", throw=True)

	try:
		import openpyxl
		from openpyxl.styles import (
			Alignment,
			Border,
			Font,
			PatternFill,
			Side,
		)
	except ImportError:
		frappe.throw(_("openpyxl is required. Run: pip install openpyxl"))

	today = date.today()
	month = int(month or today.month)
	year = int(year or today.year)
	date_label = f"{month:02d}/{year}"

	# ── Fetch Leads ───────────────────────────────────────────────────────────
	leads = frappe.get_all(
		"Lead",
		fields=[
			"name",
			"education_student_full_name",
			"education_parent_phone_number",
			"education_address",
			"education_date_of_birth",
			"education_grade_class",
			"gender",
			"education_campaign",
		],
		order_by="creation asc",
	)

	if not leads:
		frappe.throw(_("Không có dữ liệu Lead để xuất."))

	lead_names = [l.name for l in leads]

	# ── Fetch items for all leads in one query ────────────────────────────────
	# Determine which child table is being used for education_items
	child_doctype = _get_items_child_doctype()

	if child_doctype:
		items_rows = frappe.get_all(
			child_doctype,
			filters={"parenttype": "Lead", "parentfield": "education_items", "parent": ["in", lead_names]},
			fields=[
				"parent", "item_code", "item_name", "discount_percentage", "idx",
				"price_list_rate", "rate"
			],
			order_by="parent asc, idx asc",
		)
	else:
		items_rows = []

	# Group items by lead
	items_by_lead = {}
	for item in items_rows:
		items_by_lead.setdefault(item.parent, []).append(item)

	# ── Build Excel ───────────────────────────────────────────────────────────
	wb = openpyxl.Workbook()
	ws = wb.active
	ws.title = f"DoanhSoThang{month:02d}{year}"  # / not allowed in sheet names

	COLS = [
		"TÊN HỌC SINH",
		"SĐT",
		"ĐỊA CHỈ",
		"NGÀY ĐĂNG KÝ",
		"NGÀY NHẬP HỌC",
		"TUỔI",
		"KHỐI / LỚP",
		"GIỚI TÍNH",
		"KHÓA HỌC",
		"NỘI DUNG ƯU ĐÃI",
		"HỌC PHÍ NIÊM YẾT (đ)",
		"HỌC PHÍ SAU GIẢM (đ)",
		"ĐÃ CỌC",
		"ĐÃ THANH TOÁN LẦN 2 (đ)",
		"NGUỒN",
		"QUÀ TẶNG",
		"DS TÍNH HOA HỒNG (đ)",
	]
	NUM_COLS = len(COLS)

	# ── Styles ────────────────────────────────────────────────────────────────
	TITLE_FONT = Font(name="Arial", bold=True, size=13)
	HEADER_FONT = Font(name="Arial", bold=True, size=10, color="FFFFFF")
	CELL_FONT = Font(name="Arial", size=10)
	HEADER_FILL = PatternFill("solid", fgColor="1F4E79")  # dark navy blue
	ALT_FILL = PatternFill("solid", fgColor="D6E4F0")     # light blue for alt rows

	thin = Side(style="thin", color="AAAAAA")
	BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)

	CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
	LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)

	# ── Row 1: Title ─────────────────────────────────────────────────────────
	ws.row_dimensions[1].height = 32
	title_cell = ws.cell(row=1, column=1,
		value=f"WINDIFY FUTURE ACADEMY - DOANH SỐ THÁNG {date_label}")
	title_cell.font = Font(name="Arial", bold=True, size=14, color="FFFFFF")
	title_cell.alignment = CENTER
	title_cell.fill = PatternFill("solid", fgColor="1F4E79")
	ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=NUM_COLS)

	# ── Row 2: Column headers ─────────────────────────────────────────────────
	ws.row_dimensions[2].height = 36
	for col_idx, col_name in enumerate(COLS, start=1):
		cell = ws.cell(row=2, column=col_idx, value=col_name)
		cell.font = HEADER_FONT
		cell.fill = HEADER_FILL
		cell.alignment = CENTER
		cell.border = BORDER

	# ── Data rows ─────────────────────────────────────────────────────────────
	row_num = 3
	for lead_idx, lead in enumerate(leads):
		lead_items = items_by_lead.get(lead.name)

		# Calculate age
		age = ""
		if lead.get("education_date_of_birth"):
			try:
				dob = getdate(lead.education_date_of_birth)
				today_d = date.today()
				age = today_d.year - dob.year - (
					(today_d.month, today_d.day) < (dob.month, dob.day)
				)
			except Exception:
				age = ""

		# Gender display
		gender_map = {"Male": "Nam", "Female": "Nữ", "Other": "Khác"}
		gender = gender_map.get(lead.get("gender") or "", lead.get("gender") or "")

		# Base row data (shared across item rows)
		base_data = [
			lead.get("education_student_full_name") or "",  # TÊN HỌC SINH
			lead.get("education_parent_phone_number") or "",  # SĐT
			lead.get("education_address") or "",  # ĐỊA CHỈ
			"",  # NGÀY ĐĂNG KÝ
			"",  # NGÀY NHẬP HỌC
			age,  # TUỔI
			lead.get("education_grade_class") or "",  # KHỐI / LỚP
			gender,  # GIỚI TÍNH
		]

		# Campaign / source name (may be a Link or Data field)
		campaign = lead.get("education_campaign") or ""

		if lead_items:
			for item in lead_items:
				discount = flt(item.get("discount_percentage") or 0)
				uu_dai = f"Giảm {discount:g}%" if discount > 0 else ""

				row_data = base_data + [
					item.get("item_name") or item.get("item_code") or "",  # KHÓA HỌC
					uu_dai,  # NỘI DUNG ƯU ĐÃI
					flt(item.get("price_list_rate")),  # HỌC PHÍ NIÊM YẾT
					flt(item.get("rate")),  # HỌC PHÍ SAU GIẢM
					"",  # ĐÃ CỌC
					"",  # ĐÃ THANH TOÁN LẦN 2
					campaign,  # NGUỒN
					"",  # QUÀ TẶNG
					"",  # DS TÍNH HOA HỒNG
				]
				_write_data_row(ws, row_num, row_data, lead_idx, CELL_FONT, ALT_FILL, BORDER, LEFT)
				# Áp dụng format tiền tệ cho cột HỌC PHÍ (cột K = 11, cột L = 12)
				ws.cell(row=row_num, column=11).number_format = '#,##0'
				ws.cell(row=row_num, column=12).number_format = '#,##0'
				row_num += 1
		else:
			# Lead with no items — one blank row
			row_data = base_data + ["", "", "", "", "", "", campaign, "", ""]
			_write_data_row(ws, row_num, row_data, lead_idx, CELL_FONT, ALT_FILL, BORDER, LEFT)
			row_num += 1

	# ── Column widths ─────────────────────────────────────────────────────────
	col_widths = [24, 14, 28, 15, 15, 7, 13, 10, 26, 22, 22, 22, 12, 24, 18, 14, 22]
	for col_idx, width in enumerate(col_widths, start=1):
		ws.column_dimensions[_col_letter(col_idx)].width = width

	# Freeze panes: keep row 1-2 and no column freeze
	ws.freeze_panes = "A3"

	# ── Stream the file ───────────────────────────────────────────────────────
	buf = io.BytesIO()
	wb.save(buf)
	buf.seek(0)
	file_content = buf.read()

	filename = f"lead_sales_report_{year}_{month:02d}.xlsx"
	frappe.local.response.filename = filename
	frappe.local.response.filecontent = file_content
	frappe.local.response.type = "download"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_items_child_doctype():
	"""Return the child doctype used for education_items on Lead."""
	# Check Custom Field first
	cf = frappe.db.get_value("Custom Field", "Lead-education_items", "options")
	if cf:
		return cf
	return None


def _write_data_row(ws, row_num, row_data, lead_idx, font, alt_fill, border, alignment):
	use_alt = lead_idx % 2 == 1
	for col_idx, value in enumerate(row_data, start=1):
		cell = ws.cell(row=row_num, column=col_idx, value=value)
		cell.font = font
		cell.border = border
		cell.alignment = alignment
		if use_alt:
			cell.fill = alt_fill


def _col_letter(col_idx):
	"""Convert 1-based column index to Excel letter (A, B, …, Z, AA, …)."""
	result = ""
	while col_idx:
		col_idx, remainder = divmod(col_idx - 1, 26)
		result = chr(65 + remainder) + result
	return result
