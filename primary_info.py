import pandas as pd
from zipfile import ZipFile
import numpy as np
import re
import os


def year_identifier(file_name):

    '''
    Abstrait: identify the year of the file
    '''

    folder_regex = re.compile(r'20\d\d')
    match = folder_regex.search(str(file_name))
    year = match.group()
    return year


def dataframe_filtering(folder, file_name_list, company_list, prev=False):

    '''
    Input: folder name, list with important files in the folder and list with companies of interest
    Output: 
    '''

    dataframe_general = []

    for company in company_list:

        dataframe_company = []
        dataframe_list = []

        for file in file_name_list:

            # Create BPA DataFrame
            file_raw = pd.read_csv(f'raw_dfp\\{folder}\\{file}', encoding='iso-8859-1', delimiter=';', skiprows=0, low_memory=False)

            # Filter year and last year results
            if prev is False:
                file_1 = file_raw[~file_raw['ORDEM_EXERC'].str.startswith('P')]
                folder_year = year_identifier(file_name_list)
            else:
                file_1 = file_raw[file_raw['ORDEM_EXERC'].str.startswith('P')]
                folder_year = int(year_identifier(file_name_list)) - 1

            # Filter the right columns
            file_2 = file_1[['DENOM_CIA', 'DS_CONTA', 'VL_CONTA']]

            # Filter the right companies
            file_3 = file_2[file_2['DENOM_CIA'].isin([company])]

            # Filter the right data

            if file.find('DRE') != -1:
                interest_data = ['Receita de Venda de Bens e/ou Serviços', 'Resultado Bruto', 'Despesas com Vendas', 'Despesas com Pesquisa e Desenvolvimento',
            'Custos com Pesquisa e Desenvolvimento', 'Despesas com pesquisas e desenvolvimento', 'Pesquisa e Desenvolvimento', 'Pesquisa', 'Despesas com Pesquisas e Desenvolvimento',
            'Custo com Pesquisa e Desenvolvimento Tecnológico', 'Despesas com gastos com desenvolvimento', 'Despesas com desenvolvimento de tecnologia e produtos', 'Com estudos em desenvolvimento',
            'Despesas Gerais e Administrativas', 'Despesas de Depreciação', 'Despesas/Receitas Operacionais',
            'Resultado Antes do Resultado Financeiro e dos Tributos', 'Resultado Financeiro', 'Resultado Antes dos Tributos sobre o Lucro',
            'Resultado Líquido das Operações Continuadas', 'Lucro Básico por Ação', 'ON', 'Lucro Diluído por Ação']

            elif file.find('BPA') != -1:
                interest_data = ['Ativo Total', 'Ativo Circulante', 'Imobilizado']

            elif file.find('BPP') != -1:
                interest_data = ['Passivo Circulante', 'Empréstimos e Financiamentos', 'Passivo Não Circulante', 'Patrimônio Líquido Consolidado',
                                    'Reservas de Lucros', 'Lucros/Prejuízos Acumulados']

            elif file.find('DFC_MI') != -1:
                interest_data = ['Lucro Líquido do exercício', 'Depreciação, Amortização e Impairment', 'Depreciação e amortização', 'Depreciação de arrendamento', 'Depreciação e Amortização', 'Depreciações e Amortizações', 'Depreciações e Amortizações', 'Amortização e Depreciação', 'Depreciação/amortização', 'Depreciações', 'Depreciação e Amortizações', 'Depreciação do imobilizado', 'Depreciação e depleção do imobilizado', 'Depreciação, exaustão e amortização', 'Depreciação, Amortização e Exaustão',
                                'Aquisição de Imobilizado e Intangíveis', 'Adições de imobilizado', 'Compras de ativo imobilizado', 'Aquisições de imobilizado', 'Aquisições de Imobilizado',
                                'Aquisições de Imobilizado e Intangível', 'Aquisições de imobilizado e intangível', 'Aquisições de Imobilizados e Intangíveis (Exceto pelo Excedente de Cessão Onerosa)',
                                'Aquisições de imobilizados e intangíveis', 'Aquisições de imobilizado veículos frota', 'Aquisições de imobilizado de uso', 'Aquisições de Imobilizado de Uso', 'Aquisição de ativos imobilizados, intangível e propriedade para investimento']

            file_4 = file_3[file_3['DS_CONTA'].isin(interest_data)]

            dataframe_list.append(file_4)

        # Concatenate each file dataframe into one and add year column
        dataframe_company = pd.concat(dataframe_list)
        dataframe_company = dataframe_company.rename(columns={"VL_CONTA": f"{folder_year}"})

        # Append to general list
        dataframe_general.append(dataframe_company)

    return dataframe_general


