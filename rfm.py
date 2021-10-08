
import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)  
pd.set_option('display.max_rows', None) 
pd.set_option('display.float_format', lambda x: '%.5f' % x) 

df= pd.read_excel("datasets/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df.head() 
df.describe().T  # quantity nin ort:9, std: 218 aykırılıklar olabilir.
df.shape #541910 gözlem birimi , 8 değişken var

df.isnull().sum()

df.dropna(inplace=True)


df["StockCode"].nunique()


df["Description"].value_counts().head()


df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()


# Faturalardaki ‘C’ iptal edilen işlemleri göstermektedir. İptal edilen işlemleri veri setinden çıkarttık.
df = df[~df["Invoice"].str.contains("C", na=False)]

#  Fatura başına elde edilen toplam kazancı ifade eden ‘TotalPrice’ adında bir değişken oluştursuk.
df["TotalPrice"] = df["Quantity"] * df["Price"]

df = df[df["TotalPrice"] > 0]
# fiyatı 0 dan büyük olmalı
df.head()

# RFM metriklerinin hesaplanması

df["InvoiceDate"].max()

today_date = dt.datetime(2011, 12, 11)

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                     'Invoice': lambda num: num.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})
rfm.head()

rfm.columns = ['recency', 'frequency', 'monetary']



#RFM skorlarının oluşturulması


rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm.head()
rfm.describe().T
rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))



# RFM skorlarının segment olarak tanımlanması
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
rfm.head()

rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])


