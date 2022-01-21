import os
import numpy as np
from fpdf import FPDF
import matplotlib.pyplot as plt
import primary_info as pi
from PIL import Image


def line_plot(dict_list, list_year, parameter, title, comp_list=['AMBEV S.A.'], save_folder='figures'):

    # Color list
    color_list = ['#45B8AC', '#5B5EA6', '#EFC050', '#E15D44', '#B565A7', '#88B04B', '#6B5B95', '#363945', '#E0B589'
                    '#FA7A35']

    # Create figure
    fig = plt.figure(figsize=(11, 5))
    fig.gca().spines["right"].set_visible(False)
    fig.gca().spines["top"].set_visible(False)

    # Add plots for rach company
    for comp_index in range(len(dict_list)):
        color = color_list[comp_index]
        plt.plot(list_year, dict_list[comp_index][parameter], label=f'{comp_list[comp_index]}', linewidth=1.4, color=color)

    # Aditional seetings
    plt.title(title)
    plt.legend(bbox_to_anchor=(1, 0.5), loc='upper left', frameon=False)
    plt.xlabel('Anos')
    plt.ylabel(title)

    # Margem Bruta - seetings
    if parameter == 'marg_brut_list':
        plt.axhline(y=22, color='#D22B2B', linestyle='--', linewidth=0.9)
        plt.axhline(y=40, color='#7FFF00', linestyle='--', linewidth=0.9)

    # Despesas VGA - seetings
    if parameter == 'vga_lucro_brut_list':
        plt.axhline(y=-80, color='#D22B2B', linestyle='--', linewidth=0.9)

    # Despesas juros - seetings
    if parameter == 'juros_lucro_oper_list':
        plt.axhline(y=-15, color='#7FFF00', linestyle='--', linewidth=0.9)

    # Despesas juros - seetings
    if parameter == 'coef_liquidez':
        plt.axhline(y=1, color='#D22B2B', linestyle='--', linewidth=0.9)

    # Save the figure in "figures" folder
    plt.savefig(f'{save_folder}\\{parameter}.png', bbox_inches='tight', transparent=True)


# Create list of years
year_list = []
dir_elements = os.listdir('raw_dfp')
for element in dir_elements:
    if '20' in element and element == '2017':
        year_list.append(2016)
        year_list.append(2017)
    elif '20' in element:
        year_list.append(int(element))

# Create figure folder
fig_folder = 'figures'
directory_elements = os.listdir()
if fig_folder not in directory_elements:
    os.mkdir(f'{fig_folder}')
elif os.listdir(f'{fig_folder}') != []:
    fig_folder_elements = os.listdir(f'{fig_folder}')
    for element in fig_folder_elements:
        os.remove(f'{fig_folder}\\{element}')


# Create PDF class
class PDF(FPDF):

    def lines(self):
        self.rect(2.5, 2.5, 205.0, 292.0)


# Collect data from function worked_info
company_list = ['AMBEV S.A.']
return_dict_list = pi.worked_info()

# Create .pdf object
pdf = PDF('P', 'mm', 'A4')

# Set A4 page total dimensions
pdf_w = 210
pdf_h = 297

pdf.set_auto_page_break(True, margin=20)
pdf.add_page()
pdf.lines()
pdf.set_font('helvetica', '', 16)
pdf.set_x(x=55)
pdf.cell(100, 10, 'Análise de Demonstração Financeira', align='C')
pdf.ln(30)

# Plot Linha
line_plot(return_dict_list, year_list, 'marg_brut_list', 'Margem Bruta (%)', comp_list=company_list)
line_plot(return_dict_list, year_list, 'marg_liq_list', 'Margem Líquida (%)', comp_list=company_list)
line_plot(return_dict_list, year_list, 'vga_lucro_brut_list', 'Despesas VGA sobre o Lucro Bruto (%)', comp_list=company_list)
line_plot(return_dict_list, year_list, 'ped_lucro_brut_list', 'Despesas Pesquisa sobre o Lucro Bruto (%)', comp_list=company_list)
line_plot(return_dict_list, year_list, 'deprec_lucro_brut_list', 'Depreciciação sobre o Lucro Bruto (%)', comp_list=company_list)
line_plot(return_dict_list, year_list, 'juros_lucro_oper_list', 'Juros sobre o Lucro Operacional (%)', comp_list=company_list)
line_plot(return_dict_list, year_list, 'lucro_liq_list', 'Lucro líquido (mil reais)', comp_list=company_list)
line_plot(return_dict_list, year_list, 'lucroporacao_list', 'Lucro por ação (mil reais)', comp_list=company_list)
line_plot(return_dict_list, year_list, 'coef_liquidez_list', 'Coeficiente de Liquidez (Ativo Circulante/Passivo Circulante)', comp_list=company_list)
line_plot(return_dict_list, year_list, 'ativo_circ_list', 'Ativo Circulante (mil reais)', comp_list=company_list)
line_plot(return_dict_list, year_list, 'imobilizado_list', 'Ativo Imobilizado (mil reais)', comp_list=company_list)
line_plot(return_dict_list, year_list, 'passivo_tot_patrliq_list', 'Passivo Total/Patrimônio Líquido', comp_list=company_list)
line_plot(return_dict_list, year_list, 'roe_list', 'ROE (%)', comp_list=company_list)
line_plot(return_dict_list, year_list, 'roa_list', 'ROA (%)', comp_list=company_list)

for image in os.listdir(fig_folder):
    image_handle = Image.open(f'{fig_folder}\\{image}')
    im_size = image_handle.size # Return (width, heigth)

    # Add page if imagem is bigger than left space + 20 of margin
    if (im_size[1]/im_size[0]) * 100 >= (pdf_h - pdf.get_y() - 20):
        pdf.add_page()
        pdf.lines()

    pdf.image(f'{fig_folder}\\{image}', x=(pdf_w/2 - 160/2), w=160)
    pdf.ln(10)

pdf.output('tuto1.pdf', 'F')
'''
# Plot test
plt.plot([1,2,3], [1,2,3])
plt.savefig(f'{fig_folder}\\teste2.png', bbox_inches='tight', transparent=True)
plt.show()
'''
