# conda install -c anaconda mysql-connector-python
# conda install -c conda-forge mysql

import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)  # max sütun
pd.set_option('display.max_rows', None)  #max satır
pd.set_option('display.float_format', lambda x: '%.5f' % x)  #virgülden sonra 5 hane

df= pd.read_excel("datasets/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df.head() #ilk 5 gözlem
df.describe().T  # quantity nin ort:9, std: 218 aykırılıklar olabilir.
df.shape #541910 gözlem birimi , 8 değişken var

# Veri setinde eksik gözlem varmı? Varsa hangi değişkende kaç tane eksik gözlem vardır?
df.isnull().sum()  # descriptionda 1454 tane, customerid de 135080 tane eksik gözlem var.

# Eksik gözlemleri veri setinden çıkartınız. Çıkarma işleminde ‘inplace=True’parametresini kullanınız.
df.dropna(inplace=True)

# essiz urun sayisi nedir?
df["StockCode"].nunique()
# 4070 tane eşsiz ürün var


# Hangi üründen kaçar tane vardır?
df["Description"].value_counts().head()

# En çok sipariş edilen 5 ürünü çoktan aza doğru sıralayınız.
df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()
# descriptiona göre group by alıp adetlerini topladıktan sonra adetlere göre çoktan aza sıraladık.

# Faturalardaki ‘C’ iptal edilen işlemleri göstermektedir. İptal edilen işlemleri veri setinden çıkartınız.
df = df[~df["Invoice"].str.contains("C", na=False)]

#  Fatura başına elde edilen toplam kazancı ifade eden ‘TotalPrice’ adında bir değişken oluşturunuz.
df["TotalPrice"] = df["Quantity"] * df["Price"]

df = df[df["TotalPrice"] > 0]
# fiyatı 0 dan büyük olmalı
df.head()

# Görev 2

df["InvoiceDate"].max()

today_date = dt.datetime(2011, 12, 11) #recency değeri 0 çıkmasın diye 2 gün ekledik analiz gününe

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                     'Invoice': lambda num: num.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})
# dataframe customerId ye göre  group by alındıktan sonra , invoicedate e todaydate den ilgili customer
# ın en son alışveriş tarihini çıkardık ve bunu gün cinsinden ver dedik. kaç gün önce alışveriş yapmış(recency)
rfm.head()

rfm.columns = ['recency', 'frequency', 'monetary']
# isimlendirdik


# Görev 3


rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])
# qcut fonksiyonuna bu değişkeni al değerlerini küçükten büyüğe sırala, 5'e böl en küçüğüne 5 en büyüğüne 1 de diyoruz
# az olan daha iyi yani daha yeni sipariş vermiş.düşüğe büyük puan veriyoruz recency değeri için.
rfm.head()
rfm.describe().T  #ortalama 93 gün önce sipariş verilmiş, ortalama 4 birim ürün alınmış
rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))
#rfm skorlarını oluşturduk


# Görev 4


# RFM isimlendirmesi
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
# segment mapimiz var. r' --> regex kullandığımızı ifade ediyor.(dictioanary)

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
# rfm dfsinin içerisine yeni bir değişken ekledik. rfm skorlarına seg_map i getirip yerletirdik
rfm.head()



# Görev 5


rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])
#segmentleri ve r,f,m değererini seçip seggment değişkenine göe group by yapıp ortalamasını ve sayısını aldık.
#about_to_sleep segmntinde 352 müşteri varmış, ortalama 53 gündür yoklar, ort 471 para bırkışlar
#şampiyonlar ort 6 gündür yoklar. 633 tane şampiyon varmış

new_df = pd.DataFrame()
new_df["loyal_customers"] = rfm[rfm["segment"] == "loyal_customers"].index
new_df.head()

new_df.to_csv("loyal_customers.csv")

# seçtiğim 3 segment;

# need_attention
# about_to_sleep segmentiyle r ve f skorlrı açısından benzer fakat monetary değeri çok daha yüksek.
# bu segment daha az fakat daha karlı ürün satın alıyor olabilir.
# İndirimli ürün veya set ürün tavsiyeleriyle alışveriş sıklıkları arttırılabilir. üst segmentlere çıkarılabilecek bir grup.

# Champions
# ortalama 6 gündür yoklar. Düzenli müşteri diyeiliriz. satın alma potansiyelleri çok yüksek.
# yeni ürün tavsiyeleri verilebilir.
# daha pahalı ürünler sunulabilir, monetaryleri diğer segmentlere göre çok yüksek.

# loyal_customers
# ortalama 33 gündür yoklar. alışveriş fekansları ortalama 6.
# satış arttırıcı kampanyalar yapılabilir. Loyal müşterilere özel hediyeler veya indirimler yapılabilir.
# recency değerini azaltıcak her 5 aışverişe şu kadar kupon gibi uygulamalar yapılabilir.
