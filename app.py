import streamlit as st
import plotly.express as px
from utils import *

st.set_page_config(page_title="Portfolio Risk Analyzer", layout="wide")

st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        color: #DAF1DE;
    }
    [data-testid="stMetric"] {
        background: #0B2B26;
        border: 1px solid #235347;
        border-radius: 4px;
        padding: 16px;
    }
    h1 { color: #DAF1DE; font-weight: 600; }
    h3 { color: #8EB69B; font-size: 15px; text-transform: uppercase;
         letter-spacing: 0.08em; }
</style>
""", unsafe_allow_html=True)

st.title("Portfolio Risk & Performance Analyzer")

uploaded = st.file_uploader("Upload portfolio CSV (Ticker, Weight)", type="csv")
path = uploaded if uploaded else "portfolio.csv"

portfolio = load_portfolio(path)
prices = fetch_prices(portfolio["Ticker"].tolist())
returns = compute_returns(prices)
port_ret = portfolio_series(returns, portfolio)
m = metrics(port_ret)


def styled(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0B2B26",
        plot_bgcolor="#0B2B26",
        font_color="#DAF1DE",
        margin=dict(t=20, b=20, l=20, r=20),
    )
    return fig


c1, c2, c3, c4 = st.columns(4)
c1.metric("Annual Return", f"{m['annual_return']:.2%}")
c2.metric("Volatility", f"{m['annual_volatility']:.2%}")
c3.metric("Sharpe Ratio", f"{m['sharpe']:.2f}",
          delta="Below risk-free" if m["sharpe"] < 0 else "Above risk-free")
c4.metric("Max Drawdown", f"{m['max_drawdown']:.2%}")

st.subheader("Portfolio Growth")
cumulative = (1 + port_ret).cumprod()
cumulative.name = "Portfolio Value"
growth_fig = px.line(cumulative, labels={"value": "Growth (₹1 base)", "index": "Date"})
growth_fig.update_layout(showlegend=False)
st.plotly_chart(styled(growth_fig), width="stretch")

st.subheader("Correlation Matrix")
st.plotly_chart(
    styled(px.imshow(correlation_matrix(returns), text_auto=".2f",
                     aspect="auto", color_continuous_scale="Greens")),
    width="stretch",
)

st.subheader("Allocation")
st.plotly_chart(
    styled(px.pie(portfolio, values="Weight", names="Ticker",
                  color_discrete_sequence=px.colors.sequential.Greens_r)),
    width="stretch",
)