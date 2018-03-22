#%%
import pandas as pd
import numpy as np
from jieba import Tokenizer
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from mlxtend.preprocessing import DenseTransformer
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score



stop_words = [x.strip() for x in open('stopwords.txt')]
stop_words += '''
，
。
？
「
」
『
』
、
！
：
…
；
?
!
,
.
請問
我
如何
的
之
在
嗎
為何
是
哪裡
及
到
卻
請
哪些
可以
可否
會
可是
真
因為
如果
單位
哪個
'''.split('\n')


words = '''
亂丟
垃圾
柏油路面
被罰
低收入戶
為何
目前
'''.split('\n')

tokenizer = Tokenizer('./dict.txt.big.txt')

for word in words:
    tokenizer.add_word(word)


def read_answer(path):
    df = pd.read_csv(path, index_col=0)
    return df['地址'].to_dict()


def read_train_data(path, x_col, y_col):
    df = pd.read_csv(path, index_col=0)
    df.dropna(inplace=True)
    col_freq = \
        df[y_col].value_counts().to_frame() \
        .query('{} > 10'.format(y_col))
    df = df.query('{} in @col_freq.index'.format(y_col))
    size = col_freq[y_col][0]
    replace = True
    fn = lambda obj: pd.concat([
        obj,
        obj.loc[np.random.choice(obj.index, size - obj.index.size, replace),:]])
    df = df.groupby(y_col, as_index=False).apply(fn)
    X = df[x_col]
    X = df[x_col]
    Y = df[y_col]
    return (X, Y)


answer_data = read_answer('./高雄機關電話地址.csv')

path = './20170704_高雄市近期最常陳情FAQ.csv'
X, Y = read_train_data(path, '陳情內容', '回覆單位')

def analyzer(s):
    return [x for x in tokenizer.cut(s) if x not in stop_words]


label_encoder = LabelEncoder()
label_encoder = label_encoder
pipeline = Pipeline([
    ('vectorize', TfidfVectorizer(
        lowercase=False,
        analyzer=analyzer)),
    ('class', MultinomialNB()),
    ])

pipeline.fit(X, label_encoder.fit_transform(Y))

scores = cross_val_score(
    pipeline, X, label_encoder.fit_transform(Y), cv=10,
)

print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

#%%
import Levenshtein
import pandas as pd

# 讀取慣例庫
df_routine_table = pd.read_csv('routine_table.csv')
df_routine_table.fillna(value='', inplace=True) # 以免資料不等長出錯

# 計算和各類別的距離
df_routine_table['min_dist'] = [
    np.min([Levenshtein.distance('鑰匙掉了',i) for i in df_routine_table.iloc[i]])
    for i in range(df_routine_table.index.size)
]

# display(df_routine_table)

# display( 
#     df_routine_table.sort_values(by='min_dist').index[0]
# )


#%%
def predict(x):
    

    if not pipeline.named_steps['vectorize'].transform([x]).nnz:
        return \
                '請換個更仔細的方式再敘述您的問題！'
    answer = label_encoder.inverse_transform(pipeline.predict([x]))[0]
    answer_text = answer + '\n' + answer_data.get(answer, '')
    return answer_text


#%%
predict('')
