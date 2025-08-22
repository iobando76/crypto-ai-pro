import time, requests, pandas as pd, streamlit as st
from os import getenv
API_URL = getenv('API_URL', 'http://localhost:8000')
st.set_page_config(page_title='Crypto Assistant – PRO', layout='wide')
st.title('Crypto Assistant – PRO')
colA, colB = st.columns([2,2])
with colA:
    st.subheader('Cuenta')
    try:
        acc = requests.get(f"{API_URL}/account", timeout=10).json()
        st.metric('Equity (USDT)', f"{acc['equity_usdt']:.2f}")
    except Exception as e:
        st.error(f'No se pudo leer cuenta: {e}')
with colB:
    st.subheader('Señales pendientes')
    try:
        sigs = requests.get(f"{API_URL}/signals?status=pending", timeout=10).json()
        df = pd.DataFrame(sigs) if sigs else pd.DataFrame()
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f'Error obteniendo señales: {e}')
st.subheader('Aprobación manual')
signal_id = st.number_input('ID de la señal', min_value=1, step=1)
qty = st.text_input('Cantidad (opcional)')
if st.button('Aprobar'):
    try:
        params = {}
        if qty.strip(): params['qty'] = float(qty)
        r = requests.post(f"{API_URL}/signals/{int(signal_id)}/approve", params=params, timeout=20)
        st.success(r.json())
        time.sleep(1)
        st.experimental_rerun()
    except Exception as e:
        st.error(str(e))
if st.button('Rechazar'):
    try:
        r = requests.post(f"{API_URL}/signals/{int(signal_id)}/reject", timeout=20)
        st.warning(r.json())
        time.sleep(1)
        st.experimental_rerun()
    except Exception as e:
        st.error(str(e))
