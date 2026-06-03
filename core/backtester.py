st.subheader("📊 Strategy Backtest")

try:

    st.write("Before Backtest")
    st.write(df.columns.tolist())

    result = run_backtest(df)

    st.write("After Backtest")
    st.write(result)

except Exception as e:

    import traceback

    st.error(str(e))
    st.code(traceback.format_exc())