def primary_info(companies, clear_prev_folder=False):

    company_frames = []
    for company in companies:
        company_frames.append(pd.DataFrame())

    # Identify zip year
    for file in os.listdir('raw_dfp\\raw_zip'):
        zip_year = year_identifier(f'raw_dfp\\raw_zip\\{file}')

        # Create or clear the folder of the year
        output_folder = zip_year
        directory_elements = os.listdir('raw_dfp')
        if output_folder not in directory_elements:
            os.mkdir(f'raw_dfp\\{output_folder}')
        elif os.listdir(f'raw_dfp\\{output_folder}') != [] and clear_prev_folder is True:
            output_folder_elements = os.listdir(f'raw_dfp\\{output_folder}')
            for element in output_folder_elements:
                os.remove(f'raw_dfp\\{output_folder}\\{element}')

        # Extract files from zip
        if os.listdir(f'raw_dfp\\{output_folder}') == []:
            with ZipFile(f'raw_dfp\\raw_zip\\{file}', 'r') as zip:
                zip.extractall(path=f'raw_dfp\\{output_folder}')
        else:
            print(f"A pasta \"raw_dfp/{zip_year}\" ja tem arquivos internos. Confira a necessidade de descompactar o .zip.")
            print('Prosseguindo ...')

    # List folders in 'raw_dfp' and remove 'raw_zip'
    raw_folders = os.listdir('raw_dfp')
    raw_folders.remove('raw_zip')

    # Travel around raw_dfp folders excluding "raw_zip"
    for folder in raw_folders:

        # Remove all individual reports, aiming only consolidated reports
        file_list = os.listdir(f'raw_dfp\\{folder}')
        for file in file_list:
            file_regex = re.compile(r'ind_20\d\d')
            mo = file_regex.search(str(file))
            if mo is not None:
                os.remove(f'raw_dfp\\{folder}\\{file}')

        # Travel around folder files
        for file in file_list:

            # Save DRE file name in a variable
            dre_regex = re.compile(r'DRE_con_20\d\d')
            mo_dre = dre_regex.search(str(file))
            if mo_dre is not None:
                dre = file

            # Save BPA file name in a variable
            bpa_regex = re.compile(r'BPA_con_20\d\d')
            mo_bpa = bpa_regex.search(str(file))
            if mo_bpa is not None:
                bpa = file

            # Save BPP file name in a variable
            bpp_regex = re.compile(r'BPP_con_20\d\d')
            mo_bpp = bpp_regex.search(str(file))
            if mo_bpp is not None:
                bpp = file

            # Save DFC_MI file name in a variable
            dfc_regex = re.compile(r'DFC_MI_con_20\d\d')
            mo_dfc = dfc_regex.search(str(file))
            if mo_dfc is not None:
                dfc = file

        folder_list = dataframe_filtering(folder, [dre, bpa, bpp, dfc], companies)

        # Create datframe for 2016 based on 2017 folder
        if int(folder) == 2017:
            folder_list_2 = dataframe_filtering(folder, [dre, bpa, bpp, dfc], companies, prev=True)

            for company_index in range(len(companies)):
                if len(folder_list_2[company_index]) == 0: # Do not add empty dataframe
                    pass
                else:
                    company_frames[company_index] = folder_list_2[company_index]
        
        # Construct and append a final dataframe for each company with all years information
        for company_index in range(len(companies)):
            if len(folder_list[company_index]) == 0:
                pass
            elif len(company_frames[company_index]) == 0:
                company_frames[company_index] = folder_list[company_index]
            else:
                serie = folder_list[company_index][['DS_CONTA', str(folder)]]
                company_frames[company_index] = company_frames[company_index].join(serie.set_index('DS_CONTA'), on='DS_CONTA')

    return company_frames


