# -*- coding: utf-8 -*-
"""
Created on Sat Apr 17 08:34:09 2021

@author: evule
"""

"""
dRt = a * (b - Rt) dt + sigma * sqrt(Rt) dWt

Descargo la informacion de https://fred.stlouisfed.org/series/TB3MS
Voy a aproximar la short rate (tasa instantanea) por esta t bill 3 meses en tna.
Para calibrar, uso la discretizacion simple (en realidad seria mejor la discretizacion por correlaciones) de CIR y simplemente igualo los momentos (de la continua y de la discreta)
Quedaria: Rt = drift * R(t-1) + sigma * sqrt(R(t-1) centrada) * N(0;1)
"""

import pandas as pd

df = pd.read_excel('TB3MS.xlsx')[10:]
df.columns = ['Date','Rate']
df.index = df.Date
df = pd.DataFrame(df.Rate)
df.columns = ['Rate']
df.Rate = df.Rate / 100

Desde = df.index.get_loc('2010-03-01')
Hasta = df.index.get_loc('2020-03-01') + 1

df = df[Desde:Hasta]
print(df)

#Primero estimo la tasa de largo plazo:
b = df.Rate.mean()
print(b)

#Por conveniencia al discretizar, centro la tasa:
df['CenteredRate'] = df.Rate - b
print(df)

drift=0.2 #Le doy un valor inicial

#Voy a minimizar la suma de los errores (ResidualTerm) al cuadro
#Quiero minimizar RSS haciendo variar el drift
from scipy.optimize import minimize_scalar
def RSS(drift):
    return (((df.CenteredRate - drift * df.CenteredRate.shift(1)) **2) / (df.CenteredRate + b)).sum()
drift = minimize_scalar(RSS).x
print(drift)

df['ResidualTerm'] = ((df.CenteredRate - drift * df.CenteredRate.shift(1)) **2) / (df.CenteredRate + b)
df['ResidualTerm'].fillna(0, inplace = True)
print(df.head())
RSS=df['ResidualTerm'].sum()
print(RSS)

#Ahora igualo los momentos del proceso original y del discretizado, para estimar el resto de los parametros.
#Si el intervalo de tiempo es corto, la aproximacion es buena incluso si estamos trabajando con tasas anualizadas.
import math
a = - math.log(drift) #Es el logaritmo natural ln
print(a)

#Ahora con la volatilidad
DiscreteVolatility = (RSS / (len(df) - 2)) **0.5 #En realidad es dividido n-1, pero como en la primera fila me quedo N/A y lo reemplace por 0, pongo n-2
print(DiscreteVolatility)

ContinuosVolatility = (DiscreteVolatility**2 * (1-math.exp(-2*a)) / (2*a)) ** 0.5 #En algunos papers esta al reves numerador y denominador: 2a/(1-exp...)
print(ContinuosVolatility)

#Ahora q tengo los parametros a,b y ContinuosVolatility (sigma) puedo simular la short rate:
#Rt = R(t-1) + a * (b - R(t-1)) dt + sigma * sqrt(R(t-1)) * sqrt(dt) * e(t)
# Esto es pq aplico the Euler scheme, tambien conocido como la aproximacion de Euler-Maruyama
#Donde e(t) es NORMSINV(RAND())
#Esta aproximacion sirve para un dt chico, ya q el modelo es para la tasa instantanea(short rate)
#Si quiero extrapolar a tasas de mas largo plazo, puedo suponer q se mantiene la relacion con la tasa mas corta en terminos absolutos o relativos (esto ultimo es lo q hace el modelo de precios relativos)


