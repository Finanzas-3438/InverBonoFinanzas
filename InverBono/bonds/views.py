from django.shortcuts import render, redirect, get_object_or_404
from .models import Bond
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from .calculations import BondOutcome
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponse
import json
from django.contrib.auth.decorators import login_required
import pandas as pd
from io import BytesIO
import openpyxl

def bond_detail(request, pk):
    bond = get_object_or_404(Bond, pk=pk)
    return render(request, 'bonds/detail.html', {'bond': bond})

def bond_editor(request):
    return render(request, 'editor.html')

def calculate_bond_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            def parse_decimal(val, default=0):
                try:
                    if val in (None, '', ' '):
                        return Decimal(default)
                    return Decimal(val)
                except (InvalidOperation, TypeError, ValueError):
                    return Decimal(default)

            bond_data = {
                'name': data.get('name', 'Bono Temporal'),
                'nominal_value': parse_decimal(data.get('nominal_value'), 0),
                'commercial_value': parse_decimal(data.get('commercial_value'), 0),
                'issue_date': data.get('issue_date'),
                'years_number': parse_decimal(data.get('years_number'), 0),
                'coupon_frequency': data.get('coupon_frequency'),
                'interest_rate_type': data.get('interest_rate_type'),
                'capitalization': data.get('capitalization'),
                'interest_rate': parse_decimal(data.get('interest_rate'), 0),
                'annual_discount_rate': parse_decimal(data.get('annual_discount_rate'), 0),
                'income_tax': parse_decimal(data.get('income_tax'), 0),
                'premium_percentage': parse_decimal(data.get('premium_percentage'), 0),
                'structuring_percentage': parse_decimal(data.get('structuring_percentage'), 0),
                'placement_percentage': parse_decimal(data.get('placement_percentage'), 0),
                'float_percentage': parse_decimal(data.get('float_percentage'), 0),
                'cavali_percentage': parse_decimal(data.get('cavali_percentage'), 0),
                'structuring_type': data.get('structuring_type'),
                'placement_type': data.get('placement_type'),
                'float_type': data.get('float_type'),
                'cavali_type': data.get('cavali_type'),
            }

            bond_instance = Bond(**bond_data)
            outcome = BondOutcome(bond_instance)

            results = {
                'tcea_emisor': f'{outcome.tcea_emisor:.5%}' if outcome.tcea_emisor is not None else 'N/A',
                'tcea_emisor_escudo': f'{outcome.tcea_emisor_escudo:.5%}' if outcome.tcea_emisor_escudo is not None else 'N/A',
                'trea_bonista': f'{outcome.trea_bonista:.5%}' if outcome.trea_bonista is not None else 'N/A',
                'duracion': f'{outcome.duracion:.4f}' if outcome.duracion is not None else 'N/A',
                'convexidad': f'{outcome.convexidad:.4f}' if outcome.convexidad is not None else 'N/A',
                'total': f'{outcome.total:.4f}' if outcome.total is not None else 'N/A',
                'duracion_modificada': f'{outcome.duracion_modificada:.4f}' if outcome.duracion_modificada is not None else 'N/A',
                'precio_actual': f'{outcome.precio_actual:,.2f}' if outcome.precio_actual is not None else 'N/A',
                'utilidad': f'{outcome.utilidad:,.2f}' if outcome.utilidad is not None else 'N/A',
                'issuer_initial_cost': f'{outcome.issuer_initial_cost:,.2f}' if outcome.issuer_initial_cost is not None else 'N/A',
                'bondholder_initial_cost': f'{outcome.bondholder_initial_cost:,.2f}' if outcome.bondholder_initial_cost is not None else 'N/A',
                'cok': f'{outcome.cok:.5%}' if outcome.cok is not None else 'N/A',
                'total_periods': int(outcome.total_periods) if outcome.total_periods is not None else 'N/A'
            }
            return JsonResponse(results)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def truncate_decimal(value, max_digits, decimal_places):
    if value is None:
        return None
    try:
        d = Decimal(value)
    except Exception:
        return None
    # Truncar a la cantidad de decimales permitidos
    quantize_str = '1.' + ('0' * decimal_places)
    d = d.quantize(Decimal(quantize_str), rounding=ROUND_DOWN)
    # Limitar la cantidad de dígitos totales
    sign, digits, exp = d.as_tuple()
    digits = list(digits)
    if len(digits) > max_digits:
        # Quitar dígitos de la parte entera si es necesario
        extra = len(digits) - max_digits
        digits = digits[extra:]
        d = Decimal((sign, tuple(digits), exp))
    return d

