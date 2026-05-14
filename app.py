from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])
def index():

    divergencias = []
    comparado = False

    if request.method == 'POST':

        comparado = True

        arquivo1 = request.files['planilha1']
        arquivo2 = request.files['planilha2']

        caminho1 = os.path.join(
            app.config['UPLOAD_FOLDER'],
            arquivo1.filename
        )

        caminho2 = os.path.join(
            app.config['UPLOAD_FOLDER'],
            arquivo2.filename
        )

        arquivo1.save(caminho1)
        arquivo2.save(caminho2)

        # LEITURA DAS PLANILHAS
        df1 = pd.read_excel(caminho1)
        df2 = pd.read_excel(caminho2)

        # ==========================
        # CONFIGURE AQUI
        # ==========================

        coluna_id = 'CPF'
        coluna_nome = 'NOME'
        coluna_valor = 'VALOR'

        # ==========================
        # LIMPEZA DOS DADOS
        # ==========================

        df1[coluna_id] = (
            df1[coluna_id]
            .astype(str)
            .str.replace('.', '', regex=False)
            .str.replace('-', '', regex=False)
            .str.strip()
        )

        df2[coluna_id] = (
            df2[coluna_id]
            .astype(str)
            .str.replace('.', '', regex=False)
            .str.replace('-', '', regex=False)
            .str.strip()
        )

        # VALORES NUMÉRICOS

        df1[coluna_valor] = pd.to_numeric(
            df1[coluna_valor],
            errors='coerce'
        )

        df2[coluna_valor] = pd.to_numeric(
            df2[coluna_valor],
            errors='coerce'
        )

        # ==========================
        # COMPARAÇÃO
        # ==========================

        merged = pd.merge(
            df1,
            df2,
            on=coluna_id,
            suffixes=('_1', '_2'),
            how='outer'
        )

        for _, row in merged.iterrows():

            valor1 = row.get(f'{coluna_valor}_1')
            valor2 = row.get(f'{coluna_valor}_2')

            nome1 = row.get(f'{coluna_nome}_1')
            nome2 = row.get(f'{coluna_nome}_2')

            nome = nome1 if pd.notna(nome1) else nome2

            # funcionário ausente

            if pd.isna(valor1):

                divergencias.append({
                    'cpf': row[coluna_id],
                    'nome': nome,
                    'tipo': 'Não existe na planilha 1',
                    'valor1': '-',
                    'valor2': valor2
                })

                continue

            if pd.isna(valor2):

                divergencias.append({
                    'cpf': row[coluna_id],
                    'nome': nome,
                    'tipo': 'Não existe na planilha 2',
                    'valor1': valor1,
                    'valor2': '-'
                })

                continue

            # valor diferente

            if valor1 != valor2:

                divergencias.append({
                    'cpf': row[coluna_id],
                    'nome': nome,
                    'tipo': 'Valor divergente',
                    'valor1': valor1,
                    'valor2': valor2
                })

    return render_template(
        'index.html',
        divergencias=divergencias,
        comparado=comparado
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)