def worked_info(companies=['AMBEV S.A.'], clear_prev_folder=False):

    # Create return variable
    return_dict_list = []

    # Extract primary information
    prim_info = primary_info(companies, clear_prev_folder=False)

    print('-+-' * 20)
    print('CARREGANDO DATAFFRAME ...')

    # Travel throught companies
    for comp_index in range(len(companies)):

        # Extract list of years collected
        year_columns = []
        for column in prim_info[comp_index].columns:
            if '20' in column:
                year_columns.append(column)

        # Extract company frame
        primary_frame = prim_info[comp_index]
        #pd.set_option('display.expand_frame_repr', False)
        #print(primary_frame)
        #primary_frame.to_csv('primary_csv.csv',sep=' ')

        # Duplicate checker
        imobilizado_duplicate = 0
        desp_ga_duplicate = 0
        lucro_acumul_duplicate = 0
        dai_duplicate = 0
        ped_duplicate = 0
        vendas_duplicate = 0
        divida_curto_duplicate = 0
        divida_longo_duplicate = 0
        receita_duplicate = 0

        # Initialize primary variables lists
        receita_list = []
        lucro_brut_list = []
        desp_vendas_list = []
        desp_ga_list = []
        dai_list = []
        desp_oper_list = []
        financeiro_list = []
        lucropreimp_list = []
        lucro_liq_list = []
        lucro_oper_list = []
        lucroporacao_list = []

        ativo_total_list = []
        ativo_circ_list = []
        imobilizado_list = []
        passivo_circ_list = []
        divida_curto_list = []
        divida_longo_list = []
        passivo_ncirc_list = []
        patr_liq_list = []
        lucro_acumul_list = []

        lucro_liq_exerc_list = []
        desp_ativo_fixo_list = []

        # Initialize intermediate variables
        desp_vga_list = []
        desp_ped_list = []

        # Travel trought cells
        for row in range(len(primary_frame)):

            col = 'DS_CONTA'
                
            # Fill primary variable lists (DRE)
            if primary_frame.iloc[row][col] == 'Receita de Venda de Bens e/ou Serviços':
                if receita_duplicate == 0:
                    receita_duplicate += 1
                    for year in year_columns:
                        receita_list.append(primary_frame.iloc[row][year])
                else:
                    pass

            elif primary_frame.iloc[row][col] == 'Resultado Bruto':
                for year in year_columns:
                    lucro_brut_list.append(primary_frame.iloc[row][year])

            elif primary_frame.iloc[row][col] == 'Despesas com Vendas':
                if vendas_duplicate == 0:
                    vendas_duplicate += 1
                    for year in year_columns:
                        desp_vendas_list.append(primary_frame.iloc[row][year])
                else:
                    pass

            elif primary_frame.iloc[row][col] == 'Despesas Gerais e Administrativas':
                if desp_ga_duplicate == 0:
                    desp_ga_duplicate += 1
                    for year in year_columns:
                        desp_ga_list.append(primary_frame.iloc[row][year])
                else:
                    pass

            elif primary_frame.iloc[row][col] in ['Despesas de Depreciação', 'Depreciação, Amortização e Impairment', 'Depreciação e amortização', 'Depreciação de arrendamento',
                                                    'Depreciação e Amortização', 'Depreciações e Amortizações', 'Depreciações e Amortizações', 'Amortização e Depreciação', 'Depreciação/amortização',
                                                    'Depreciações', 'Depreciação e Amortizações', 'Depreciação do imobilizado', 'Depreciação e depleção do imobilizado', 'Depreciação, exaustão e amortização',
                                                    'Depreciação, Amortização e Exaustão']:
                if dai_duplicate == 0:
                    dai_duplicate += 1
                    for year in year_columns:
                        dai_list.append(primary_frame.iloc[row][year])
                else:
                    pass

            elif primary_frame.iloc[row][col] in ['Despesas com Pesquisa e Desenvolvimento',
            'Custos com Pesquisa e Desenvolvimento', 'Despesas com pesquisas e desenvolvimento', 'Pesquisa e Desenvolvimento', 'Pesquisa', 'Despesas com Pesquisas e Desenvolvimento',
            'Custo com Pesquisa e Desenvolvimento Tecnológico', 'Despesas com gastos com desenvolvimento', 'Despesas com desenvolvimento de tecnologia e produtos', 'Com estudos em desenvolvimento']:
                if ped_duplicate == 0:
                    ped_duplicate += 1
                    for year in year_columns:
                        desp_ped_list.append(primary_frame.iloc[row][year])
                else:
                    pass

            elif primary_frame.iloc[row][col] == 'Despesas/Receitas Operacionais':
                for year in year_columns:
                    desp_oper_list.append(primary_frame.iloc[row][year])

            elif primary_frame.iloc[row][col] == 'Resultado Antes do Resultado Financeiro e dos Tributos':
                for year in year_columns:
                    lucro_oper_list.append(primary_frame.iloc[row][year]) 

            elif primary_frame.iloc[row][col] == 'Resultado Financeiro':
                for year in year_columns:
                    financeiro_list.append(primary_frame.iloc[row][year])

            elif primary_frame.iloc[row][col] == 'Resultado Antes dos Tributos sobre o Lucro':
                for year in year_columns:
                    lucropreimp_list.append(primary_frame.iloc[row][year])

            elif primary_frame.iloc[row][col] == 'Resultado Líquido das Operações Continuadas':
                for year in year_columns:
                    lucro_liq_list.append(primary_frame.iloc[row][year])

            elif primary_frame.iloc[row][col] == 'Lucro Básico por Ação':
                for year in year_columns:
                    lucroporacao_list.append(primary_frame.iloc[row+2][year])

            # Fill primary variable lists (BPA and BPP)
            if primary_frame.iloc[row][col] == 'Ativo Total':
                for year in year_columns:
                    ativo_total_list.append(primary_frame.iloc[row][year])

            elif primary_frame.iloc[row][col] == 'Ativo Circulante':
                for year in year_columns:
                    ativo_circ_list.append(primary_frame.iloc[row][year])

            elif primary_frame.iloc[row][col] == 'Imobilizado':
                if imobilizado_duplicate == 0:
                    imobilizado_duplicate += 1
                    for year in year_columns:
                        imobilizado_list.append(primary_frame.iloc[row][year])
                else:
                    pass

            elif primary_frame.iloc[row][col] == 'Passivo Circulante':
                for year in year_columns:
                    passivo_circ_list.append(primary_frame.iloc[row][year])

            elif primary_frame.iloc[row][col] == 'Empréstimos e Financiamentos':
                if divida_curto_duplicate == 0:
                    divida_curto_duplicate += 1
                    for year in year_columns:
                        divida_curto_list.append(primary_frame.iloc[row][year])
                        divida_longo_list.append(primary_frame.iloc[row+2][year])
                else:
                    pass

            elif primary_frame.iloc[row][col] == 'Passivo Não Circulante':
                for year in year_columns:
                    passivo_ncirc_list.append(primary_frame.iloc[row][year])

            elif primary_frame.iloc[row][col] == 'Patrimônio Líquido Consolidado':
                for year in year_columns:
                    patr_liq_list.append(primary_frame.iloc[row][year])

            elif primary_frame.iloc[row][col] == 'Reservas de Lucros' or primary_frame.iloc[row][col] == 'Lucros/Prejuízos Acumulados':
                if lucro_acumul_duplicate == 0:
                    lucro_acumul_duplicate += 1
                    for year in year_columns:
                        lucro_acumul_list.append(primary_frame.iloc[row][year])
                else:
                    pass

            # Fill primary variable lists (DFC)
            elif primary_frame.iloc[row][col] == 'Lucro Líquido do exercício':
                for year in year_columns:
                    lucro_liq_exerc_list.append(primary_frame.iloc[row][year])

            elif primary_frame.iloc[row][col] in ['Aquisição de Imobilizado e Intangíveis',
                                'Adições de imobilizado', 'Compras de ativo imobilizado', 'Aquisições de imobilizado', 'Aquisições de Imobilizado',
                                'Aquisições de Imobilizado e Intangível', 'Aquisições de imobilizado e intangível', 'Aquisições de Imobilizados e Intangíveis (Exceto pelo Excedente de Cessão Onerosa)',
                                'Aquisições de imobilizados e intangíveis', 'Aquisições de imobilizado veículos frota', 'Aquisições de imobilizado de uso', 'Aquisições de Imobilizado de Uso',
                                'Aquisição de ativos imobilizados, intangível e propriedade para investimento']:
                for year in year_columns:
                    desp_ativo_fixo_list.append(primary_frame.iloc[row][year])

        # Build intermediate Variables
        desp_vga_list = np.array(desp_vendas_list) + np.array(desp_ga_list)
        divida_tot_list = np.array(divida_curto_list) + np.array(divida_longo_list)

        if lucro_brut_list == []:
            lucro_brut_list = np.zeros(len(year_columns))
        if desp_ped_list == []:
            desp_ped_list = np.zeros(len(year_columns))
        if dai_list == []:
            dai_list = np.zeros(len(year_columns))
        if desp_ativo_fixo_list == []:
            desp_ativo_fixo_list = np.zeros(len(year_columns))
        if lucro_liq_exerc_list == []:
            lucro_liq_exerc_list = lucro_liq_list

        # Build worked info
        marg_brut_list = 100 * np.divide(np.array(lucro_brut_list), np.array(receita_list))
        marg_liq_list = 100 * np.divide(np.array(lucro_liq_list), np.array(receita_list))
        vga_lucro_brut_list = 100 * np.divide(np.array(desp_vga_list), np.array(lucro_brut_list))
        ped_lucro_brut_list = 100 * np.divide(np.array(desp_ped_list), np.array(lucro_brut_list))
        deprec_lucro_brut_list = 100 * np.divide(np.array(dai_list), np.array(lucro_brut_list))
        juros_lucro_oper_list = 100 * np.divide(np.array(financeiro_list), np.array(lucro_oper_list))
        coef_liquidez_list = np.divide(np.array(ativo_circ_list), np.array(passivo_circ_list))
        passivo_tot_patrliq_list = np.divide((np.array(passivo_circ_list) + np.array(passivo_ncirc_list)), np.array(patr_liq_list))
        roe_list = 100 * np.divide(np.array(lucro_liq_list), np.array(patr_liq_list))
        roa_list = 100 * np.divide(np.array(lucro_liq_list), np.array(ativo_total_list))
        desp_ativo_fixo_lucro_liq_exerc_list = 100 * np.divide(np.array(desp_ativo_fixo_list), np.array(lucro_liq_exerc_list))
        divida_curto_tot_list = 100 * np.divide(np.array(divida_curto_list), np.array(divida_tot_list))
        divida_tot_lucro_oper_list = np.divide(np.array(divida_tot_list), np.array(lucro_oper_list))

        company_dict = {
        'year_columns': year_columns,
        'marg_brut_list': marg_brut_list,
        'marg_liq_list': marg_liq_list,
        'vga_lucro_brut_list': vga_lucro_brut_list,
        'ped_lucro_brut_list': ped_lucro_brut_list,
        'deprec_lucro_brut_list': deprec_lucro_brut_list,
        'juros_lucro_oper_list': juros_lucro_oper_list,
        'lucro_brut_list': lucro_brut_list,
        'lucro_liq_list': lucro_liq_list,
        'lucroporacao_list':lucroporacao_list,
        'coef_liquidez_list': coef_liquidez_list,
        'imobilizado_list': imobilizado_list,
        'passivo_tot_patrliq_list': passivo_tot_patrliq_list,
        'roe_list': roe_list,
        'roa_list': roa_list,
        'lucro_acumul_list': lucro_acumul_list,
        'desp_ativo_fixo_lucro_liq_exerc_list': desp_ativo_fixo_lucro_liq_exerc_list,
        'divida_curto_tot_list': divida_curto_tot_list,
        'divida_tot_lucro_oper_list': divida_tot_lucro_oper_list
        }

        return_dict_list.append(company_dict)

    return return_dict_list

