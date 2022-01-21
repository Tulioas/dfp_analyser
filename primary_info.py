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
                interest_data = ['Receita de Venda de Bens e/ou Serviços', 'Resultado Bruto', 'Despesas com Vendas',
            'Despesas Gerais e Administrativas', 'Despesas/Receitas Operacionais', 'Resultado Antes do Resultado Financeiro e dos Tributos',
            'Resultado Financeiro', 'Resultado Antes dos Tributos sobre o Lucro', 'Resultado Líquido das Operações Continuadas',
            'Lucro Básico por Ação', 'ON', 'Lucro Diluído por Ação']

            elif file.find('BPA') != -1:
                interest_data = ['Ativo Total', 'Ativo Circulante', 'Imobilizado']

            elif file.find('BPP') != -1:
                interest_data = ['Passivo Total', 'Passivo Circulante', 'Passivo Não Circulante', 'Patrimônio Líquido Consolidado']

            elif file.find('DFC_MI') != -1:
                interest_data = ['Lucro Líquido do exercício', 'Depreciação, Amortização e Impairment']

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
            print("Year DFP folder is already filled. Check the need of extraction")

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
                company_frames.append(folder_list_2[company_index])

        # Construct and append a final dataframe for each company with all years information
        for company_index in range(len(companies)):
            serie = folder_list[company_index][['DS_CONTA', str(folder)]]
            company_frames[company_index] = company_frames[company_index].join(serie.set_index('DS_CONTA'), on='DS_CONTA')

    # pd.set_option('display.expand_frame_repr', False)
    # print(company_frames[0])

    return company_frames


def worked_info(companies=['AMBEV S.A.'], clear_prev_folder=False):

    # Create return variable
    return_dict_list = []

    # Extract primary information
    prim_info = primary_info(companies, clear_prev_folder=False)

    # Extract list of years collected
    year_columns = []
    for column in prim_info[0].columns:
        if '20' in column:
            year_columns.append(column)

    # Travel throught companies
    for comp_index in range(len(companies)):

        # Extract company frame
        primary_frame = prim_info[comp_index]
        #pd.set_option('display.expand_frame_repr', False)
        #print(primary_frame)

        # Initialize primary variables lists
        receita_list = []
        lucro_brut_list = []
        desp_vendas_list = []
        desp_ga_list = []
        desp_oper_list = []
        financeiro_list = []
        lucropreimp_list = []
        lucro_liq_list = []
        lucro_oper_list = []
        lucroporacao_list = []

        ativo_total_list = []
        ativo_circ_list = []
        imobilizado_list = []
        passivo_total_list = []
        passivo_circ_list = []
        patr_liq_list = []

        lucro_liq_exerc_list = []
        dai_list = []

        # Initialize intermediate variables
        desp_vga_list = []
        desp_ped_list = []

        # Travel trought cells
        for row in range(len(primary_frame)):

            col = 'DS_CONTA'
                
            # Fill primary variable lists (DRE)
            if primary_frame.iloc[row][col] == 'Receita de Venda de Bens e/ou Serviços':
                for year in year_columns:
                    receita_list.append(primary_frame.iloc[row][year])

            elif primary_frame.iloc[row][col] == 'Resultado Bruto':
                for year in year_columns:
                    lucro_brut_list.append(primary_frame.iloc[row][year])

            elif primary_frame.iloc[row][col] == 'Despesas com Vendas':
                for year in year_columns:
                    desp_vendas_list.append(primary_frame.iloc[row][year])

            elif primary_frame.iloc[row][col] == 'Despesas Gerais e Administrativas':
                for year in year_columns:
                    desp_ga_list.append(primary_frame.iloc[row][year])

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

            elif primary_frame.iloc[row][col] == 'Lucro Diluído por Ação':
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
                for year in year_columns:
                    imobilizado_list.append(primary_frame.iloc[row][year])

            elif primary_frame.iloc[row][col] == 'Passivo Total':
                for year in year_columns:
                    passivo_total_list.append(primary_frame.iloc[row][year])

            elif primary_frame.iloc[row][col] == 'Passivo Circulante':
                for year in year_columns:
                    passivo_circ_list.append(primary_frame.iloc[row][year])

            elif primary_frame.iloc[row][col] == 'Patrimônio Líquido Consolidado':
                for year in year_columns:
                    patr_liq_list.append(primary_frame.iloc[row][year])

            # Fill primary variable lists (DFC)
            elif primary_frame.iloc[row][col] == 'Lucro Líquido do exercício':
                for year in year_columns:
                    lucro_liq_exerc_list.append(primary_frame.iloc[row][year])

            elif primary_frame.iloc[row][col] == 'Depreciação, Amortização e Impairment':
                for year in year_columns:
                    dai_list.append(primary_frame.iloc[row][year])

        # Build intermediate Variables
        desp_vga_list = np.array(desp_vendas_list) + np.array(desp_ga_list)

        if desp_ped_list == []:
            desp_ped_list = np.zeros(len(year_columns))

        # Build worked info
        marg_brut_list = 100 * np.divide(np.array(lucro_brut_list), np.array(receita_list))
        marg_liq_list = 100 * np.divide(np.array(lucro_liq_list), np.array(receita_list))
        vga_lucro_brut_list = 100 * np.divide(np.array(desp_vga_list), np.array(lucro_brut_list))
        ped_lucro_brut_list = 100 * np.divide(np.array(desp_ped_list), np.array(lucro_brut_list))
        deprec_lucro_brut_list = 100 * np.divide(np.array(dai_list), np.array(lucro_brut_list))
        juros_lucro_oper_list = 100 * np.divide(np.array(financeiro_list), np.array(lucro_oper_list))
        coef_liquidez_list = np.divide(np.array(ativo_circ_list), np.array(passivo_circ_list))
        passivo_tot_patrliq_list = np.divide(np.array(passivo_total_list), np.array(patr_liq_list))
        roe_list = 100 * np.divide(np.array(lucro_liq_list), np.array(patr_liq_list))
        roa_list = 100 * np.divide(np.array(lucro_liq_list), np.array(ativo_total_list))

        company_dict = {
        'marg_brut_list': marg_brut_list,
        'marg_liq_list': marg_liq_list,
        'vga_lucro_brut_list': vga_lucro_brut_list,
        'ped_lucro_brut_list': ped_lucro_brut_list,
        'deprec_lucro_brut_list': deprec_lucro_brut_list,
        'juros_lucro_oper_list': juros_lucro_oper_list,
        'lucro_liq_list': lucro_liq_list,
        'lucroporacao_list':lucroporacao_list,
        'coef_liquidez_list': coef_liquidez_list,
        'ativo_circ_list': ativo_circ_list,
        'imobilizado_list': imobilizado_list,
        'passivo_tot_patrliq_list': passivo_tot_patrliq_list,
        'roe_list': roe_list,
        'roa_list': roa_list
        }

        return_dict_list.append(company_dict)

    return return_dict_list
