from flask import Flask, render_template, request

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def encontrar_coluna(df, possibilidades):
    colunas = {col.lower().strip(): col for col in df.columns}

    for possibilidade in possibilidades:
        for coluna_lower, coluna_original in colunas.items():
            if possibilidade in coluna_lower:
                return coluna_original

    return None


@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    erro = None

    if request.method == 'POST':
        try:
            arquivo1 = request.files['planilha1']
            arquivo2 = request.files['planilha2']

            caminho1 = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(arquivo1.filename))
            caminho2 = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(arquivo2.filename))

            arquivo1.save(caminho1)
            arquivo2.save(caminho2)

            df1 = pd.read_excel(caminho1)
            df2 = pd.read_excel(caminho2)

            id1 = encontrar_coluna(df1, ['cpf', 'matricula', 'funcionario', 'codigo', 'id'])
            id2 = encontrar_coluna(df2, ['cpf', 'matricula', 'funcionario', 'codigo', 'id'])

            valor1 = encontrar_coluna(df1, ['valor', 'salario', 'líquido', 'liquido', 'pagamento', 'total'])
            valor2 = encontrar_coluna(df2, ['valor', 'salario', 'líquido', 'liquido', 'pagamento', 'total'])

            nome1 = encontrar_coluna(df1, ['nome', 'funcionario', 'colaborador'])
            nome2 = encontrar_coluna(df2, ['nome', 'funcionario', 'colaborador'])

            if not id1 or not id2:
                erro = 'Não foi possível identificar a coluna de identificação.'
                return render_template('index.html', erro=erro)

            if not valor1 or not valor2:
                erro = 'Não foi possível identificar a coluna de valores.'
                return render_template('index.html', erro=erro)

            df1 = df1[[id1, valor1] + ([nome1] if nome1 else [])]
            df2 = df2[[id2, valor2] + ([nome2] if nome2 else [])]

            df1.columns = ['ID', 'VALOR_1'] + (['NOME'] if nome1 else [])
            df2.columns = ['ID', 'VALOR_2'] + (['NOME_2'] if nome2 else [])

            comparacao = pd.merge(df1, df2, on='ID', how='outer')

            comparacao['VALOR_1'] = pd.to_numeric(comparacao['VALOR_1'], errors='coerce').fillna(0)
            comparacao['VALOR_2'] = pd.to_numeric(comparacao['VALOR_2'], errors='coerce').fillna(0)

            comparacao['DIFERENCA'] = comparacao['VALOR_1'] - comparacao['VALOR_2']

            divergencias = comparacao[comparacao['DIFERENCA'] != 0]

            resultado = divergencias.to_dict(orient='records')

        except Exception as e:
            erro = str(e)

    return render_template('index.html', resultado=resultado, erro=erro)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)