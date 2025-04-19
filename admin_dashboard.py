import streamlit as st
import pandas as pd
import mysql.connector
import io

# MySQL connection
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="activity_logs"
    )
    cursor = conn.cursor()

    # Fetch data
    cursor.execute("SELECT * FROM detections ORDER BY timestamp DESC LIMIT 100")
    rows = cursor.fetchall()

    # Define column headers based on your table structure
    columns = ['ID', 'Timestamp', 'Phone Users', 'Yawning Users', 'Session ID']
    df = pd.DataFrame(rows, columns=columns)

    # Show dashboard
    st.title("📊 Admin Dashboard - Phone & Yawning Detection Logs")
    st.write(df)

    # Stats summary
    total_logs = len(df)
    total_phone = df['Phone Users'].sum()
    total_yawn = df['Yawning Users'].sum()

    st.markdown(f"✅ Total Logs: **{total_logs}**")
    st.markdown(f"📱 Total Phone Usage Events: **{total_phone}**")
    st.markdown(f"😴 Total Yawning Events: **{total_yawn}**")

    # Export buttons
    st.download_button("⬇️ Download as CSV", df.to_csv(index=False), "logs.csv", "text/csv")

    try:
        import openpyxl
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        st.download_button("⬇️ Download as Excel", buffer.getvalue(), "logs.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except ImportError:
        st.warning("Install openpyxl to enable Excel export: `pip install openpyxl`")

except mysql.connector.Error as err:
    st.error(f"Database error: {err}")

finally:
    try:
        cursor.close()
        conn.close()
    except:
        pass