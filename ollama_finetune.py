import pandas as pd
import multiprocessing, os, sys
from groq import Groq
# 將 KG_RAG 目錄添加到 sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "KG_RAG"))
df = pd.read_csv('dataset.csv')
df2 = pd.read_csv('dataset(no_law).csv')
inputs = df["模擬輸入內容"].tolist()
template_output = df2["gpt-4o-mini-2024-07-18\n3000筆"].tolist()
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)


laws = ""
prompt = f"""
請嚴格遵照範例格式撰寫，確保語言嚴謹，條理清晰

**範例格式：**
一、事故發生緣由：(結合事故發生緣由以及原告受傷情形)
緣原告/被告於...
二、法律依據：
{laws}
三、損害賠償請求：
(一)原告xxx部分:
1. 費用:xx元
原告xxx因為...
(二)原告xxx部分:
1. 費用 :xx元
原告xxx因為...
四、總結賠償請求：
綜上所陳，被告xxx應連帶賠償原告之損害，包含：...總計...
"""
tmp_input = """一、事故發生緣由：
被告於民國94年10月10日20時6分許，駕駛車牌號碼3191-XA號自小客車，沿台南縣山上鄉○○村○○○○○道路由東往西方向行駛，於行經明和村明和192之6號前時，原應注意汽車不得逆向行駛，且應注意車前狀況，並減速慢行，作好隨時準備煞車之安全措施，依當時天氣晴朗、路面平坦無缺陷、無障礙物、桅距良好等，並無不能注意之情事，竟仍疏未注意，逆向駛入對向車道，致其上開自小客車車頭與由乙○○所騎乘、後方搭載其妹丙○○，行駛於對向車道之UWL-1855號輕型機車發生對撞，致原告乙○○、丙○○人車倒地。

二、原告受傷情形：
原告乙○○因而受有頭部挫傷合併顏面多處擦傷及牙齒斷裂、下腹部挫傷合併恥骨之兩側下分枝斷裂（骨折）、右側卵巢巧克力囊腫破裂致腹膜炎等傷害，丙○○因而受有顱腦損傷、顱內出血、顏面骨骨折等傷害。

三、請求賠償的事實根據：
（一）丙○○部分：
1. 醫藥費用：共新台幣38,706元。

2. 不能工作之損失：原告因傷至少2個月不能工作，以92年、93年度扣繳憑單給付總額之平均數1個月34,860元計算，共損失69,728元。

3. 精神慰撫金：原告因被告之侵權行為導致顱內出血及顏面骨折，有頭疼、頭暈且記憶力減退之後遺症等現象，均影響生活、工作及女生外貌甚鉅，導致原告精神痛苦不堪，為此爰請求精神賠償300,000元。

（二）乙○○部分:
1. 醫藥費用：共274,874元。

2. 不能工作之損失：原告因傷無法工作期間達6個月以上，以其92年度綜合所得稅各類所得資料可知其每月工作所得為30,157元，以6個月計，則損失約180,942元。

3. 精神慰撫金：原告因被告之侵權行為而導致下腹部挫傷合併恥骨骨折、卵巢破裂合併內出血等傷害，已切除卵巢百分之50且可能導致終生不孕。而生育對多數女性而言乃視為極為重要之天職，若無法生孕，甚至可能造成婚姻之不幸福及家庭之缺憾，因而使原告極其痛苦，爰請求精神慰撫金2,000,000元。

4. 原告乙○○大學畢業，現在豐年豐和企業股份有限公司上班，月薪約30,000元左右，名下無不動產；原告丙○○為二專畢業，受傷之前的月薪約34,000元左右，名下有汽車1輛，無不動產。"""
input = f"""
輸入:
{tmp_input}
{prompt}
"""

def generate_response(input_data):
    """發送單次生成請求並回傳結果"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": input_data,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"



def worker(input_data):
    """處理單個生成請求並輸出結果"""
    from KG_RAG.KG_Generate import generate_legal_references, split_input
    global laws
    data = split_input(input_data)
    laws = generate_legal_references(data["case_facts"], data["injury_details"])
    result = generate_response(input_data)
    print(f"{result}\n{'-' * 50}")  # 實時顯示輸出
    return result

if __name__ == "__main__":
    inputs = [input] * 5
    multiprocessing.set_start_method("spawn")
    with multiprocessing.Pool(processes=5) as pool:
        # 使用 map 同時對10個輸入進行處理
        results = pool.map(worker, inputs)