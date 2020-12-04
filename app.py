from flask import Flask, send_file, render_template, request
import os
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from joblib import load

#fig2,ax=plt.subplots(figsize=(6,3))
#ax = sns.set(style="darkgrid")
app = Flask(__name__)
port = int(os.environ.get("PORT", 5000))
#genre_model = load("genre_model")
#genre_list = ["Hip Hop", "Metal", "Pop", "Rock"]
#global lyrics
#lyrics = 100002
#print(os.listdir("../../DockerFlask3"))
df = pd.read_csv("../../DockerFlask3/Desafio4_ValidacionProba.csv")
#ax = sns.set(style="darkgrid")
#print(data.head(1))

@app.route('/')
def home():
    #credit_codes = df.SK_ID_CURR.unique()
    #cc_options = "<option value="" disabled selected>Elige una opción</option>"
    #i = 0
    #for credit_code in credit_codes:
    #    i = i+1
    #    cc_options = cc_options +  "<option value=" + str(i) + ">" + str(credit_code) + "</option>"
    return render_template('index.html')#, credit_code_options = cc_options)

@app.route('/predict')
def predict():
    fig2,ax=plt.subplots(figsize=(8,4))
    #lyrics = request.args.get('lyrics', '100002')
    #ax = sns.set(style="darkgrid")
    prob = df[df.SK_ID_CURR == int(lyrics)]

    #df_prediction = pd.concat([pd.DataFrame(genre_list, columns = ["Genre"]),
    #                       pd.DataFrame(prob[0], columns = ["Probability"])], axis = 1)
    
    #sns.kdeplot(data = df, x ="Probability")
    sns.kdeplot(data = df, x ="Probability", cumulative = True, fill = True)
    plt.xlabel("Probabilidad estimada de retraso en el pago", fontsize = 12)
    plt.ylabel("Percentil de morosidad", fontsize = 12)
    plt.title("Probabilidad de morosidad en relación a otras solicitudes de crédito")

    plt.axvline(prob.Probability.iloc[0], 0, 1, color = "dodgerblue", lw = 2)

    min_prob = df[df.Perc > 0.92].Probability.min()
    plt.axvline(min_prob, 0, 1, color = "tomato", lw = 2)
    plt.legend(["Probabilidad solicitud evaluada", "Probabilidad límite de aprobación"])
    
    canvas=FigureCanvas(fig2)
    img2 = io.BytesIO()
    fig2.savefig(img2)
    img2.seek(0)
    return send_file(img2,mimetype='img/png', cache_timeout=0);

#@app.route('/predict2')
#def predict2():
#    global lyrics = request.args.get('lyrics')

def ObtenerProbabilidad(dframe, Percentil):
    return str(int(round(dframe.Probability[dframe.Perc <= Percentil].max() * 100,0))) + "%"

@app.route("/prediction/")
def predict2():
    global lyrics
    lyrics = request.args.get('lyrics', '100001')
    df2 = df[df.SK_ID_CURR == float(lyrics)]

    if len(df2.Perc) == 0:
        return render_template('index.html')

    Perc = df2.Perc.iloc[0]
    if Perc < 0.92:
        estado = 'Aprobado'
    else:
        estado = 'Rechazado'

    prob_m = df2.Probability.iloc[0]

    pprob = {0.10 : ObtenerProbabilidad(df, 0.10),
            0.36 : ObtenerProbabilidad(df, 0.36),
            0.64 : ObtenerProbabilidad(df, 0.64),
            0.92 : ObtenerProbabilidad(df, 0.92),
            1 : ObtenerProbabilidad(df, 1)}
            
    if Perc <= 0.10:
	    clasificacion = "Clase A+"
	    CR = 1.05
    elif Perc <= 0.36:
	    clasificacion = "Clase A"
	    CR = 1.1
    elif Perc <= 0.64:
	    clasificacion = "Clase B"
	    CR = 1.2
    elif Perc <= 0.92:
	    clasificacion = "Clase C"
	    CR = 1.5
    else:
	    clasificacion = "Clase D"

    if clasificacion == "Clase D":
	    tasa = "No aplica"
    else:
        tasa = 0.02/(1-prob_m)*CR
        if tasa > 0.08:
            tasa = 0.08
        tasa = str(round(tasa*100,2)) + "%"

    return render_template('prediction.html',
        clase = clasificacion,
        aprob = estado,
        prob_morosidad = str(round(prob_m * 100,2)) + "%",
        rprob1 = "0% - " + pprob[0.10],
        rprob2 = pprob[0.10] + " - " + pprob[0.36],
        rprob3 = pprob[0.36] + " - " + pprob[0.64],
        rprob4 = pprob[0.64] + " - " + pprob[0.92],
        rprob5 = pprob[0.92] + " - 100%",
        tasa_int = tasa);

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=port)