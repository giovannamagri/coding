import pandas as pd
import numpy as np

file_path = "/Users/accountmario/Desktop/matrix.xlsx"
df = pd.read_excel(file_path, sheet_name="betastardata")

#CREO SHARES 

total_op_rev = df.drop_duplicates(subset=["Firm"])["Op. Rev."].sum()
df["Op. Rev._Total"] = total_op_rev
df["Op. Rev. Fraction"] = df["Op. Rev."] / df["Op. Rev._Total"]
print(df)

#SPLIT DATASET 

df_betastar = df[~df['Sh.'].isin(df['Firm'])]
df_beta = df[df['Sh.'].isin(df['Firm'])]

print("dataset betastar")
print(df_betastar)
print("dataset beta")
print(df_beta)

#BETASTAR

betastarmatrix = df_betastar.pivot(index='Sh.', columns='Firm', values='Beta')
betastarmatrix = betastarmatrix.fillna(0)
print("beta star matrix:")
print(betastarmatrix)

#BETA

identificatori = list(set(df_beta['Sh.']).union(set(df_beta['Firm'])))
betamatrix = pd.DataFrame(index=identificatori, columns=identificatori)
betamatrix.update(df_beta.pivot_table(index='Sh.', columns='Firm', values='Beta', fill_value=0))
betamatrix = betamatrix.fillna(0)

print("beta matrix:")
print(betamatrix)

#FARE IN MODO CHE LE COLONNE DI BETASTAR COINCIDANO CON LE RIGHE DI BETA 

betastarmatrix = betastarmatrix[betamatrix.index]

print("betastarmatrix correct:")
print(betastarmatrix)

#CALCOLO ULTIMATE BETA 
num_cols = betamatrix.shape[1]
I = np.identity(num_cols)
I_minus_beta = I - betamatrix
beta_inverse = np.linalg.inv(I_minus_beta)
beta_u = np.dot(betastarmatrix.values, beta_inverse)
beta_u = pd.DataFrame(data=beta_u, index=betastarmatrix.index, columns=betastarmatrix.columns)

print("Matrice beta_u:")
print(beta_u)


#CALCOLO WEIGHTS 

num_matrix = beta_u.T.dot(beta_u)
den_matrix = beta_u.apply(lambda x: np.sum(x**2)).values

weights = num_matrix / den_matrix
weights.index = weights.columns = beta_u.columns

print("weights ultimate")
print(weights)

#CALCOLO I WEIGHTS MEDI 

media_weights = np.mean(weights)
print(media_weights)

#CALCOLO WEIGHTS UTILIZZANDO I DIRECT BETA INVECE DEGLI ULTIMATE 

betastarmatrix = pd.DataFrame(data=betastarmatrix, index=betastarmatrix.index, columns=betastarmatrix.columns)

num_matrix = betastarmatrix.T.dot(betastarmatrix)
den_matrix = betastarmatrix.apply(lambda x: np.sum(x**2)).values

weights_direct = num_matrix / den_matrix
weights_direct.index = weights_direct.columns = betastarmatrix.columns

#CALCOLO I WEIGHTS MEDI CON DIRECT BETA 

media_weights_direct = np.mean(weights_direct)
#print(media_weights_direct)

print("Media direct weights", media_weights_direct)
print("Media ultimate weights", media_weights)

#GHHI

#creo dataset weights 
w_data = []

for firm1 in weights.columns:
    for firm2 in weights.index:
        if firm1 != firm2:
            w_data.append({'Firm 1': firm1, 'Firm 2': firm2, 'W': weights.at[firm2, firm1]})

w_dataset = pd.DataFrame(w_data)
print(w_dataset)

op_rev_frac_dict = dict(zip(df['Firm'], df['Op. Rev. Fraction']))

GHHI_w_dataset = w_dataset.copy()  # Copia del secondo dataset

# Aggiunta delle colonne Op. Rev. Fraction per Firm 1 e Firm 2
GHHI_w_dataset['Op. Rev. Fraction Firm 1'] = GHHI_w_dataset['Firm 1'].map(op_rev_frac_dict)
GHHI_w_dataset['Op. Rev. Fraction Firm 2'] = GHHI_w_dataset['Firm 2'].map(op_rev_frac_dict)

print(GHHI_w_dataset)
ghhi = (GHHI_w_dataset['W'] * GHHI_w_dataset['Op. Rev. Fraction Firm 1'] * GHHI_w_dataset['Op. Rev. Fraction Firm 2']).sum()
print("GHHI:", ghhi)

#CALCOLO GHHI IGNORANDO I PESI RELATIVI IN TERMINI DI OP. REV. DELLE IMPRESE 
op_rev_fraction_media = GHHI_w_dataset['Op. Rev. Fraction Firm 1'].mean()
GHHI_w_dataset['Op. Rev. Fraction Media'] = op_rev_fraction_media
print(GHHI_w_dataset)

# Calcola l'indice GHHI utilizzando l'Op. Rev. Fraction medio per tutte le aziende
ghhi_con_media = (GHHI_w_dataset['W'] * GHHI_w_dataset['Op. Rev. Fraction Media'] * GHHI_w_dataset['Op. Rev. Fraction Media']).sum()

#confronto tra i due valori 
print("GHHI con Op. Rev. Fraction Media:", ghhi_con_media)
print("GHHI:", ghhi)

#CALCOLO CO_P PER I SINGOLI SH. 


beta_u = pd.DataFrame(data=beta_u, index=betastarmatrix.index, columns=betastarmatrix.columns)

den_matrix = beta_u.apply(lambda x: np.sum(x**2)).values

beta_u_array = beta_u.values  # Converte beta_u in un array numpy

num_matrix_kappa = np.zeros_like(beta_u_array)
num_righe, num_colonne = beta_u.shape
for i in range(num_righe):
    for j in range(num_colonne):
        if i != j:
            # Calcola la somma dei valori beta_i,f per f diverso da j
            somma_beta = np.sum(beta_u_array[i, np.arange(num_colonne) != j])
            # Calcola kappa_i,j
            num_matrix_kappa[i, j] = beta_u_array[i, j] * somma_beta

# Stampa la matrice num_matrix_kappa
print("Matrice num_matrix_kappa:")
print(num_matrix_kappa)

kappa = num_matrix_kappa / den_matrix
kappa = pd.DataFrame(data=kappa, index=beta_u.index, columns=beta_u.columns)

print("Matrice kappa:")
print(kappa)


kappa = pd.DataFrame(data=kappa, index=kappa.index, columns=kappa.columns)
CO_p = kappa.sum(axis=1)
CO_p = pd.DataFrame(data=CO_p, index=kappa.index)


# Stampa il vettore CO_p
print(CO_p)
total_sum = CO_p.sum()
CO_p_percent = (CO_p / total_sum) * 100
print(CO_p_percent)