def create_bond_view(request):
    error_message = None
    if request.method == 'POST':
        def parse_decimal(val, default=0):
            try:
                if val in (None, '', ' '):
                    return Decimal(default)
                return Decimal(val)
            except (InvalidOperation, TypeError, ValueError):
                return Decimal(default)

        bond_data = {
            'name': request.POST.get('name', 'Bono #1'),
            'nominal_value': parse_decimal(request.POST.get('nominal_value'), 0),
            'commercial_value': parse_decimal(request.POST.get('commercial_value'), 0),
            'issue_date': request.POST.get('issue_date'),
            'years_number': parse_decimal(request.POST.get('years_number'), 0),
            'coupon_frequency': request.POST.get('coupon_frequency'),
            'interest_rate_type': request.POST.get('interest_rate_type'),
            'capitalization': request.POST.get('capitalization'),
            'interest_rate': parse_decimal(request.POST.get('interest_rate'), 0),
            'annual_discount_rate': parse_decimal(request.POST.get('annual_discount_rate'), 0),
            'income_tax': parse_decimal(request.POST.get('income_tax'), 0),
            'premium_percentage': parse_decimal(request.POST.get('premium_percentage'), 0),
            'structuring_percentage': parse_decimal(request.POST.get('structuring_percentage'), 0),
            'placement_percentage': parse_decimal(request.POST.get('placement_percentage'), 0),
            'float_percentage': parse_decimal(request.POST.get('float_percentage'), 0),
            'cavali_percentage': parse_decimal(request.POST.get('cavali_percentage'), 0),
            'structuring_type': request.POST.get('structuring_type'),
            'placement_type': request.POST.get('placement_type'),
            'float_type': request.POST.get('float_type'),
            'cavali_type': request.POST.get('cavali_type'),
        }

        try:
            bond_instance = Bond(**bond_data)
            # calcular
            outcome = BondOutcome(bond_instance)
            def to_decimal(val):
                if val is None:
                    return None
                try:
                    return Decimal(val)
                except Exception:
                    return Decimal('0')
            # Truncar los campos calculados según el modelo
            bond_instance.tcea_emisor = truncate_decimal(outcome.tcea_emisor, 10, 5)
            bond_instance.tcea_emisor_escudo = truncate_decimal(outcome.tcea_emisor_escudo, 10, 5)
            bond_instance.trea_bonista = truncate_decimal(outcome.trea_bonista, 10, 5)
            bond_instance.duracion = truncate_decimal(outcome.duracion, 10, 4)
            bond_instance.convexidad = truncate_decimal(outcome.convexidad, 10, 4)
            bond_instance.total = truncate_decimal(outcome.total, 10, 4)
            bond_instance.duracion_modificada = truncate_decimal(outcome.duracion_modificada, 10, 4)
            bond_instance.precio_actual = truncate_decimal(outcome.precio_actual, 20, 2)
            bond_instance.utilidad = truncate_decimal(outcome.utilidad, 20, 2)
            bond_instance.issuer_initial_cost = truncate_decimal(outcome.issuer_initial_cost, 20, 2)
            bond_instance.bondholder_initial_cost = truncate_decimal(outcome.bondholder_initial_cost, 20, 2)
            bond_instance.cok = truncate_decimal(outcome.cok, 10, 5)
            bond_instance.effective_annual_rate = truncate_decimal(outcome.effective_annual_rate, 10, 5)
            bond_instance.effective_coupon_rate = truncate_decimal(outcome.effective_coupon_rate, 10, 5)
            bond_instance.capitalization_days = outcome.capitalization_days
            bond_instance.total_periods = int(outcome.total_periods) if outcome.total_periods is not None else 0
            bond_instance.coupon_frequency_days = outcome.coupon_frequency_days
            bond_instance.periods_per_year = to_decimal(outcome.periods_per_year)
            
            # save
            bond_instance.save()
            return redirect('bonds:detail', pk=bond_instance.pk)
        except ValidationError as e:
            error_message = f'Error de validación: {e}'
        except Exception as e:
            error_message = f'Ocurrió un error inesperado al registrar el bono: {e}'
    return render(request, 'create-bond.html', {'error_message': error_message})

def list_bonds_view(request):
    try:
        bonds = list(Bond.objects.all().order_by('-issue_date'))
        db_error = False
    except Exception:
        bonds = []
        db_error = True
    return render(request, 'list.html', {'bonds': bonds, 'db_error': db_error})

def delete_bond_view(request, pk):
    bond = get_object_or_404(Bond, pk=pk)
    if request.method == 'POST':
        bond.delete()
    return redirect('bonds:list_bonds')

@login_required
def download_bond_excel(request, bond_id):

    bond = get_object_or_404(Bond, pk=bond_id)
    
    # Create a BytesIO buffer to save Excel to
    buffer = BytesIO()
    
    # Create Excel writer
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Detalle del Bono'
    
    col_widths = [6, 24, 18, 2, 6, 24, 18]
    for col, width in enumerate(col_widths, 1):
        col_letter = openpyxl.utils.get_column_letter(col)
        worksheet.column_dimensions[col_letter].width = width
    

    # Main title styles
    title_style = {
        'font': {'bold': True, 'size': 18, 'color': 'FFFFFF'},
        'fill': {'fgColor': '2C3E50', 'patternType': 'solid'},
        'alignment': {'horizontal': 'center', 'vertical': 'center'}
    }
    
    # Section header styles
    data_header_style = {
        'font': {'bold': True, 'size': 14, 'color': 'FFFFFF'},
        'fill': {'fgColor': '16A085', 'patternType': 'solid'},
        'alignment': {'horizontal': 'center', 'vertical': 'center', 'textRotation': 90}
    }
    
    results_header_style = {
        'font': {'bold': True, 'size': 14, 'color': 'FFFFFF'},
        'fill': {'fgColor': '2980B9', 'patternType': 'solid'},
        'alignment': {'horizontal': 'center', 'vertical': 'center', 'textRotation': 90}
    }
    
    # Subsection styles
    data_subheader_style = {
        'font': {'bold': True, 'size': 12, 'color': 'FFFFFF'},
        'fill': {'fgColor': '27AE60', 'patternType': 'solid'},
        'border': {'left': {'style': 'thin', 'color': '000000'},
                  'right': {'style': 'thin', 'color': '000000'}, 
                  'top': {'style': 'thin', 'color': '000000'}, 
                  'bottom': {'style': 'thin', 'color': '000000'}},
        'alignment': {'horizontal': 'center', 'vertical': 'center'}
    }
    
    results_subheader_style = {
        'font': {'bold': True, 'size': 12, 'color': 'FFFFFF'},
        'fill': {'fgColor': '3498DB', 'patternType': 'solid'},
        'border': {'left': {'style': 'thin', 'color': '000000'},
                  'right': {'style': 'thin', 'color': '000000'}, 
                  'top': {'style': 'thin', 'color': '000000'}, 
                  'bottom': {'style': 'thin', 'color': '000000'}},
        'alignment': {'horizontal': 'center', 'vertical': 'center'}
    }
    
    # Data section styles
    data_label_style = {
        'font': {'bold': True, 'size': 10, 'color': '000000'},
        'fill': {'fgColor': 'A9DFBF', 'patternType': 'solid'},
        'border': {'left': {'style': 'thin', 'color': '000000'},
                  'right': {'style': 'thin', 'color': '000000'}, 
                  'top': {'style': 'thin', 'color': '000000'}, 
                  'bottom': {'style': 'thin', 'color': '000000'}},
        'alignment': {'horizontal': 'left', 'vertical': 'center'}
    }
    
    data_value_style = {
        'font': {'bold': False, 'size': 10, 'color': '000000'},
        'fill': {'fgColor': 'EAFAF1', 'patternType': 'solid'},
        'border': {'left': {'style': 'thin', 'color': '000000'},
                  'right': {'style': 'thin', 'color': '000000'},
                  'top': {'style': 'thin', 'color': '000000'}, 
                  'bottom': {'style': 'thin', 'color': '000000'}},
        'alignment': {'horizontal': 'left', 'vertical': 'center'}
    }
    
    # Results section styles
    results_label_style = {
        'font': {'bold': True, 'size': 10, 'color': '000000'},
        'fill': {'fgColor': 'AED6F1', 'patternType': 'solid'},
        'border': {'left': {'style': 'thin', 'color': '000000'},
                  'right': {'style': 'thin', 'color': '000000'}, 
                  'top': {'style': 'thin', 'color': '000000'}, 
                  'bottom': {'style': 'thin', 'color': '000000'}},
        'alignment': {'horizontal': 'left', 'vertical': 'center'}
    }
    
    results_value_style = {
        'font': {'bold': False, 'size': 10, 'color': '000000'},
        'fill': {'fgColor': 'EBF5FB', 'patternType': 'solid'},
        'border': {'left': {'style': 'thin', 'color': '000000'},
                  'right': {'style': 'thin', 'color': '000000'}, 
                  'top': {'style': 'thin', 'color': '000000'}, 
                  'bottom': {'style': 'thin', 'color': '000000'}},
        'alignment': {'horizontal': 'left', 'vertical': 'center'}
    }
    
    footer_style = {
        'font': {'italic': True, 'size': 9, 'color': '000000'},
        'fill': {'fgColor': 'EAEDED', 'patternType': 'solid'},
        'border': {'left': {'style': 'thin', 'color': '000000'},
                  'right': {'style': 'thin', 'color': '000000'}, 
                  'top': {'style': 'thin', 'color': '000000'}, 
                  'bottom': {'style': 'thin', 'color': '000000'}},
        'alignment': {'horizontal': 'right', 'vertical': 'center'}
    }
    
    # Estilo para subtítulo
    subtitle_style = {
        'font': {'bold': True, 'size': 14, 'color': 'FFFFFF'},
        'fill': {'fgColor': '16A085', 'patternType': 'solid'},
        'border': {'left': {'style': 'medium', 'color': '000000'},
                  'right': {'style': 'medium', 'color': '000000'}, 
                  'top': {'style': 'medium', 'color': '000000'}, 
                  'bottom': {'style': 'medium', 'color': '000000'}},
        'alignment': {'horizontal': 'center', 'vertical': 'center'}
    }
    
    # Apply style function with fixed border application
    def apply_style(cell, style_dict):
        if 'font' in style_dict:
            font_params = {
                'bold': style_dict['font'].get('bold', False),
                'size': style_dict['font'].get('size', 11),
                'color': style_dict['font'].get('color', '000000'),
                'italic': style_dict['font'].get('italic', False)
            }
            cell.font = openpyxl.styles.Font(**font_params)
            
        if 'fill' in style_dict:
            cell.fill = openpyxl.styles.PatternFill(
                start_color=style_dict['fill'].get('fgColor', 'FFFFFF'),
                fill_type=style_dict['fill'].get('patternType', 'solid')
            )
        
        if 'border' in style_dict:
            border = openpyxl.styles.Border(
                left=openpyxl.styles.Side(
                    style=style_dict['border']['left']['style'],
                    color=style_dict['border']['left']['color']
                ),
                right=openpyxl.styles.Side(
                    style=style_dict['border']['right']['style'],
                    color=style_dict['border']['right']['color']
                ),
                top=openpyxl.styles.Side(
                    style=style_dict['border']['top']['style'],
                    color=style_dict['border']['top']['color']
                ),
                bottom=openpyxl.styles.Side(
                    style=style_dict['border']['bottom']['style'],
                    color=style_dict['border']['bottom']['color']
                )
            )
            cell.border = border
            
        if 'alignment' in style_dict:
            alignment_params = {
                'horizontal': style_dict['alignment'].get('horizontal', 'general'),
                'vertical': style_dict['alignment'].get('vertical', 'bottom'),
                'wrap_text': style_dict['alignment'].get('wrap_text', False)
            }
            if 'textRotation' in style_dict['alignment']:
                alignment_params['text_rotation'] = style_dict['alignment']['textRotation']
            
            cell.alignment = openpyxl.styles.Alignment(**alignment_params)
    
    # Title and subtitle
    worksheet.merge_cells('A1:G1')
    title_cell = worksheet['A1']
    title_cell.value = f"DETALLE DEL BONO: {bond.name}"
    apply_style(title_cell, title_style)
    worksheet.row_dimensions[1].height = 30
    
    worksheet.merge_cells('A2:G2')
    subtitle_cell = worksheet['A2']
    subtitle_cell.value = f"Emitido el {bond.issue_date.strftime('%d/%m/%Y')}"
    apply_style(subtitle_cell, subtitle_style)
    worksheet.row_dimensions[2].height = 22
    
    start_data_row = 5
    
    data_row = start_data_row
    results_row = start_data_row
    
    # --- COLUMNA DE DATOS ---
    
    # Sección 1: Del Bono
    worksheet.merge_cells(f'B{data_row}:C{data_row}')
    data_subheader = worksheet[f'B{data_row}']
    data_subheader.value = "Del Bono"
    apply_style(data_subheader, data_subheader_style)
    worksheet.row_dimensions[data_row].height = 20
    data_row += 1
    
    # Datos del Bono
    bond_data = [
        ["Valor Nominal", f"S/ {bond.nominal_value:.2f}"],
        ["Valor Comercial", f"S/ {bond.commercial_value:.2f}"],
        ["Nº de Años", f"{bond.years_number}"],
        ["Frecuencia del cupón", bond.get_coupon_frequency_display()],
        ["Días x Año", "360"],
        ["Tipo de Tasa de Interés", bond.get_interest_rate_type_display()],
        ["Capitalización", bond.get_capitalization_display()],
        ["Tasa de interés", f"{bond.interest_rate}%"],
        ["Tasa anual de descuento", f"{bond.annual_discount_rate}%"],
        ["Imp. a la Renta", f"{bond.income_tax}%"],
        ["Fecha de Emisión", bond.issue_date.strftime('%d/%m/%Y')]
    ]
    
    for item in bond_data:
        label_cell = worksheet.cell(row=data_row, column=2, value=item[0])
        apply_style(label_cell, data_label_style)
        value_cell = worksheet.cell(row=data_row, column=3, value=item[1])
        apply_style(value_cell, data_value_style)
        worksheet.row_dimensions[data_row].height = 18
        data_row += 1
    
    # Sección 2: De los Gastos Iniciales
    worksheet.merge_cells(f'B{data_row}:C{data_row}')
    expenses_header = worksheet[f'B{data_row}']
    expenses_header.value = "De los Gastos Iniciales"
    apply_style(expenses_header, data_subheader_style)
    worksheet.row_dimensions[data_row].height = 20
    data_row += 1
    
    # Datos de gastos iniciales
    expenses_data = [
        ["% Prima", f"{bond.premium_percentage}%"],
        ["% Estructuración", f"{bond.structuring_percentage}% ({bond.get_structuring_type_display()})"],
        ["% Colocación", f"{bond.placement_percentage}% ({bond.get_placement_type_display()})"],
        ["% Flotación", f"{bond.float_percentage}% ({bond.get_float_type_display()})"],
        ["% CAVALI", f"{bond.cavali_percentage}% ({bond.get_cavali_type_display()})"]
    ]
    
    for item in expenses_data:
        label_cell = worksheet.cell(row=data_row, column=2, value=item[0])
        apply_style(label_cell, data_label_style)
        value_cell = worksheet.cell(row=data_row, column=3, value=item[1])
        apply_style(value_cell, data_value_style)
        worksheet.row_dimensions[data_row].height = 18
        data_row += 1
    
    # --- COLUMNA DE RESULTADOS ---
    
    # Sección 1: De la Estructuración del Bono
    worksheet.merge_cells(f'F{results_row}:G{results_row}')
    results_subheader = worksheet[f'F{results_row}']
    results_subheader.value = "De la Estructuración del Bono"
    apply_style(results_subheader, results_subheader_style)
    worksheet.row_dimensions[results_row].height = 20
    results_row += 1
    
    # Resultados de la estructuración
    structure_results = [
        ["Días capitalización", str(bond.capitalization_days)],
        ["Nº Períodos por Año", str(bond.periods_per_year)],
        ["Nº Total de Periodos", str(bond.total_periods)],
        ["Tasa efectiva anual", f"{bond.effective_annual_rate*100:.3f}%"],
        ["Tasa efectiva {0}".format(bond.get_coupon_frequency_display()), f"{bond.effective_coupon_rate*100:.3f}%"],
        ["COK {0}".format(bond.get_coupon_frequency_display()), f"{bond.cok*100:.3f}%"],
        ["Costes Iniciales Emisor", f"S/ {bond.issuer_initial_cost:.2f}"],
        ["Costes Iniciales Bonista", f"S/ {bond.bondholder_initial_cost:.2f}"]
    ]
    
    for item in structure_results:
        result_label_cell = worksheet.cell(row=results_row, column=6, value=item[0])
        apply_style(result_label_cell, results_label_style)
        result_value_cell = worksheet.cell(row=results_row, column=7, value=item[1])
        apply_style(result_value_cell, results_value_style)
        worksheet.row_dimensions[results_row].height = 18
        results_row += 1
    
    # Sección 2: Del Precio Actual y Utilidad
    worksheet.merge_cells(f'F{results_row}:G{results_row}')
    price_header = worksheet[f'F{results_row}']
    price_header.value = "Del Precio Actual y Utilidad"
    apply_style(price_header, results_subheader_style)
    worksheet.row_dimensions[results_row].height = 20
    results_row += 1
    
    # Datos de precio y utilidad
    price_results = [
        ["Precio Actual", f"S/ {bond.precio_actual:.2f}"],
        ["Utilidad / Pérdida", f"S/ {bond.utilidad:.2f}"]
    ]
    
    for item in price_results:
        result_label_cell = worksheet.cell(row=results_row, column=6, value=item[0])
        apply_style(result_label_cell, results_label_style)
        result_value_cell = worksheet.cell(row=results_row, column=7, value=item[1])
        apply_style(result_value_cell, results_value_style)
        worksheet.row_dimensions[results_row].height = 18
        results_row += 1
    
    # Sección 3: De los Ratios de Decisión
    worksheet.merge_cells(f'F{results_row}:G{results_row}')
    risk_header = worksheet[f'F{results_row}']
    risk_header.value = "De los Ratios de Decisión"
    apply_style(risk_header, results_subheader_style)
    worksheet.row_dimensions[results_row].height = 20
    results_row += 1
    
    # Datos de ratios de decisión
    risk_data = [
        ["Duración", f"{bond.duracion:.2f}"],
        ["Convexidad", f"{bond.convexidad:.2f}"],
        ["Total", f"{bond.total:.2f}"],
        ["Duración Modificada", f"{bond.duracion_modificada:.2f}"]
    ]
    
    for item in risk_data:
        result_label_cell = worksheet.cell(row=results_row, column=6, value=item[0])
        apply_style(result_label_cell, results_label_style)
        result_value_cell = worksheet.cell(row=results_row, column=7, value=item[1])
        apply_style(result_value_cell, results_value_style)
        worksheet.row_dimensions[results_row].height = 18
        results_row += 1
    
    # Sección 4: De los Indicadores de Rentabilidad
    worksheet.merge_cells(f'F{results_row}:G{results_row}')
    profitability_header = worksheet[f'F{results_row}']
    profitability_header.value = "De los Indicadores de Rentabilidad"
    apply_style(profitability_header, results_subheader_style)
    worksheet.row_dimensions[results_row].height = 20
    results_row += 1
    
    # Datos de rentabilidad
    profitability_data = [
        ["TCEA Emisor", f"{bond.tcea_emisor*100:.3f}%"],
        ["TCEA Emisor c/Escudo", f"{bond.tcea_emisor_escudo*100:.3f}%"],
        ["TREA Bonista", f"{bond.trea_bonista*100:.3f}%"]
    ]
    
    for item in profitability_data:
        result_label_cell = worksheet.cell(row=results_row, column=6, value=item[0])
        apply_style(result_label_cell, results_label_style)
        result_value_cell = worksheet.cell(row=results_row, column=7, value=item[1])
        apply_style(result_value_cell, results_value_style)
        worksheet.row_dimensions[results_row].height = 18
        results_row += 1
    

    data_end_row = data_row - 1
    results_end_row = results_row - 1

    # Merge cells for main headers
    worksheet.merge_cells(f'A{start_data_row}:A{data_end_row}')
    data_main_header = worksheet[f'A{start_data_row}']
    data_main_header.value = "D A T O S"
    apply_style(data_main_header, data_header_style)
    
    worksheet.merge_cells(f'E{start_data_row}:E{results_end_row}')
    results_main_header = worksheet[f'E{start_data_row}']
    results_main_header.value = "R E S U L T A D O S"
    apply_style(results_main_header, results_header_style)
    
    # Pie de página
    current_row = max(data_end_row, results_end_row) + 1
    worksheet.merge_cells(f'A{current_row}:G{current_row}')
    note_cell = worksheet[f'A{current_row}']
    note_cell.value = f"InverBono - Exportado el {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}"
    apply_style(note_cell, footer_style)
    
    # Guardar a buffer
    workbook.save(buffer)
    buffer.seek(0)
    
    # Crear respuesta HTTP
    response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=bono_{bond.name.replace(" ", "_")}.xlsx'
    
    return response

